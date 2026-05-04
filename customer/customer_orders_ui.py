import customtkinter as ctk
import json
import os
import sqlite3
from PIL import Image
from tkinter import messagebox
from shared.image_utils import DEFAULT_PRODUCT_IMAGE, product_image_name
from shared.paths import DB_PATH, IMAGES_DIR
from shared.session_utils import get_current_username, load_all_orders, load_user_cart, save_user_cart

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CustomerOrdersUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("My Orders")
        self.controller.geometry("1200x760")
        self.current_username = get_current_username()
        self.orders_data = self.load_orders()
        self.image_refs = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_body()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search orders...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_body(self):
        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main, text="My Orders", font=("Arial", 26, "bold")).pack(anchor="w", padx=20, pady=(20, 10))

        orders = ctk.CTkScrollableFrame(main)
        orders.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        if not self.orders_data:
            ctk.CTkLabel(
                orders,
                text="No purchases yet.",
                text_color="gray"
            ).pack(anchor="w", padx=15, pady=15)
            return

        for order in reversed(self.orders_data):
            card = ctk.CTkFrame(orders, corner_radius=12)
            card.pack(fill="x", pady=8)
            card.grid_columnconfigure(1, weight=1)

            thumbnails = ctk.CTkFrame(card, fg_color="transparent")
            thumbnails.grid(row=0, column=0, rowspan=4, sticky="nw", padx=(14, 8), pady=14)
            self.create_order_thumbnails(thumbnails, order.get("items", []))

            purchase_button = ctk.CTkButton(
                card,
                text=order["purchase_id"],
                width=160,
                fg_color="transparent",
                hover_color="#3a3a3a",
                anchor="w",
                command=lambda current_order=order: self.show_order_history(current_order)
            )
            purchase_button.grid(row=0, column=1, sticky="w", padx=8, pady=(14, 4))

            items_text = ", ".join(item["name"] for item in order["items"])

            ctk.CTkLabel(card, text=f"Status: {order['status']}", text_color="#7ddc7a").grid(row=1, column=1, sticky="w", padx=8, pady=2)
            ctk.CTkLabel(card, text=f"Date: {order['date']}", text_color="gray").grid(row=2, column=1, sticky="w", padx=8, pady=2)
            ctk.CTkLabel(card, text=f"Items: {items_text}", wraplength=900, justify="left").grid(row=3, column=1, sticky="w", padx=8, pady=(2, 14))

            total = order.get("summary", {}).get("total", 0)
            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=0, column=2, rowspan=4, sticky="e", padx=16, pady=14)
            ctk.CTkLabel(actions, text=f"${total:.2f}", font=("Arial", 18, "bold")).pack(anchor="e", pady=(0, 10))
            ctk.CTkButton(
                actions,
                text="Details",
                width=110,
                command=lambda current_order=order: self.show_order_history(current_order)
            ).pack(anchor="e")

    def create_order_thumbnails(self, parent, items):
        shown_items = items[:4]

        for index, item in enumerate(shown_items):
            image_label = self.create_item_image(parent, item, size=(74, 74))
            image_label.grid(row=0, column=index, padx=(0, 8))

        remaining_count = len(items) - len(shown_items)
        if remaining_count > 0:
            ctk.CTkLabel(
                parent,
                text=f"+{remaining_count}",
                width=74,
                height=74,
                fg_color="#343a40",
                corner_radius=8,
                font=("Arial", 16, "bold")
            ).grid(row=0, column=len(shown_items), padx=(0, 8))

    def create_item_image(self, parent, item, size=(74, 74)):
        image_name = item.get("image") or product_image_name(item.get("name"), DEFAULT_PRODUCT_IMAGE)
        image_path = os.path.join(IMAGES_DIR, image_name)

        if not os.path.exists(image_path):
            image_path = os.path.join(IMAGES_DIR, product_image_name(item.get("name"), DEFAULT_PRODUCT_IMAGE))

        try:
            image = Image.open(image_path)
        except (FileNotFoundError, OSError):
            image = Image.new("RGB", size, "#3a3a3a")

        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
        self.image_refs.append(ctk_image)

        return ctk.CTkLabel(parent, image=ctk_image, text="", width=size[0], height=size[1], corner_radius=8)

    def load_orders(self):
        if not self.current_username:
            return []

        all_orders = load_all_orders()
        return [
            order for order in all_orders
            if order.get("customer", {}).get("username") == self.current_username
        ]

    def show_order_history(self, order):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(order["purchase_id"])
        detail_window.geometry("700x620")
        detail_window.grid_columnconfigure(0, weight=1)
        detail_window.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            detail_window,
            text=f"Purchase History: {order['purchase_id']}",
            font=("Arial", 24, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        body = ctk.CTkScrollableFrame(detail_window)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(body, text=f"Status: {order['status']}", text_color="#7ddc7a").pack(anchor="w", padx=15, pady=(15, 4))
        ctk.CTkLabel(body, text=f"Date: {order['date']}", text_color="gray").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Customer: {order['customer']['full_name']}").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Phone: {order['customer']['phone']}").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Email: {order['customer']['email'] or 'N/A'}").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"City: {order['customer']['city'] or 'N/A'}").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Address: {order['customer']['address']}", wraplength=620, justify="left").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Payment: {order['customer']['payment_method']}").pack(anchor="w", padx=15, pady=4)
        ctk.CTkLabel(body, text=f"Notes: {order['notes'] or 'None'}", wraplength=620, justify="left").pack(anchor="w", padx=15, pady=(4, 12))

        ctk.CTkLabel(body, text="Purchased Items", font=("Arial", 18, "bold")).pack(anchor="w", padx=15, pady=(6, 8))

        selected_items = []
        for item in order["items"]:
            item_card = ctk.CTkFrame(body, corner_radius=10)
            item_card.pack(fill="x", padx=15, pady=6)
            item_card.grid_columnconfigure(2, weight=1)

            selected_var = ctk.BooleanVar(value=True)
            selected_items.append((selected_var, item))

            ctk.CTkCheckBox(
                item_card,
                text="",
                width=24,
                variable=selected_var
            ).grid(row=0, column=0, rowspan=2, padx=(12, 0), pady=12)

            image_label = self.create_item_image(item_card, item, size=(82, 82))
            image_label.grid(row=0, column=1, rowspan=2, padx=12, pady=12)

            ctk.CTkLabel(item_card, text=item["name"], font=("Arial", 15, "bold")).grid(row=0, column=2, sticky="w", padx=8, pady=(14, 4))
            ctk.CTkLabel(
                item_card,
                text=f"Quantity: {item['qty']}  |  Price: ${item['price']:.2f}  |  Line Total: ${item['qty'] * item['price']:.2f}",
                text_color="gray"
            ).grid(row=1, column=2, sticky="w", padx=8, pady=(0, 14))

        totals_card = ctk.CTkFrame(body, corner_radius=10)
        totals_card.pack(fill="x", padx=15, pady=(10, 15))
        ctk.CTkLabel(totals_card, text=f"Subtotal: ${order['summary']['subtotal']:.2f}").pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(totals_card, text=f"Tax: ${order['summary']['tax']:.2f}").pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(totals_card, text=f"Total: ${order['summary']['total']:.2f}", font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(4, 10))

        ctk.CTkButton(
            body,
            text="Add Selected to Cart",
            height=40,
            command=lambda selections=selected_items, window=detail_window: self.reorder_selected(selections, window)
        ).pack(anchor="w", padx=15, pady=(0, 15))

    def reorder_selected(self, selected_items, detail_window=None):
        items_to_reorder = [item for selected_var, item in selected_items if selected_var.get()]

        if not items_to_reorder:
            messagebox.showwarning("Reorder", "Select at least one item to reorder.")
            return

        self.reorder(items_to_reorder, detail_window)

    def reorder(self, items, detail_window=None):
        cart_items = load_user_cart()
        added_items = []
        skipped_items = []

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for item in items:
            item_id = str(item.get("id"))
            requested_qty = item.get("qty", 0)

            cursor.execute("SELECT name, price, stock FROM inventory WHERE id=?", (item.get("id"),))
            result = cursor.fetchone()
            if result is None:
                skipped_items.append(f"{item.get('name', 'Item')} is no longer available")
                continue

            name, price, stock = result
            current_cart_qty = cart_items.get(item_id, {}).get("qty", 0)
            available_to_add = stock - current_cart_qty

            if available_to_add <= 0:
                skipped_items.append(f"{name} is out of stock for reorder")
                continue

            qty_to_add = min(requested_qty, available_to_add)
            if item_id in cart_items:
                cart_items[item_id]["qty"] += qty_to_add
                cart_items[item_id]["price"] = price
                cart_items[item_id]["name"] = name
            else:
                cart_items[item_id] = {
                    "id": item.get("id"),
                    "name": name,
                    "price": price,
                    "qty": qty_to_add,
                    "image": item.get("image") or product_image_name(name),
                }

            added_items.append(f"{name} x{qty_to_add}")
            if qty_to_add < requested_qty:
                skipped_items.append(f"{name}: only {qty_to_add} of {requested_qty} added")

        conn.close()

        if not added_items:
            messagebox.showwarning("Reorder", "No items could be added.\n" + "\n".join(skipped_items))
            return

        save_user_cart(cart_items)

        message = "Added to cart:\n" + "\n".join(added_items)
        if skipped_items:
            message += "\n\nNot fully added:\n" + "\n".join(skipped_items)
        messagebox.showinfo("Reorder", message)

        if detail_window is not None and detail_window.winfo_exists():
            detail_window.destroy()

        self.open_cart()

    def open_orders(self):
        pass

    def open_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        self.controller.show_page("customer_account")


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("customer_orders")
