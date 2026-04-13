import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")

DB_PATH = os.path.join(DATA_DIR, "app_data.db")
SESSION_FILE = os.path.join(DATA_DIR, "current_user.json")
CART_FILE = os.path.join(DATA_DIR, "cart_data.json")
ORDERS_FILE = os.path.join(DATA_DIR, "customer_orders_data.json")
CHECKOUT_DETAILS_FILE = os.path.join(DATA_DIR, "customer_checkout_data.json")
PAYMENT_METHODS_FILE = os.path.join(DATA_DIR, "customer_payment_methods.json")
RECEIPTS_DIR = os.path.join(DATA_DIR, "receipts")
