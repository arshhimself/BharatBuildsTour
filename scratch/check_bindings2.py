import sys
sys.path.insert(0, "server")

from app.db.session import SessionLocal
from sqlalchemy import text

try:
    db = SessionLocal()
    rows = db.execute(text("SELECT provider, phone_number_id, business_id, experience, enabled FROM whatsapp_number_bindings")).fetchall()
    print("BINDINGS:")
    for row in rows:
        print(row)
    db.close()
except Exception as e:
    print(e)
