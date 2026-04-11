import customtkinter as ctk
import sqlite3
import os
import subprocess
import sys
from category_utils import get_category_where_values, repair_inventory_categories
from session_utils import load_user_cart, save_user_cart

print("USING DB:", os.path.abspath("app_data.db"))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PAGE_CATEGORY = "Personal"
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
SIDEBAR_ITEM_WIDTH = 150
TABLE_COLUMN_WIDTHS = [80, 320, 100, 90, 90, 110]


class PersonalUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Manage Personal Care Items")
        self.geometry("1100x700")

        self.conn = sqlite3.connect("app_data.db")
        self.cursor = self.conn.cursor()
        repair_inventory_categories(self.cursor)
        self.conn.commit()

        self.cart = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()

        sidebar = ctk.CTkFrame(self, width=220)
        sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 0), pady=10)
        sidebar.grid_propagate(False)

        sidebar_content = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            sidebar_content,
            text="Personal Care",
            font=ctk.CTkFont(size=18, weight="bold"),
            width=SIDEBAR_ITEM_WIDTH,
            height=28,
            anchor="w",
            fg_color="transparent",
            hover=False,
            state="disabled",
            text_color_disabled="white",
            border_width=0,
            corner_radius=0
        ).pack(anchor="w", pady=(0, 24))

        ctk.CTkButton(
            sidebar_content,
            text="Checkout",
            command=self.checkout,
            anchor="w",
            width=SIDEBAR_ITEM_WIDTH
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkButton(
            sidebar_content,
            text="Back to Dashboard",
            command=self.go_to_dashboard,
            anchor="w",
            width=SIDEBAR_ITEM_WIDTH
        ).pack(anchor="w")

        self.content = ctk.CTkScrollableFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.create_header()
        self.load_personal_items()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search products...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.go_to_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_header(self):
        header = ctk.CTkFrame(self.content, fg_color="#2b2b2b")
        header.pack(fill="x", padx=10, pady=(0, 5))

        headers = ["Image", "Item Name", "Price", "Stock", "Qty", "Actions"]
        for col, width in enumerate(TABLE_COLUMN_WIDTHS):
            header.grid_columnconfigure(col, minsize=width)

        for i, text in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=text,
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=i, padx=5, pady=8, sticky="w")

    def load_personal_items(self):
        category_values = get_category_where_values(PAGE_CATEGORY)
        placeholders = ",".join("?" for _ in category_values)
        self.cursor.execute(
            f"""
            SELECT * FROM inventory
            WHERE category IN ({placeholders})
            ORDER BY name
            """,
            category_values
        )
        items = self.cursor.fetchall()

        for index, item in enumerate(items):
            self.create_row(item, index)

    def create_row(self, data, index):
        bg_color = "#1f1f1f" if index % 2 == 0 else "#2a2a2a"

        row = ctk.CTkFrame(self.content, fg_color=bg_color)
        row.pack(fill="x", padx=10, pady=2)
        for col, width in enumerate(TABLE_COLUMN_WIDTHS):
            row.grid_columnconfigure(col, minsize=width)

        ctk.CTkLabel(row, text="IMG", anchor="w").grid(row=0, column=0, padx=5, sticky="w")

        ctk.CTkLabel(row, text=data[1], anchor="w").grid(row=0, column=1, padx=5, sticky="w")
        ctk.CTkLabel(row, text=f"${data[2]}", anchor="w").grid(row=0, column=2, padx=5, sticky="w")
        ctk.CTkLabel(row, text=str(data[3]), anchor="w").grid(row=0, column=3, padx=5, sticky="w")

        qty = ctk.CTkEntry(row, width=70)
        qty.insert(0, "1")
        qty.grid(row=0, column=4, padx=5, sticky="w")

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5, padx=5, sticky="w")

        ctk.CTkButton(
            actions,
            text="Add",
            width=60,
            command=lambda d=data, q=qty: self.add_to_cart(d, q)
        ).pack(side="left", padx=3)

    def add_to_cart(self, data, qty_entry):
        try:
            qty = int(qty_entry.get())
        except ValueError:
            return

        if qty <= 0:
            return

        if data[0] in self.cart:
            self.cart[data[0]] += qty
        else:
            self.cart[data[0]] = qty

        self.save_cart_item(data, qty)
        print("Cart:", self.cart)

    def save_cart_item(self, data, qty):
        item_id = str(data[0])
        cart_items = load_user_cart()

        if item_id in cart_items:
            cart_items[item_id]["qty"] += qty
        else:
            cart_items[item_id] = {
                "id": data[0],
                "name": data[1],
                "price": data[2],
                "qty": qty,
                "image": "personal.png"
            }

        save_user_cart(cart_items)

    def checkout(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "cart_ui.py")])
        self.destroy()

    def open_orders(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "customer_orders_ui.py")])
        self.destroy()

    def open_cart(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "cart_ui.py")])
        self.destroy()

    def open_account(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "customer_account_ui.py")])
        self.destroy()

    def go_to_dashboard(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "customer_dashboard_ui.py")])
        self.destroy()

if __name__ == "__main__":
    app = PersonalUI()
    app.mainloop()
