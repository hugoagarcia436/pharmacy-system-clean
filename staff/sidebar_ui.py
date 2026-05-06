import customtkinter as ctk

from shared.session_utils import clear_current_user


SIDEBAR_COLOR = "#e5f7f2"
BUTTON_COLOR = "#ffffff"
BUTTON_HOVER = "#d6f2e8"
ACTIVE_BUTTON = "#b7ded4"
BUTTON_TEXT = "#114d48"
LOGOUT_COLOR = "#d64545"
LOGOUT_HOVER = "#b83232"


class EmployeeSidebar(ctk.CTkFrame):
    def __init__(self, parent, controller, active_page):
        super().__init__(parent, width=240, fg_color=SIDEBAR_COLOR)
        self.controller = controller
        self.active_page = active_page

        self.grid(row=0, column=0, sticky="ns")
        self.grid_propagate(False)

        ctk.CTkLabel(
            self,
            text="EMPLOYEE",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(28, 28))

        self.add_button("Dashboard", "dashboard")
        self.add_button("Process Sale", "sales")
        self.add_button("Inventory", "inventory")
        self.add_button("Customer Records", "customers")
        self.add_button("Employee Records", "employees")

        self.logout_button = ctk.CTkButton(
            self,
            text="Log Out",
            height=42,
            fg_color=LOGOUT_COLOR,
            hover_color=LOGOUT_HOVER,
            corner_radius=8,
            command=self.logout,
        )
        self.logout_button.pack(side="bottom", fill="x", padx=18, pady=(8, 18))

    def add_button(self, text, page_name):
        is_active = page_name == self.active_page
        ctk.CTkButton(
            self,
            text=text,
            height=42,
            fg_color=ACTIVE_BUTTON if is_active else BUTTON_COLOR,
            hover_color=BUTTON_HOVER,
            text_color=BUTTON_TEXT,
            border_width=1,
            border_color="#b7ded4",
            corner_radius=8,
            command=None if is_active else lambda: self.controller.show_page(page_name)
        ).pack(fill="x", padx=18, pady=8)

    def logout(self):
        clear_current_user()
        if "login" in getattr(self.controller, "pages", {}):
            self.controller.show_page("login")
        else:
            self.controller.destroy()
