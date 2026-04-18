import customtkinter as ctk
import json
import sqlite3
from datetime import datetime
from shared.inventory_utils import sell_inventory, validate_cart_stock
from shared.paths import DB_PATH
from shared.session_utils import (
    get_current_user,
    load_all_orders,
    save_all_orders,
    load_user_cart,
    clear_user_cart,
    load_checkout_details,
    save_checkout_details,
    load_payment_methods,
    save_payment_methods,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CheckoutUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Checkout")
        self.controller.geometry("1200x760")
        self.current_user = get_current_user()
        self.cart_items = load_user_cart()
        self.saved_details = load_checkout_details()
        self.payment_profiles = load_payment_methods()

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_scrollable_body()

        self.build_left_panel()
        self.build_right_panel()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search products...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_scrollable_body(self):
        self.body_scroll = ctk.CTkScrollableFrame(self)
        self.body_scroll.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=0)
        self.body_scroll.grid_columnconfigure(0, weight=3)
        self.body_scroll.grid_columnconfigure(1, weight=2)

    def build_left_panel(self):
        left = ctk.CTkFrame(self.body_scroll, corner_radius=14)
        left.grid(row=1, column=0, sticky="nsew", padx=(14, 7), pady=14)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="Checkout Details",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        form = ctk.CTkFrame(left, fg_color="transparent")
        form.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        self.full_name = ctk.CTkEntry(form, placeholder_text="Full Name")
        self.full_name.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.phone = ctk.CTkEntry(form, placeholder_text="Phone Number")
        self.phone.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="ew")

        self.email = ctk.CTkEntry(form, placeholder_text="Email Address")
        self.email.grid(row=1, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.city = ctk.CTkEntry(form, placeholder_text="City")
        self.city.grid(row=1, column=1, padx=(8, 0), pady=8, sticky="ew")

        self.address = ctk.CTkTextbox(form, height=110)
        self.address.grid(row=2, column=0, columnspan=2, pady=8, sticky="ew")
        self.address.insert("1.0", "Delivery Address")

        ctk.CTkLabel(
            left,
            text="Payment Method",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(12, 6))

        saved_methods_frame = ctk.CTkFrame(left, fg_color="transparent")
        saved_methods_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        saved_methods_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(saved_methods_frame, text="Saved Payment").grid(row=0, column=0, padx=(0, 10), sticky="w")

        profile_values = ["Select Saved Payment"] + list(self.payment_profiles.keys())
        self.saved_payment_menu = ctk.CTkOptionMenu(
            saved_methods_frame,
            values=profile_values,
            command=self.apply_saved_payment_method
        )
        self.saved_payment_menu.grid(row=0, column=1, sticky="ew")
        self.saved_payment_menu.set("Select Saved Payment")

        self.payment_profile_name = ctk.CTkEntry(left, placeholder_text="Payment Profile Name")
        self.payment_profile_name.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))

        self.payment_method = ctk.CTkOptionMenu(
            left,
            values=["Cash on Delivery", "Credit Card", "GCash"]
        )
        self.payment_method.grid(row=5, column=0, sticky="w", padx=20, pady=(0, 12))

        card_form = ctk.CTkFrame(left, fg_color="transparent")
        card_form.grid(row=6, column=0, sticky="ew", padx=20, pady=6)
        card_form.grid_columnconfigure(0, weight=1)
        card_form.grid_columnconfigure(1, weight=1)

        self.card_name = ctk.CTkEntry(card_form, placeholder_text="Name on Card")
        self.card_name.grid(row=0, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.card_number = ctk.CTkEntry(card_form, placeholder_text="Card Number")
        self.card_number.grid(row=0, column=1, padx=(8, 0), pady=8, sticky="ew")

        self.expiry = ctk.CTkEntry(card_form, placeholder_text="Expiry MM/YY")
        self.expiry.grid(row=1, column=0, padx=(0, 8), pady=8, sticky="ew")

        self.cvv = ctk.CTkEntry(card_form, placeholder_text="CVV")
        self.cvv.grid(row=1, column=1, padx=(8, 0), pady=8, sticky="ew")

        self.notes = ctk.CTkTextbox(left, height=120)
        self.notes.grid(row=7, column=0, sticky="ew", padx=20, pady=12)
        self.notes.insert("1.0", "Order notes")

        self.save_details_var = ctk.BooleanVar(value=bool(self.saved_details))
        self.save_details_checkbox = ctk.CTkCheckBox(
            left,
            text="Save checkout details for next time",
            variable=self.save_details_var
        )
        self.save_details_checkbox.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 8))

        ctk.CTkButton(
            left,
            text="Save Payment Method",
            height=38,
            command=self.save_payment_method
        ).grid(row=9, column=0, sticky="ew", padx=20, pady=(0, 8))

        self.status_label = ctk.CTkLabel(left, text="", text_color="#7ddc7a")
        self.status_label.grid(row=10, column=0, sticky="w", padx=20, pady=(0, 8))

        ctk.CTkButton(
            left,
            text="Place Order",
            height=46,
            command=self.place_order
        ).grid(row=11, column=0, sticky="ew", padx=20, pady=(4, 20))

        self.prefill_checkout_details()

    def build_right_panel(self):
        right = ctk.CTkFrame(self.body_scroll, corner_radius=14)
        right.grid(row=1, column=1, sticky="nsew", padx=(7, 14), pady=14)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right,
            text="Order Summary",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        summary_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        summary_scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=8)
        summary_scroll.grid_columnconfigure(0, weight=1)

        if self.cart_items:
            for row, item in enumerate(self.cart_items.values()):
                card = ctk.CTkFrame(summary_scroll)
                card.grid(row=row, column=0, sticky="ew", pady=6)
                card.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    card,
                    text=item["name"],
                    font=ctk.CTkFont(size=16, weight="bold")
                ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

                ctk.CTkLabel(
                    card,
                    text=f"Qty: {item['qty']}  |  Price: ${item['price']:.2f}",
                    text_color="gray"
                ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))
        else:
            ctk.CTkLabel(
                summary_scroll,
                text="No items in cart yet.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        totals = ctk.CTkFrame(right)
        totals.grid(row=2, column=0, sticky="ew", padx=16, pady=(6, 16))
        totals.grid_columnconfigure(0, weight=1)

        subtotal = sum(item["price"] * item["qty"] for item in self.cart_items.values())
        tax = round(subtotal * 0.07, 2)
        total = subtotal + tax

        ctk.CTkLabel(totals, text=f"Subtotal: ${subtotal:.2f}")\
            .grid(row=0, column=0, sticky="w", padx=14, pady=(14, 6))
        ctk.CTkLabel(totals, text="Shipping: Free")\
            .grid(row=1, column=0, sticky="w", padx=14, pady=6)
        ctk.CTkLabel(totals, text=f"Tax: ${tax:.2f}")\
            .grid(row=2, column=0, sticky="w", padx=14, pady=6)
        ctk.CTkLabel(
            totals,
            text=f"Total: ${total:.2f}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=3, column=0, sticky="w", padx=14, pady=(6, 14))

    def place_order(self):
        if not self.cart_items:
            self.status_label.configure(text="Your cart is empty.")
            return

        if not self.full_name.get().strip() or not self.phone.get().strip():
            self.status_label.configure(text="Please enter your name and phone number.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        shortages = validate_cart_stock(cursor, self.cart_items)
        if shortages:
            conn.close()
            conn = None
            self.status_label.configure(text="Not enough stock for: " + "; ".join(shortages))
            return

        orders = load_all_orders()
        purchase_number = 1000 + len(orders) + 1
        purchase_id = f"PUR-{purchase_number}"
        subtotal = sum(item["price"] * item["qty"] for item in self.cart_items.values())
        tax = round(subtotal * 0.07, 2)
        total = subtotal + tax

        order_record = {
            "purchase_id": purchase_id,
            "status": "Processing",
            "date": datetime.now().strftime("%B %d, %Y"),
            "customer": {
                "full_name": self.full_name.get().strip(),
                "phone": self.phone.get().strip(),
                "email": self.email.get().strip(),
                "city": self.city.get().strip(),
                "address": self.address.get("1.0", "end").strip(),
                "payment_method": self.payment_method.get(),
                "card_name": self.card_name.get().strip(),
                "username": self.current_user.get("username", ""),
            },
            "notes": self.notes.get("1.0", "end").strip(),
            "items": list(self.cart_items.values()),
            "summary": {
                "subtotal": subtotal,
                "tax": tax,
                "total": total
            }
        }

        try:
            for item in self.cart_items.values():
                sell_inventory(cursor, item["id"], item["qty"], purchase_id)
            conn.commit()
        except ValueError as error:
            conn.rollback()
            conn.close()
            conn = None
            self.status_label.configure(text=str(error))
            return
        finally:
            if conn:
                conn.close()

        orders.append(order_record)
        save_all_orders(orders)

        if self.save_details_var.get():
            save_checkout_details({
                "full_name": self.full_name.get().strip(),
                "phone": self.phone.get().strip(),
                "email": self.email.get().strip(),
                "city": self.city.get().strip(),
                "address": self.address.get("1.0", "end").strip(),
                "payment_method": self.payment_method.get(),
                "card_name": self.card_name.get().strip(),
                "card_number": self.card_number.get().strip(),
                "expiry": self.expiry.get().strip(),
                "cvv": self.cvv.get().strip(),
            })

        clear_user_cart()
        self.cart_items = {}
        self.status_label.configure(text=f"Order placed successfully. Purchase ID: {purchase_id}")
        self.open_orders()

    def prefill_checkout_details(self):
        self.reset_checkout_form()

    def clear_entry(self, widget):
        widget.delete(0, "end")

    def set_entry_value(self, widget, value):
        self.clear_entry(widget)
        if value:
            widget.insert(0, value)

    def reset_checkout_form(self):
        self.set_entry_value(self.full_name, self.current_user.get("name", ""))
        self.clear_entry(self.phone)
        self.set_entry_value(self.email, self.current_user.get("email", ""))
        self.clear_entry(self.city)
        self.clear_entry(self.payment_profile_name)
        self.payment_method.set("Cash on Delivery")

        self.address.delete("1.0", "end")
        self.address.insert("1.0", "Delivery Address")

        self.clear_entry(self.card_name)
        self.clear_entry(self.card_number)
        self.clear_entry(self.expiry)
        self.clear_entry(self.cvv)

        self.notes.delete("1.0", "end")
        self.notes.insert("1.0", "Order notes")

        if hasattr(self, "saved_payment_menu"):
            self.saved_payment_menu.set("Select Saved Payment")

    def save_payment_method(self):
        profile_name = self.payment_profile_name.get().strip()

        if not profile_name:
            self.status_label.configure(text="Enter a payment profile name first.")
            return

        self.payment_profiles[profile_name] = {
            "full_name": self.full_name.get().strip(),
            "phone": self.phone.get().strip(),
            "email": self.email.get().strip(),
            "city": self.city.get().strip(),
            "address": self.address.get("1.0", "end").strip(),
            "payment_method": self.payment_method.get(),
            "card_name": self.card_name.get().strip(),
            "card_number": self.card_number.get().strip(),
            "expiry": self.expiry.get().strip(),
            "cvv": self.cvv.get().strip(),
        }
        save_payment_methods(self.payment_profiles)
        self.saved_payment_menu.configure(values=["Select Saved Payment"] + list(self.payment_profiles.keys()))
        self.saved_payment_menu.set(profile_name)
        self.status_label.configure(text=f"Saved payment method: {profile_name}")

    def apply_saved_payment_method(self, selected_name):
        if selected_name == "Select Saved Payment":
            self.reset_checkout_form()
            return

        details = self.payment_profiles.get(selected_name)
        if not details:
            return

        self.set_entry_value(self.payment_profile_name, selected_name)
        self.set_entry_value(self.full_name, details.get("full_name", ""))
        self.set_entry_value(self.phone, details.get("phone", ""))
        self.set_entry_value(self.email, details.get("email", ""))
        self.set_entry_value(self.city, details.get("city", ""))
        self.address.delete("1.0", "end")
        self.address.insert("1.0", details.get("address", ""))
        self.payment_method.set(details.get("payment_method", "Cash on Delivery"))
        self.set_entry_value(self.card_name, details.get("card_name", ""))
        self.set_entry_value(self.card_number, details.get("card_number", ""))
        self.set_entry_value(self.expiry, details.get("expiry", ""))
        self.set_entry_value(self.cvv, details.get("cvv", ""))

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        self.controller.show_page("customer_account")


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("checkout")
