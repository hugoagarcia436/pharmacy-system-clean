import sqlite3
import os
print("FIXING DB:", os.path.abspath("app_data.db"))

conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

# Add category column safely
try:
    cursor.execute("ALTER TABLE inventory ADD COLUMN category TEXT")
    print("✅ category column added")
except:
    print("⚠️ category column already exists")

# Update old rows
cursor.execute("UPDATE inventory SET category='Medicine' WHERE category IS NULL")

conn.commit()
conn.close()

print("✅ Database fixed successfully")