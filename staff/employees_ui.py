import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


class EmployeesUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Employee Dashboard")
        self.controller.geometry("1280x760")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # =========================
        # SAMPLE DATA
        # =========================
        self.employees = [
            {
                "id": "EMP-001",
                "name": "Maria Lopez",
                "role": "Pharmacist",
                "shift": "Morning",
                "status": "Active",
                "phone": "(956) 555-1201",
                "email": "maria.lopez@pharmacy.com",
                "hire_date": "2024-01-15",
                "username": "mlopez",
                "last_login": "2026-04-10 08:12 AM",
                "orders_handled": 42,
                "items_processed": 315,
                "activity": "Processed 12 orders today"
            },
            {
                "id": "EMP-002",
                "name": "John Smith",
                "role": "Cashier",
                "shift": "Night",
                "status": "Active",
                "phone": "(956) 555-1202",
                "email": "john.smith@pharmacy.com",
                "hire_date": "2024-03-11",
                "username": "jsmith",
                "last_login": "2026-04-10 07:45 PM",
                "orders_handled": 28,
                "items_processed": 189,
                "activity": "Updated 4 sale transactions"
            },
            {
                "id": "EMP-003",
                "name": "Sofia Ramirez",
                "role": "Manager",
                "shift": "Afternoon",
                "status": "Active",
                "phone": "(956) 555-1203",
                "email": "sofia.ramirez@pharmacy.com",
                "hire_date": "2023-10-02",
                "username": "sramirez",
                "last_login": "2026-04-10 02:30 PM",
                "orders_handled": 65,
                "items_processed": 510,
                "activity": "Reviewed inventory alerts"
            },
            {
                "id": "EMP-004",
                "name": "Carlos Gomez",
                "role": "Cashier",
                "shift": "Morning",
                "status": "On Leave",
                "phone": "(956) 555-1204",
                "email": "carlos.gomez@pharmacy.com",
                "hire_date": "2024-05-08",
                "username": "cgomez",
                "last_login": "2026-04-08 09:20 AM",
                "orders_handled": 19,
                "items_processed": 140,
                "activity": "No activity today"
            },
            {
                "id": "EMP-005",
                "name": "Ana Torres",
                "role": "Pharmacist",
                "shift": "Night",
                "status": "Suspended",
                "phone": "(956) 555-1205",
                "email": "ana.torres@pharmacy.com",
                "hire_date": "2024-02-21",
                "username": "atorres",
                "last_login": "2026-04-05 10:11 PM",
                "orders_handled": 31,
                "items_processed": 228,
                "activity": "Account suspended"
            },
            {
                "id": "EMP-006",
                "name": "Luis Hernandez",
                "role": "Manager",
                "shift": "Morning",
                "status": "Active",
                "phone": "(956) 555-1206",
                "email": "luis.hernandez@pharmacy.com",
                "hire_date": "2023-08-17",
                "username": "lhernandez",
                "last_login": "2026-04-10 09:05 AM",
                "orders_handled": 71,
                "items_processed": 560,
                "activity": "Assigned new weekly shifts"
            }
        ]

        self.filtered_employees = self.employees[:]
        self.detail_frame = None

        # =========================
        # SIDEBAR
        # =========================
        sidebar = ctk.CTkFrame(self, width=240, fg_color=SIDEBAR_COLOR)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="EMPLOYEE",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(28, 28))

        self.create_sidebar_button(sidebar, "Dashboard", self.open_dashboard)
        self.create_sidebar_button(sidebar, "Inventory", self.open_inventory)
        self.create_sidebar_button(sidebar, "Orders", self.open_orders)
        self.create_sidebar_button(sidebar, "Employees", active=True)
        self.create_sidebar_button(sidebar, "History", self.open_history)

        # =========================
        # MAIN
        # =========================
        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(main)
        topbar.grid(row=0, column=0, sticky="ew", padx=15, pady=8)
        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topbar,
            text="Employee Directory",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.content = ctk.CTkFrame(main)
        self.content.grid(row=1, column=0, sticky="nsew", padx=15, pady=8)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.show_employees()

    def create_sidebar_button(self, sidebar, text, command=None, active=False):
        ctk.CTkButton(
            sidebar,
            text=text,
            height=42,
            fg_color=ACTIVE_BUTTON if active else BUTTON_COLOR,
            hover_color=BUTTON_HOVER,
            corner_radius=8,
            command=command
        ).pack(fill="x", padx=18, pady=8)

    # =========================
    # HELPERS
    # =========================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.detail_frame = None

    def remove_details(self):
        if self.detail_frame is not None and self.detail_frame.winfo_exists():
            self.detail_frame.destroy()
            self.detail_frame = None

    def refresh_filters(self):
        query = self.search_entry.get().strip().lower()
        role_value = self.role_filter.get()
        shift_value = self.shift_filter.get()
        status_value = self.status_filter.get()

        results = []

        for emp in self.employees:
            matches_query = (
                query in emp["id"].lower()
                or query in emp["name"].lower()
                or query in emp["username"].lower()
                or query in emp["email"].lower()
            )

            matches_role = role_value == "All Roles" or emp["role"] == role_value
            matches_shift = shift_value == "All Shifts" or emp["shift"] == shift_value
            matches_status = status_value == "All Status" or emp["status"] == status_value

            if matches_query and matches_role and matches_shift and matches_status:
                results.append(emp)

        self.filtered_employees = results
        self.render_table()

    def clear_filters(self):
        self.search_entry.delete(0, "end")
        self.role_filter.set("All Roles")
        self.shift_filter.set("All Shifts")
        self.status_filter.set("All Status")
        self.filtered_employees = self.employees[:]
        self.render_table()

    def generate_new_employee_id(self):
        max_num = 0
        for emp in self.employees:
            try:
                current = int(emp["id"].split("-")[1])
                if current > max_num:
                    max_num = current
            except:
                pass
        return f"EMP-{max_num + 1:03d}"

    def toggle_employee_status(self, emp):
        if emp["status"] == "Active":
            emp["status"] = "Suspended"
            emp["activity"] = "Account suspended"
        else:
            emp["status"] = "Active"
            emp["activity"] = "Account reactivated"

        self.render_table()

    def reset_password(self, emp):
        emp["activity"] = "Password reset requested"
        self.show_employee_detail(emp)

    def assign_shift(self, emp, new_shift):
        emp["shift"] = new_shift
        emp["activity"] = f"Shift changed to {new_shift}"
        self.show_employee_detail(emp)
        self.render_table()

    # =========================
    # MAIN PAGE
    # =========================
    def show_employees(self):
        self.clear_content()

        container = ctk.CTkScrollableFrame(self.content)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Employees",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 8))

        # =========================
        # FILTER BAR
        # =========================
        filter_bar = ctk.CTkFrame(container, fg_color="transparent")
        filter_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        filter_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_bar,
            width=220,
            placeholder_text="Search by ID, name, username..."
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="w")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_filters())

        self.role_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Roles", "Pharmacist", "Cashier", "Manager"],
            command=lambda value: self.refresh_filters()
        )
        self.role_filter.grid(row=0, column=1, padx=8, pady=5)
        self.role_filter.set("All Roles")

        self.shift_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Shifts", "Morning", "Afternoon", "Night"],
            command=lambda value: self.refresh_filters()
        )
        self.shift_filter.grid(row=0, column=2, padx=8, pady=5)
        self.shift_filter.set("All Shifts")

        self.status_filter = ctk.CTkOptionMenu(
            filter_bar,
            values=["All Status", "Active", "On Leave", "Suspended"],
            command=lambda value: self.refresh_filters()
        )
        self.status_filter.grid(row=0, column=3, padx=8, pady=5)
        self.status_filter.set("All Status")

        ctk.CTkButton(
            filter_bar,
            text="+ Add Employee",
            width=130,
            command=self.show_add_employee_form
        ).grid(row=0, column=4, padx=(14, 8), pady=5)

        ctk.CTkButton(
            filter_bar,
            text="Clear",
            width=90,
            command=self.clear_filters
        ).grid(row=0, column=5, padx=8, pady=5)

        # =========================
        # DETAIL AREA
        # =========================
        self.detail_host = ctk.CTkFrame(container, fg_color="transparent")
        self.detail_host.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        self.detail_host.grid_columnconfigure(0, weight=1)

        # =========================
        # TABLE HOLDER
        # =========================
        self.table_holder = ctk.CTkFrame(container, fg_color="transparent")
        self.table_holder.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.table_holder.grid_columnconfigure(0, weight=1)

        self.render_table()

    # =========================
    # TABLE
    # =========================
    def render_table(self):
        for widget in self.table_holder.winfo_children():
            widget.destroy()

        headers = ["Employee ID", "Name", "Role", "Shift", "Status", "Actions"]
        col_widths = [120, 220, 130, 120, 120, 300]

        table = ctk.CTkFrame(self.table_holder, fg_color="transparent")
        table.grid(row=0, column=0, sticky="ew")
        table.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(table, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        
        # ===== LINE UNDER HEADER =====
        separator = ctk.CTkFrame(table, height=2, fg_color="#3a3a3a")
        separator.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        for i, w in enumerate(col_widths):
            header.grid_columnconfigure(i, minsize=w, weight=1 if i in [1, 5] else 0)

        for col, text in enumerate(headers):
            anchor = "w" if col in [0, 1, 5] else "center"
            ctk.CTkLabel(
                header,
                text=text,
                font=ctk.CTkFont(weight="bold"),
                anchor=anchor
            ).grid(row=0, column=col, padx=10, pady=8, sticky="ew")

        for i, emp in enumerate(self.filtered_employees, start=2):
            bg = "#2b2b2b" if (i - 1) % 2 == 0 else "#242424"

            row = ctk.CTkFrame(table, fg_color=bg, corner_radius=8)
            row.grid(row=i, column=0, sticky="ew", pady=3)

            for j, w in enumerate(col_widths):
                row.grid_columnconfigure(j, minsize=w, weight=1 if j in [1, 5] else 0)

            status_color = "#00c853"
            if emp["status"] == "On Leave":
                status_color = "#f4b400"
            elif emp["status"] == "Suspended":
                status_color = "#ff4d4f"

            values = [
                emp["id"],
                emp["name"],
                emp["role"],
                emp["shift"],
                emp["status"]
            ]

            for col, val in enumerate(values):
                anchor = "w" if col in [0, 1] else "center"
                color = status_color if col == 4 else "white"

                ctk.CTkLabel(
                    row,
                    text=val,
                    text_color=color,
                    anchor=anchor
                ).grid(row=0, column=col, padx=10, pady=10, sticky="ew")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=5, padx=8, pady=6, sticky="e")

            ctk.CTkButton(
                actions,
                text="View",
                width=60,
                command=lambda e=emp: self.show_employee_detail(e)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                actions,
                text="Shift",
                width=60,
                command=lambda e=emp: self.show_shift_panel(e)
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                actions,
                text="Reset",
                width=60,
                command=lambda e=emp: self.reset_password(e)
            ).pack(side="left", padx=3)

            status_btn_text = "Suspend" if emp["status"] == "Active" else "Activate"
            status_btn_color = "#8b0000" if emp["status"] == "Active" else "#2e7d32"

            ctk.CTkButton(
                actions,
                text=status_btn_text,
                width=80,
                fg_color=status_btn_color,
                command=lambda e=emp: self.toggle_employee_status(e)
            ).pack(side="left", padx=3)

    # =========================
    # VIEW DETAIL
    # =========================
    def show_employee_detail(self, emp):
        self.remove_details()

        self.detail_frame = ctk.CTkFrame(self.detail_host, fg_color="#1f1f1f", corner_radius=10)
        self.detail_frame.grid(row=0, column=0, sticky="ew")
        self.detail_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            self.detail_frame,
            text=f"{emp['name']}  |  {emp['id']}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 10), sticky="w")

        # basic info
        left = ctk.CTkFrame(self.detail_frame, fg_color="#252525")
        left.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(left, text="Basic Info", font=ctk.CTkFont(weight="bold"))\
            .grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")
        ctk.CTkLabel(left, text=f"Full Name: {emp['name']}").grid(row=1, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(left, text=f"Employee ID: {emp['id']}").grid(row=2, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(left, text=f"Phone: {emp['phone']}").grid(row=3, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(left, text=f"Email: {emp['email']}").grid(row=4, column=0, padx=12, pady=(4, 10), sticky="w")

        # work info
        middle = ctk.CTkFrame(self.detail_frame, fg_color="#252525")
        middle.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(middle, text="Work Info", font=ctk.CTkFont(weight="bold"))\
            .grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")
        ctk.CTkLabel(middle, text=f"Role: {emp['role']}").grid(row=1, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(middle, text=f"Shift: {emp['shift']}").grid(row=2, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(middle, text=f"Status: {emp['status']}").grid(row=3, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(middle, text=f"Hire Date: {emp['hire_date']}").grid(row=4, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(middle, text=f"Username: {emp['username']}").grid(row=5, column=0, padx=12, pady=(4, 10), sticky="w")

        # activity
        right = ctk.CTkFrame(self.detail_frame, fg_color="#252525")
        right.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(right, text="Performance / Activity", font=ctk.CTkFont(weight="bold"))\
            .grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")
        ctk.CTkLabel(right, text=f"Orders Handled: {emp['orders_handled']}").grid(row=1, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(right, text=f"Items Processed: {emp['items_processed']}").grid(row=2, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(right, text=f"Last Login: {emp['last_login']}").grid(row=3, column=0, padx=12, pady=4, sticky="w")
        ctk.CTkLabel(right, text=f"Activity: {emp['activity']}").grid(row=4, column=0, padx=12, pady=(4, 10), sticky="w")

        action_bar = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        action_bar.grid(row=2, column=0, columnspan=3, padx=12, pady=(0, 12), sticky="e")

        ctk.CTkButton(
            action_bar,
            text="Assign Shift",
            width=100,
            command=lambda e=emp: self.show_shift_panel(e)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar,
            text="Reset Password",
            width=120,
            command=lambda e=emp: self.reset_password(e)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar,
            text="Close",
            width=80,
            command=self.remove_details
        ).pack(side="left", padx=5)

    # =========================
    # SHIFT PANEL
    # =========================
    def show_shift_panel(self, emp):
        self.remove_details()

        self.detail_frame = ctk.CTkFrame(self.detail_host, fg_color="#1f1f1f", corner_radius=10)
        self.detail_frame.grid(row=0, column=0, sticky="ew")
        self.detail_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(
            self.detail_frame,
            text=f"Assign Shift - {emp['name']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 10), sticky="w")

        shift_menu = ctk.CTkOptionMenu(
            self.detail_frame,
            values=["Morning", "Afternoon", "Night"]
        )
        shift_menu.grid(row=1, column=0, padx=15, pady=8, sticky="w")
        shift_menu.set(emp["shift"])

        ctk.CTkButton(
            self.detail_frame,
            text="Save Shift",
            width=100,
            command=lambda e=emp: self.assign_shift(e, shift_menu.get())
        ).grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkButton(
            self.detail_frame,
            text="Close",
            width=80,
            command=self.remove_details
        ).grid(row=1, column=2, padx=15, pady=8, sticky="e")

    # =========================
    # ADD EMPLOYEE FORM
    # =========================
    def show_add_employee_form(self):
        self.remove_details()

        self.detail_frame = ctk.CTkFrame(self.detail_host, fg_color="#1f1f1f", corner_radius=10)
        self.detail_frame.grid(row=0, column=0, sticky="ew")
        self.detail_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(
            self.detail_frame,
            text="Add Employee",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=4, padx=15, pady=(12, 10), sticky="w")

        name_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Full Name")
        name_entry.grid(row=1, column=0, padx=10, pady=8, sticky="ew")

        phone_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Phone")
        phone_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")

        email_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Email")
        email_entry.grid(row=1, column=2, padx=10, pady=8, sticky="ew")

        username_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Username")
        username_entry.grid(row=1, column=3, padx=10, pady=8, sticky="ew")

        role_menu = ctk.CTkOptionMenu(self.detail_frame, values=["Pharmacist", "Cashier", "Manager"])
        role_menu.grid(row=2, column=0, padx=10, pady=8, sticky="ew")
        role_menu.set("Cashier")

        shift_menu = ctk.CTkOptionMenu(self.detail_frame, values=["Morning", "Afternoon", "Night"])
        shift_menu.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        shift_menu.set("Morning")

        status_menu = ctk.CTkOptionMenu(self.detail_frame, values=["Active", "On Leave", "Suspended"])
        status_menu.grid(row=2, column=2, padx=10, pady=8, sticky="ew")
        status_menu.set("Active")

        password_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Password", show="*")
        password_entry.grid(row=2, column=3, padx=10, pady=8, sticky="ew")

        def save_employee():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not name or not phone or not email or not username or not password:
                return

            new_emp = {
                "id": self.generate_new_employee_id(),
                "name": name,
                "role": role_menu.get(),
                "shift": shift_menu.get(),
                "status": status_menu.get(),
                "phone": phone,
                "email": email,
                "hire_date": "2026-04-10",
                "username": username,
                "last_login": "Never",
                "orders_handled": 0,
                "items_processed": 0,
                "activity": "Employee account created"
            }

            self.employees.append(new_emp)
            self.filtered_employees = self.employees[:]
            self.remove_details()
            self.render_table()

        action_bar = ctk.CTkFrame(self.detail_frame, fg_color="transparent")
        action_bar.grid(row=3, column=0, columnspan=4, padx=10, pady=(8, 12), sticky="e")

        ctk.CTkButton(
            action_bar,
            text="Create Employee",
            width=130,
            command=save_employee
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            action_bar,
            text="Close",
            width=90,
            command=self.remove_details
        ).pack(side="left", padx=5)

    def open_dashboard(self):
        self.controller.show_page("dashboard")

    def open_orders(self):
        self.controller.show_page("orders")

    def open_inventory(self):
        self.controller.show_page("inventory")

    def open_history(self):
        self.controller.show_page("history")


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("employees")
