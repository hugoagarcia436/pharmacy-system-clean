import customtkinter as ctk
import json
import os
from datetime import datetime
from shared.paths import ORDERS_FILE
from staff.employees_ui import EmployeesUI
from staff.inventory_ui import InventoryUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Employee Dashboard")
        self.controller.geometry("1200x700")

        # ========== LAYOUT ==========
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # ========== SIDEBAR ==========
        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="EMPLOYEE", font=("Arial", 20, "bold")).pack(pady=(28, 28))

        self.create_sidebar_button("Dashboard", active=True)
        self.create_sidebar_button("Inventory", self.open_inventory)
        self.create_sidebar_button("Orders", self.open_orders)
        self.create_sidebar_button("Employees", self.open_employees)
        self.create_sidebar_button("History", self.open_history)

        # ========== MAIN AREA ==========
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)

        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # ========== TOP STATS ==========
        stats = self.load_order_stats()
        self.create_stat_card("Total Orders", str(stats["total_orders"]), 0, 0)
        self.create_stat_card("Pending Orders", str(stats["pending_orders"]), 0, 1)
        self.create_stat_card("Revenue", f"${stats['revenue']:.2f}", 1, 0)
        self.create_stat_card("Delivered Orders", str(stats["delivered_orders"]), 1, 1)

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

    def create_sidebar_button(self, text, command=None, active=False):
        ctk.CTkButton(
            self.sidebar,
            text=text,
            height=42,
            fg_color=ACTIVE_BUTTON if active else BUTTON_COLOR,
            hover_color=BUTTON_HOVER,
            corner_radius=8,
            command=command
        ).pack(fill="x", padx=18, pady=8)

    # ========== LOAD ORDERS ==========
    def load_orders(self):
        orders = self.read_customer_orders()[:6]

        if not orders:
            ctk.CTkLabel(self.orders_table, text="No customer orders found.", text_color="gray").pack(anchor="w", padx=10, pady=10)
            return

        for order in orders:
            row = ctk.CTkFrame(self.orders_table)
            row.pack(fill="x", pady=5)

            ctk.CTkLabel(row, text=order.get("purchase_id", "N/A"), width=110).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=order.get("customer", {}).get("full_name", "Unknown"), width=180).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"${order.get('summary', {}).get('total', 0):.2f}", width=100).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=order.get("status", "N/A"), width=100).pack(side="left", padx=5)

            ctk.CTkButton(
                row,
                text="View",
                width=60,
                command=lambda o=order: self.view_order(o)
            ).pack(side="right", padx=5)

    def read_customer_orders(self):
        if not os.path.exists(ORDERS_FILE):
            return []
        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as orders_file:
                orders = json.load(orders_file)
        except (json.JSONDecodeError, OSError):
            return []
        return sorted(orders, key=lambda order: order.get("purchase_id", ""), reverse=True)

    def load_order_stats(self):
        orders = self.read_customer_orders()
        return {
            "total_orders": len(orders),
            "pending_orders": sum(1 for order in orders if order.get("status") == "Processing"),
            "delivered_orders": sum(1 for order in orders if order.get("status") == "Delivered"),
            "revenue": sum(order.get("summary", {}).get("total", 0) for order in orders),
        }

    # ========== VIEW ORDER ==========
    def view_order(self, order):
        popup = ctk.CTkToplevel(self)
        popup.title(order.get("purchase_id", "Order"))
        popup.geometry("480x420")

        customer = order.get("customer", {})
        summary = order.get("summary", {})

        details = [
            f"Purchase ID: {order.get('purchase_id', 'N/A')}",
            f"Customer: {customer.get('full_name', 'Unknown')}",
            f"Date: {order.get('date', 'N/A')}",
            f"Payment Method: {customer.get('payment_method', 'N/A')}",
            f"Status: {order.get('status', 'N/A')}",
            f"Total: ${summary.get('total', 0):.2f}",
        ]

        for line in details:
            ctk.CTkLabel(popup, text=line).pack(anchor="w", padx=20, pady=6)

        ctk.CTkLabel(popup, text="Items", font=("Arial", 16, "bold")).pack(anchor="w", padx=20, pady=(14, 6))
        for item in order.get("items", []):
            ctk.CTkLabel(
                popup,
                text=f"{item.get('name', 'Item')} x{item.get('qty', 0)}  ${item.get('price', 0):.2f}"
            ).pack(anchor="w", padx=20, pady=3)

    # ========== NAVIGATION ==========
  
  
    def open_inventory(self):
        self.controller.show_page("inventory")
  
  
    def open_orders(self):
        self.controller.show_page("orders")

    def open_employees(self):
        self.controller.show_page("employees")
              
    def open_history(self):
        self.controller.show_page("history")


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("dashboard")
