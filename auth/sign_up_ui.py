import customtkinter as ctk
from PIL import Image
import os
import sqlite3
import re
from datetime import datetime
from tkinter import messagebox
from shared.employee_auth import ensure_employee_user_schema
from shared.paths import DB_PATH, IMAGES_DIR

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SignUpUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Sign Up")
        self.controller.geometry("1000x680")

        # ================= DATABASE =================
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        ensure_employee_user_schema(self.cursor)
        self.conn.commit()

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

        image_path = os.path.join(IMAGES_DIR, "waiting.png")

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
        self.username.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= PHONE =================
        self.phone = ctk.CTkEntry(self.form_card, placeholder_text="Phone Number")
        self.phone.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= PASSWORD =================
        self.password = ctk.CTkEntry(self.form_card, placeholder_text="Password", show="*")
        self.password.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= CONFIRM =================
        self.confirm_password = ctk.CTkEntry(self.form_card, placeholder_text="Confirm Password", show="*")
        self.confirm_password.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # ================= EMPLOYEE ID =================
        self.employee_id_entry = ctk.CTkEntry(self.form_card, placeholder_text="Employee ID")

        # ================= RULES =================
        self.rules = ctk.CTkLabel(
            self.form_card,
            text="• 12-16 characters • Uppercase • Number • Special character",
            font=ctk.CTkFont(size=11)
        )
        self.rules.grid(row=8, column=0, columnspan=2, pady=5)

        # ================= BUTTON =================
        self.signup_btn = ctk.CTkButton(
            self.form_card,
            text="Sign Up",
            height=40,
            command=self.create_account  # 🔥 CONNECTED
        )
        self.signup_btn.grid(row=9, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

        self.cancel_btn = ctk.CTkButton(
            self.form_card,
            text="Cancel",
            height=40,
            fg_color="gray",
            hover_color="#555555",
            command=self.go_back_login  
        )
        self.cancel_btn.grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")

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

    def validate_employee_id(self, employee_id):
        return re.fullmatch(r"EMP-\d{3,}", employee_id.strip().upper()) is not None

    # ================= CREATE ACCOUNT =================
    def create_account(self):
        first = self.first_name.get().strip()
        last = self.last_name.get().strip()
        email = self.email.get().strip()
        username = self.username.get().strip()
        phone = self.phone.get().strip()
        password = self.password.get()
        confirm = self.confirm_password.get()
        role = self.account_type.get().lower()

        if role == "employee":
            self.create_employee_account(first, last, email, username, password, confirm)
            return

        # Empty check
        if not all([first, last, email, username, phone, password, confirm]):
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

        # Check duplicate username
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        # Insert into database
        self.cursor.execute(
            "INSERT INTO users (name, email, username, phone, password, role) VALUES (?, ?, ?, ?, ?, ?)",
            (first + " " + last, email, username, phone, password, role)
        )
        self.conn.commit()

        messagebox.showinfo("Success", "Account created successfully")

        # Return to login
        self.controller.show_page("login")

    def create_employee_account(self, first, last, email, username, password, confirm):
        employee_id = self.employee_id_entry.get().strip().upper()

        if not all([first, last, email, username, password, confirm, employee_id]):
            messagebox.showerror("Error", "All fields are required")
            return

        if not self.validate_employee_id(employee_id):
            messagebox.showerror("Error", "Invalid employee ID.")
            return

        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return

        if not self.validate_password(password):
            messagebox.showerror("Error", "Invalid password.")
            return

        self.cursor.execute(
            "SELECT id FROM users WHERE role='employee' AND lower(email)=lower(?)",
            (email,)
        )
        if self.cursor.fetchone():
            messagebox.showerror(
                "Account Exists",
                "An account with this email already exists. Please log in using the existing account."
            )
            return

        self.cursor.execute(
            "SELECT id FROM users WHERE role='employee' AND lower(employee_id)=lower(?)",
            (employee_id,)
        )
        if self.cursor.fetchone():
            messagebox.showerror(
                "Account Exists",
                "An employee account with this ID already exists. Please log in using the existing account."
            )
            return

        self.cursor.execute("SELECT id FROM users WHERE lower(username)=lower(?)", (username,))
        if self.cursor.fetchone():
            messagebox.showerror("Error", "Username already exists")
            return

        full_name = f"{first} {last}"
        hire_date = datetime.now().strftime("%Y-%m-%d")
        last_login = datetime.now().strftime("%Y-%m-%d %I:%M %p")

        self.cursor.execute(
            """
            INSERT INTO users (
                name,
                email,
                username,
                password,
                role,
                employee_id,
                employee_position,
                shift,
                status,
                hire_date,
                last_login,
                password_setup_required
            )
            VALUES (?, ?, ?, ?, 'employee', ?, 'Employee', 'Unassigned', 'Active', ?, ?, 0)
            """,
            (full_name, email, username, password, employee_id, hire_date, last_login)
        )
        self.conn.commit()

        messagebox.showinfo(
            "Success",
            "Employee account created successfully. Please log in with the new employee credentials."
        )
        self.controller.show_page("login")

    # ================= TOGGLE =================
    def toggle_employee_fields(self):
        if self.account_type.get() == "Employee":
            self.phone.grid_remove()
            self.employee_id_entry.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        else:
            self.phone.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
            self.employee_id_entry.grid_remove()

    def go_back_login(self):
        self.controller.show_page("login")

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("signup")
