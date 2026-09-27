import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.db.base import Base

# ensure all models are imported

for name, table in Base.metadata.tables.items():
    print(f"--- Table: {name} ---")
    for column in table.columns:
        print(
            f"  {column.name}: {column.type} (PK: {column.primary_key}, Nullable: {column.nullable})"
        )
    print("\n")
