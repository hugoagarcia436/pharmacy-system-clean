import os
import sqlite3

import customtkinter as ctk
from PIL import Image

from catalog.category_utils import (
    CATEGORY_DISPLAY_NAMES,
    get_category_where_values,
    normalize_category,
    repair_inventory_categories,
)
from shared.paths import DB_PATH, IMAGES_DIR
from shared.image_utils import product_image_name
from shared.session_utils import load_user_cart, save_user_cart


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

SIDEBAR_ITEM_WIDTH = 150
TABLE_COLUMN_WIDTHS = [80, 320, 100, 90, 90, 110]

CATEGORY_PAGE_TITLES = {
    "Medicine": "Manage Medicine Items",
    "Cosmetic": "Manage Cosmetic Items",
    "Personal": "Manage Personal Care Items",
    "FirstAid": "Manage First Aid Items",
    "Travel": "Manage Travel Items",
}

CATEGORY_SIDE_LABELS = {
    "Medicine": "Medicine",
    "Cosmetic": "Cosmetics",
    "Personal": "Personal Care",
    "FirstAid": "First Aid",
    "Travel": "Travel Essentials",
}

CATEGORY_IMAGE_KEYS = {
    "Medicine": "Paracetamol.png",
    "Cosmetic": "Moisturizing Cream.png",
    "Personal": "Shampoo.png",
    "FirstAid": "Bandages Pack.png",
    "Travel": "travel.png",
}


