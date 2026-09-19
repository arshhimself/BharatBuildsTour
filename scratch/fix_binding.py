import sys
sys.path.insert(0, "server")
from app.db.session import get_sessionmaker
from sqlalchemy import text

try:
    db = get_sessionmaker()()
    db.execute(text("""
        UPDATE whatsapp_number_bindings
        SET experience = 'customer_commerce'
        WHERE phone_number_id = '1313207358540995'
    """))
    db.commit()
    print("Successfully updated binding to customer_commerce!")

    rows = db.execute(text("SELECT provider, phone_number_id, experience, enabled FROM whatsapp_number_bindings")).fetchall()
    for row in rows:
        print(row)
    db.close()
except Exception as e:
    print(e)
