from datetime import datetime


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now_timestamp():
    return datetime.now().strftime("%Y-%m-%d %I:%M %p")


def inventory_status(stock):
    if stock <= 0:
        return "Out of Stock"
    if stock <= 25:
        return "Low Stock"
    return "In Stock"


def inventory_status_color(status):
    normalized = str(status).strip().lower()
    if normalized == "out of stock":
        return "#ff4d4d"
    if normalized == "low stock":
        return "#ff4d4d"
    if normalized == "in stock":
        return "#00c853"
    return "white"


def ensure_inventory_transaction_schema(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inventory_id INTEGER NOT NULL,
        item_name TEXT NOT NULL,
        change_type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        stock_before INTEGER NOT NULL,
        stock_after INTEGER NOT NULL,
        reference TEXT,
        created_at TEXT NOT NULL
    )
    """)


def record_inventory_transaction(cursor, item_id, item_name, change_type, quantity, before, after, reference=""):
    ensure_inventory_transaction_schema(cursor)
    cursor.execute(
        """
        INSERT INTO inventory_transactions (
            inventory_id,
            item_name,
            change_type,
            quantity,
            stock_before,
            stock_after,
            reference,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (item_id, item_name, change_type, quantity, before, after, reference, now_timestamp())
    )


def receive_inventory(cursor, item_id, quantity, reference="Received stock"):
    cursor.execute("SELECT name, stock, total_stock FROM inventory WHERE id=?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise ValueError("Inventory item not found")

    name, current_stock, total_stock = item
    new_stock = current_stock + quantity
    new_total = (total_stock or current_stock) + quantity

    cursor.execute(
        """
        UPDATE inventory
        SET stock=?, total_stock=?, status=?, updated=?
        WHERE id=?
        """,
        (new_stock, new_total, inventory_status(new_stock), today(), item_id)
    )
    record_inventory_transaction(cursor, item_id, name, "received", quantity, current_stock, new_stock, reference)
    return new_stock


def set_inventory_stock(cursor, item_id, new_stock, reference="Employee stock update"):
    cursor.execute("SELECT name, stock, total_stock FROM inventory WHERE id=?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise ValueError("Inventory item not found")

    name, current_stock, total_stock = item
    stock_difference = new_stock - current_stock
    new_total = total_stock or current_stock
    if stock_difference > 0:
        new_total += stock_difference

    cursor.execute(
        """
        UPDATE inventory
        SET stock=?, total_stock=?, status=?, updated=?
        WHERE id=?
        """,
        (new_stock, new_total, inventory_status(new_stock), today(), item_id)
    )

    change_type = "received" if stock_difference >= 0 else "adjusted"
    record_inventory_transaction(
        cursor,
        item_id,
        name,
        change_type,
        abs(stock_difference),
        current_stock,
        new_stock,
        reference
    )
    return new_stock


def sell_inventory(cursor, item_id, quantity, reference="Customer purchase"):
    cursor.execute("SELECT name, stock, sold FROM inventory WHERE id=?", (item_id,))
    item = cursor.fetchone()
    if item is None:
        raise ValueError("Inventory item not found")

    name, current_stock, current_sold = item
    if quantity > current_stock:
        raise ValueError(f"Only {current_stock} left for {name}")

    new_stock = current_stock - quantity
    new_sold = (current_sold or 0) + quantity

    cursor.execute(
        """
        UPDATE inventory
        SET stock=?, sold=?, status=?, updated=?
        WHERE id=?
        """,
        (new_stock, new_sold, inventory_status(new_stock), today(), item_id)
    )
    record_inventory_transaction(cursor, item_id, name, "sold", quantity, current_stock, new_stock, reference)
    return new_stock


def validate_cart_stock(cursor, cart_items):
    shortages = []
    for item in cart_items.values():
        item_id = item.get("id")
        requested_qty = item.get("qty", 0)
        cursor.execute("SELECT name, stock FROM inventory WHERE id=?", (item_id,))
        result = cursor.fetchone()
        if result is None:
            shortages.append(f"{item.get('name', 'Item')} is no longer available")
            continue

        name, available_stock = result
        if requested_qty > available_stock:
            shortages.append(f"{name}: requested {requested_qty}, available {available_stock}")

    return shortages
