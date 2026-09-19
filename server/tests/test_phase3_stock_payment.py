import os
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.commercial import CommercialError
from app.modules.commerce.models import Order, OrderItem
from app.modules.inventory.models import Inventory, StockMovement, StockReservation
from app.modules.inventory.reservation import (
    _get_active_reserved_qty,
    consume_order_reservations,
    expire_reservations,
    release_order_reservations,
    reserve_order_stock,
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
def product_id():
    return uuid4()


@pytest.fixture
def setup_inventory(pg_engine, business_id, product_id):
    # Tests use pg_engine from conftest/pytest which yields Engine.
    # We need a Session. But wait, `db` fixture is usually available if `conftest.py` is loaded.
    pass


def test_reserve_available_stock(pg_session: Session, business_id, product_id):
    db = pg_session
    # Setup dummy business and product for FKs
    db.execute(
        text(
            f"INSERT INTO businesses (id, name, timezone) VALUES ('{business_id}', 'Test Biz', 'UTC') ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO products (id, business_id, sku, name) VALUES ('{product_id}', '{business_id}', 'SKU-1', 'Product 1') ON CONFLICT DO NOTHING"
        )
    )

    inv = Inventory(
        business_id=business_id,
        product_id=product_id,
        on_hand_qty=Decimal("10.000"),
        reorder_threshold=Decimal("2.000"),
    )
    db.add(inv)
    db.commit()

    # Create order
    buyer_id = uuid4()
    db.execute(
        text(
            f"INSERT INTO buyers (id, business_id, is_customer) VALUES ('{buyer_id}', '{business_id}', false) ON CONFLICT DO NOTHING"
        )
    )

    order = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order,
        product_id=product_id,
        quantity=3,
        unit_price_paise=100,
        sku_snapshot="SKU-1",
        name_snapshot="Product 1",
    )
    db.add(order)
    db.commit()

    # 1. reserve available stock
    res = reserve_order_stock(db, business_id, order.id)
    assert len(res) == 1
    assert res[0].quantity == Decimal("3.000")
    assert res[0].status == "ACTIVE"
    db.commit()

    # 2. reservation reduces available_to_sell
    assert _get_active_reserved_qty(db, business_id, product_id) == 3.0

    # 3. reservation does NOT immediately decrement on_hand
    db.refresh(inv)
    assert inv.on_hand_qty == Decimal("10.000")

    # 4. duplicate reservation idempotent
    res2 = reserve_order_stock(db, business_id, order.id)
    assert len(res2) == 1
    assert res2[0].id == res[0].id
    db.commit()


def test_concurrent_reservations_last_unit(pg_session: Session, business_id, product_id):
    db = pg_session
    buyer_id = uuid4()
    db.execute(
        text(
            f"INSERT INTO businesses (id, name, timezone) VALUES ('{business_id}', 'Test Biz', 'UTC') ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO products (id, business_id, sku, name) VALUES ('{product_id}', '{business_id}', 'SKU-1', 'Product 1') ON CONFLICT DO NOTHING"
        )
    )
    inv = Inventory(
        business_id=business_id,
        product_id=product_id,
        on_hand_qty=Decimal("1.000"),
        reorder_threshold=Decimal("2.000"),
    )
    db.add(inv)
    db.commit()

    db.execute(
        text(
            f"INSERT INTO buyers (id, business_id, is_customer) VALUES ('{buyer_id}', '{business_id}', false) ON CONFLICT DO NOTHING"
        )
    )

    # 5. two orders compete for last unit
    order1 = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order1,
        product_id=product_id,
        quantity=1,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )

    order2 = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order2,
        product_id=product_id,
        quantity=1,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )
    db.add_all([order1, order2])
    db.commit()

    # Exactly one wins
    reserve_order_stock(db, business_id, order1.id)
    db.commit()

    with pytest.raises(CommercialError) as exc:
        reserve_order_stock(db, business_id, order2.id)

    # 6. exactly one wins
    assert exc.value.status_code == 409
    assert "Insufficient available stock" in exc.value.message


