import customtkinter as ctk
from PIL import Image
import os
import sqlite3
from datetime import datetime, timedelta
from shared.paths import DB_PATH, IMAGES_DIR
from shared.employee_auth import assign_missing_employee_ids, ensure_employee_user_schema
from shared.session_utils import set_current_user

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
LOGIN_ATTEMPTS = {}


class LoginUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Login")
        self.controller.geometry("1000x600")

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ========== LEFT ==========
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        image_path = os.path.join(IMAGES_DIR, "pharmacy.png")

        self.image = ctk.CTkImage(
            light_image=Image.open(image_path),
            size=(450, 450)
        )

        self.left_label = ctk.CTkLabel(
            self.left_frame,
            image=self.image,
            text=""
        )
        self.left_label.pack(expand=True)

        # ========== RIGHT ==========
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(2, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        self.center_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.center_frame.grid(row=1, column=0, sticky="nsew", padx=120)

        # Title
        self.title_label = ctk.CTkLabel(
            self.center_frame,
            text="Welcome Back",
            font=("Arial", 36, "bold")
        )
        self.title_label.pack(pady=(0, 10))

        self.subtitle = ctk.CTkLabel(
            self.center_frame,
            text="Login to your account",
            font=("Arial", 16)
        )
        self.subtitle.pack(pady=(0, 25))

        self.login_mode = "standard"
        self.mode_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.mode_frame.pack(fill="x", pady=(0, 10))
        self.mode_frame.grid_columnconfigure((0, 1), weight=1)

        self.standard_login_button = ctk.CTkButton(
            self.mode_frame,
            text="Customer Login",
            height=34,
            command=self.use_standard_login
        )
        self.standard_login_button.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.standard_login_button.configure(state="disabled")

        self.employee_login_button = ctk.CTkButton(
            self.mode_frame,
            text="Employee Login",
            height=34,
            fg_color="#2f2f2f",
            hover_color="#3a3a3a",
            command=self.use_employee_login
        )
        self.employee_login_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")

        # Email
        self.email_entry_standard = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Email or Username",
            height=40
        )
        self.email_entry_standard.pack(fill="x", pady=10)

        self.email_entry_employee = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Employee ID",
            height=40
        )
        self.email_entry_employee.pack_forget()

        # Password
        self.password_entry_standard = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Password",
            show="*",
            height=40
        )
        self.password_entry_standard.pack(fill="x", pady=10)

        self.password_entry_employee = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Password",
            show="*",
            height=40
        )
        self.password_entry_employee.pack_forget()

        # Options
        self.options_frame = ctk.CTkFrame(self.center_frame, fg_color="transparent")
        self.options_frame.pack(fill="x", pady=(10, 15))

        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)

        self.remember_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Remember me"
        )
        self.remember_checkbox.grid(row=0, column=0, sticky="w", padx=(5, 0))

        self.forgot_label = ctk.CTkLabel(
            self.options_frame,
            text="Forgot Password?",
            text_color="#4da6ff",
            cursor="hand2"
        )
        self.forgot_label.grid(row=0, column=1, sticky="e", padx=(0, 5))

        # Login button
        self.login_button = ctk.CTkButton(
            self.center_frame,
            text="Login",
            height=40,
            command=self.login_user 
        )
        self.login_button.pack(fill="x", pady=10)

        # OR
        self.or_label = ctk.CTkLabel(
            self.center_frame,
            text="──────── OR ────────"
        )
        self.or_label.pack(pady=15)

        # Social
        self.google_button = ctk.CTkButton(
            self.center_frame,
            text="Continue with Google",
            height=40
        )
        self.google_button.pack(fill="x", pady=5)

        self.facebook_button = ctk.CTkButton(
            self.center_frame,
            text="Continue with Facebook",
            height=40
        )
        self.facebook_button.pack(fill="x", pady=5)

        # SIGN UP LABEL
        self.signup_label = ctk.CTkLabel(
            self.center_frame,
            text="Don't have an account? Sign up",
            text_color="#4da6ff",
            cursor="hand2",
            font=("Arial", 14)
        )
        self.signup_label.pack(pady=20)

        
        self.signup_label.bind("<Button-1>", self.open_signup)

    #FUNCTION TO OPEN SIGN UP
    def open_signup(self, event):
        self.controller.show_page("signup")

    def use_standard_login(self):
        self.login_mode = "standard"

        self.standard_login_button.configure(state="disabled")
        self.employee_login_button.configure(state="normal")

        self.email_entry_standard.pack(after=self.email_entry_employee, fill="x", pady=10)
        self.email_entry_employee.pack_forget()
        self.email_entry_standard.configure(placeholder_text="Email or Username")

        self.password_entry_standard.pack(after=self.password_entry_employee, fill="x", pady=10)
        self.password_entry_employee.pack_forget()
        self.password_entry_standard.configure(placeholder_text="Password")

        
        self.subtitle.configure(text="Login to your account")
        self.standard_login_button.configure(fg_color="#2f66db", hover_color="#3a73e3")
        self.employee_login_button.configure(fg_color="#2f2f2f", hover_color="#3a3a3a")

    def use_employee_login(self):
        self.login_mode = "employee"

        self.standard_login_button.configure(state="normal")
        self.employee_login_button.configure(state="disabled")

        self.email_entry_employee.pack(after=self.email_entry_standard, fill="x", pady=10)
        self.email_entry_standard.pack_forget()
        self.email_entry_employee.configure(placeholder_text="Employee ID")

        self.password_entry_employee.pack(after=self.password_entry_standard, fill="x", pady=10)
        self.password_entry_standard.pack_forget()
        self.password_entry_employee.configure(placeholder_text="Password")

        self.subtitle.configure(text="Employee Login")
        self.employee_login_button.configure(fg_color="#2f66db", hover_color="#3a73e3")
        self.standard_login_button.configure(fg_color="#2f2f2f", hover_color="#3a3a3a")

    def login_user(self):
        from tkinter import messagebox

        login_identifier_standard = self.email_entry_standard.get().strip()
        password_standard = self.password_entry_standard.get()

        login_identifier_employee = self.email_entry_employee.get().strip()
        password_employee = self.password_entry_employee.get()

        if self.is_locked_out(login_identifier_standard):
            messagebox.showerror("Error", "Too many invalid attempts. Please try again later.")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        ensure_employee_user_schema(cursor)
        assign_missing_employee_ids(cursor)
        conn.commit()

        if self.login_mode == "employee":

            if login_identifier_employee == "" or password_employee == "":
                messagebox.showerror("Error", "Please fill all fields")
                return
        
            cursor.execute(
                """
                SELECT id, name, email, username, role, employee_id, password_setup_required
                FROM users
                WHERE role='employee'
                AND lower(employee_id)=lower(?)
                """,
                (login_identifier_employee,)
            )
            employee_account = cursor.fetchone()

            if employee_account is None:
                conn.close()
                messagebox.showerror(
                    "Employee Account Not Found",
                    "Employee account not found. Please use Sign Up or contact a manager to create your employee account."
                )
                return

            user_id, name, email, username, role, employee_id, setup_required = employee_account

            cursor.execute(
                """
                SELECT id, name, email, username, role, employee_id, password_setup_required
                FROM users
                WHERE role='employee'
                AND lower(employee_id)=lower(?)
                AND password=?
                """,
                (login_identifier_employee, password_employee)
            )
        else:

            if login_identifier_standard == "" or password_standard == "":
                messagebox.showerror("Error", "Please fill all fields")
                return
        
            cursor.execute(
                """
                SELECT id, name, email, username, role, employee_id, password_setup_required
                FROM users
                WHERE (lower(username)=lower(?) OR lower(email)=lower(?))
                AND password=?
                """,
                (login_identifier_standard, login_identifier_standard, password_standard)
            )

        result = cursor.fetchone()

        if result:
            user_id, name, email, username, role, employee_id, setup_required = result
            if role == "employee" and setup_required:
                conn.close()
                messagebox.showerror("Error", "Please use Sign Up or contact a manager to finish your employee account.")
                return

            self.clear_failed_attempts(login_identifier_employee)

            cursor.execute(
                "UPDATE users SET last_login=? WHERE id=?",
                (datetime.now().strftime("%Y-%m-%d %I:%M %p"), user_id)
            )
            conn.commit()
            conn.close()

            set_current_user({
                "name": name,
                "email": email,
                "username": username,
                "role": role,
                "employee_id": employee_id
            })

            if role == "customer":
                self.controller.show_page("customer_dashboard")

            elif role in ("employee", "admin"):
                self.controller.open_staff_dashboard()

        else:
            conn.close()
            attempts_left = self.register_failed_attempt(login_identifier_standard)
            if attempts_left <= 0:
                messagebox.showerror("Error", "Too many invalid attempts. Login is temporarily locked.")
            elif self.login_mode == "employee":
                messagebox.showerror("Error", "Invalid employee ID or password.")
            else:
                messagebox.showerror("Error", f"Invalid credentials. Attempts left: {attempts_left}")

    def attempt_key(self, username):
        return username.strip().lower()

    def is_locked_out(self, username):
        key = self.attempt_key(username)
        attempt_data = LOGIN_ATTEMPTS.get(key)
        if not attempt_data:
            return False

        locked_until = attempt_data.get("locked_until")
        if locked_until is None:
            return False

        if datetime.now() >= locked_until:
            LOGIN_ATTEMPTS.pop(key, None)
            return False

        return True

    def register_failed_attempt(self, username):
        key = self.attempt_key(username)
        attempt_data = LOGIN_ATTEMPTS.setdefault(key, {"count": 0, "locked_until": None})
        attempt_data["count"] += 1

        attempts_left = MAX_LOGIN_ATTEMPTS - attempt_data["count"]
        if attempts_left <= 0:
            attempt_data["locked_until"] = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
            return 0

        return attempts_left

    def clear_failed_attempts(self, username):
        LOGIN_ATTEMPTS.pop(self.attempt_key(username), None)


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("login")
