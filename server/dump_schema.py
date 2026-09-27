import sys
import os
from sqlalchemy.schema import CreateTable

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.base import Base
# ensure all models are imported
from app.modules.payments import models as _
from app.modules.identity import models as _
from app.modules.social import models as _
from app.modules.catalog import models as _
from app.modules.invoices import models as _
from app.modules.inventory import models as _
from app.modules.runs import models as _
from app.modules.pricing import models as _
from app.modules.commerce import models as _
from app.modules.whatsapp import models as _

for name, table in Base.metadata.tables.items():
    print(f"--- Table: {name} ---")
    for column in table.columns:
        print(f"  {column.name}: {column.type} (PK: {column.primary_key}, Nullable: {column.nullable})")
    print("\n")
