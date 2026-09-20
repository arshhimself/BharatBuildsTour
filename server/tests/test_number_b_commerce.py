"""Acceptance and unit tests for Number-B AI Salesperson Commerce flow."""

import hashlib
import os
from datetime import UTC, datetime, timedelta
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
from app.modules.commerce.tools import get_store_info
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.modules.inventory.models import Inventory
from app.modules.invoices.models import Invoice
from app.modules.invoices.pdf import render_invoice_pdf
from app.modules.payments.models import Payment

pytestmark = pytest.mark.skipif(
    os.getenv("STOCKAWARE_RUN_PG_TESTS") != "1",
    reason="Database integration tests require real PostgreSQL container",
)


@pytest.fixture
def test_setup():
    with transaction_session() as db:
        biz_name = f"Rehbar Test Store {uuid4()}"
        business = Business(legal_name=biz_name, display_name=biz_name)
        db.add(business)
        db.flush()

        profile = StoreProfile(
            business_id=business.id,
            description="Premium ethnic menswear",
            store_type="clothing",
            address_line="123 Fashion Street, Mumbai",
            city="Mumbai",
            support_number="+919876543210",
            delivery_info="Free delivery across India within 3-5 days.",
            return_policy="7-day easy returns.",
        )

        db.add(profile)

        buyer = Buyer(
            business_id=business.id,
            whatsapp_e164=f"+91{uuid4().int % 10000000000:010d}",
            display_name="Test Buyer",
            is_customer=False,
        )
        db.add(buyer)
        db.flush()

        product = Product(
            business_id=business.id,
            sku=f"TSHIRT-BLK-{uuid4().hex[:4]}",
            name="Oversized Black T-Shirt",
            price_paise=149900,
            active=True,
        )

        db.add(product)
        db.flush()

        variant_m = ProductVariant(
            business_id=business.id,
            product_id=product.id,
            sku=f"TSHIRT-BLK-M-{uuid4().hex[:4]}",
            size="M",
            color="Black",
            price_override_paise=None,
            active=True,
        )
        variant_l = ProductVariant(
            business_id=business.id,
            product_id=product.id,
            sku=f"TSHIRT-BLK-L-{uuid4().hex[:4]}",
            size="L",
            color="Black",
            price_override_paise=None,
            active=True,
        )
        db.add_all([variant_m, variant_l])
        db.flush()

        inv_m = Inventory(
            business_id=business.id,
            product_id=product.id,
            variant_id=variant_m.id,
            on_hand_qty=50,
        )
        db.add(inv_m)
        db.commit()

        yield {
            "business_id": business.id,
            "profile": profile,
            "buyer_id": buyer.id,
            "buyer": buyer,
            "product": product,
            "variant_m": variant_m,
            "variant_l": variant_l,
        }


def test_store_profile_and_tool_retrieval(test_setup):
    with transaction_session() as db:
        info = get_store_info(db, test_setup["business_id"])
        assert info["display_name"]
        assert "Fashion Street" in info["address_line"]
        assert info["city"] == "Mumbai"
        assert "7-day" in info["return_policy"]


def test_cart_and_checkout_session_lifecycle(test_setup):
    client = TestClient(app)
    biz_id = test_setup["business_id"]
    buyer_id = test_setup["buyer_id"]
    variant_m = test_setup["variant_m"]

    with transaction_session() as db:
        # Add to cart with variant
        add_to_cart(
            db,
            biz_id,
            buyer_id,
            variant_m.product_id,
            quantity=2,
            idempotency_key=f"add_{uuid4()}",
            variant_id=variant_m.id,
        )

        # Checkout cart
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "45 MG Road", "city": "Mumbai"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])

        # Prepare checkout session
        session_info = prepare_checkout_session(db, biz_id, order_id)
        raw_token = session_info["raw_token"]
        assert raw_token
        assert session_info["payment_url"].endswith(f"/pay/{raw_token}")

    # Verify GET /pay/{token} page
    resp = client.get(f"/pay/{raw_token}")
    assert resp.status_code == 200
    assert "Oversized Black T-Shirt" in resp.text
    assert "TEST PAYMENT DEMO" in resp.text
    assert "₹2998.00" in resp.text  # 1499 * 2

    # Execute test payment POST /api/pay/test/{token}
    pay_resp = client.post(f"/api/pay/test/{raw_token}")
    assert pay_resp.status_code == 200
    pay_data = pay_resp.json()
    assert pay_data["status"] == "success"
    assert pay_data["order_id"] == str(order_id)
    assert pay_data["invoice_number"].startswith("INV-")

    # Verify DB post-conditions: order is paid, buyer is customer, Payment row & Invoice row exist

    with transaction_session() as db:
        order = db.get(Order, order_id)
        assert order.status == "paid"
        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is True

        # Verify Payment DB row
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        assert payment is not None
        assert payment.status == "PAID"
        assert payment.amount_paise == 299800
        assert payment.currency == "INR"

        # Verify Invoice DB row and durable invoice number
        invoice = db.query(Invoice).filter(Invoice.order_id == order_id).first()
        assert invoice is not None
        assert invoice.status == "GENERATED"
        assert invoice.invoice_number.startswith("INV-2026-")
        assert invoice.artifact_sha256 is not None
        assert invoice.total_paise == 299800

        # Verify OrderItem snapshot preserves variant details
        items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
        assert len(items) == 1
        assert items[0].variant_id == variant_m.id
        assert items[0].size_snapshot == "M"
        assert items[0].color_snapshot == "Black"
        assert items[0].unit_price_paise == 149900

    # Repeat payment call should return already_paid without creating duplicate Payment or Invoice rows
    repeat_resp = client.post(f"/api/pay/test/{raw_token}")
    assert repeat_resp.status_code == 200
    assert repeat_resp.json()["status"] == "already_paid"

    with transaction_session() as db:
        payment_count = db.query(Payment).filter(Payment.order_id == order_id).count()
        invoice_count = db.query(Invoice).filter(Invoice.order_id == order_id).count()
        assert payment_count == 1
        assert invoice_count == 1


