import pytest
import os
from uuid import uuid4
from sqlalchemy import select
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app
from app.db.session import transaction_session
from app.modules.commerce.customer_service import process_customer_commerce_message, load_commerce_state
from app.modules.whatsapp.models import WhatsAppMessage
from app.modules.commerce.lifecycle import mark_order_paid_from_verified_payment
from app.modules.payments.models import Payment
from app.modules.commerce.models import CheckoutSession, Order
from app.modules.identity.models import Business, Buyer
from app.modules.catalog.models import Product
from app.modules.commerce.cart_service import add_to_cart, checkout_cart
from app.api.routes.checkout import prepare_checkout_session
from app.seed import DEMO_BUSINESS_ID, seed_demo

pytestmark = pytest.mark.skipif(
    os.getenv("STOCKAWARE_RUN_PG_TESTS") != "1",
    reason="Database integration tests require real PostgreSQL container",
)

client = TestClient(app)

def simulate_chat(db, business_id, wa_id, phone_number_id, message: str) -> dict:
    inbound_id = f"test_msg_{uuid4().hex[:8]}"
    msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        direction="in",
        business_id=business_id,
        phone_number_id=phone_number_id,
        wa_id=wa_id,
        payload={"text": message}
    )
    db.add(msg)
    db.flush()

    outbound_messages = process_customer_commerce_message(
        db, business_id, phone_number_id, wa_id, message, inbound_message_id=inbound_id
    )
    for m in outbound_messages:
        msg = WhatsAppMessage(
            provider_message_id=f"test_out_{uuid4().hex[:8]}",
            direction="out",
            business_id=business_id,
            phone_number_id=phone_number_id,
            wa_id=wa_id,
            payload={"text": m.text, "commerce_context": getattr(m, 'commerce_context', None)}
        )
        db.add(msg)
    db.commit()
    return load_commerce_state(db, business_id, phone_number_id, wa_id)

def test_returning_customer_flow():
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID

    from app.db.session import get_sessionmaker
    db_session = get_sessionmaker()()
    try:
        seed_demo(db_session)
        buyer = db_session.scalar(select(Buyer).where(Buyer.business_id == business_id).limit(1))
        wa_id = buyer.whatsapp_e164
        product = db_session.scalar(select(Product).where(Product.business_id == business_id).limit(1))

        # Setup cart manually
        add_to_cart(db_session, business_id, buyer.id, product.id, quantity=1, idempotency_key=f"add_{uuid4().hex}")
        order_dict = checkout_cart(db_session, business_id, buyer.id, delivery_address={"city": "Mumbai"}, idempotency_key=f"chk_{uuid4().hex}")
        order_id = order_dict["order_id"]

        cs_info = prepare_checkout_session(db_session, business_id, order_id)
        raw_token = cs_info["raw_token"]

        db_session.commit()

        with patch("app.api.routes.checkout.send_whatsapp_message") as mock_send, patch("app.api.routes.checkout.send_whatsapp_media") as mock_media:
            response = client.post(f"/api/pay/test/{raw_token}")
            assert response.status_code == 200

        db_session.expire_all()

        # H. Verify Payment
        payment = db_session.scalar(select(Payment).where(Payment.order_id == order_id))
        order = db_session.scalar(select(Order).where(Order.id == order_id))

        assert payment.status == "PAID"
        assert order.status == "paid"

        # THEN inspect commerce state
        post_payment_state = load_commerce_state(db_session, business_id, phone_number_id, wa_id)
        assert post_payment_state.get("order_id") is None
        assert post_payment_state.get("checkout_stage") is None
        assert post_payment_state.get("last_intent") == "payment_confirmed"

        # Same buyer sends Hello
        state_after_hello = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Hello")
        assert state_after_hello.get("order_id") is None
    finally:
        db_session.close()

def test_pending_checkout_continuation():
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID

    from app.db.session import get_sessionmaker
    db_session = get_sessionmaker()()
    try:
        buyer = db_session.scalar(select(Buyer).where(Buyer.business_id == business_id).limit(1))
        wa_id = buyer.whatsapp_e164
        wa_id = buyer.whatsapp_e164
        product = db_session.scalar(select(Product).where(Product.business_id == business_id).limit(1))

        # Setup cart manually
        add_to_cart(db_session, business_id, buyer.id, product.id, quantity=1, idempotency_key=f"add_{uuid4().hex}")
        order_dict = checkout_cart(db_session, business_id, buyer.id, delivery_address={"city": "Mumbai"}, idempotency_key=f"chk_{uuid4().hex}")
        order_id = str(order_dict["order_id"])

        # Mock what the AI does before returning payment link: sets order_id in commerce_context
        # So we just insert a dummy message with context
        msg = WhatsAppMessage(
            provider_message_id=f"test_out_{uuid4().hex[:8]}",
            direction="out",
            business_id=business_id,
            phone_number_id=phone_number_id,
            wa_id=wa_id,
            payload={"text": "Checkout", "commerce_context": {"version": 2, "order_id": order_id, "checkout_stage": "awaiting_payment"}},
        )
        db_session.add(msg)
        db_session.commit()

        # Must retain existing order_id
        state2 = load_commerce_state(db_session, business_id, phone_number_id, wa_id)
        assert state2.get("order_id") == order_id
    finally:
        db_session.close()

