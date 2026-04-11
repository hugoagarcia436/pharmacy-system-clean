import customtkinter as ctk
import os
import subprocess
import sys
from session_utils import load_payment_methods, save_payment_methods

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CustomerPaymentMethodsUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Payment Methods")
        self.geometry("1200x760")
        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.payment_profiles = load_payment_methods()
        self.selected_profile = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_body()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search payments...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_body(self):
        left = ctk.CTkFrame(self, corner_radius=12)
        left.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(left, text="Saved Payment Methods", font=("Arial", 24, "bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10)
        )

        self.methods_list = ctk.CTkScrollableFrame(left)
        self.methods_list.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.methods_list.grid_columnconfigure(0, weight=1)

        right = ctk.CTkFrame(self, corner_radius=12)
        right.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right, text="Add or Edit Payment Method", font=("Arial", 24, "bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10)
        )

        self.profile_name = ctk.CTkEntry(right, placeholder_text="Payment Profile Name")
        self.profile_name.grid(row=1, column=0, sticky="ew", padx=20, pady=8)

        self.full_name = ctk.CTkEntry(right, placeholder_text="Full Name")
        self.full_name.grid(row=2, column=0, sticky="ew", padx=20, pady=8)

        self.phone = ctk.CTkEntry(right, placeholder_text="Phone Number")
        self.phone.grid(row=3, column=0, sticky="ew", padx=20, pady=8)

        self.email = ctk.CTkEntry(right, placeholder_text="Email Address")
        self.email.grid(row=4, column=0, sticky="ew", padx=20, pady=8)

        self.city = ctk.CTkEntry(right, placeholder_text="City")
        self.city.grid(row=5, column=0, sticky="ew", padx=20, pady=8)

        self.address = ctk.CTkTextbox(right, height=90)
        self.address.grid(row=6, column=0, sticky="ew", padx=20, pady=8)
        self.address.insert("1.0", "Delivery Address")

        self.payment_method = ctk.CTkOptionMenu(right, values=["Cash on Delivery", "Credit Card", "GCash"])
        self.payment_method.grid(row=7, column=0, sticky="w", padx=20, pady=8)

        self.card_name = ctk.CTkEntry(right, placeholder_text="Name on Card")
        self.card_name.grid(row=8, column=0, sticky="ew", padx=20, pady=8)

        self.card_number = ctk.CTkEntry(right, placeholder_text="Card Number")
        self.card_number.grid(row=9, column=0, sticky="ew", padx=20, pady=8)

        self.expiry = ctk.CTkEntry(right, placeholder_text="Expiry MM/YY")
        self.expiry.grid(row=10, column=0, sticky="ew", padx=20, pady=8)

        self.cvv = ctk.CTkEntry(right, placeholder_text="CVV")
        self.cvv.grid(row=11, column=0, sticky="ew", padx=20, pady=8)

        buttons = ctk.CTkFrame(right, fg_color="transparent")
        buttons.grid(row=12, column=0, sticky="w", padx=20, pady=(10, 8))

        ctk.CTkButton(buttons, text="Save Method", command=self.save_profile).pack(side="left", padx=(0, 10))
        ctk.CTkButton(buttons, text="Clear", fg_color="gray", hover_color="#555555", command=self.reset_form).pack(side="left")

        self.status_label = ctk.CTkLabel(right, text="", text_color="#7ddc7a")
        self.status_label.grid(row=13, column=0, sticky="w", padx=20, pady=(0, 20))

        self.refresh_methods()
        self.reset_form()

    def refresh_methods(self):
        for widget in self.methods_list.winfo_children():
            widget.destroy()

        if not self.payment_profiles:
            ctk.CTkLabel(self.methods_list, text="No saved payment methods yet.", text_color="gray").grid(
                row=0, column=0, sticky="w", padx=10, pady=10
            )
            return

        for row, (profile_name, details) in enumerate(self.payment_profiles.items()):
            card = ctk.CTkFrame(self.methods_list, corner_radius=10)
            card.grid(row=row, column=0, sticky="ew", pady=6)
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(card, text=profile_name, font=("Arial", 16, "bold")).grid(
                row=0, column=0, sticky="w", padx=12, pady=(10, 4)
            )
            ctk.CTkLabel(
                card,
                text=f"{details.get('payment_method', 'Cash on Delivery')} | {details.get('card_name', 'No card name')}",
                text_color="gray"
            ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 10))

            actions = ctk.CTkFrame(card, fg_color="transparent")
            actions.grid(row=0, column=1, rowspan=2, padx=12)
            ctk.CTkButton(actions, text="Edit", width=70, command=lambda name=profile_name: self.load_profile(name)).pack(side="left", padx=4)
            ctk.CTkButton(
                actions,
                text="Delete",
                width=70,
                fg_color="#b22222",
                hover_color="#8b1a1a",
                command=lambda name=profile_name: self.delete_profile(name)
            ).pack(side="left", padx=4)

    def clear_entry(self, widget):
        widget.delete(0, "end")

    def set_entry(self, widget, value):
        self.clear_entry(widget)
        if value:
            widget.insert(0, value)

    def reset_form(self):
        self.selected_profile = None
        self.set_entry(self.profile_name, "")
        self.set_entry(self.full_name, "")
        self.set_entry(self.phone, "")
        self.set_entry(self.email, "")
        self.set_entry(self.city, "")
        self.address.delete("1.0", "end")
        self.address.insert("1.0", "Delivery Address")
        self.payment_method.set("Cash on Delivery")
        self.set_entry(self.card_name, "")
        self.set_entry(self.card_number, "")
        self.set_entry(self.expiry, "")
        self.set_entry(self.cvv, "")
        self.status_label.configure(text="")

    def load_profile(self, profile_name):
        details = self.payment_profiles.get(profile_name, {})
        self.selected_profile = profile_name
        self.set_entry(self.profile_name, profile_name)
        self.set_entry(self.full_name, details.get("full_name", ""))
        self.set_entry(self.phone, details.get("phone", ""))
        self.set_entry(self.email, details.get("email", ""))
        self.set_entry(self.city, details.get("city", ""))
        self.address.delete("1.0", "end")
        self.address.insert("1.0", details.get("address", ""))
        self.payment_method.set(details.get("payment_method", "Cash on Delivery"))
        self.set_entry(self.card_name, details.get("card_name", ""))
        self.set_entry(self.card_number, details.get("card_number", ""))
        self.set_entry(self.expiry, details.get("expiry", ""))
        self.set_entry(self.cvv, details.get("cvv", ""))
        self.status_label.configure(text=f"Editing payment method: {profile_name}")

    def save_profile(self):
        profile_name = self.profile_name.get().strip()
        if not profile_name:
            self.status_label.configure(text="Enter a payment profile name first.", text_color="#ff8080")
            return

        if self.selected_profile and self.selected_profile != profile_name:
            self.payment_profiles.pop(self.selected_profile, None)

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
        self.selected_profile = profile_name
        self.refresh_methods()
        self.status_label.configure(text=f"Saved payment method: {profile_name}", text_color="#7ddc7a")

    def delete_profile(self, profile_name):
        if profile_name in self.payment_profiles:
            self.payment_profiles.pop(profile_name)
            save_payment_methods(self.payment_profiles)
            if self.selected_profile == profile_name:
                self.reset_form()
            self.refresh_methods()
            self.status_label.configure(text=f"Deleted payment method: {profile_name}", text_color="#7ddc7a")

    def open_dashboard(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_dashboard_ui.py")])
        self.destroy()

    def open_orders(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_orders_ui.py")])
        self.destroy()

    def open_cart(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "cart_ui.py")])
        self.destroy()

    def open_account(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_account_ui.py")])
        self.destroy()


if __name__ == "__main__":
    app = CustomerPaymentMethodsUI()
    app.mainloop()
