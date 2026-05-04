import sqlite3
from datetime import datetime

import customtkinter as ctk

from shared.paths import DB_PATH
from shared.session_utils import get_current_user, set_current_user


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CustomerSecurityUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Security Settings")
        self.controller.geometry("1100x720")
        self.current_user = get_current_user()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_topbar()
        self.create_body()

    def create_topbar(self):
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search security...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

    def create_body(self):
        main = ctk.CTkScrollableFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(main, text="Security Settings", font=("Arial", 26, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(20, 6)
        )
        ctk.CTkLabel(
            main,
            text="Manage password, sign-in protection, and account access.",
            text_color="gray",
            justify="left",
        ).grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 15))

        self.create_password_card(main)
        self.create_protection_card(main)
        self.create_activity_card(main)
        self.create_account_access_card(main)

    def create_password_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=2, column=0, sticky="nsew", padx=(20, 10), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Password", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 8)
        )
        ctk.CTkLabel(
            card,
            text="Use a strong password that you do not use anywhere else.",
            text_color="gray",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        self.current_password = ctk.CTkEntry(card, placeholder_text="Current Password", show="*")
        self.current_password.grid(row=2, column=0, sticky="ew", padx=18, pady=8)

        self.new_password = ctk.CTkEntry(card, placeholder_text="New Password", show="*")
        self.new_password.grid(row=3, column=0, sticky="ew", padx=18, pady=8)

        self.confirm_password = ctk.CTkEntry(card, placeholder_text="Confirm New Password", show="*")
        self.confirm_password.grid(row=4, column=0, sticky="ew", padx=18, pady=8)

        ctk.CTkButton(card, text="Update Password", command=self.save_password).grid(
            row=5, column=0, sticky="w", padx=18, pady=(10, 8)
        )

        self.status_label = ctk.CTkLabel(card, text="", text_color="#7ddc7a")
        self.status_label.grid(row=6, column=0, sticky="w", padx=18, pady=(0, 18))

    def create_protection_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=2, column=1, sticky="nsew", padx=(10, 20), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Sign-In Protection", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 8)
        )

        self.two_step_var = ctk.BooleanVar(value=False)
        self.login_alerts_var = ctk.BooleanVar(value=True)
        self.remember_device_var = ctk.BooleanVar(value=True)

        ctk.CTkSwitch(
            card,
            text="Two-step verification",
            variable=self.two_step_var,
            command=lambda: self.set_protection_status("Two-step verification setting updated."),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=8)

        ctk.CTkSwitch(
            card,
            text="Email me about new sign-ins",
            variable=self.login_alerts_var,
            command=lambda: self.set_protection_status("Login alert preference updated."),
        ).grid(row=2, column=0, sticky="w", padx=18, pady=8)

        ctk.CTkSwitch(
            card,
            text="Remember this device",
            variable=self.remember_device_var,
            command=lambda: self.set_protection_status("Remembered-device preference updated."),
        ).grid(row=3, column=0, sticky="w", padx=18, pady=8)

        self.protection_status = ctk.CTkLabel(card, text="", text_color="#7ddc7a")
        self.protection_status.grid(row=4, column=0, sticky="w", padx=18, pady=(4, 18))

    def create_activity_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=3, column=0, sticky="nsew", padx=(20, 10), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Login Activity", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 8)
        )

        username = self.current_user.get("username", "Unknown user")
        ctk.CTkLabel(card, text=f"Signed in as: {username}").grid(row=1, column=0, sticky="w", padx=18, pady=4)
        ctk.CTkLabel(card, text=f"Current session: {datetime.now().strftime('%B %d, %Y %I:%M %p')}").grid(
            row=2, column=0, sticky="w", padx=18, pady=4
        )
        ctk.CTkLabel(card, text="Device: This Windows desktop").grid(row=3, column=0, sticky="w", padx=18, pady=4)

        ctk.CTkButton(
            card,
            text="Sign Out of Other Devices",
            fg_color="#5d6570",
            hover_color="#4b535d",
            command=lambda: self.activity_status.configure(text="Other active sessions were signed out."),
        ).grid(row=4, column=0, sticky="w", padx=18, pady=(12, 6))

        self.activity_status = ctk.CTkLabel(card, text="", text_color="#7ddc7a")
        self.activity_status.grid(row=5, column=0, sticky="w", padx=18, pady=(0, 18))

    def create_account_access_card(self, parent):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.grid(row=3, column=1, sticky="nsew", padx=(10, 20), pady=10)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text="Account Access", font=("Arial", 20, "bold")).grid(
            row=0, column=0, sticky="w", padx=18, pady=(18, 8)
        )
        ctk.CTkLabel(
            card,
            text="Use these only if you need to protect or close your account.",
            text_color="gray",
            justify="left",
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 10))

        ctk.CTkButton(
            card,
            text="Lock Account Temporarily",
            fg_color="#5d6570",
            hover_color="#4b535d",
            command=lambda: self.account_status.configure(text="Temporary account lock requested."),
        ).grid(row=2, column=0, sticky="w", padx=18, pady=6)

        ctk.CTkButton(
            card,
            text="Deactivate Account",
            fg_color="#b22222",
            hover_color="#8b1a1a",
            command=lambda: self.account_status.configure(text="Contact support to finish account deactivation."),
        ).grid(row=3, column=0, sticky="w", padx=18, pady=6)

        self.account_status = ctk.CTkLabel(card, text="", text_color="#ffcc66")
        self.account_status.grid(row=4, column=0, sticky="w", padx=18, pady=(4, 18))

    def set_protection_status(self, message):
        self.protection_status.configure(text=message, text_color="#7ddc7a")

    def save_password(self):
        username = self.current_user.get("username", "")
        current_password = self.current_password.get()
        new_password = self.new_password.get()
        confirm_password = self.confirm_password.get()

        if not username:
            self.status_label.configure(text="No active user session found.", text_color="#ff8080")
            return

        if not current_password or not new_password or not confirm_password:
            self.status_label.configure(text="Fill out all password fields.", text_color="#ff8080")
            return

        if new_password != confirm_password:
            self.status_label.configure(text="New passwords do not match.", text_color="#ff8080")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            self.status_label.configure(text="User account could not be found.", text_color="#ff8080")
            return

        stored_password, role = result
        if current_password != stored_password:
            conn.close()
            self.status_label.configure(text="Current password is incorrect.", text_color="#ff8080")
            return

        cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        conn.close()

        self.current_user["role"] = role
        set_current_user(self.current_user)

        self.current_password.delete(0, "end")
        self.new_password.delete(0, "end")
        self.confirm_password.delete(0, "end")
        self.status_label.configure(text="Password updated successfully.", text_color="#7ddc7a")

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

    launch_customer_app("customer_security")