def test_payment_claim_trust_boundary():
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID

    from app.db.session import get_sessionmaker
    db_session = get_sessionmaker()()
    try:
        seed_demo(db_session)

        buyer = db_session.scalar(select(Buyer).where(Buyer.business_id == business_id).limit(1))
        wa_id = buyer.whatsapp_e164
        product = db_session.scalar(select(Product).where(Product.business_id == business_id).limit(1))

        add_to_cart(db_session, business_id, buyer.id, product.id, quantity=1, idempotency_key=f"add_{uuid4().hex}")
        order_dict = checkout_cart(db_session, business_id, buyer.id, delivery_address={"city": "Mumbai"}, idempotency_key=f"chk_{uuid4().hex}")
        order_id = str(order_dict["order_id"])

        msg = WhatsAppMessage(
            provider_message_id=f"test_out_{uuid4().hex[:8]}",
            direction="out",
            business_id=business_id,
            phone_number_id=phone_number_id,
            wa_id=wa_id,
            payload={"text": "Checkout", "commerce_context": {"version": 2, "order_id": order_id, "checkout_stage": "awaiting_payment"}},
        )
        db_session.add(msg)
        db_session.commit()

        # Check that payment is NOT PAID in DB
        order = db_session.scalar(select(Order).where(Order.id == order_id))
        assert order.status != "paid"
        state2 = load_commerce_state(db_session, business_id, phone_number_id, wa_id)
        assert state2.get("order_id") == order_id # Session still active
    finally:
        db_session.close()

def test_second_purchase():
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID

    from app.db.session import get_sessionmaker
    db_session = get_sessionmaker()()
    try:
        seed_demo(db_session)

        buyer = db_session.scalar(select(Buyer).where(Buyer.business_id == business_id).limit(1))
        wa_id = buyer.whatsapp_e164
        product = db_session.scalar(select(Product).where(Product.business_id == business_id).limit(1))

        add_to_cart(db_session, business_id, buyer.id, product.id, quantity=1, idempotency_key=f"add_{uuid4().hex}")
        order_dict = checkout_cart(db_session, business_id, buyer.id, delivery_address={"city": "Mumbai"}, idempotency_key=f"chk_{uuid4().hex}")
        order_id1 = str(order_dict["order_id"])

        cs_info = prepare_checkout_session(db_session, business_id, order_id1)
        raw_token = cs_info["raw_token"]

        db_session.commit()

        with patch("app.api.routes.checkout.send_whatsapp_message") as mock_send, patch("app.api.routes.checkout.send_whatsapp_media") as mock_media:
            response = client.post(f"/api/pay/test/{raw_token}")
            assert response.status_code == 200

        db_session.expire_all()

        # Start second purchase with dummy commerce context
        msg = WhatsAppMessage(
            provider_message_id=f"test_out_{uuid4().hex[:8]}",
            direction="out",
            business_id=business_id,
            phone_number_id=phone_number_id,
            wa_id=wa_id,
            payload={"text": "Checkout", "commerce_context": {"version": 2, "order_id": order_id1, "checkout_stage": "awaiting_payment"}}, # This old state shouldn't break next purchase
        )
        db_session.add(msg)
        db_session.commit()

        # Start second purchase
        add_to_cart(db_session, business_id, buyer.id, product.id, quantity=2, idempotency_key=f"add_{uuid4().hex}")
        order_dict2 = checkout_cart(db_session, business_id, buyer.id, delivery_address={"city": "Mumbai"}, idempotency_key=f"chk_{uuid4().hex}")
        order_id2 = str(order_dict2["order_id"])

        # First order should still be paid
        order1 = db_session.scalar(select(Order).where(Order.id == order_id1))
        assert order1.status == "paid"

        # Second order should be pending
        order2 = db_session.scalar(select(Order).where(Order.id == order_id2))
        assert order2.status == "pending_payment"
    finally:
        db_session.close()
