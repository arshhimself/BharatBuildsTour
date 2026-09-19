from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.catalog.models import Product
from app.modules.commerce.cart_service import (
    add_to_cart,
    checkout_cart,
    remove_from_cart,
    update_cart_quantity,
    view_cart,
)
from app.modules.commerce.models import Cart, Order
from app.modules.identity.models import Business, Buyer
from app.seed import DEMO_BUSINESS_ID, seed_demo

pytest_plugins = ["test_phase1_postgres"]


def test_commerce_cart_lifecycle(pg_session: Session) -> None:
    seed_demo(pg_session)

    business_id = DEMO_BUSINESS_ID
    # Fetch a buyer
    buyer = pg_session.scalar(select(Buyer).where(Buyer.business_id == business_id).limit(1))
    assert buyer is not None

    # Fetch a product
    product = pg_session.scalar(select(Product).where(Product.business_id == business_id).limit(1))
    assert product is not None

    # 1. Add to cart (idempotency test)
    res = add_to_cart(pg_session, business_id, buyer.id, product.id, 2, "msg-1")
    assert res.get("status") == "added"
    assert res.get("new_quantity") == 2

    # Duplicate add (same idempotency key) should be ignored
    res_dup = add_to_cart(pg_session, business_id, buyer.id, product.id, 2, "msg-1")
    assert res_dup.get("status") == "duplicate_ignored"

    # New add (different key) should increment
    res2 = add_to_cart(pg_session, business_id, buyer.id, product.id, 1, "msg-2")
    assert res2.get("new_quantity") == 3

    # 2. View cart
    cart_data = view_cart(pg_session, business_id, buyer.id)
    assert len(cart_data["items"]) == 1
    assert cart_data["items"][0]["quantity"] == 3
    assert cart_data["items"][0]["unit_price_paise"] == product.base_unit_price_paise
    assert cart_data["total_paise"] == product.base_unit_price_paise * 3

    # 3. Update quantity
    res_upd = update_cart_quantity(pg_session, business_id, buyer.id, product.id, 5)
    assert res_upd.get("status") == "updated"
    assert res_upd.get("new_quantity") == 5

    # 4. Remove item
    res_rem = remove_from_cart(pg_session, business_id, buyer.id, product.id)
    assert res_rem.get("status") == "removed"

    # Add back for checkout
    add_to_cart(pg_session, business_id, buyer.id, product.id, 1, "msg-3")

    # 5. Checkout
    addr = {"street": "Test"}
    checkout_res = checkout_cart(pg_session, business_id, buyer.id, addr, "checkout-1")
    assert checkout_res.get("status") == "success"
    order_id = checkout_res.get("order_id")

    # Cart should be converted
    cart = pg_session.scalar(
        select(Cart).where(
            Cart.business_id == business_id, Cart.buyer_id == buyer.id, Cart.status == "active"
        )
    )
    assert cart is None

    # Verify Order
    order = pg_session.get(Order, order_id)
    assert order.status == "pending_payment"
    assert len(order.items) == 1
    assert order.items[0].unit_price_paise == product.base_unit_price_paise

    # Buyer is still NOT a customer
    pg_session.refresh(buyer)


def test_tenant_isolation(pg_session: Session) -> None:
    # Business A setup
    seed_demo(pg_session)
    biz_a = DEMO_BUSINESS_ID
    buyer_a = pg_session.scalar(select(Buyer).where(Buyer.business_id == biz_a).limit(1))

    # Create Business B and product
    biz_b = Business(id=uuid4(), display_name="B")
    pg_session.add(biz_b)
    pg_session.flush()
    prod_b = Product(
        id=uuid4(),
        business_id=biz_b.id,
        sku="B1",
        normalized_sku="b1",
        name="B1",
        normalized_name="b1",
        sellable_unit="pc",
        stock_unit="pc",
        cost_unit_paise=50,
        base_unit_price_paise=100,
        gst_rate_bps=1800,
        pack_size=Decimal("1.0"),
    )
    pg_session.add(prod_b)
    pg_session.flush()

    # Try adding B's product to A's cart
    res = add_to_cart(pg_session, biz_a, buyer_a.id, prod_b.id, 1, "msg-isol-v2")
    assert res.get("error") == "Product not found."
