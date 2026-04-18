import re
from datetime import datetime


EMPLOYEE_ROLE_VALUES = ("employee",)


def ensure_employee_user_schema(cursor):
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

    cursor.execute("PRAGMA table_info(users)")
    columns = {row[1] for row in cursor.fetchall()}

    additions = {
        "employee_id": "TEXT",
        "phone": "TEXT",
        "employee_position": "TEXT",
        "shift": "TEXT",
        "status": "TEXT DEFAULT 'Active'",
        "hire_date": "TEXT",
        "last_login": "TEXT",
        "password_setup_required": "INTEGER DEFAULT 0",
    }

    for column, definition in additions.items():
        if column not in columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")


def generate_employee_id(cursor):
    cursor.execute("""
        SELECT employee_id FROM users
        WHERE employee_id IS NOT NULL AND employee_id LIKE 'EMP-%'
    """)
    max_number = 0
    for (employee_id,) in cursor.fetchall():
        try:
            number = int(employee_id.split("-")[1])
            max_number = max(max_number, number)
        except (IndexError, ValueError):
            pass
    return f"EMP-{max_number + 1:03d}"


def assign_missing_employee_ids(cursor):
    cursor.execute("""
        SELECT id FROM users
        WHERE role IN ('employee')
        AND (employee_id IS NULL OR employee_id = '')
        ORDER BY id
    """)
    for (user_id,) in cursor.fetchall():
        cursor.execute(
            "UPDATE users SET employee_id=? WHERE id=?",
            (generate_employee_id(cursor), user_id)
        )


def validate_employee_password(password):
    if len(password) < 12 or len(password) > 16:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def normalize_text(value):
    return " ".join(value.strip().lower().split())


def find_employee_for_password_setup(cursor, employee_id, identifier, full_name):
    cursor.execute("""
        SELECT id, name, email, username, password_setup_required
        FROM users
        WHERE role IN ('employee')
        AND lower(employee_id) = lower(?)
        AND (lower(username) = lower(?) OR lower(email) = lower(?))
    """, (employee_id.strip(), identifier.strip(), identifier.strip()))

    user = cursor.fetchone()
    if user is None:
        return None

    _, name, _, _, _ = user
    if normalize_text(name) != normalize_text(full_name):
        return None

    return user


def employee_row_to_dict(row):
    (
        employee_id,
        name,
        email,
        username,
        phone,
        employee_position,
        shift,
        status,
        hire_date,
        last_login,
        password_setup_required,
    ) = row

    return {
        "id": employee_id,
        "name": name,
        "role": employee_position or "Employee",
        "shift": shift or "Unassigned",
        "status": status or "Active",
        "phone": phone or "N/A",
        "email": email,
        "hire_date": hire_date or datetime.now().strftime("%Y-%m-%d"),
        "username": username,
        "last_login": last_login or "Never",
        "orders_handled": 0,
        "items_processed": 0,
        "activity": "Password setup pending" if password_setup_required else "Account ready",
    }
