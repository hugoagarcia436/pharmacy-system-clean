import sqlite3

# Connect (creates file if it doesn't exist)
conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

# =========================
# 👤 USERS TABLE
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

# =========================
# 👤 DEFAULT USERS
# =========================
cursor.execute("""
INSERT OR IGNORE INTO users (name, email, username, password, role)
VALUES 
("Admin User", "admin@email.com", "admin", "admin123", "admin"),
("Employee User", "employee@email.com", "employee", "employee123", "employee"),
("Customer User", "customer@email.com", "customer", "customer123", "customer")
""")

# =========================
# 💊 INVENTORY TABLE
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    sold INTEGER DEFAULT 0,
    total_stock INTEGER,
    updated TEXT,
    status TEXT,
    category TEXT
)
""")

# =========================
# 🔥 ADD CATEGORY COLUMN (SAFE)
# =========================
try:
    cursor.execute("ALTER TABLE inventory ADD COLUMN category TEXT")
except:
    pass  # already exists


# =========================
# 🔥 UPDATE EXISTING DATA WITH CATEGORY (SAFE)
# =========================
cursor.execute("SELECT COUNT(*) FROM inventory WHERE category IS NULL OR category=''")
missing_category = cursor.fetchone()[0]

if missing_category > 0:
    print("🔄 Updating existing items with categories...")

    # 💊 MEDICINE
    cursor.execute("""
    UPDATE inventory SET category='Medicine'
    WHERE name IN (
        'Paracetamol','Ibuprofen','Amoxicillin','Aspirin',
        'Cough Syrup','Allergy Pills','Antibiotic Cream',
        'Insulin','Vitamin C Tablets','Multivitamins',
        'Motion Sickness Pills'
    )
    """)

    # 🧴 COSMETIC
    cursor.execute("""
    UPDATE inventory SET category='Cosmetic'
    WHERE name IN (
        'Face Cleanser','Moisturizing Cream','Sunscreen SPF 50',
        'Aloe Vera Gel','Acne Treatment Gel','Lip Balm'
    )
    """)

    # 🧼 PERSONAL
    cursor.execute("""
    UPDATE inventory SET category='Personal'
    WHERE name IN (
        'Hand Sanitizer','Body Lotion','Shampoo',
        'Conditioner','Toothpaste','Mouthwash'
    )
    """)

    # 🩹 FIRST AID
    cursor.execute("""
    UPDATE inventory SET category='FirstAid'
    WHERE name IN (
        'Bandages Pack','Antiseptic Liquid',
        'Hydrogen Peroxide','Medical Gloves','Thermometer'
    )
    """)

    # ✈️ TRAVEL
    cursor.execute("""
    UPDATE inventory SET category='Travel'
    WHERE name IN (
        'Travel First Aid Kit','Travel Size Shampoo',
        'Travel Size Toothpaste'
    )
    """)

# =========================
# 💊 INSERT INVENTORY DATA
# =========================
cursor.execute("SELECT COUNT(*) FROM inventory")
count = cursor.fetchone()[0]

if count == 0:
    sample_data = [

        # 💊 MEDICINE
        ("Paracetamol", 10.0, 150, 30, 180, "2026-04-08", "In Stock", "Medicine"),
        ("Ibuprofen", 12.5, 100, 20, 120, "2026-04-08", "In Stock", "Medicine"),
        ("Amoxicillin", 25.0, 80, 10, 90, "2026-04-08", "Low Stock", "Medicine"),
        ("Aspirin", 9.0, 140, 40, 180, "2026-04-08", "In Stock", "Medicine"),
        ("Cough Syrup", 15.0, 60, 15, 75, "2026-04-08", "In Stock", "Medicine"),
        ("Allergy Pills", 11.0, 90, 30, 120, "2026-04-08", "In Stock", "Medicine"),
        ("Antibiotic Cream", 18.0, 70, 25, 95, "2026-04-08", "In Stock", "Medicine"),
        ("Insulin", 50.0, 20, 5, 25, "2026-04-08", "Low Stock", "Medicine"),
        ("Vitamin C Tablets", 8.0, 200, 50, 250, "2026-04-08", "In Stock", "Medicine"),
        ("Multivitamins", 14.0, 120, 40, 160, "2026-04-08", "In Stock", "Medicine"),

        # 🧴 SKIN CARE
        ("Face Cleanser", 16.0, 85, 20, 105, "2026-04-08", "In Stock", "Cosmetic"),
        ("Moisturizing Cream", 20.0, 75, 15, 90, "2026-04-08", "In Stock", "Cosmetic"),
        ("Sunscreen SPF 50", 22.0, 60, 10, 70, "2026-04-08", "Low Stock", "Cosmetic"),
        ("Aloe Vera Gel", 13.0, 95, 30, 125, "2026-04-08", "In Stock", "Cosmetic"),
        ("Acne Treatment Gel", 19.0, 50, 10, 60, "2026-04-08", "Low Stock", "Cosmetic"),

        # 🧼 PERSONAL CARE
        ("Hand Sanitizer", 6.0, 300, 120, 420, "2026-04-08", "In Stock", "Personal"),
        ("Body Lotion", 12.0, 110, 35, 145, "2026-04-08", "In Stock", "Personal"),
        ("Shampoo", 9.5, 130, 45, 175, "2026-04-08", "In Stock", "Personal"),
        ("Conditioner", 9.5, 120, 40, 160, "2026-04-08", "In Stock", "Personal"),
        ("Toothpaste", 5.0, 200, 80, 280, "2026-04-08", "In Stock", "Personal"),
        ("Mouthwash", 7.5, 150, 60, 210, "2026-04-08", "In Stock", "Personal"),

        # 🩹 FIRST AID
        ("Bandages Pack", 4.0, 180, 70, 250, "2026-04-08", "In Stock", "FirstAid"),
        ("Antiseptic Liquid", 10.0, 90, 25, 115, "2026-04-08", "In Stock", "FirstAid"),
        ("Hydrogen Peroxide", 8.0, 70, 20, 90, "2026-04-08", "In Stock", "FirstAid"),
        ("Medical Gloves", 6.5, 140, 50, 190, "2026-04-08", "In Stock", "FirstAid"),
        ("Thermometer", 25.0, 40, 10, 50, "2026-04-08", "Low Stock", "FirstAid"),

        # ✈️ TRAVEL
        ("Travel First Aid Kit", 18.0, 60, 20, 80, "2026-04-08", "In Stock", "Travel"),
        ("Motion Sickness Pills", 11.0, 55, 15, 70, "2026-04-08", "In Stock", "Medicine"),
        ("Travel Size Shampoo", 4.5, 100, 30, 130, "2026-04-08", "In Stock", "Travel"),
        ("Travel Size Toothpaste", 3.0, 120, 40, 160, "2026-04-08", "In Stock", "Travel"),
        ("Lip Balm", 2.5, 200, 90, 290, "2026-04-08", "In Stock", "Cosmetic"),
    ]

    cursor.executemany("""
    INSERT INTO inventory (name, price, stock, sold, total_stock, updated, status, category)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_data)

# =========================
# SAVE & CLOSE
# =========================
conn.commit()
conn.close()

print("✅ Database ready with category support")