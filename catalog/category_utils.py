INVENTORY_CATEGORIES = ["Medicine", "Cosmetic", "Personal", "FirstAid", "Travel"]

CATEGORY_DISPLAY_NAMES = {
    "Medicine": "Medicine",
    "Cosmetic": "Cosmetic",
    "Personal": "Personal Care",
    "FirstAid": "First Aid",
    "Travel": "Travel",
}

PRODUCT_CATEGORY_MAP = {
    "Paracetamol": "Medicine",
    "Ibuprofen": "Medicine",
    "Amoxicillin": "Medicine",
    "Aspirin": "Medicine",
    "Cough Syrup": "Medicine",
    "Allergy Pills": "Medicine",
    "Antibiotic Cream": "Medicine",
    "Insulin": "Medicine",
    "Vitamin C Tablets": "Medicine",
    "Multivitamins": "Medicine",
    "Motion Sickness Pills": "Medicine",
    "Face Cleanser": "Cosmetic",
    "Moisturizing Cream": "Cosmetic",
    "Sunscreen SPF 50": "Cosmetic",
    "Aloe Vera Gel": "Cosmetic",
    "Acne Treatment Gel": "Cosmetic",
    "Lip Balm": "Cosmetic",
    "Hand Sanitizer": "Personal",
    "Body Lotion": "Personal",
    "Shampoo": "Personal",
    "Conditioner": "Personal",
    "Toothpaste": "Personal",
    "Mouthwash": "Personal",
    "Bandages Pack": "FirstAid",
    "Antiseptic Liquid": "FirstAid",
    "Hydrogen Peroxide": "FirstAid",
    "Medical Gloves": "FirstAid",
    "Thermometer": "FirstAid",
    "Travel First Aid Kit": "Travel",
    "Travel Size Shampoo": "Travel",
    "Travel Size Toothpaste": "Travel",
}

_CATEGORY_ALIASES = {
    "medicine": "Medicine",
    "cosmetic": "Cosmetic",
    "personal": "Personal",
    "personalcare": "Personal",
    "firstaid": "FirstAid",
    "travel": "Travel",
}


def normalize_category(category):
    if not category:
        return None

    key = "".join(str(category).strip().lower().split())
    return _CATEGORY_ALIASES.get(key)


def get_category_where_values(category):
    normalized = normalize_category(category)
    if normalized == "Personal":
        return ["Personal", "Personal Care"]
    if normalized == "FirstAid":
        return ["FirstAid", "First Aid"]
    if normalized:
        return [normalized]
    return [category]


def repair_inventory_categories(cursor):
    cursor.execute("SELECT id, name, category FROM inventory")
    rows = cursor.fetchall()

    updates = []

    for item_id, name, current_category in rows:
        expected_category = PRODUCT_CATEGORY_MAP.get(name)
        normalized_current = normalize_category(current_category)

        if expected_category and normalized_current != expected_category:
            updates.append((expected_category, item_id))
        elif not expected_category and current_category != normalized_current and normalized_current:
            updates.append((normalized_current, item_id))

    if updates:
        cursor.executemany(
            "UPDATE inventory SET category=? WHERE id=?",
            updates
        )

    return len(updates)
