import logging
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, UTC

from app.db.session import get_sessionmaker
from app.modules.commerce.customer_service import process_customer_commerce_message, load_commerce_state
from app.modules.whatsapp.models import WhatsAppMessage
from app.modules.commerce.lifecycle import mark_order_paid_from_verified_payment
from app.modules.payments.models import Payment
from app.modules.commerce.models import CheckoutSession, Order, OrderItem
from app.modules.identity.models import Business, Buyer, StoreProfile
from app.modules.runs.conversation_graph import load_conversation_history

logging.basicConfig(level=logging.WARNING)

def simulate_chat(db: Session, business_id, wa_id, phone_number_id, message: str) -> dict:
    print(f"\n[CUSTOMER]: {message}")
    
    state_before = load_commerce_state(db, business_id, phone_number_id, wa_id)
    print(f"[STATE BEFORE]: route={state_before.get('route')} | intent={state_before.get('last_intent')} | order_id={state_before.get('order_id')} | checkout_stage={state_before.get('checkout_stage')}")
    hist = load_conversation_history(db, wa_id, phone_number_id, business_id=business_id)
    print(f"[HISTORY LENGTH]: {len(hist)}")
    
    inbound_id = f"test_msg_{uuid4().hex[:8]}"
    msg = WhatsAppMessage(
        provider_message_id=inbound_id,
        direction="in",
        business_id=business_id,
        phone_number_id=phone_number_id,
        wa_id=wa_id,
        payload={"text": message},
    )
    db.add(msg)
    db.flush()
    
    outbound_messages = process_customer_commerce_message(
        db, business_id, phone_number_id, wa_id, message, inbound_message_id=inbound_id
    )
    
    if not outbound_messages:
        print("[SALESPERSON]: None")
    
    for m in outbound_messages:
        print(f"[SALESPERSON]: {m.text[:100]}...")
        msg = WhatsAppMessage(
            provider_message_id=f"test_out_{uuid4().hex[:8]}",
            direction="out",
            business_id=business_id,
            phone_number_id=phone_number_id,
            wa_id=wa_id,
            payload={"text": m.text, "commerce_context": getattr(m, 'commerce_context', None)},
        )
        db.add(msg)
    db.commit()
    
    state_after = load_commerce_state(db, business_id, phone_number_id, wa_id)
    return state_after

def main():
    db = get_sessionmaker()()
    from app.seed import DEMO_BUSINESS_ID
    
    wa_id = f"91{uuid4().int % 10000000000:010d}"
    phone_number_id = "1313207358540995"
    business_id = DEMO_BUSINESS_ID
    
    print(f"--- STARTING NEW PURCHASE FLOW ---")
    simulate_chat(db, business_id, wa_id, phone_number_id, "show products")
    simulate_chat(db, business_id, wa_id, phone_number_id, "Ribbed Knit Grey Winter Beanie dikhao")
    simulate_chat(db, business_id, wa_id, phone_number_id, "Free size dedo aur checkout karo")
    
    state = load_commerce_state(db, business_id, phone_number_id, wa_id)
    order_id = state.get("order_id")
    print(f"\n[SYSTEM] Simulating payment success for order_id: {order_id}")
    
    if order_id:
        cs = db.scalar(select(CheckoutSession).where(CheckoutSession.order_id == order_id))
        order = db.scalar(select(Order).where(Order.id == order_id))
        if cs and order:
            cs.status = "completed"
            cs.completed_at = datetime.now(UTC)
            payment = Payment(
                business_id=business_id,
                order_id=order.id,
                status="PAID",
                amount_paise=1000,
                currency="INR",
                provider_account_key="test",
                provider_reference_id="test",
                provider_payment_id="test",
                link_expires_at=datetime.now(UTC),
                paid_at=datetime.now(UTC),
            )
            db.add(payment)
            db.flush()
            mark_order_paid_from_verified_payment(db, business_id, order.id, payment.id)
            db.commit()
            print("[SYSTEM] Payment marked PAID and order marked PAID")
            
            # Simulate the Invoice / confirmation message
            conf_msg = WhatsAppMessage(
                provider_message_id=f"test_conf_{uuid4().hex[:8]}",
                direction="out",
                business_id=business_id,
                phone_number_id=phone_number_id,
                wa_id=wa_id,
                payload={"text": f"Payment received ✅\nOrder #{str(order.id)[:8]} confirmed!\nInvoice generate ho gaya hai."},
            )
            db.add(conf_msg)
            db.commit()
    
    print(f"\n--- STARTING POST-PURCHASE FLOW (SAME BUYER) ---")
    simulate_chat(db, business_id, wa_id, phone_number_id, "Hello")
    simulate_chat(db, business_id, wa_id, phone_number_id, "Mujhe aur products dekhne hai")
    simulate_chat(db, business_id, wa_id, phone_number_id, "Tshirts dikhao")

    print(f"\n--- STARTING FRESH BUYER FLOW ---")
    fresh_wa_id = f"91{uuid4().int % 10000000000:010d}"
    simulate_chat(db, business_id, fresh_wa_id, phone_number_id, "Hello")

if __name__ == "__main__":
    main()
