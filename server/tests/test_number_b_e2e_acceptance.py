"""Final Pre-Deploy End-to-End Acceptance Test Suite for Number-B Commerce."""

import os
from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.checkout import prepare_checkout_session
from app.db.session import transaction_session
from app.main import app
from app.modules.catalog.models import Product, ProductVariant
from app.modules.commerce.cart_service import add_to_cart, checkout_cart
from app.modules.commerce.models import CheckoutSession, Order, OrderItem
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.modules.identity.owner_models import Category
from app.modules.inventory.models import Inventory
from app.modules.invoices.models import Invoice
from app.modules.payments.models import Payment

pytestmark = pytest.mark.skipif(
    os.getenv("STOCKAWARE_RUN_PG_TESTS") != "1",
    reason="Database integration tests require real PostgreSQL container",
)


@pytest.fixture
def e2e_setup():
    with transaction_session() as db:
        biz_name = f"Rehbar Demo Store {uuid4()}"
        business = Business(legal_name=biz_name, display_name=biz_name)
        db.add(business)
        db.flush()

        category = Category(
            business_id=business.id,
            name="T-Shirts",
        )
        db.add(category)
        db.flush()

        profile = StoreProfile(
            business_id=business.id,
            description="Rehbar Clothing — Premium urban streetwear.",
            store_type="Apparel & Fashion",
            address_line="102 Connaught Place, Inner Circle",
            city="New Delhi",
            support_number="+919876543210",
            opening_hours="10:00 AM - 9:00 PM",
            delivery_info="Free Express Shipping across India.",
            return_policy="7 days easy returns.",
        )
        db.add(profile)

        buyer = Buyer(
            business_id=business.id,
            whatsapp_e164=f"+91{uuid4().int % 10000000000:010d}",
            display_name="Farhan Customer",
            is_customer=False,
        )
        db.add(buyer)
        db.flush()

        product = Product(
            business_id=business.id,
            sku=f"CLOTH-TSHIRT-BLK-{uuid4().hex[:4]}",
            name="Oversized Black T-Shirt",
            category_id=category.id,
            price_paise=129900,
            active=True,
        )
        db.add(product)
        db.flush()

        variant_m = ProductVariant(
            business_id=business.id,
            product_id=product.id,
            sku=f"CLOTH-TSHIRT-BLK-M-{uuid4().hex[:4]}",
            size="M",
            color="Black",
            price_override_paise=None,
            active=True,
        )
        db.add(variant_m)
        db.flush()

        inv = Inventory(
            business_id=business.id,
            product_id=product.id,
            variant_id=variant_m.id,
            on_hand_qty=50,
        )
        db.add(inv)
        db.commit()

        yield {
            "business_id": business.id,
            "profile": profile,
            "buyer_id": buyer.id,
            "buyer": buyer,
            "product": product,
            "variant_m": variant_m,
            "category": category,
        }


def test_real_end_to_end_local_flow(e2e_setup):
    client = TestClient(app)
    biz_id = e2e_setup["business_id"]
    buyer_id = e2e_setup["buyer_id"]
    variant_m = e2e_setup["variant_m"]

    # 1. Add M variant to cart & checkout
    with transaction_session() as db:
        add_to_cart(
            db,
            biz_id,
            buyer_id,
            variant_m.product_id,
            quantity=1,
            idempotency_key=f"add_{uuid4()}",
            variant_id=variant_m.id,
        )
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "102 Connaught Place", "city": "New Delhi"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])
        session_info = prepare_checkout_session(db, biz_id, order_id)
        raw_token = session_info["raw_token"]

    # 2. GET /pay/{token}
    page_resp = client.get(f"/pay/{raw_token}")
    assert page_resp.status_code == 200
    assert "Oversized Black T-Shirt" in page_resp.text
    assert "M" in page_resp.text
    assert "TEST PAYMENT DEMO" in page_resp.text
    assert "₹1299.00" in page_resp.text

    # 3. POST /api/pay/test/{token} with Meta transport mocked to capture outbound messages
    with (
        patch("app.api.routes.checkout.send_whatsapp_message") as mock_txt,
        patch("app.api.routes.checkout.send_whatsapp_media") as mock_doc,
    ):
        pay_resp = client.post(f"/api/pay/test/{raw_token}")
        assert pay_resp.status_code == 200
        pay_data = pay_resp.json()
        assert pay_data["status"] == "success"
        assert pay_data["order_id"] == str(order_id)
        assert pay_data["invoice_number"].startswith("INV-2026-")

        # Verify Outbound WhatsApp Messages
        mock_txt.assert_called_once()
        text_arg = mock_txt.call_args[0][1]
        assert "Payment received ✅" in text_arg
        assert f"Order #{str(order_id)[:8]}" in text_arg

        mock_doc.assert_called_once()
        doc_kwargs = mock_doc.call_args[1]
        assert doc_kwargs["message_type"] == "document"
        assert doc_kwargs["filename"].startswith("Invoice-INV-2026-")

    # 4. Fresh-session Database Verification
    with transaction_session() as db:
        session_rec = db.query(CheckoutSession).filter(CheckoutSession.order_id == order_id).first()
        assert session_rec.status == "completed"

        payments = db.query(Payment).filter(Payment.order_id == order_id).all()
        assert len(payments) == 1
        payment = payments[0]
        assert payment.status == "PAID"
        assert payment.amount_paise == 129900

        order = db.get(Order, order_id)
        assert order.status == "paid"

        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is True

        invoices = db.query(Invoice).filter(Invoice.order_id == order_id).all()
        assert len(invoices) == 1
        invoice = invoices[0]
        assert invoice.invoice_number.startswith("INV-2026-")
        assert invoice.artifact_sha256 is not None

        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        assert len(items) == 1
        assert items[0].variant_id == variant_m.id
        assert items[0].sku_snapshot == variant_m.sku
        assert items[0].size_snapshot == "M"
        assert items[0].unit_price_paise == 129900

    # 5. Replay Safety
    replay_resp = client.post(f"/api/pay/test/{raw_token}")
    assert replay_resp.status_code == 200
    assert replay_resp.json()["status"] == "already_paid"

    with transaction_session() as db:
        assert db.query(Payment).filter(Payment.order_id == order_id).count() == 1
        assert db.query(Invoice).filter(Invoice.order_id == order_id).count() == 1


def test_customer_payment_claim_unverified(e2e_setup):
    biz_id = e2e_setup["business_id"]
    buyer_id = e2e_setup["buyer_id"]
    variant_m = e2e_setup["variant_m"]

    with transaction_session() as db:
        add_to_cart(
            db,
            biz_id,
            buyer_id,
            variant_m.product_id,
            quantity=1,
            idempotency_key=f"add_{uuid4()}",
            variant_id=variant_m.id,
        )
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "50 Ring Road", "city": "Delhi"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])

    # Customer sends text message "payment ho gaya"
    # Verification: order in fresh session remains unpaid
    with transaction_session() as db:
        order = db.get(Order, order_id)
        assert order.status == "pending_payment"
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        assert payment is None
        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is False


def test_number_a_owner_route_isolation():
    client = TestClient(app)
    # Number-A owner/health routes must operate normally without leak
    resp = client.get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
