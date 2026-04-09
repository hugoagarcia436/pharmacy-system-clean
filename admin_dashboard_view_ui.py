import customtkinter as ctk
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Admin Dashboard")
        self.geometry("1200x700")

        # ========== LAYOUT ==========
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        ctk.CTkLabel(self.sidebar, text="ADMIN", font=("Arial", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self.sidebar, text="Dashboard").pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(self.sidebar,text="Inventory",command=self.open_inventory).pack(pady=10, 
        padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="Orders").pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="Employees").pack(pady=10, padx=10, fill="x")

        # ========== MAIN AREA ==========
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # ========== TOP STATS ==========
        self.create_stat_card("Total Orders", "128", 0, 0)
        self.create_stat_card("Pending Orders", "12", 0, 1)
        self.create_stat_card("Revenue Today", "$2,340", 1, 0)
        self.create_stat_card("Low Stock Items", "6", 1, 1)

        # ========== ORDER TABLE ==========
        self.orders_frame = ctk.CTkFrame(self.main_frame)
        self.orders_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)

        ctk.CTkLabel(self.orders_frame, text="Recent Orders", font=("Arial", 16, "bold")).pack(anchor="w", padx=10, pady=10)

        self.orders_table = ctk.CTkScrollableFrame(self.orders_frame, height=200)
        self.orders_table.pack(fill="both", expand=True, padx=10, pady=5)

        self.load_orders()

        # ========== REMINDERS ==========
        self.reminder_frame = ctk.CTkFrame(self.sidebar)
        self.reminder_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.reminder_frame, text="Reminders", font=("Arial", 14, "bold")).pack(pady=5)

        self.reminder_box = ctk.CTkTextbox(self.reminder_frame, height=120)
        self.reminder_box.pack(fill="x", padx=5, pady=5)

        self.reminder_box.insert("end",
            "• Meeting with staff - 5:30 PM\n"
            "• Restock insulin\n"
            "• Review sales report\n"
        )

    # ========== STAT CARDS ==========
    def create_stat_card(self, title, value, row, col):
        frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(frame, text=title, font=("Arial", 14)).pack(anchor="w", padx=10, pady=(10, 0))
        ctk.CTkLabel(frame, text=value, font=("Arial", 24, "bold")).pack(anchor="w", padx=10, pady=(0, 10))

    # ========== LOAD ORDERS ==========
    def load_orders(self):
        # SAMPLE DATA (replace later with database)
        orders = [
            {"id": "1001", "customer": "John Doe", "total": "$45.00", "status": "Completed"},
            {"id": "1002", "customer": "Maria Lopez", "total": "$120.00", "status": "Pending"},
            {"id": "1003", "customer": "Carlos Ruiz", "total": "$75.00", "status": "Completed"},
            {"id": "1004", "customer": "Ana Torres", "total": "$33.00", "status": "Pending"},
        ]

        for order in orders:
            row = ctk.CTkFrame(self.orders_table)
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(row, text=f"#{order['id']}", width=80).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=order["customer"], width=150).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=order["total"], width=100).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=order["status"], width=100).pack(side="left", padx=5)

            ctk.CTkButton(row, text="View", width=60, command=lambda o=order: self.view_order(o)).pack(side="right", padx=5)

    # ========== VIEW ORDER ==========
    def view_order(self, order):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Order #{order['id']}")
        popup.geometry("400x300")

        ctk.CTkLabel(popup, text=f"Order ID: {order['id']}").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Customer: {order['customer']}").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Total: {order['total']}").pack(pady=5)
        ctk.CTkLabel(popup, text=f"Status: {order['status']}").pack(pady=5)

        ctk.CTkButton(popup, text="Print Receipt").pack(pady=20)

    def open_inventory(self):
        self.destroy()
        import os
        os.system("python admin_dashboard_ui.py")

if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()