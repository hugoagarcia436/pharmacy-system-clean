import json
import os

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SESSION_FILE = os.path.join(BASE_DIR, "current_user.json")
CART_FILE = os.path.join(BASE_DIR, "cart_data.json")
ORDERS_FILE = os.path.join(BASE_DIR, "customer_orders_data.json")
CHECKOUT_DETAILS_FILE = os.path.join(BASE_DIR, "customer_checkout_data.json")
PAYMENT_METHODS_FILE = os.path.join(BASE_DIR, "customer_payment_methods.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def set_current_user(user_data):
    save_json(SESSION_FILE, user_data)


def get_current_user():
    return load_json(SESSION_FILE, {})


def clear_current_user():
    save_json(SESSION_FILE, {})


def get_current_username():
    return get_current_user().get("username", "")


def load_user_cart():
    username = get_current_username()
    if not username:
        return {}

    cart_store = load_json(CART_FILE, {})

    # Backward compatibility with the old single-user cart format.
    if cart_store and all(isinstance(value, dict) and "id" in value for value in cart_store.values()):
        return cart_store

    return cart_store.get(username, {})


def save_user_cart(cart_items):
    username = get_current_username()
    if not username:
        return

    cart_store = load_json(CART_FILE, {})

    if cart_store and all(isinstance(value, dict) and "id" in value for value in cart_store.values()):
        cart_store = {}

    cart_store[username] = cart_items
    save_json(CART_FILE, cart_store)


def clear_user_cart():
    username = get_current_username()
    if not username:
        return

    cart_store = load_json(CART_FILE, {})

    if cart_store and all(isinstance(value, dict) and "id" in value for value in cart_store.values()):
        cart_store = {}

    cart_store[username] = {}
    save_json(CART_FILE, cart_store)


def load_all_orders():
    return load_json(ORDERS_FILE, [])


def save_all_orders(orders):
    save_json(ORDERS_FILE, orders)


def load_checkout_details():
    username = get_current_username()
    if not username:
        return {}

    details_store = load_json(CHECKOUT_DETAILS_FILE, {})
    return details_store.get(username, {})


def save_checkout_details(details):
    username = get_current_username()
    if not username:
        return

    details_store = load_json(CHECKOUT_DETAILS_FILE, {})
    details_store[username] = details
    save_json(CHECKOUT_DETAILS_FILE, details_store)


def load_payment_methods():
    username = get_current_username()
    if not username:
        return {}

    methods_store = load_json(PAYMENT_METHODS_FILE, {})
    return methods_store.get(username, {})


def save_payment_methods(methods):
    username = get_current_username()
    if not username:
        return

    methods_store = load_json(PAYMENT_METHODS_FILE, {})
    methods_store[username] = methods
    save_json(PAYMENT_METHODS_FILE, methods_store)
