from app.db.session import get_sessionmaker
from app.modules.commerce import customer_service
from app.seed import DEMO_BUSINESS_ID

SessionLocal = get_sessionmaker()
db = SessionLocal()

print("Testing Hello Bhai...")
try:
    responses = customer_service.process_customer_commerce_message(
        db, DEMO_BUSINESS_ID, "test-phone-id", "919999999999", "Hello Bhai"
    )
    for r in responses:
        print(f"RESPONSE: {r.text}")
finally:
    db.close()
