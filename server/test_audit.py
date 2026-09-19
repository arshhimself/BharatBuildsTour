import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))
sys.path.append(os.path.dirname(__file__))

from datetime import UTC, datetime

from app.db.session import transaction_session
from app.modules.commerce.discovery_service import process_customer_commerce_message
from app.modules.whatsapp.models import WhatsAppMessage
from app.seed import DEMO_BUSINESS_ID


def _turn(db, business_id, phone_id, wa_id, sequence, text):
    outbound = process_customer_commerce_message(db, business_id, phone_id, wa_id, text)
    msg = outbound[-1]
    db.add(
        WhatsAppMessage(
            provider_message_id=f"audit-out-{wa_id}-{sequence}",
            direction="out",
            wa_id=wa_id,
            phone_number_id=phone_id,
            business_id=business_id,
            created_at=datetime.now(UTC),
            payload={
                "text": msg.text,
                "commerce_context": getattr(msg, "commerce_context", {}),
            },
        )
    )
    db.commit()
    return msg


import random


def run_test():
    phone_id = "test-phone-123"
    wa_id = f"+9190000{random.randint(10000, 99999)}"

    with transaction_session() as db:
        print("REQUEST 1: products dikhao")
        msg1 = _turn(db, DEMO_BUSINESS_ID, phone_id, wa_id, 1, "products dikhao")
        print("Response 1:", msg1.text)
        print("Context 1:", msg1.commerce_context)
        print("-" * 50)

    with transaction_session() as db:
        print("REQUEST 2: second wala")
        msg2 = _turn(db, DEMO_BUSINESS_ID, phone_id, wa_id, 2, "second wala")
        print("Response 2:", msg2.text)
        print("Context 2:", msg2.commerce_context)
        print("-" * 50)

    with transaction_session() as db:
        print("REQUEST 3: ek chahiye")
        msg3 = _turn(db, DEMO_BUSINESS_ID, phone_id, wa_id, 3, "ek chahiye")
        print("Response 3:", msg3.text)
        print("Context 3:", msg3.commerce_context)
        print("-" * 50)

    with transaction_session() as db:
        print("REQUEST 4: haa checkout bana do")
        msg4 = _turn(db, DEMO_BUSINESS_ID, phone_id, wa_id, 4, "haa checkout bana do")
        print("Response 4:", msg4.text)
        print("Context 4:", msg4.commerce_context)
        print("-" * 50)


if __name__ == "__main__":
    run_test()
