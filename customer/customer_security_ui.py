import customtkinter as ctk
import sqlite3
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
        main = ctk.CTkFrame(self, corner_radius=12)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main, text="Security Settings", font=("Arial", 26, "bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(20, 10)
        )

        ctk.CTkLabel(main, text="Update your account information and password.", text_color="gray").grid(
            row=1, column=0, sticky="w", padx=20, pady=(0, 15)
        )

        self.full_name = ctk.CTkEntry(main, placeholder_text="Full Name")
        self.full_name.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        self.full_name.insert(0, self.current_user.get("name", ""))

        self.email = ctk.CTkEntry(main, placeholder_text="Email Address")
        self.email.grid(row=3, column=0, sticky="ew", padx=20, pady=8)
        self.email.insert(0, self.current_user.get("email", ""))

        self.current_password = ctk.CTkEntry(main, placeholder_text="Current Password", show="*")
        self.current_password.grid(row=4, column=0, sticky="ew", padx=20, pady=(16, 8))

        self.new_password = ctk.CTkEntry(main, placeholder_text="New Password", show="*")
        self.new_password.grid(row=5, column=0, sticky="ew", padx=20, pady=8)

        self.confirm_password = ctk.CTkEntry(main, placeholder_text="Confirm New Password", show="*")
        self.confirm_password.grid(row=6, column=0, sticky="ew", padx=20, pady=8)

        ctk.CTkLabel(
            main,
            text="Leave the new password fields empty if you only want to update your name or email.",
            text_color="gray"
        ).grid(row=7, column=0, sticky="w", padx=20, pady=(0, 12))

        ctk.CTkButton(main, text="Save Changes", command=self.save_changes).grid(
            row=8, column=0, sticky="w", padx=20, pady=(0, 8)
        )

        self.status_label = ctk.CTkLabel(main, text="", text_color="#7ddc7a")
        self.status_label.grid(row=9, column=0, sticky="w", padx=20, pady=(0, 20))

    def save_changes(self):
        username = self.current_user.get("username", "")
        full_name = self.full_name.get().strip()
        email = self.email.get().strip()
        current_password = self.current_password.get().strip()
        new_password = self.new_password.get().strip()
        confirm_password = self.confirm_password.get().strip()

        if not username:
            self.status_label.configure(text="No active user session found.", text_color="#ff8080")
            return

        if not full_name or not email:
            self.status_label.configure(text="Name and email are required.", text_color="#ff8080")
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
        updated_password = stored_password

        if new_password or confirm_password:
            if current_password != stored_password:
                conn.close()
                self.status_label.configure(text="Current password is incorrect.", text_color="#ff8080")
                return
            if new_password != confirm_password:
                conn.close()
                self.status_label.configure(text="New passwords do not match.", text_color="#ff8080")
                return
            updated_password = new_password

        cursor.execute(
            "UPDATE users SET name=?, email=?, password=? WHERE username=?",
            (full_name, email, updated_password, username)
        )
        conn.commit()
        conn.close()

        self.current_user["name"] = full_name
        self.current_user["email"] = email
        self.current_user["role"] = role
        set_current_user(self.current_user)

        self.current_password.delete(0, "end")
        self.new_password.delete(0, "end")
        self.confirm_password.delete(0, "end")
        self.status_label.configure(text="Security settings updated successfully.", text_color="#7ddc7a")

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
