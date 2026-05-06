import sqlite3
 
import customtkinter as ctk

from shared.paths import DB_PATH
from shared.session_utils import (
    get_current_user,
    load_checkout_details,
    save_checkout_details,
    set_current_user,
)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CustomerProfileUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Edit Profile")
        self.controller.geometry("1200x760")
        self.current_user = get_current_user()
        self.saved_details = load_checkout_details()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_body()
        self.prefill_profile()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search profile...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_body(self):
        main = ctk.CTkScrollableFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(main, text="Edit Profile", font=("Arial", 26, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 6)
        )
        ctk.CTkLabel(
            main,
            text="Manage your personal details and default delivery information.",
            text_color="gray",
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 18))

        personal = ctk.CTkFrame(main, corner_radius=12)
        personal.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)
        personal.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(personal, text="Personal Information", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 10)
        )

        self.full_name = ctk.CTkEntry(personal, placeholder_text="Full Name")
        self.full_name.grid(row=1, column=0, sticky="ew", padx=18, pady=8)

        self.email = ctk.CTkEntry(personal, placeholder_text="Email Address")
        self.email.grid(row=2, column=0, sticky="ew", padx=18, pady=8)

        self.phone = ctk.CTkEntry(personal, placeholder_text="Phone Number")
        self.phone.grid(row=3, column=0, sticky="ew", padx=18, pady=8)

        self.promos_var = ctk.BooleanVar(value=False)
        self.order_updates_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            personal,
            text="Send me order status updates",
            variable=self.order_updates_var,
        ).grid(row=4, column=0, sticky="w", padx=18, pady=(14, 6))
        ctk.CTkCheckBox(
            personal,
            text="Send me deals and refill reminders",
            variable=self.promos_var,
        ).grid(row=5, column=0, sticky="w", padx=18, pady=(0, 18))

        delivery = ctk.CTkFrame(main, corner_radius=12)
        delivery.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)
        delivery.grid_columnconfigure(0, weight=1)
        delivery.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(delivery, text="Default Delivery Details", font=("Arial", 20, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=18, pady=(18, 10)
        )

        self.street_address = ctk.CTkEntry(delivery, placeholder_text="Street Address")
        self.street_address.grid(row=1, column=0, columnspan=2, sticky="ew", padx=18, pady=8)

        self.city = ctk.CTkEntry(delivery, placeholder_text="City")
        self.city.grid(row=2, column=0, sticky="ew", padx=(18, 8), pady=8)

        self.state = ctk.CTkEntry(delivery, placeholder_text="State")
        self.state.grid(row=2, column=1, sticky="ew", padx=(8, 18), pady=8)

        self.zipcode = ctk.CTkEntry(delivery, placeholder_text="ZIP Code")
        self.zipcode.grid(row=3, column=0, sticky="ew", padx=(18, 8), pady=8)

        self.delivery_notes = ctk.CTkTextbox(delivery, height=90)
        self.delivery_notes.grid(row=4, column=0, columnspan=2, sticky="ew", padx=18, pady=(8, 18))
        self.delivery_notes.insert("1.0", "Delivery notes")

        actions = ctk.CTkFrame(main, fg_color="transparent")
        actions.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(12, 6))

        ctk.CTkButton(actions, text="Save Profile", height=40, command=self.save_profile).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            actions,
            text="Cancel",
            height=40,
            fg_color="#7a8d99",
            hover_color="#657783",
            command=self.open_account,
        ).pack(side="left")

        self.status_label = ctk.CTkLabel(main, text="", text_color="#167a3f")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 20))

    def prefill_profile(self):
        self.set_entry(self.full_name, self.current_user.get("name", ""))
        self.set_entry(self.email, self.current_user.get("email", ""))
        self.set_entry(self.phone, self.load_user_phone())
        self.set_entry(
            self.street_address,
            self.saved_details.get("street_address", self.saved_details.get("address", "")),
        )
        self.set_entry(self.city, self.saved_details.get("city", ""))
        self.set_entry(self.state, self.saved_details.get("state", ""))
        self.set_entry(self.zipcode, self.saved_details.get("zipcode", ""))
        self.delivery_notes.delete("1.0", "end")
        self.delivery_notes.insert("1.0", self.saved_details.get("delivery_notes", "Delivery notes"))

    def load_user_phone(self):
        username = self.current_user.get("username", "")
        if not username:
            return ""

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        self.ensure_phone_column(cursor)
        cursor.execute("SELECT phone FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else ""

    def ensure_phone_column(self, cursor):
        cursor.execute("PRAGMA table_info(users)")
        columns = {row[1] for row in cursor.fetchall()}
        if "phone" not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

    def clear_entry(self, widget):
        widget.delete(0, "end")

    def set_entry(self, widget, value):
        self.clear_entry(widget)
        if value:
            widget.insert(0, value)

    def get_address_data(self):
        street_address = self.street_address.get().strip()
        city = self.city.get().strip()
        state = self.state.get().strip()
        zipcode = self.zipcode.get().strip()
        city_state_zip = " ".join(part for part in [city, state, zipcode] if part)
        address = ", ".join(part for part in [street_address, city_state_zip] if part)

        return {
            "street_address": street_address,
            "city": city,
            "state": state,
            "zipcode": zipcode,
            "address": address,
        }

    def save_profile(self):
        username = self.current_user.get("username", "")
        full_name = self.full_name.get().strip()
        email = self.email.get().strip()
        phone = self.phone.get().strip()

        if not username:
            self.status_label.configure(text="No active user session found.", text_color="#c62828")
            return

        if not full_name or not email or not phone:
            self.status_label.configure(text="Name, email, and phone number are required.", text_color="#c62828")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        self.ensure_phone_column(cursor)
        cursor.execute(
            "UPDATE users SET name=?, email=?, phone=? WHERE username=?",
            (full_name, email, phone, username),
        )
        conn.commit()
        conn.close()

        address_data = self.get_address_data()
        saved_details = dict(self.saved_details)
        saved_details.update({
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "street_address": address_data["street_address"],
            "city": address_data["city"],
            "state": address_data["state"],
            "zipcode": address_data["zipcode"],
            "address": address_data["address"],
            "delivery_notes": self.delivery_notes.get("1.0", "end").strip(),
            "order_updates": self.order_updates_var.get(),
            "promotions": self.promos_var.get(),
        })
        save_checkout_details(saved_details)
        self.saved_details = saved_details

        self.current_user["name"] = full_name
        self.current_user["email"] = email
        set_current_user(self.current_user)
        self.status_label.configure(text="Profile updated successfully.", text_color="#167a3f")

    def open_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        self.controller.show_page("customer_account")


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("customer_profile")
