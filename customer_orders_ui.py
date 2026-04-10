import customtkinter as ctk
import os
import subprocess
import sys
import json
from session_utils import get_current_username, load_all_orders

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CustomerOrdersUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My Orders")
        self.geometry("1200x760")
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.current_username = get_current_username()
        self.orders_data = self.load_orders()

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

            purchase_button = ctk.CTkButton(
                card,
                text=order["purchase_id"],
                width=160,
                fg_color="transparent",
                hover_color="#3a3a3a",
                anchor="w",
                command=lambda current_order=order: self.show_order_history(current_order)
            )
            purchase_button.pack(anchor="w", padx=15, pady=(12, 4))

            items_text = ", ".join(item["name"] for item in order["items"])

            ctk.CTkLabel(card, text=f"Status: {order['status']}", text_color="#7ddc7a").pack(anchor="w", padx=15, pady=2)
            ctk.CTkLabel(card, text=f"Date: {order['date']}", text_color="gray").pack(anchor="w", padx=15, pady=2)
            ctk.CTkLabel(card, text=f"Items: {items_text}", wraplength=900, justify="left").pack(anchor="w", padx=15, pady=(2, 12))

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

        for item in order["items"]:
            item_card = ctk.CTkFrame(body, corner_radius=10)
            item_card.pack(fill="x", padx=15, pady=6)

            ctk.CTkLabel(item_card, text=item["name"], font=("Arial", 15, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(
                item_card,
                text=f"Quantity: {item['qty']}  |  Price: ${item['price']:.2f}  |  Line Total: ${item['qty'] * item['price']:.2f}",
                text_color="gray"
            ).pack(anchor="w", padx=12, pady=(0, 10))

        totals_card = ctk.CTkFrame(body, corner_radius=10)
        totals_card.pack(fill="x", padx=15, pady=(10, 15))
        ctk.CTkLabel(totals_card, text=f"Subtotal: ${order['summary']['subtotal']:.2f}").pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(totals_card, text=f"Tax: ${order['summary']['tax']:.2f}").pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(totals_card, text=f"Total: ${order['summary']['total']:.2f}", font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(4, 10))

    def open_orders(self):
        pass

    def open_dashboard(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_dashboard_ui.py")])
        self.destroy()

    def open_cart(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "cart_ui.py")])
        self.destroy()

    def open_account(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_account_ui.py")])
        self.destroy()


if __name__ == "__main__":
    app = CustomerOrdersUI()
    app.mainloop()
