import customtkinter as ctk


SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


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
        self.add_button("Sales", "sales")
        self.add_button("View Inventory", "sales")
        self.add_button("Update Inventory", "inventory")
        self.add_button("Orders", "orders")
        self.add_button("Customer Records", "customers")
        self.add_button("Employee Records", "employees")
        self.add_button("History", "history")

    def add_button(self, text, page_name):
        is_active = page_name == self.active_page
        ctk.CTkButton(
            self,
            text=text,
            height=42,
            fg_color=ACTIVE_BUTTON if is_active else BUTTON_COLOR,
            hover_color=BUTTON_HOVER,
            corner_radius=8,
            command=None if is_active else lambda: self.controller.show_page(page_name)
        ).pack(fill="x", padx=18, pady=8)
