from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.commerce.models import Fulfilment, Order, OrderEvent
from app.modules.inventory.reservation import release_order_reservations


def _record_event(
    session: Session,
    business_id: UUID,
    order_id: UUID,
    event_type: str,
    prev: str | None,
    new: str,
    source: str,
    metadata: dict | None = None,
) -> None:
    event = OrderEvent(
        business_id=business_id,
        order_id=order_id,
        event_type=event_type,
        previous_status=prev,
        new_status=new,
        source=source,
        metadata_payload=metadata,
    )
    session.add(event)


def mark_order_paid_from_verified_payment(
    session: Session, business_id: UUID, order_id: UUID, payment_id: UUID
) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status == "paid":
        return

    if order.status == "cancelled":
        raise CommercialError(
            409, "ORDER_CANCELLED", "Order was cancelled before payment was verified"
        )

    if order.status != "pending_payment":
        raise CommercialError(400, "INVALID_STATE", f"Cannot mark paid from state: {order.status}")

    prev = order.status
    order.status = "paid"
    _record_event(
        session,
        business_id,
        order.id,
        "order.paid",
        prev,
        "paid",
        "payment_service",
        {"payment_id": str(payment_id)},
    )


def confirm_order(session: Session, business_id: UUID, order_id: UUID) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status == "confirmed":
        return

    if order.status != "paid":
        raise CommercialError(400, "INVALID_STATE", f"Cannot confirm from state: {order.status}")

    prev = order.status
    order.status = "confirmed"
    _record_event(session, business_id, order.id, "order.confirmed", prev, "confirmed", "merchant")


def process_order(session: Session, business_id: UUID, order_id: UUID) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status == "processing":
        return

    if order.status != "confirmed":
        raise CommercialError(400, "INVALID_STATE", f"Cannot process from state: {order.status}")

    prev = order.status
    order.status = "processing"
    _record_event(
        session, business_id, order.id, "order.processing", prev, "processing", "merchant"
    )


def cancel_order(session: Session, business_id: UUID, order_id: UUID, reason: str) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status in ("cancelled", "refund_pending", "refunded"):
        return

    if order.status in ("shipped", "delivered"):
        raise CommercialError(400, "INVALID_STATE", f"Cannot cancel from state: {order.status}")

    prev = order.status
    if order.status in ("pending_checkout", "pending_payment"):
        order.status = "cancelled"
        _record_event(
            session,
            business_id,
            order.id,
            "order.cancelled",
            prev,
            "cancelled",
            "merchant",
            {"reason": reason},
        )
        release_order_reservations(session, business_id, order.id)
    else:
        # paid, confirmed, processing -> refund required
        order.status = "refund_pending"
        _record_event(
            session,
            business_id,
            order.id,
            "order.refund_pending",
            prev,
            "refund_pending",
            "merchant",
            {"reason": reason},
        )


def get_order_status(session: Session, business_id: UUID, buyer_id: UUID, order_id: UUID) -> dict:
    order = session.scalar(
        select(Order).where(
            Order.business_id == business_id,
            Order.buyer_id == buyer_id,
            Order.id == order_id,
        )
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    fulfilment = session.scalar(
        select(Fulfilment).where(
            Fulfilment.business_id == business_id, Fulfilment.order_id == order_id
        )
    )

    return {
        "order_id": str(order.id),
        "status": order.status,
        "created_at": order.created_at.isoformat(),
        "fulfilment_status": fulfilment.status if fulfilment else None,
        "tracking_carrier": fulfilment.carrier if fulfilment else None,
        "tracking_number": fulfilment.tracking_number if fulfilment else None,
        "tracking_url": fulfilment.tracking_url if fulfilment else None,
    }
