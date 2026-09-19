from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.commerce.models import OrderItem
from app.modules.inventory.models import Inventory, StockMovement, StockReservation


def _get_active_reserved_qty(session: Session, business_id: UUID, product_id: UUID) -> float:
    now = datetime.now(UTC)
    result = session.scalar(
        select(func.sum(StockReservation.quantity)).where(
            StockReservation.business_id == business_id,
            StockReservation.product_id == product_id,
            StockReservation.status == "ACTIVE",
            StockReservation.expires_at > now,
        )
    )
    return float(result) if result is not None else 0.0


def reserve_order_stock(
    session: Session, business_id: UUID, order_id: UUID, expires_in_minutes: int = 15
) -> list[StockReservation]:
    now = datetime.now(UTC)

    # Idempotency check
    existing = session.scalars(
        select(StockReservation).where(
            StockReservation.business_id == business_id,
            StockReservation.order_id == order_id,
        )
    ).all()

    if existing:
        return list(existing)

    # Fetch order items
    order_items = session.scalars(
        select(OrderItem).where(OrderItem.order_id == order_id).order_by(OrderItem.product_id)
    ).all()

    if not order_items:
        raise CommercialError(400, "INVALID_ORDER", "Order has no items.")

    # Lock inventory rows in product_id order (deadlock prevention)
    product_ids = [item.product_id for item in order_items]
    inventories = session.scalars(
        select(Inventory)
        .where(Inventory.business_id == business_id, Inventory.product_id.in_(product_ids))
        .order_by(Inventory.product_id)
        .with_for_update()
    ).all()

    inventory_map = {inv.product_id: inv for inv in inventories}

    for item in order_items:
        inv = inventory_map.get(item.product_id)
        if not inv:
            raise CommercialError(
                404, "NOT_FOUND", f"Inventory record missing for {item.product_id}"
            )

        reserved = _get_active_reserved_qty(session, business_id, item.product_id)
        available = float(inv.on_hand_qty) - reserved

        if available < float(item.quantity):
            raise CommercialError(
                409,
                "INSUFFICIENT_STOCK",
                f"Insufficient available stock for product {item.product_id}",
            )

    # Create reservations
    reservations = []
    expires_at = now + timedelta(minutes=expires_in_minutes)
    for item in order_items:
        res = StockReservation(
            business_id=business_id,
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            status="ACTIVE",
            expires_at=expires_at,
        )
        session.add(res)
        reservations.append(res)

    session.flush()
    return reservations


def release_order_reservations(session: Session, business_id: UUID, order_id: UUID) -> None:
    reservations = session.scalars(
        select(StockReservation)
        .where(
            StockReservation.business_id == business_id,
            StockReservation.order_id == order_id,
            StockReservation.status == "ACTIVE",
        )
        .with_for_update()
    ).all()

    for res in reservations:
        res.status = "RELEASED"

    session.flush()


def expire_reservations(session: Session) -> int:
    now = datetime.now(UTC)
    reservations = session.scalars(
        select(StockReservation)
        .where(StockReservation.status == "ACTIVE", StockReservation.expires_at <= now)
        .with_for_update(skip_locked=True)
    ).all()

    for res in reservations:
        res.status = "EXPIRED"

    session.flush()
    return len(reservations)


def consume_order_reservations(
    session: Session, business_id: UUID, order_id: UUID, movement_key_prefix: str
) -> bool:
    """
    Attempts to permanently consume stock for an order.
    Returns True if successful.
    Returns False if reconciliation is required (e.g., late payment with no stock).
    """
    now = datetime.now(UTC)

    reservations = session.scalars(
        select(StockReservation)
        .where(StockReservation.business_id == business_id, StockReservation.order_id == order_id)
        .order_by(StockReservation.product_id)
        .with_for_update()
    ).all()

    if not reservations:
        raise CommercialError(404, "NOT_FOUND", "No reservations found for order.")

    # Idempotency
    if all(r.status == "CONSUMED" for r in reservations):
        return True

    # Lock inventory
    product_ids = [r.product_id for r in reservations]
    inventories = session.scalars(
        select(Inventory)
        .where(Inventory.business_id == business_id, Inventory.product_id.in_(product_ids))
        .order_by(Inventory.product_id)
        .with_for_update()
    ).all()

    inventory_map = {inv.product_id: inv for inv in inventories}

    # Verification pass
    for res in reservations:
        inv = inventory_map.get(res.product_id)
        if not inv:
            raise CommercialError(500, "INTERNAL_ERROR", f"Inventory missing for {res.product_id}")

        is_active = res.status == "ACTIVE" and res.expires_at > now
        if not is_active:
            # If expired/released, check if we can still grab it
            reserved = _get_active_reserved_qty(session, business_id, res.product_id)
            available = float(inv.on_hand_qty) - reserved
            if available < float(res.quantity):
                return False  # Reconciliation required

    # Allocation pass
    for res in reservations:
        if res.status == "CONSUMED":
            continue

        inv = inventory_map[res.product_id]
        new_on_hand = float(inv.on_hand_qty) - float(res.quantity)

        if new_on_hand < 0:
            raise CommercialError(500, "INTERNAL_ERROR", "Negative stock not allowed.")

        movement = StockMovement(
            business_id=business_id,
            product_id=res.product_id,
            movement_key=f"{movement_key_prefix}-{order_id}-{res.product_id}",
            quantity_delta=-res.quantity,
            resulting_on_hand_qty=new_on_hand,
        )
        session.add(movement)

        inv.on_hand_qty = new_on_hand
        inv.version += 1
        res.status = "CONSUMED"

    session.flush()
    return True
