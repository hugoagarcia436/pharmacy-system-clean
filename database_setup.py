import sqlite3

# Connect (this creates the file automatically)
conn = sqlite3.connect("app_data.db")
cursor = conn.cursor()

# =========================
# CREATE USERS TABLE
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
# INSERT DEFAULT USERS
# =========================
cursor.execute("""
INSERT OR IGNORE INTO users (name, email, username, password, role)
VALUES 
("Admin User", "admin@email.com", "admin", "admin123", "admin"),
("Employee User", "employee@email.com", "employee", "employee123", "employee"),
("Customer User", "customer@email.com", "customer", "customer123", "customer")
""")

conn.commit()
conn.close()

print("Database created successfully ")