"""Comprehensive PostgreSQL test coverage for variant-aware cart, checkout, inventory, and invoice hardening."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.checkout import process_test_payment
from app.modules.catalog.models import Product, ProductVariant
from app.modules.commerce import customer_service, discovery_service
from app.modules.commerce.cart_tools import build_cart_tools
from app.modules.commerce.models import Cart, CheckoutSession, Order
from app.modules.identity.models import Business, Buyer
from app.modules.inventory.models import Inventory
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.whatsapp.models import WhatsAppMessage
from app.seed import DEMO_BUSINESS_ID
from seed_demo_clothing import seed_clothing_catalog

pytest_plugins = ["test_phase1_postgres"]


@pytest.fixture(autouse=True)
def no_external_llm(monkeypatch):
    monkeypatch.setattr(customer_service, "customer_salesperson_chat", lambda *_a, **_k: None)


def _persist_out(
    db: Session,
    *,
    phone: str,
    wa_id: str,
    context: dict,
    text: str = "options",
) -> None:
    db.add(
        WhatsAppMessage(
            provider_message_id=f"test-out-{uuid4()}",
            direction="out",
            wa_id=wa_id,
            phone_number_id=phone,
            business_id=DEMO_BUSINESS_ID,
            payload={"text": text, "commerce_context": context},
            created_at=datetime.now(UTC),
        )
    )
    db.flush()


def _setup_hoodie_variants(db: Session) -> tuple[Product, ProductVariant, ProductVariant]:
    seed_clothing_catalog(db, DEMO_BUSINESS_ID)
    db.flush()
    hoodie = db.scalar(
        select(Product).where(
            Product.business_id == DEMO_BUSINESS_ID,
            Product.name == "Signature Black Zip Hoodie",
        )
    )
    assert hoodie is not None
    variants = db.scalars(
        select(ProductVariant).where(
            ProductVariant.business_id == DEMO_BUSINESS_ID,
            ProductVariant.product_id == hoodie.id,
        )
    ).all()

    v_m = next(v for v in variants if v.size == "M")
    v_l = next(v for v in variants if v.size == "L")
    return hoodie, v_m, v_l


def test_variant_aware_add_to_cart_resolves_context(pg_session: Session) -> None:
    hoodie, v_m, _ = _setup_hoodie_variants(pg_session)
    buyer = Buyer(
        business_id=DEMO_BUSINESS_ID, whatsapp_e164="919800000001", display_name="Cart Test"
    )
    pg_session.add(buyer)
    pg_session.flush()

    context = {
        "selected_product_id": str(hoodie.id),
        "selected_variant_id": str(v_m.id),
    }

    tools = build_cart_tools(pg_session, DEMO_BUSINESS_ID, buyer.id, "test_msg_1", context=context)
    add_tool = next(t for t in tools if t.name == "add_to_cart")

    res = add_tool.invoke({"quantity": 1})
    assert res.get("status") == "added"

    cart = pg_session.scalar(
        select(Cart).where(
            Cart.business_id == DEMO_BUSINESS_ID, Cart.buyer_id == buyer.id, Cart.status == "active"
        )
    )
    assert cart is not None
    assert len(cart.items) == 1
    assert cart.items[0].product_id == hoodie.id
    assert cart.items[0].variant_id == v_m.id


def test_trusted_variant_validation_rejects_cross_tenant_and_mismatched(
    pg_session: Session,
) -> None:
    hoodie, v_m, _ = _setup_hoodie_variants(pg_session)
    buyer = Buyer(
        business_id=DEMO_BUSINESS_ID, whatsapp_e164="919800000002", display_name="Validation Test"
    )
    other_biz = Business(display_name="Other Store")
    pg_session.add_all([buyer, other_biz])
    pg_session.flush()

    other_product = Product(
        business_id=other_biz.id,
        sku="OTHER-1",
        normalized_sku="other-1",
        name="Other Tee",
        normalized_name="other tee",
        base_unit_price_paise=50000,
    )
    pg_session.add(other_product)
    pg_session.flush()

    other_variant = ProductVariant(
        business_id=other_biz.id,
        product_id=other_product.id,
        sku="OTHER-1-M",
        size="M",
    )
    pg_session.add(other_variant)
    pg_session.flush()

    context = {
        "selected_product_id": str(hoodie.id),
        "selected_variant_id": str(other_variant.id),
    }

    tools = build_cart_tools(pg_session, DEMO_BUSINESS_ID, buyer.id, "test_msg_2", context=context)
    add_tool = next(t for t in tools if t.name == "add_to_cart")

    res = add_tool.invoke({"quantity": 1})
    assert "error" in res
    assert "invalid or inactive" in res["error"].casefold()


def test_variant_specific_inventory_and_out_of_stock_prevention(pg_session: Session) -> None:
    hoodie, v_m, v_l = _setup_hoodie_variants(pg_session)

    inv = pg_session.scalar(
        select(Inventory).where(
            Inventory.business_id == DEMO_BUSINESS_ID,
            Inventory.product_id == hoodie.id,
        )
    )
    assert inv is not None
    inv.on_hand_qty = Decimal("0.000")
    pg_session.flush()

    phone = "number-b-inv-test"
    wa_id = "919800000003"
    state = {
        **customer_service._empty_state(),
        "shown_product_ids": [str(hoodie.id)],
        "selected_product_id": str(hoodie.id),
    }
    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=state)

    m_check = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "M hai?"
    )[0]
    assert "out of stock" in m_check.text.casefold()

    inv.on_hand_qty = Decimal("5.000")
    pg_session.flush()

    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=state)
    l_check = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "L hai?"
    )[0]
    assert "available" in l_check.text.casefold()
    assert l_check.commerce_context["selected_variant_id"] == str(v_l.id)


def test_multi_color_same_size_clarification(pg_session: Session) -> None:
    seed_clothing_catalog(pg_session, DEMO_BUSINESS_ID)
    pg_session.flush()

    # Create a product with Black/M and Navy/M variants
    product = Product(
        business_id=DEMO_BUSINESS_ID,
        sku="CLOTH-POLO-MULTI",
        normalized_sku="cloth-polo-multi",
        name="Polo Shirt Multi Color",
        normalized_name="polo shirt multi color",
        base_unit_price_paise=150000,
    )
    pg_session.add(product)
    pg_session.flush()

    v_black_m = ProductVariant(
        business_id=DEMO_BUSINESS_ID,
        product_id=product.id,
        sku="CLOTH-POLO-BLK-M",
        size="M",
        color="Black",
    )
    v_navy_m = ProductVariant(
        business_id=DEMO_BUSINESS_ID,
        product_id=product.id,
        sku="CLOTH-POLO-NVY-M",
        size="M",
        color="Navy",
    )
    pg_session.add_all([v_black_m, v_navy_m])
    pg_session.flush()

    inv_p = Inventory(
        business_id=DEMO_BUSINESS_ID,
        product_id=product.id,
        on_hand_qty=Decimal("10.000"),
    )
    pg_session.add(inv_p)
    pg_session.flush()

    phone = "number-b-color-test"
    wa_id = "919800000004"
    state = {
        **customer_service._empty_state(),
        "shown_product_ids": [str(product.id)],
        "selected_product_id": str(product.id),
    }
    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=state)

    m_ask = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "M chahiye"
    )[0]
    assert "Kaunsa color chahiye" in m_ask.text or "Black" in m_ask.text or "Navy" in m_ask.text

    _persist_out(pg_session, phone=phone, wa_id=wa_id, context=m_ask.commerce_context)
    black_ask = discovery_service.process_customer_commerce_message(
        pg_session, DEMO_BUSINESS_ID, phone, wa_id, "black"
    )[0]
    assert black_ask.commerce_context["selected_variant_id"] == str(v_black_m.id)


def test_full_cross_request_checkout_continuation_and_invoice(pg_engine) -> None:
    phone = "number-b-e2e-checkout"
    wa_id = f"9198{uuid4().int % 100000000:08d}"

    with Session(pg_engine) as db1:
        hoodie, v_m, _ = _setup_hoodie_variants(db1)
        v_m.price_override_paise = 299900
        db1.flush()

        inv = db1.scalar(
            select(Inventory).where(
                Inventory.business_id == DEMO_BUSINESS_ID,
                Inventory.product_id == hoodie.id,
            )
        )
        if inv:
            inv.on_hand_qty = Decimal("10.000")
            inv.variant_id = v_m.id
        db1.commit()
        hoodie_id = str(hoodie.id)
        v_m_id = str(v_m.id)

    # Turn 1: Discover hoodie
    with Session(pg_engine) as db2:
        r1 = discovery_service.process_customer_commerce_message(
            db2, DEMO_BUSINESS_ID, phone, wa_id, "Signature black zip hoodie dikhao"
        )[0]
        assert r1.commerce_context["selected_product_id"] == hoodie_id
        _persist_out(db2, phone=phone, wa_id=wa_id, context=r1.commerce_context)
        db2.commit()

    # Turn 2: Select size M
    with Session(pg_engine) as db3:
        r2 = discovery_service.process_customer_commerce_message(
            db3, DEMO_BUSINESS_ID, phone, wa_id, "M hai?"
        )[0]
        assert r2.commerce_context["selected_variant_id"] == v_m_id
        assert r2.commerce_context["selected_size"] == "M"
        _persist_out(db3, phone=phone, wa_id=wa_id, context=r2.commerce_context)
        db3.commit()

    # Turn 3: Add 1 to cart
    with Session(pg_engine) as db4:
        buyer = db4.scalar(
            select(Buyer).where(Buyer.business_id == DEMO_BUSINESS_ID, Buyer.whatsapp_e164 == wa_id)
        )
        assert buyer is not None
        context = customer_service.load_commerce_state(db4, DEMO_BUSINESS_ID, phone, wa_id)
        tools = build_cart_tools(db4, DEMO_BUSINESS_ID, buyer.id, "t3", context=context)
        add_tool = next(t for t in tools if t.name == "add_to_cart")
        res_add = add_tool.invoke({"quantity": 1})
        assert res_add["status"] == "added"

        checkout_tool = next(t for t in tools if t.name == "checkout_cart")
        res_chk = checkout_tool.invoke(
            {"delivery_address": {"street": "Connaught Place", "city": "Delhi"}}
        )
        assert res_chk["status"] == "success"
        order_id = UUID(res_chk["order_id"])
        payment_url = res_chk["payment_url"]
        db4.commit()

    # Turn 4: Verify Order, OrderItem, and CheckoutSession in DB
    with Session(pg_engine) as db5:
        order = db5.scalar(select(Order).where(Order.id == order_id))
        assert order is not None
        assert order.status == "pending_payment"
        assert len(order.items) == 1

        item = order.items[0]
        assert item.product_id == UUID(hoodie_id)
        assert item.variant_id == UUID(v_m_id)
        assert item.size_snapshot == "M"
        assert item.unit_price_paise == 299900
        assert item.quantity == 1

        raw_token = payment_url.split("/pay/")[-1]
        token_hash = customer_service.hashlib.sha256(raw_token.encode()).hexdigest()
        session_rec = db5.scalar(
            select(CheckoutSession).where(CheckoutSession.token_hash == token_hash)
        )
        assert session_rec is not None
        assert session_rec.order_id == order_id
        assert session_rec.status == "pending"

        # Turn 5: Process Authoritative Test Payment
        pay_result = process_test_payment(raw_token, db5)
        assert pay_result["status"] in {"success", "already_paid"}

        # Verify Payment, Order, Buyer, and Invoice status post-payment
        db5.refresh(order)
        buyer_rec = db5.scalar(select(Buyer).where(Buyer.id == order.buyer_id))
        assert buyer_rec.is_customer is True
        assert order.status == "paid"

        payment_rec = db5.scalar(select(Payment).where(Payment.order_id == order_id))
        assert payment_rec is not None
        assert payment_rec.status == "PAID"
        assert payment_rec.amount_paise == 299900

        invoice_rec = db5.scalar(select(Invoice).where(Invoice.order_id == order_id))
        assert invoice_rec is not None
        assert invoice_rec.invoice_number.startswith("INV-")
        assert invoice_rec.total_paise == 299900
        db5.commit()
