import customtkinter as ctk
from shared.session_utils import get_current_user, clear_current_user

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CustomerAccountUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("My Account")
        self.controller.geometry("1300x800")

        self.current_user = get_current_user()
        header = ctk.CTkFrame(self, height=70)
        header.pack(fill="x", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search account...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

        main = ctk.CTkFrame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        for i in range(3):
            main.grid_columnconfigure(i, weight=1)

        profile = ctk.CTkFrame(main, corner_radius=12)
        profile.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        display_name = self.current_user.get("name", "Customer")
        display_email = self.current_user.get("email", "N/A")
        ctk.CTkLabel(profile, text=f"Hello, {display_name}", font=("Arial", 22, "bold")).pack(anchor="w", padx=20, pady=10)
        ctk.CTkLabel(profile, text=f"Email: {display_email}", font=("Arial", 14)).pack(anchor="w", padx=20)
        ctk.CTkButton(profile, text="Edit Profile", command=self.open_profile).pack(anchor="w", padx=20, pady=10)

        def create_box(row, col, title, desc, btn_text, command=None):
            box = ctk.CTkFrame(main, corner_radius=12)
            box.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(box, text=title, font=("Arial", 16, "bold")).pack(anchor="w", padx=15, pady=10)
            ctk.CTkLabel(box, text=desc, wraplength=250, justify="left").pack(anchor="w", padx=15)
            ctk.CTkButton(box, text=btn_text, command=command).pack(anchor="w", padx=15, pady=10)

        create_box(1, 0, "Your Orders", "Track, return, or buy again", "View Orders", self.open_orders)
        create_box(1, 1, "History", "See your activity & past interactions", "View History", self.open_history)
        create_box(1, 2, "Security", "Password and login settings", "Security Settings", self.open_security)

        create_box(2, 0, "Payment Methods", "Manage your full payment, billing, and delivery details", "Manage Payments", self.open_payments)
        create_box(2, 1, "Support", "Get help or contact us", "Contact Support", self.open_support)

        logout = ctk.CTkFrame(main, corner_radius=12)
        logout.grid(row=2, column=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkButton(
            logout,
            text="Log Out",
            fg_color="red",
            hover_color="#b30000",
            command=self.logout
        ).pack(anchor="w", padx=15, pady=20)

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_history(self):
        self.controller.show_page("customer_orders")

    def open_payments(self):
        self.controller.show_page("customer_payments")

    def open_profile(self):
        self.controller.show_page("customer_profile")

    def open_security(self):
        self.controller.show_page("customer_security")

    def open_support(self):
        support_window = ctk.CTkToplevel(self)
        support_window.title("Support")
        support_window.geometry("460x260")

        ctk.CTkLabel(
            support_window,
            text="Support",
            font=("Arial", 22, "bold")
        ).pack(anchor="w", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            support_window,
            text="For help with orders, payments, or account access, contact support below.",
            wraplength=400,
            justify="left"
        ).pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(support_window, text="Email: support@pharmacyplus.local").pack(anchor="w", padx=20, pady=5)
        ctk.CTkLabel(support_window, text="Phone: (555) 010-2026").pack(anchor="w", padx=20, pady=5)

    def logout(self):
        clear_current_user()
        self.controller.show_page("login")

    def open_dashboard(self):
        self.controller.show_page("customer_dashboard")

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        pass


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("customer_account")
