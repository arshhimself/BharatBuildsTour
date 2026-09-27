import pytest
import logging
from uuid import uuid4
from datetime import datetime, UTC
from sqlalchemy import select
from app.modules.commerce.customer_service import process_customer_commerce_message, load_commerce_state
from app.modules.whatsapp.models import WhatsAppMessage
from app.modules.commerce.lifecycle import mark_order_paid_from_verified_payment
from app.modules.payments.models import Payment
from app.modules.commerce.models import CheckoutSession, Order, OrderItem
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.seed import DEMO_BUSINESS_ID
from app.api.routes.checkout import process_test_payment
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def simulate_chat(db, business_id, wa_id, phone_number_id, message: str) -> dict:
    inbound_id = f"test_msg_{uuid4().hex[:8]}"
    msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        direction="in",
        business_id=business_id,
        phone_number_id=phone_number_id,
        wa_id=wa_id,
        payload={"text": message},
        status="received"
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
            payload={"text": m.text, "commerce_context": getattr(m, 'commerce_context', None)},
            status="sent"
        )
        db.add(msg)
    db.commit()
    return load_commerce_state(db, business_id, phone_number_id, wa_id)

def test_returning_customer_flow(db_session):
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID
    
    # A. Browse products
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "show products")
    # B/C. Select product/variant
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "Ribbed Knit Grey Winter Beanie dikhao")
    # D/E/F. Checkout
    state = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Free size dedo aur checkout karo")
    
    order_id = state.get("order_id")
    assert order_id is not None
    checkout_session_id = state.get("checkout_session_id")
    
    # G. Complete authoritative TEST payment
    cs = db_session.scalar(select(CheckoutSession).where(CheckoutSession.id == checkout_session_id))
    
    # Use the test client to hit the checkout API to simulate real behavior!
    response = client.post(f"/api/checkout/test-payment/{cs.token_hash}")
    assert response.status_code == 200
    db_session.commit()
    
    # H. Verify Payment
    payment = db_session.scalar(select(Payment).where(Payment.order_id == order_id))
    order = db_session.scalar(select(Order).where(Order.id == order_id))
    buyer = db_session.scalar(select(Buyer).where(Buyer.whatsapp_e164 == wa_id))
    
    assert payment.status == "PAID"
    assert order.status == "paid"
    assert buyer.is_customer == True
    
    # THEN inspect commerce state
    post_payment_state = load_commerce_state(db_session, business_id, phone_number_id, wa_id)
    assert post_payment_state.get("order_id") is None
    assert post_payment_state.get("checkout_stage") is None
    assert post_payment_state.get("last_intent") == "payment_confirmed"
    
    # Same buyer sends Hello
    state_after_hello = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Hello")
    assert state_after_hello.get("order_id") is None
    
def test_pending_checkout_continuation(db_session):
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID
    
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "show products")
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "Ribbed Knit Grey Winter Beanie dikhao")
    state = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Free size dedo aur checkout karo")
    
    order_id = state.get("order_id")
    assert order_id is not None
    
    # Customer asks for payment link
    state2 = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Kaha payment karna hai?")
    
    # Must retain existing order_id
    assert state2.get("order_id") == order_id
    
def test_payment_claim_trust_boundary(db_session):
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID
    
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "show products")
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "Ribbed Knit Grey Winter Beanie dikhao")
    state = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Free size dedo aur checkout karo")
    
    order_id = state.get("order_id")
    
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "payment ho gaya")
    
    # Check that payment is NOT PAID in DB
    order = db_session.scalar(select(Order).where(Order.id == order_id))
    assert order.status != "paid"
    
def test_second_purchase(db_session):
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID
    
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "show products")
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "Ribbed Knit Grey Winter Beanie dikhao")
    state = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Free size dedo aur checkout karo")
    order_id1 = state.get("order_id")
    cs = db_session.scalar(select(CheckoutSession).where(CheckoutSession.id == state.get("checkout_session_id")))
    
    response = client.post(f"/api/checkout/test-payment/{cs.token_hash}")
    assert response.status_code == 200
    db_session.commit()
    
    # Start second purchase
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "aur kuch dikhao")
    simulate_chat(db_session, business_id, wa_id, phone_number_id, "Embroidered Streetwear Baseball Cap dikhao")
    state2 = simulate_chat(db_session, business_id, wa_id, phone_number_id, "Free size add to cart aur checkout")
    
    order_id2 = state2.get("order_id")
    assert order_id2 is not None
    assert order_id2 != order_id1
