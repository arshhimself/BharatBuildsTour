"""Regression Test Suite for Payment / Checkout Handoff Fix."""

import os
from decimal import Decimal
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.checkout import prepare_checkout_session
from app.db.session import transaction_session
from app.main import app
from app.modules.catalog.models import Product, ProductVariant
from app.modules.commerce import customer_service
from app.modules.commerce.cart_service import add_to_cart, checkout_cart
from app.modules.commerce.models import CheckoutSession, Order
from app.modules.commerce.sales_tools import _quantity
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.modules.identity.owner_models import Category
from app.modules.inventory.models import Inventory
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment
from app.modules.whatsapp.models import WhatsAppMessage

pytestmark = pytest.mark.skipif(
    os.getenv("STOCKAWARE_RUN_PG_TESTS") != "1",
    reason="Database integration tests require real PostgreSQL container",
)


@pytest.fixture
def checkout_handoff_setup():
    with transaction_session() as db:
        biz_name = f"Cargo Test Store {uuid4()}"
        business = Business(legal_name=biz_name, display_name=biz_name)
        db.add(business)
        db.flush()

        category = Category(business_id=business.id, name="Pants")
        db.add(category)
        db.flush()

        profile = StoreProfile(
            business_id=business.id,
            description="Urban Tactical Gear Store",
            store_type="Apparel",
            address_line="100 Commercial Belt",
            city="Delhi",
            support_number="+919999888877",
            opening_hours="9 AM - 9 PM",
            delivery_info="Fast Express Delivery",
            return_policy="7 days return",
        )
        db.add(profile)

        buyer = Buyer(
            business_id=business.id,
            whatsapp_e164=f"91{uuid4().int % 10000000000:010d}",
            display_name="Test Buyer",
            is_customer=False,
        )
        db.add(buyer)
        db.flush()

        product = Product(
            business_id=business.id,
            sku=f"PANTS-CARGO-OLIVE-{uuid4().hex[:4]}",
            name="Tactical Olive Green Cargo Pants",
            category_id=category.id,
            price_paise=229900,
            active=True,
        )
        db.add(product)
        db.flush()

        variant_m = ProductVariant(
            business_id=business.id,
            product_id=product.id,
            sku=f"PANTS-CARGO-OLIVE-M-{uuid4().hex[:4]}",
            size="M",
            color="Olive Green",
            price_override_paise=None,
            active=True,
        )
        db.add(variant_m)
        db.flush()

        inv = Inventory(
            business_id=business.id,
            product_id=product.id,
            variant_id=variant_m.id,
            on_hand_qty=Decimal("50.000"),
        )
        db.add(inv)
        db.commit()

        yield {
            "business_id": business.id,
            "buyer_id": buyer.id,
            "buyer_phone": buyer.whatsapp_e164.replace("+", ""),
            "product": product,
            "variant_m": variant_m,
            "phone_number_id": "1353344187842745",
        }


def test_inventory_quantity_formatting():
    assert _quantity(Decimal("50.000")) == "50"
    assert _quantity(Decimal("3.000")) == "3"
    assert _quantity(Decimal("3.5")) == "3.5"
    assert _quantity(None) is None


def test_real_checkout_intent_and_url_resend_idempotency(checkout_handoff_setup):
    biz_id = checkout_handoff_setup["business_id"]
    phone_id = checkout_handoff_setup["phone_number_id"]
    wa_id = checkout_handoff_setup["buyer_phone"]
    product = checkout_handoff_setup["product"]
    variant = checkout_handoff_setup["variant_m"]

    # Step 1: Pre-seed commerce context with product and variant selected
    with transaction_session() as db:
        db.add(
            WhatsAppMessage(
                provider_message_id=f"test-ctx-{uuid4()}",
                direction="out",
                wa_id=wa_id,
                phone_number_id=phone_id,
                business_id=biz_id,
                payload={
                    "text": "Done bhai! M resolve ho gaya",
                    "commerce_context": {
                        "version": 2,
                        "shown_product_ids": [str(product.id)],
                        "selected_product_id": str(product.id),
                        "selected_variant_id": str(variant.id),
                        "selected_size": "M",
                        "selected_color": "Olive Green",
                        "quantity": 1,
                    },
                },
            )
        )
        db.commit()

    # Step 2: "Yes proceed karo na payment ke liye"
    with transaction_session() as db:
        msgs = customer_service.process_customer_commerce_message(
            db, biz_id, phone_id, wa_id, "Yes proceed karo na payment ke liye"
        )
        assert len(msgs) > 0
        out_text = msgs[0].text
        ctx = msgs[0].commerce_context

        # ASSERTIONS
        assert "http" in out_text
        assert "/pay/" in out_text
        assert "localhost" not in out_text
        assert ctx.get("checkout_stage") == "awaiting_payment"
        assert ctx.get("order_id") is not None
        assert ctx.get("checkout_session_id") is not None
        assert ctx.get("payment_url") is not None

        order_id = UUID(ctx["order_id"])

    # Verify Order and CheckoutSession in DB
    with transaction_session() as db:
        order = db.get(Order, order_id)
        assert order is not None
        assert order.status == "pending_payment"
        session_rec = db.query(CheckoutSession).filter(CheckoutSession.order_id == order_id).first()
        assert session_rec is not None
        assert session_rec.status == "pending"

        # Count total orders for buyer so far
        order_count = (
            db.query(Order).filter(Order.buyer_id == checkout_handoff_setup["buyer_id"]).count()
        )
        assert order_count == 1

    # Step 3: "Kaha payment karna hai?" -> Must resend url idempotently, NO new order!
    with transaction_session() as db:
        msgs2 = customer_service.process_customer_commerce_message(
            db, biz_id, phone_id, wa_id, "Kaha payment karna hai?"
        )
        assert len(msgs2) > 0
        out_text2 = msgs2[0].text
        ctx2 = msgs2[0].commerce_context

        assert "http" in out_text2
        assert "/pay/" in out_text2
        assert ctx2.get("order_id") == str(order_id)

    # Verify NO duplicate order was created
    with transaction_session() as db:
        order_count2 = (
            db.query(Order).filter(Order.buyer_id == checkout_handoff_setup["buyer_id"]).count()
        )
        assert order_count2 == 1