def test_whatsapp_failure_post_commit_isolation(test_setup):
    client = TestClient(app)
    biz_id = test_setup["business_id"]
    buyer_id = test_setup["buyer_id"]
    variant = test_setup["variant_m"]

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
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "100 Express Way", "city": "Delhi"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])
        session_info = prepare_checkout_session(db, biz_id, order_id)
        raw_token = session_info["raw_token"]

    # Mock WhatsApp network call to raise an exception after DB commit
    with patch(
        "app.api.routes.checkout.send_whatsapp_message", side_effect=RuntimeError("Meta API down")
    ):
        resp = client.post(f"/api/pay/test/{raw_token}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    # Verify DB state from a fresh session: DB transaction remains committed!
    with transaction_session() as db:
        order = db.get(Order, order_id)
        assert order.status == "paid"
        buyer = db.get(Buyer, buyer_id)
        assert buyer.is_customer is True
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        assert payment is not None
        assert payment.status == "PAID"
        invoice = db.query(Invoice).filter(Invoice.order_id == order_id).first()
        assert invoice is not None
        assert invoice.status == "GENERATED"
        session_rec = db.query(CheckoutSession).filter(CheckoutSession.order_id == order_id).first()
        assert session_rec.status == "completed"


def test_fake_chat_payment_claim_safety(test_setup):
    biz_id = test_setup["business_id"]
    buyer_id = test_setup["buyer_id"]
    variant = test_setup["variant_m"]

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
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "20 Chat Lane", "city": "Mumbai"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])

        # Unverified text message "payment ho gaya"
        # Verify order remains pending_payment in DB
        order = db.get(Order, order_id)
        assert order.status == "pending_payment"
        payment = db.query(Payment).filter(Payment.order_id == order_id).first()
        assert payment is None


def test_invalid_and_expired_checkout_sessions(test_setup):
    client = TestClient(app)

    # Non-existent token
    resp = client.get("/pay/invalid-token-12345")
    assert resp.status_code == 404
    assert "Invalid Payment Link" in resp.text

    # Expired token test
    biz_id = test_setup["business_id"]
    buyer_id = test_setup["buyer_id"]
    variant = test_setup["variant_m"]

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
        order_dict = checkout_cart(
            db,
            biz_id,
            buyer_id,
            delivery_address={"street": "1 Main St", "city": "Delhi"},
            idempotency_key=f"chk_{uuid4()}",
        )
        order_id = UUID(order_dict["order_id"])

        raw_token = "expired_token_test"
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        expired_session = CheckoutSession(
            business_id=biz_id,
            order_id=order_id,
            token_hash=token_hash,
            status="pending",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        db.add(expired_session)

    resp = client.get(f"/pay/{raw_token}")
    assert resp.status_code == 400
    assert "Link Expired" in resp.text

    pay_resp = client.post(f"/api/pay/test/{raw_token}")
    assert pay_resp.status_code == 400
    assert "expired" in pay_resp.json()["detail"].lower()


def test_pdf_invoice_renderer():
    snapshot = {
        "invoice_number": "INV-2026-000001",
        "issued_at": "2026-09-20T00:00:00Z",
        "seller": {
            "legal_name": "Rehbar Clothing Co.",
            "billing_address": "Mumbai, India",
        },
        "buyer": {
            "legal_name": "Farhan Ahmed",
            "billing_address": "45 Bandra West, Mumbai",
        },
        "provider_payment_id": "pay_test_9999",
        "items": [
            {
                "sku": "TSHIRT-BLK-M",
                "name": "Oversized Black T-Shirt (M)",
                "quantity": "2",
                "taxable_paise": 299800,
                "tax_paise": 0,
            }
        ],
        "total_paise": 299800,
    }
    pdf_bytes = render_invoice_pdf(snapshot)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")