class CategoryUI(ctk.CTkFrame):
    def __init__(self, parent, controller, category):
        super().__init__(parent)
        self.controller = controller
        self.category = normalize_category(category)

        if self.category is None:
            raise ValueError(f"Unknown category: {category}")

        display_name = CATEGORY_DISPLAY_NAMES.get(self.category, self.category)
        self.controller.title(CATEGORY_PAGE_TITLES.get(self.category, f"Manage {display_name} Items"))
        self.controller.geometry("1100x700")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        repair_inventory_categories(self.cursor)
        self.conn.commit()

        self.cart = {}
        self.feedback_labels = {}
        self.image_refs = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_sidebar()

        self.content = ctk.CTkScrollableFrame(self, fg_color="#f6fbf9")
        self.content.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        self.load_items()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70, fg_color="#e4f7f0")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search products or ID...", height=40)
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=20)
        self.search_entry.bind("<KeyRelease>", lambda event: self.load_items())
        self.search_entry.bind("<Return>", lambda event: self.load_items())
        ctk.CTkButton(header, text="Dashboard", command=self.go_to_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        self.cart_button = ctk.CTkButton(header, text="My Cart", command=self.open_cart)
        self.cart_button.grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)
        self.update_cart_button()

    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, fg_color="#dcf4ec")
        sidebar.grid(row=1, column=0, sticky="ns", padx=(10, 0), pady=10)
        sidebar.grid_propagate(False)

        sidebar_content = ctk.CTkFrame(sidebar, fg_color="transparent")
        sidebar_content.pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(
            sidebar_content,
            text=CATEGORY_SIDE_LABELS.get(self.category, self.category),
            font=ctk.CTkFont(size=18, weight="bold"),
            width=SIDEBAR_ITEM_WIDTH,
            height=28,
            anchor="w",
            fg_color="transparent",
            hover=False,
            state="disabled",
            text_color_disabled="#114d48",
            border_width=0,
            corner_radius=0,
        ).pack(anchor="w", pady=(0, 24))

        ctk.CTkButton(
            sidebar_content,
            text="Checkout",
            command=self.checkout,
            anchor="w",
            width=SIDEBAR_ITEM_WIDTH,
        ).pack(anchor="w", pady=(0, 12))

        ctk.CTkButton(
            sidebar_content,
            text="Back to Dashboard",
            command=self.go_to_dashboard,
            anchor="w",
            width=SIDEBAR_ITEM_WIDTH,
        ).pack(anchor="w")

    def create_header(self):
        header = ctk.CTkFrame(self.content, fg_color="#d6f2e8")
        header.pack(fill="x", padx=10, pady=(0, 5))

        headers = ["Image", "Item Name", "Price", "Stock", "Qty", "Actions"]
        for col, width in enumerate(TABLE_COLUMN_WIDTHS):
            header.grid_columnconfigure(col, minsize=width)

        for i, text in enumerate(headers):
            ctk.CTkLabel(
                header,
                text=text,
                anchor="w",
                font=ctk.CTkFont(weight="bold"),
            ).grid(row=0, column=i, padx=5, pady=8, sticky="w")

    def load_items(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        self.feedback_labels = {}
        self.image_refs = []
        self.create_header()

        category_values = get_category_where_values(self.category)
        placeholders = ",".join("?" for _ in category_values)
        query = self.search_entry.get().strip()
        params = list(category_values)
        query_filter = ""

        if query:
            if query.upper().startswith("ID-"):
                query = query[3:]
            query_filter = "AND (name LIKE ? OR CAST(id AS TEXT) LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])

        self.cursor.execute(
            f"""
            SELECT * FROM inventory
            WHERE category IN ({placeholders})
            {query_filter}
            ORDER BY name
            """,
            params,
        )

        items = self.cursor.fetchall()
        if not items:
            ctk.CTkLabel(
                self.content,
                text="No matching products found.",
                text_color="gray"
            ).pack(anchor="w", padx=10, pady=12)
            return

        for index, item in enumerate(items):
            self.create_row(item, index)

    def create_row(self, data, index):
        bg_color = "#ffffff" if index % 2 == 0 else "#edf8f4"

        row = ctk.CTkFrame(self.content, fg_color=bg_color)
        row.pack(fill="x", padx=10, pady=2)
        for col, width in enumerate(TABLE_COLUMN_WIDTHS):
            row.grid_columnconfigure(col, minsize=width)

        image_label = self.create_item_image(row, data[1])
        image_label.grid(row=0, column=0, padx=8, pady=6, sticky="w")
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
            command=lambda d=data, q=qty: self.add_to_cart(d, q),
        ).pack(side="left", padx=3)

        feedback = ctk.CTkLabel(
            actions,
            text="",
            width=120,
            anchor="w",
            text_color="#167a3f",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        feedback.pack(side="left", padx=(6, 0))
        self.feedback_labels[data[0]] = feedback

    def create_item_image(self, parent, product_name):
        image_name = product_image_name(product_name, CATEGORY_IMAGE_KEYS.get(self.category, "Paracetamol.png"))
        image_path = os.path.join(IMAGES_DIR, image_name)

        try:
            image = Image.open(image_path)
        except (FileNotFoundError, OSError):
            image = Image.new("RGB", (58, 58), "#e4eef5")

        item_image = ctk.CTkImage(light_image=image, size=(58, 58))
        self.image_refs.append(item_image)

        return ctk.CTkLabel(parent, image=item_image, text="", width=58, height=58)

    def add_to_cart(self, data, qty_entry):
        try:
            qty = int(qty_entry.get())
        except ValueError:
            self.show_add_feedback(data[0], "Enter a number", "#b56b00")
            return

        if qty <= 0:
            self.show_add_feedback(data[0], "Qty must be 1+", "#b56b00")
            return

        self.cart[data[0]] = self.cart.get(data[0], 0) + qty
        self.save_cart_item(data, qty)
        self.update_cart_button()
        self.show_add_feedback(data[0], f"Added {qty} to cart", "#167a3f")

    def show_add_feedback(self, item_id, message, color):
        label = self.feedback_labels.get(item_id)
        if label is None:
            return

        label.configure(text=message, text_color=color)
        label.after(2200, lambda current_label=label: current_label.configure(text=""))

    def update_cart_button(self):
        if not hasattr(self, "cart_button"):
            return

        cart_items = load_user_cart()
        total_qty = sum(item.get("qty", 0) for item in cart_items.values())
        label = "My Cart" if total_qty == 0 else f"My Cart ({total_qty})"
        self.cart_button.configure(text=label)

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
                "image": product_image_name(data[1], CATEGORY_IMAGE_KEYS.get(self.category, "Paracetamol.png")),
            }

        save_user_cart(cart_items)

    def checkout(self):
        self.controller.show_page("cart")

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        self.controller.show_page("customer_account")

    def go_to_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


def category_page(category):
    class ConfiguredCategoryUI(CategoryUI):
        def __init__(self, parent, controller):
            super().__init__(parent, controller, category)

    return ConfiguredCategoryUI