def test_release_and_expire(pg_session: Session, business_id, product_id):
    db = pg_session
    buyer_id = uuid4()
    db.execute(
        text(
            f"INSERT INTO businesses (id, name, timezone) VALUES ('{business_id}', 'Test Biz', 'UTC') ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO products (id, business_id, sku, name) VALUES ('{product_id}', '{business_id}', 'SKU-1', 'Product 1') ON CONFLICT DO NOTHING"
        )
    )
    inv = Inventory(
        business_id=business_id,
        product_id=product_id,
        on_hand_qty=Decimal("10.000"),
        reorder_threshold=Decimal("2.000"),
    )
    db.add(inv)
    db.commit()
    db.execute(
        text(
            f"INSERT INTO buyers (id, business_id, is_customer) VALUES ('{buyer_id}', '{business_id}', false) ON CONFLICT DO NOTHING"
        )
    )

    order = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order,
        product_id=product_id,
        quantity=4,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )
    db.add(order)
    db.commit()

    # Reserve
    reserve_order_stock(db, business_id, order.id, expires_in_minutes=-1)  # expires in past
    db.commit()

    # 10. expired reservation ignored from reserved total
    # active query should ignore it because expires_at < now
    assert _get_active_reserved_qty(db, business_id, product_id) == 0.0

    # expire service updates state
    expire_reservations(db)
    db.commit()

    res = db.query(StockReservation).filter_by(order_id=order.id).first()
    assert res.status == "EXPIRED"

    # Release
    order2 = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order2,
        product_id=product_id,
        quantity=2,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )
    db.add(order2)
    db.commit()

    reserve_order_stock(db, business_id, order2.id)
    db.commit()

    # 8. release reservation
    release_order_reservations(db, business_id, order2.id)
    db.commit()

    res2 = db.query(StockReservation).filter_by(order_id=order2.id).first()
    assert res2.status == "RELEASED"

    # 9. duplicate release safe
    release_order_reservations(db, business_id, order2.id)
    db.commit()

    assert _get_active_reserved_qty(db, business_id, product_id) == 0.0


def test_consume_reservation(pg_session: Session, business_id, product_id):
    db = pg_session
    buyer_id = uuid4()
    db.execute(
        text(
            f"INSERT INTO businesses (id, name, timezone) VALUES ('{business_id}', 'Test Biz', 'UTC') ON CONFLICT DO NOTHING"
        )
    )
    db.execute(
        text(
            f"INSERT INTO products (id, business_id, sku, name) VALUES ('{product_id}', '{business_id}', 'SKU-1', 'Product 1') ON CONFLICT DO NOTHING"
        )
    )
    inv = Inventory(
        business_id=business_id,
        product_id=product_id,
        on_hand_qty=Decimal("10.000"),
        reorder_threshold=Decimal("2.000"),
    )
    db.add(inv)
    db.commit()
    db.execute(
        text(
            f"INSERT INTO buyers (id, business_id, is_customer) VALUES ('{buyer_id}', '{business_id}', false) ON CONFLICT DO NOTHING"
        )
    )

    order = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order,
        product_id=product_id,
        quantity=2,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )
    db.add(order)
    db.commit()

    reserve_order_stock(db, business_id, order.id)
    db.commit()

    assert _get_active_reserved_qty(db, business_id, product_id) == 2.0

    # 11. consume reservation decrements once
    success = consume_order_reservations(db, business_id, order.id, "pay-1")
    db.commit()
    assert success is True

    db.refresh(inv)
    assert inv.on_hand_qty == Decimal("8.000")

    # 13. StockMovement created exactly once
    movements = db.query(StockMovement).filter_by(business_id=business_id).all()
    assert len(movements) == 1
    assert movements[0].quantity_delta == Decimal("-2.000")
    assert movements[0].movement_key == f"pay-1-{order.id}-{product_id}"

    # 12. duplicate consume does not decrement twice
    success = consume_order_reservations(db, business_id, order.id, "pay-1")
    db.commit()
    assert success is True

    db.refresh(inv)
    assert inv.on_hand_qty == Decimal("8.000")

    # 17. Late payment (expired) -> reconciliation if no stock
    order3 = Order(business_id=business_id, buyer_id=buyer_id)
    OrderItem(
        order=order3,
        product_id=product_id,
        quantity=10,
        unit_price_paise=100,
        sku_snapshot="S",
        name_snapshot="P",
    )
    db.add(order3)
    db.commit()

    reserve_order_stock(db, business_id, order3.id, expires_in_minutes=-5)
    db.commit()

    success = consume_order_reservations(db, business_id, order3.id, "pay-2")
    db.commit()
    assert (
        success is False
    )  # reconciliation required because 10 > 8 on hand and reservation expired
