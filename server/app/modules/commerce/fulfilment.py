from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.commerce.lifecycle import _record_event
from app.modules.commerce.models import Fulfilment, Order


def _get_or_create_fulfilment(session: Session, business_id: UUID, order_id: UUID) -> Fulfilment:
    f = session.scalar(
        select(Fulfilment)
        .where(Fulfilment.business_id == business_id, Fulfilment.order_id == order_id)
        .with_for_update()
    )
    if not f:
        f = Fulfilment(business_id=business_id, order_id=order_id, status="pending")
        session.add(f)
        session.flush()
    return f


def set_tracking_information(
    session: Session,
    business_id: UUID,
    order_id: UUID,
    carrier: str,
    tracking_number: str,
    tracking_url: str | None = None,
) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status in (
        "pending_checkout",
        "pending_payment",
        "cancelled",
        "refund_pending",
        "refunded",
    ):
        raise CommercialError(400, "INVALID_STATE", "Cannot set tracking info on this order state")

    fulfilment = _get_or_create_fulfilment(session, business_id, order_id)
    fulfilment.carrier = carrier
    fulfilment.tracking_number = tracking_number
    fulfilment.tracking_url = tracking_url


def mark_order_shipped(session: Session, business_id: UUID, order_id: UUID) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status in ("shipped", "delivered"):
        return

    if order.status not in ("paid", "confirmed", "processing"):
        raise CommercialError(400, "INVALID_STATE", f"Cannot ship order from state: {order.status}")

    fulfilment = _get_or_create_fulfilment(session, business_id, order_id)
    fulfilment.status = "shipped"
    fulfilment.shipped_at = datetime.now(UTC)

    prev = order.status
    order.status = "shipped"
    _record_event(session, business_id, order_id, "order.shipped", prev, "shipped", "merchant")


def mark_order_delivered(session: Session, business_id: UUID, order_id: UUID) -> None:
    order = session.scalar(
        select(Order)
        .where(Order.business_id == business_id, Order.id == order_id)
        .with_for_update()
    )
    if not order:
        raise CommercialError(404, "NOT_FOUND", "Order not found")

    if order.status == "delivered":
        return

    if order.status != "shipped":
        raise CommercialError(
            400, "INVALID_STATE", f"Cannot deliver order from state: {order.status}"
        )

    fulfilment = _get_or_create_fulfilment(session, business_id, order_id)
    fulfilment.status = "delivered"
    fulfilment.delivered_at = datetime.now(UTC)

    prev = order.status
    order.status = "delivered"
    _record_event(session, business_id, order_id, "order.delivered", prev, "delivered", "merchant")
