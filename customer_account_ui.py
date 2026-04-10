import customtkinter as ctk
from PIL import Image
import os
import subprocess
import sys
from session_utils import get_current_user

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CustomerAccountUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("My Account")
        self.geometry("1300x800")

        self.base_path = os.path.dirname(os.path.realpath(__file__))
        self.current_user = get_current_user()
        img_path = os.path.join(self.base_path, "assets", "images")

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
        ctk.CTkButton(profile, text="Edit Profile").pack(anchor="w", padx=20, pady=10)

        def create_box(row, col, title, desc, btn_text):
            box = ctk.CTkFrame(main, corner_radius=12)
            box.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(box, text=title, font=("Arial", 16, "bold")).pack(anchor="w", padx=15, pady=10)
            ctk.CTkLabel(box, text=desc, wraplength=250).pack(anchor="w", padx=15)
            ctk.CTkButton(box, text=btn_text).pack(anchor="w", padx=15, pady=10)

        create_box(1, 0, "Your Orders", "Track, return, or buy again", "View Orders")
        create_box(1, 1, "History", "See your activity & past interactions", "View History")

        create_box(2, 0, "Payment Methods", "Manage cards and billing", "Manage Payments")
        create_box(2, 1, "Addresses", "Edit shipping and billing addresses", "Manage Addresses")
        create_box(2, 2, "Security", "Password and login settings", "Security Settings")

        create_box(3, 0, "Support", "Get help or contact us", "Contact Support")

        logout = ctk.CTkFrame(main, corner_radius=12)
        logout.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(logout, text="Account Actions", font=("Arial", 16, "bold")).pack(pady=10)
        ctk.CTkButton(logout, text="Log Out", fg_color="red").pack(pady=10)

    def open_orders(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_orders_ui.py")])
        self.destroy()

    def open_dashboard(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "customer_dashboard_ui.py")])
        self.destroy()

    def open_cart(self):
        subprocess.Popen([sys.executable, os.path.join(self.base_path, "cart_ui.py")])
        self.destroy()

    def open_account(self):
        pass


if __name__ == "__main__":
    app = CustomerAccountUI()
    app.mainloop()
