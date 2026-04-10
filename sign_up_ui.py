import customtkinter as ctk
from PIL import Image
import os
import sqlite3
import re
from tkinter import messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SignUpUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sign Up")
        self.geometry("1000x600")

        # ================= DATABASE =================
        self.conn = sqlite3.connect("app_data.db")
        self.cursor = self.conn.cursor()

        # 🔐 EMPLOYEE AUTH KEY
        self.EMPLOYEE_KEY = "PHARM2026"

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= MAIN CONTAINER =================
        self.container = ctk.CTkFrame(self, corner_radius=15)
        self.container.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=1)

        # ================= LEFT SIDE =================
        self.left_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, padx=30, pady=30, sticky="nsew")

        script_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(script_dir, "assets", "images", "waiting.png")

        self.image = ctk.CTkImage(
            light_image=Image.open(image_path),
            dark_image=Image.open(image_path),
            size=(320, 320)
        )

        self.title_label = ctk.CTkLabel(
            self.left_frame,
            text="Let's get started!",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(anchor="center", pady=(20, 10))

        self.subtitle = ctk.CTkLabel(
            self.left_frame,
            text="Create your account to access the system.",
            font=ctk.CTkFont(size=14)
        )
        self.subtitle.pack(anchor="center", pady=(5, 10))

        self.image_label = ctk.CTkLabel(self.left_frame, image=self.image, text="")
        self.image_label.pack()

        # ================= RIGHT SIDE =================
        self.form_card = ctk.CTkFrame(self.container, corner_radius=15)
        self.form_card.grid(row=0, column=1, padx=30, pady=30, sticky="nsew")

        self.form_card.grid_columnconfigure(0, weight=1)
        self.form_card.grid_columnconfigure(1, weight=1)

        # ================= ACCOUNT TYPE =================
        self.account_type = ctk.StringVar(value="Customer")

        self.customer_radio = ctk.CTkRadioButton(
            self.form_card,
            text="Customer",
            variable=self.account_type,
            value="Customer",
            command=self.toggle_employee_fields
        )
        self.customer_radio.grid(row=0, column=0, pady=10)

        self.employee_radio = ctk.CTkRadioButton(
            self.form_card,
            text="Employee",
            variable=self.account_type,
            value="Employee",
            command=self.toggle_employee_fields
        )
        self.employee_radio.grid(row=0, column=1, pady=10)


        # ================= NAME =================
        self.first_name = ctk.CTkEntry(self.form_card, placeholder_text="First Name")
        self.first_name.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.last_name = ctk.CTkEntry(self.form_card, placeholder_text="Last Name")
        self.last_name.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # ================= EMAIL =================
        self.email = ctk.CTkEntry(self.form_card, placeholder_text="Email")
        self.email.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= USERNAME =================
        self.username = ctk.CTkEntry(self.form_card, placeholder_text="Username")
        self.username.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= PASSWORD =================
        self.password = ctk.CTkEntry(self.form_card, placeholder_text="Password", show="*")
        self.password.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= CONFIRM =================
        self.confirm_password = ctk.CTkEntry(self.form_card, placeholder_text="Confirm Password", show="*")
        self.confirm_password.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= EMPLOYEE KEY =================
        self.employee_key = ctk.CTkEntry(self.form_card, placeholder_text="Employee Auth Key")

        # ================= RULES =================
        self.rules = ctk.CTkLabel(
            self.form_card,
            text="• 12-16 characters • Uppercase • Number • Special character",
            font=ctk.CTkFont(size=11)
        )
        self.rules.grid(row=7, column=0, columnspan=2, pady=5)

        # ================= BUTTON =================
        self.signup_btn = ctk.CTkButton(
            self.form_card,
            text="Sign Up",
            height=40,
            command=self.create_account  # 🔥 CONNECTED
        )
        self.signup_btn.grid(row=8, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            self.form_card,
            text="Cancel",
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self.go_back_login  
        )
        self.cancel_btn.grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

    # ================= PASSWORD VALIDATION =================
    def validate_password(self, password):
        if len(password) < 12 or len(password) > 16:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    # ================= CREATE ACCOUNT =================
    def create_account(self):
        first = self.first_name.get()
        last = self.last_name.get()
        email = self.email.get()
        username = self.username.get()
        password = self.password.get()
        confirm = self.confirm_password.get()
        role = self.account_type.get().lower()

        # Empty check
        if not all([first, last, email, username, password, confirm]):
            messagebox.showerror("Error", "All fields are required")
            return

        # Password match
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        # Password rules
        if not self.validate_password(password):
            messagebox.showerror("Error", "Password does not meet requirements")
            return

        # 🔥 EMPLOYEE VALIDATION
        if role == "employee":
            key = self.employee_key.get().strip()

            if key == "":
                messagebox.showerror("Error", "Employee key is required")
                return

            if key != self.EMPLOYEE_KEY:
                messagebox.showerror("Error", "Invalid employee key")
                return

        # Check duplicate username
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        # Insert into database
        self.cursor.execute(
            "INSERT INTO users (name, email, username, password, role) VALUES (?, ?, ?, ?, ?)",
            (first + " " + last, email, username, password, role)
        )
        self.conn.commit()

        messagebox.showinfo("Success", "Account created successfully")

        # Return to login
        self.destroy()
        os.system("python login_ui.py")

    # ================= TOGGLE =================
    def toggle_employee_fields(self):
        if self.account_type.get() == "Employee":
            self.employee_key.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        else:
            self.employee_key.grid_remove()

    def go_back_login(self):
        self.destroy()
        os.system("python login_ui.py") 


if __name__ == "__main__":
    app = SignUpUI()
    app.mainloop()
