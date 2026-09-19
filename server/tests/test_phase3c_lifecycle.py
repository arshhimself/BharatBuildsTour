import os
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.commerce.fulfilment import (
    mark_order_delivered,
    mark_order_shipped,
    set_tracking_information,
)
from app.modules.commerce.lifecycle import (
    cancel_order,
    confirm_order,
    mark_order_paid_from_verified_payment,
    process_order,
)

if os.environ.get("STOCKAWARE_RUN_PG_TESTS") != "1":
    pytest.skip(
        "set STOCKAWARE_RUN_PG_TESTS=1 to run isolated PostgreSQL tests", allow_module_level=True
    )

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture
def business_id():
    return uuid4()


@pytest.fixture
def buyer_id():
    return uuid4()


@pytest.fixture
def product_id():
    return uuid4()


@pytest.fixture
def order_id():
    return uuid4()


def setup_order(
    db: Session, business_id, buyer_id, product_id, order_id, initial_status="pending_payment"
):
    db.execute(
        text(
            f"INSERT INTO businesses (id, display_name, timezone) VALUES ('{business_id}', 'Test Biz', 'UTC') ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO buyers (id, business_id, display_name, is_customer) VALUES ('{buyer_id}', '{business_id}', 'Test Buyer', false) ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO products (id, business_id, sku, normalized_sku, name, normalized_name, sellable_unit, stock_unit, cost_unit_paise, base_unit_price_paise, gst_rate_bps, pack_size) VALUES ('{product_id}', '{business_id}', 'SKU-1', 'sku-1', 'Product 1', 'product 1', 'pc', 'pc', 1000, 2000, 1800, 1) ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO orders (id, business_id, buyer_id, status) VALUES ('{order_id}', '{business_id}', '{buyer_id}', '{initial_status}')"
        )
    )
    db.commit()


def test_normal_transition_flow(pg_session: Session, business_id, buyer_id, product_id, order_id):
    setup_order(pg_session, business_id, buyer_id, product_id, order_id)

    # 1. Payment verifies -> paid
    payment_id = uuid4()
    mark_order_paid_from_verified_payment(pg_session, business_id, order_id, payment_id)

    # 2. Merchant confirms -> confirmed
    confirm_order(pg_session, business_id, order_id)

    # 3. Processing -> processing
    process_order(pg_session, business_id, order_id)

    # 4. Fulfilment shipped -> shipped
    set_tracking_information(
        pg_session, business_id, order_id, "FedEx", "123456", "https://fedex.com/123456"
    )
    mark_order_shipped(pg_session, business_id, order_id)

    # 5. Fulfilment delivered -> delivered
    mark_order_delivered(pg_session, business_id, order_id)

    # Try cancelling delivered (should fail)
    with pytest.raises(CommercialError) as exc:
        cancel_order(pg_session, business_id, order_id, "changed mind")
    assert exc.value.status_code == 400
    assert "Cannot cancel from state: delivered" in exc.value.message


def test_cancel_unpaid(pg_session: Session, business_id, buyer_id, product_id, order_id):
    setup_order(pg_session, business_id, buyer_id, product_id, order_id)

    cancel_order(pg_session, business_id, order_id, "out of stock")

    pg_session.commit()
    res = pg_session.execute(text(f"SELECT status FROM orders WHERE id='{order_id}'")).scalar_one()
    assert res == "cancelled"

    # Try paying cancelled
    payment_id = uuid4()
    with pytest.raises(CommercialError) as exc:
        mark_order_paid_from_verified_payment(pg_session, business_id, order_id, payment_id)
    assert exc.value.status_code == 409
    assert "Order was cancelled before payment was verified" in exc.value.message


def test_cancel_paid_triggers_refund(
    pg_session: Session, business_id, buyer_id, product_id, order_id
):
    setup_order(pg_session, business_id, buyer_id, product_id, order_id)

    payment_id = uuid4()
    mark_order_paid_from_verified_payment(pg_session, business_id, order_id, payment_id)

    # Customer cancels
    cancel_order(pg_session, business_id, order_id, "ordered wrong item")

    pg_session.commit()
    res = pg_session.execute(text(f"SELECT status FROM orders WHERE id='{order_id}'")).scalar_one()
    assert res == "refund_pending"


def test_invalid_transitions(pg_session: Session, business_id, buyer_id, product_id, order_id):
    setup_order(pg_session, business_id, buyer_id, product_id, order_id)

    # Cannot confirm unpaid
    with pytest.raises(CommercialError) as exc:
        confirm_order(pg_session, business_id, order_id)
    assert "Cannot confirm from state: pending_payment" in exc.value.message

    # Cannot process unpaid
    with pytest.raises(CommercialError):
        process_order(pg_session, business_id, order_id)

    # Cannot ship unpaid
    with pytest.raises(CommercialError):
        mark_order_shipped(pg_session, business_id, order_id)
