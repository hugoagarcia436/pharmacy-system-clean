import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class LoginUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Login")
        self.geometry("1000x600")

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ========== LEFT ==========
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        script_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(script_dir, "assets", "images", "pharmacy.png")

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

        # Email
        self.email_entry = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Email or Username",
            height=40
        )
        self.email_entry.pack(fill="x", pady=10)

        # Password
        self.password_entry = ctk.CTkEntry(
            self.center_frame,
            placeholder_text="Password",
            show="*",
            height=40
        )
        self.password_entry.pack(fill="x", pady=10)

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
        self.destroy()
        os.system("python sign_up_ui.py")

    def login_user(self):
        import sqlite3
        from tkinter import messagebox

        username = self.email_entry.get()
        password = self.password_entry.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill all fields")
            return

        conn = sqlite3.connect("app_data.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )

        result = cursor.fetchone()
        conn.close()

        if result:
            role = result[0]

            messagebox.showinfo("Success", f"Logged in as {role}")

             
            self.destroy()

            if role == "customer":
                os.system("python customer_dashboard_ui.py")

            elif role == "employee":
                os.system("python admin_dashboard_view_ui.py")

            elif role == "admin":
                print("Admin dashboard coming soon")

        else:
            messagebox.showerror("Error", "Invalid credentials")    


if __name__ == "__main__":
    app = LoginUI()
    app.mainloop()