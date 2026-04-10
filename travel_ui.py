import customtkinter as ctk
import sqlite3
from PIL import Image
import os
import json
import subprocess
import sys
from session_utils import load_user_cart, save_user_cart

print("USING DB:", os.path.abspath("app_data.db"))

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

TRAVEL_ITEMS = (
    "Travel First Aid Kit",
    "Travel Size Shampoo",
    "Travel Size Toothpaste",
)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))


class TravelUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Manage Travel Items")
        self.geometry("1100x700")

        self.conn = sqlite3.connect("app_data.db")
        self.cursor = self.conn.cursor()

        self.cart = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()

        sidebar = ctk.CTkFrame(self, width=220)
        sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 0), pady=10)
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="Travel Essentials",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        ctk.CTkButton(
            sidebar,
            text="Checkout",
            command=self.checkout
        ).pack(pady=10, padx=10, fill="x")

        ctk.CTkButton(
            sidebar,
            text="Back to Dashboard",
            command=self.go_to_dashboard
        ).pack(pady=10, padx=10, fill="x")

        self.content = ctk.CTkScrollableFrame(self)
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.create_header()
        self.load_travel_items()

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
        widths = [80, 250, 100, 100, 80, 200]

        for i, text in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=text,
                width=widths[i],
                anchor="w",
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=i, padx=5, pady=8, sticky="w")

    def load_travel_items(self):
        placeholders = ",".join("?" for _ in TRAVEL_ITEMS)
        self.cursor.execute(
            f"""
            SELECT * FROM inventory
            WHERE name IN ({placeholders})
            ORDER BY name
            """,
            TRAVEL_ITEMS
        )
        items = self.cursor.fetchall()

        for index, item in enumerate(items):
            self.create_row(item, index)

    def create_row(self, data, index):
        bg_color = "#1f1f1f" if index % 2 == 0 else "#2a2a2a"

        row = ctk.CTkFrame(self.content, fg_color=bg_color)
        row.pack(fill="x", padx=10, pady=2)

        img_path = "assets/images/travel.png"

        if os.path.exists(img_path):
            img = Image.open(img_path)
            img = ctk.CTkImage(img, size=(40, 40))
            ctk.CTkLabel(row, image=img, text="", width=80).grid(row=0, column=0, padx=5)
        else:
            ctk.CTkLabel(row, text="IMG", width=80).grid(row=0, column=0)

        ctk.CTkLabel(row, text=data[1], width=250, anchor="w").grid(row=0, column=1, padx=5)
        ctk.CTkLabel(row, text=f"${data[2]}", width=100).grid(row=0, column=2)
        ctk.CTkLabel(row, text=str(data[3]), width=100).grid(row=0, column=3)

        qty = ctk.CTkEntry(row, width=60)
        qty.insert(0, "1")
        qty.grid(row=0, column=4)

        actions = ctk.CTkFrame(row, fg_color="transparent")
        actions.grid(row=0, column=5, padx=5)

        ctk.CTkButton(
            actions,
            text="Add",
            width=60,
            command=lambda d=data, q=qty: self.add_to_cart(d, q)
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            actions,
            text="Buy Now",
            width=80,
            command=lambda d=data, q=qty: self.buy_now(d, q)
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
                "image": "travel.png"
            }

        save_user_cart(cart_items)

    def buy_now(self, data, qty_entry):
        try:
            qty = int(qty_entry.get())
        except ValueError:
            return

        self.process_order(data[0], qty)

    def checkout(self):
        subprocess.Popen([sys.executable, os.path.join(BASE_DIR, "cart_ui.py")])

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

    def process_order(self, item_id, qty):
        self.cursor.execute("SELECT stock FROM inventory WHERE id=?", (item_id,))
        result = self.cursor.fetchone()

        if not result:
            return

        stock = result[0]

        if qty > stock:
            print("Not enough stock")
            return

        new_stock = stock - qty

        self.cursor.execute(
            "UPDATE inventory SET stock=? WHERE id=?",
            (new_stock, item_id)
        )
        self.conn.commit()

        self.reload()

    def reload(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.create_header()
        self.load_travel_items()


if __name__ == "__main__":
    app = TravelUI()
    app.mainloop()
