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
    status TEXT
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
        ("Paracetamol", 10.0, 150, 30, 180, "2026-04-08", "In Stock"),
        ("Ibuprofen", 12.5, 100, 20, 120, "2026-04-08", "In Stock"),
        ("Amoxicillin", 25.0, 80, 10, 90, "2026-04-08", "Low Stock"),
        ("Aspirin", 9.0, 140, 40, 180, "2026-04-08", "In Stock"),
        ("Cough Syrup", 15.0, 60, 15, 75, "2026-04-08", "In Stock"),
        ("Allergy Pills", 11.0, 90, 30, 120, "2026-04-08", "In Stock"),
        ("Antibiotic Cream", 18.0, 70, 25, 95, "2026-04-08", "In Stock"),
        ("Insulin", 50.0, 20, 5, 25, "2026-04-08", "Low Stock"),
        ("Vitamin C Tablets", 8.0, 200, 50, 250, "2026-04-08", "In Stock"),
        ("Multivitamins", 14.0, 120, 40, 160, "2026-04-08", "In Stock"),

        # 🧴 SKIN CARE
        ("Face Cleanser", 16.0, 85, 20, 105, "2026-04-08", "In Stock"),
        ("Moisturizing Cream", 20.0, 75, 15, 90, "2026-04-08", "In Stock"),
        ("Sunscreen SPF 50", 22.0, 60, 10, 70, "2026-04-08", "Low Stock"),
        ("Aloe Vera Gel", 13.0, 95, 30, 125, "2026-04-08", "In Stock"),
        ("Acne Treatment Gel", 19.0, 50, 10, 60, "2026-04-08", "Low Stock"),

        # 🧼 PERSONAL CARE
        ("Hand Sanitizer", 6.0, 300, 120, 420, "2026-04-08", "In Stock"),
        ("Body Lotion", 12.0, 110, 35, 145, "2026-04-08", "In Stock"),
        ("Shampoo", 9.5, 130, 45, 175, "2026-04-08", "In Stock"),
        ("Conditioner", 9.5, 120, 40, 160, "2026-04-08", "In Stock"),
        ("Toothpaste", 5.0, 200, 80, 280, "2026-04-08", "In Stock"),
        ("Mouthwash", 7.5, 150, 60, 210, "2026-04-08", "In Stock"),

        # 🩹 FIRST AID
        ("Bandages Pack", 4.0, 180, 70, 250, "2026-04-08", "In Stock"),
        ("Antiseptic Liquid", 10.0, 90, 25, 115, "2026-04-08", "In Stock"),
        ("Hydrogen Peroxide", 8.0, 70, 20, 90, "2026-04-08", "In Stock"),
        ("Medical Gloves", 6.5, 140, 50, 190, "2026-04-08", "In Stock"),
        ("Thermometer", 25.0, 40, 10, 50, "2026-04-08", "Low Stock"),

        # ✈️ TRAVEL ESSENTIALS
        ("Travel First Aid Kit", 18.0, 60, 20, 80, "2026-04-08", "In Stock"),
        ("Motion Sickness Pills", 11.0, 55, 15, 70, "2026-04-08", "In Stock"),
        ("Travel Size Shampoo", 4.5, 100, 30, 130, "2026-04-08", "In Stock"),
        ("Travel Size Toothpaste", 3.0, 120, 40, 160, "2026-04-08", "In Stock"),
        ("Lip Balm", 2.5, 200, 90, 290, "2026-04-08", "In Stock"),
    ]

    cursor.executemany("""
    INSERT INTO inventory (name, price, stock, sold, total_stock, updated, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, sample_data)

# =========================
# SAVE & CLOSE
# =========================
conn.commit()
conn.close()

print("✅ Database ready: users + inventory")