import customtkinter as ctk
from PIL import Image
import os
import json
from shared.paths import IMAGES_DIR
from shared.session_utils import load_user_cart, save_user_cart

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CartUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Shopping Cart")
        self.controller.geometry("1350x850")

        self.quantity_labels = {}
        self.pending_quantities = {}
        self.cart_items = load_user_cart()

        self.build_ui()

    def build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        img_path = IMAGES_DIR

        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold"))\
            .grid(row=0, column=0, padx=15)

        search = ctk.CTkEntry(header, placeholder_text="Search medications...", height=40)
        search.grid(row=0, column=1, sticky="ew", padx=20)

        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(main)
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="Your Cart", font=("Arial", 26, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.quantity_labels = {}
        self.pending_quantities = {}

        if self.cart_items:
            for row, item in enumerate(self.cart_items.values(), start=1):
                self.create_item(scroll, img_path, row, item)
        else:
            ctk.CTkLabel(
                scroll,
                text="Your cart is empty.",
                text_color="gray"
            ).grid(row=1, column=0, sticky="w", padx=10, pady=15)

        summary = ctk.CTkFrame(main, corner_radius=12)
        summary.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(summary, text="Order Summary", font=("Arial", 20, "bold"))\
            .pack(pady=20)

        self.items_label = ctk.CTkLabel(summary, text="")
        self.items_label.pack(pady=5)

        ctk.CTkLabel(summary, text="Shipping: Free").pack(pady=5)

        self.tax_label = ctk.CTkLabel(summary, text="")
        self.tax_label.pack(pady=5)

        self.total_label = ctk.CTkLabel(summary, text="", font=("Arial", 18, "bold"))
        self.total_label.pack(pady=10)

        ctk.CTkButton(summary, text="Proceed to Checkout", height=50)\
            .pack(pady=20)

        for widget in summary.winfo_children():
            if isinstance(widget, ctk.CTkButton) and widget.cget("text") == "Proceed to Checkout":
                widget.configure(command=self.open_checkout)

        self.update_summary()

    def create_item(self, scroll, img_path, row, item):
        card = ctk.CTkFrame(scroll, corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
        card.grid_columnconfigure(1, weight=1)

        image_path = os.path.join(img_path, item.get("image", "medicine.png"))
        if os.path.exists(image_path):
            image = Image.open(image_path)
        else:
            image = Image.new("RGB", (110, 80), "#3a3a3a")

        img = ctk.CTkImage(light_image=image, size=(110, 80))
        image_label = ctk.CTkLabel(card, image=img, text="")
        image_label.image = img
        image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10)

        ctk.CTkLabel(card, text=item["name"], font=("Arial", 15, "bold"))\
            .grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(card, text="In Stock", text_color="green")\
            .grid(row=1, column=1, sticky="w")

        ctk.CTkLabel(card, text="Free delivery", text_color="gray")\
            .grid(row=2, column=1, sticky="w")

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=2, rowspan=3, padx=10)

        ctk.CTkLabel(right, text=f"${item['price']:.2f}", font=("Arial", 16, "bold"))\
            .pack()

        qty = ctk.CTkFrame(right, fg_color="transparent")
        qty.pack(pady=5)

        item_id = str(item["id"])
        self.pending_quantities[item_id] = item["qty"]

        ctk.CTkButton(
            qty,
            text="-",
            width=30,
            command=lambda current_id=item_id: self.change_quantity(current_id, -1)
        ).pack(side="left", padx=2)

        qty_label = ctk.CTkLabel(qty, text=str(item["qty"]))
        qty_label.pack(side="left", padx=5)
        self.quantity_labels[item_id] = qty_label

        ctk.CTkButton(
            qty,
            text="+",
            width=30,
            command=lambda current_id=item_id: self.change_quantity(current_id, 1)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            right,
            text="Remove",
            width=80,
            command=lambda current_id=item_id: self.remove_item(current_id)
        ).pack(pady=2)

        ctk.CTkButton(
            right,
            text="Save",
            width=80,
            command=lambda current_id=item_id: self.save_quantity(current_id)
        ).pack(pady=2)

    def change_quantity(self, item_id, delta):
        current_qty = self.pending_quantities.get(item_id, 1)
        new_qty = max(1, current_qty + delta)
        self.pending_quantities[item_id] = new_qty

        if item_id in self.quantity_labels:
            self.quantity_labels[item_id].configure(text=str(new_qty))

    def save_quantity(self, item_id):
        if item_id not in self.cart_items:
            return

        self.cart_items[item_id]["qty"] = self.pending_quantities.get(item_id, 1)
        self.write_cart_items()
        self.update_summary()

    def remove_item(self, item_id):
        if item_id not in self.cart_items:
            return

        del self.cart_items[item_id]
        self.pending_quantities.pop(item_id, None)
        self.quantity_labels.pop(item_id, None)
        self.write_cart_items()
        self.build_ui()

    def write_cart_items(self):
        save_user_cart(self.cart_items)

    def update_summary(self):
        total_quantity = sum(item["qty"] for item in self.cart_items.values())
        subtotal = sum(item["price"] * item["qty"] for item in self.cart_items.values())
        tax = round(subtotal * 0.07, 2)
        total = subtotal + tax

        self.items_label.configure(text=f"Items ({total_quantity}): ${subtotal:.2f}")
        self.tax_label.configure(text=f"Tax: ${tax:.2f}")
        self.total_label.configure(text=f"Total: ${total:.2f}")

    def open_checkout(self):
        self.controller.show_page("checkout")

    def open_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_cart(self):
        self.build_ui()

    def open_account(self):
        self.controller.show_page("customer_account")


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("cart")
