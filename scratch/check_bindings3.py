import sys
sys.path.insert(0, ".")

from app.db.session import get_sessionmaker
from sqlalchemy import text

try:
    db = get_sessionmaker()()
    rows = db.execute(text("SELECT provider, phone_number_id, business_id, experience, enabled FROM whatsapp_number_bindings")).fetchall()
    print("BINDINGS:")
    for row in rows:
        print(row)
    db.close()
except Exception as e:
    print(e)
