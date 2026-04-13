import sqlite3
import os
from catalog.category_utils import repair_inventory_categories
from shared.paths import DB_PATH
print("FIXING DB:", DB_PATH)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Add category column safely
try:
    cursor.execute("ALTER TABLE inventory ADD COLUMN category TEXT")
    print("✅ category column added")
except:
    print("⚠️ category column already exists")

# Update old rows safely using known product-category mappings
repair_inventory_categories(cursor)

conn.commit()
conn.close()

print("✅ Database fixed successfully")