def test_payment_claim_security_regression(checkout_handoff_setup):
    biz_id = checkout_handoff_setup["business_id"]
    phone_id = checkout_handoff_setup["phone_number_id"]
    wa_id = checkout_handoff_setup["buyer_phone"]
    buyer_id = checkout_handoff_setup["buyer_id"]
    variant = checkout_handoff_setup["variant_m"]

    # Prepare cart & order
    with transaction_session() as db:
        add_to_cart(
            db,
            biz_id,
            buyer_id,
            variant.product_id,
            quantity=1,
            idempotency_key=f"add_{uuid4()}",
            variant_id=variant.id,
        )
        chk_res = checkout_cart(
            db, biz_id, buyer_id, delivery_address={}, idempotency_key=f"chk_{uuid4()}"
        )
        order_id = UUID(chk_res["order_id"])

    # Customer sends payment claim text "payment ho gaya"
    with transaction_session() as db:
        msgs = customer_service.process_customer_commerce_message(
            db, biz_id, phone_id, wa_id, "payment ho gaya"
        )
        assert len(msgs) > 0
        assert "Payment confirm hote hi" in msgs[0].text

    # ASSERT Security Boundary: Payment NOT PAID, Order NOT PAID, Buyer is NOT customer
    with transaction_session() as db:
        order = db.get(Order, order_id)
        assert order.status == "pending_payment"
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        assert payment is None
        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is False
        invoice = db.query(Invoice).filter(Invoice.order_id == order_id).first()
        assert invoice is None


def test_authoritative_test_payment_execution(checkout_handoff_setup):
    client = TestClient(app)
    biz_id = checkout_handoff_setup["business_id"]
    buyer_id = checkout_handoff_setup["buyer_id"]
    variant = checkout_handoff_setup["variant_m"]

    with transaction_session() as db:
        add_to_cart(
            db,
            biz_id,
            buyer_id,
            variant.product_id,
            quantity=1,
            idempotency_key=f"add_{uuid4()}",
            variant_id=variant.id,
        )
        chk_res = checkout_cart(
            db, biz_id, buyer_id, delivery_address={}, idempotency_key=f"chk_{uuid4()}"
        )
        order_id = UUID(chk_res["order_id"])
        session_info = prepare_checkout_session(db, biz_id, order_id)
        raw_token = session_info["raw_token"]

    # Execute test payment API
    with (
        patch("app.api.routes.checkout.send_whatsapp_message") as mock_txt,
        patch("app.api.routes.checkout.send_whatsapp_media") as mock_doc,
    ):
        pay_resp = client.post(f"/api/pay/test/{raw_token}")
        assert pay_resp.status_code == 200
        assert pay_resp.json()["status"] == "success"

        mock_txt.assert_called_once()
        mock_doc.assert_called_once()

    # DB Assertions
    with transaction_session() as db:
        session_rec = db.query(CheckoutSession).filter(CheckoutSession.order_id == order_id).first()
        assert session_rec.status == "completed"

        payment = db.query(Payment).filter(Payment.order_id == order_id).one()
        assert payment.status == "PAID"
        assert payment.amount_paise == 229900

        order = db.get(Order, order_id)
        assert order.status == "paid"

        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is True

        invoice = db.query(Invoice).filter(Invoice.order_id == order_id).one()
        assert invoice.status == "GENERATED"
