import customtkinter as ctk
import json
import os
import tkinter as tk
from tkinter import messagebox
from shared.paths import ORDERS_FILE, RECEIPTS_DIR

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


class AdminHistoryUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Employee Dashboard")
        self.controller.geometry("1320x760")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.column_specs = [
            ("Purchase ID", 130),
            ("Customer", 220),
            ("Payment", 140),
            ("Date", 140),
            ("Items", 120),
            ("Status", 140),
            ("Total", 120),
            ("Action", 160),
        ]

        self.sidebar = ctk.CTkFrame(self, width=240, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="EMPLOYEE", font=("Arial", 20, "bold")).pack(pady=(28, 28))

        self.create_sidebar_button("Dashboard", self.open_dashboard)
        self.create_sidebar_button("Inventory", self.open_inventory)
        self.create_sidebar_button("Orders", self.open_orders)
        self.create_sidebar_button("Employees", self.open_employees)
        self.create_sidebar_button("History", self.open_history, active=True)

        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_rowconfigure(3, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.all_orders = self.load_orders()
        self.orders = self.all_orders[:]
        self.current_page = 0
        self.rows_per_page = 6

        self.build_ui()

    def create_sidebar_button(self, text, command, active=False):
        color = ACTIVE_BUTTON if active else BUTTON_COLOR
        ctk.CTkButton(
            self.sidebar,
            text=text,
            height=42,
            fg_color=color,
            hover_color=BUTTON_HOVER,
            corner_radius=8,
            command=command
        ).pack(fill="x", padx=20, pady=8)

    def build_ui(self):
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(top_bar, text="Customer Order History", font=("Arial", 26, "bold")).pack(side="left")

        right = ctk.CTkFrame(top_bar, fg_color="transparent")
        right.pack(side="right")

        self.search_entry = ctk.CTkEntry(right, width=340, placeholder_text="Search by purchase ID or customer...")
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(right, text="Search", command=self.search_orders).pack(side="left", padx=5)
        ctk.CTkButton(right, text="Reset", command=self.reset_orders).pack(side="left", padx=5)

        self.header = ctk.CTkFrame(self.main, fg_color="#1c2d4a", height=50)
        self.header.grid(row=1, column=0, sticky="ew", padx=20)
        self.header.grid_propagate(False)
        self.build_header()

        self.scroll = ctk.CTkScrollableFrame(self.main)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        bottom = ctk.CTkFrame(self.main, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        bottom.grid_columnconfigure(0, weight=1)

        controls = ctk.CTkFrame(bottom, fg_color="transparent")
        controls.grid(row=0, column=0)

        self.prev_button = ctk.CTkButton(controls, text="Previous", width=120, command=self.prev_page)
        self.prev_button.grid(row=0, column=0, padx=8)

        self.page_label = ctk.CTkLabel(controls, text="")
        self.page_label.grid(row=0, column=1, padx=12)

        self.next_button = ctk.CTkButton(controls, text="Next", width=120, command=self.next_page)
        self.next_button.grid(row=0, column=2, padx=8)

        self.render_orders()

    def build_header(self):
        x = 0
        for col, width in self.column_specs:
            frame = ctk.CTkFrame(self.header, width=width, height=50, fg_color="transparent")
            frame.place(x=x, y=0)
            frame.pack_propagate(False)
            ctk.CTkLabel(frame, text=col, font=("Arial", 12, "bold")).pack(anchor="w", padx=10)
            x += width

    def load_orders(self):
        if not os.path.exists(ORDERS_FILE):
            return []

        try:
            with open(ORDERS_FILE, "r", encoding="utf-8") as orders_file:
                return json.load(orders_file)
        except (json.JSONDecodeError, OSError):
            return []

    def status_color(self, status):
        return "#16e06e" if status in {"Delivered", "Processing"} else "#ffb300"

    def render_orders(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not self.orders:
            ctk.CTkLabel(self.scroll, text="No customer orders found.", text_color="gray").pack(anchor="w", padx=10, pady=10)
            self.page_label.configure(text="Showing 0 of 0 orders")
            self.prev_button.configure(state="disabled")
            self.next_button.configure(state="disabled")
            return

        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page
        visible_end = min(end, len(self.orders))

        for index, order in enumerate(self.orders[start:end]):
            self.create_row(order, index)

        total_pages = (len(self.orders) - 1) // self.rows_per_page + 1
        self.page_label.configure(
            text=f"Showing {start + 1}-{visible_end} of {len(self.orders)} orders  |  Page {self.current_page + 1} of {total_pages}"
        )
        self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.configure(state="normal" if visible_end < len(self.orders) else "disabled")

    def create_row(self, order, index):
        color = "#000000" if index % 2 == 0 else "#2f2f2f"

        row = ctk.CTkFrame(self.scroll, fg_color=color, height=55)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        values = [
            order.get("purchase_id", "N/A"),
            order.get("customer", {}).get("full_name", "Unknown"),
            order.get("customer", {}).get("payment_method", "N/A"),
            order.get("date", "N/A"),
            str(sum(item.get("qty", 0) for item in order.get("items", []))),
            order.get("status", "N/A"),
            f"${order.get('summary', {}).get('total', 0):.2f}",
        ]

        x = 0
        for i, ((_, width), val) in enumerate(zip(self.column_specs[:-1], values)):
            cell = ctk.CTkFrame(row, width=width, height=55, fg_color="transparent")
            cell.place(x=x, y=0)
            cell.pack_propagate(False)

            ctk.CTkLabel(
                cell,
                text=val,
                text_color=self.status_color(val) if i == 5 else "white"
            ).pack(anchor="w", padx=10)

            x += width

        action_cell = ctk.CTkFrame(row, width=self.column_specs[-1][1], height=55, fg_color="transparent")
        action_cell.place(x=x, y=0)
        action_cell.pack_propagate(False)

        btn = ctk.CTkButton(action_cell, text="Actions", width=100)
        btn.pack(padx=10, pady=10)
        btn.configure(command=lambda current_order=order, button=btn: self.show_menu(current_order, button))

    def show_menu(self, order, button):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="View Order", command=lambda: self.show_order_detail(order))
        menu.add_command(label="Print Receipt", command=lambda: self.save_receipt(order, "receipt"))
        menu.add_command(label="Verification", command=lambda: self.save_receipt(order, "verification"))

        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        menu.tk_popup(x, y)

    def show_order_detail(self, order):
        popup = ctk.CTkToplevel(self)
        popup.title(order.get("purchase_id", "Order Detail"))
        popup.geometry("760x660")
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            popup,
            text=f"Order Detail: {order.get('purchase_id', 'N/A')}",
            font=("Arial", 24, "bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        body = ctk.CTkScrollableFrame(popup)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))

        customer = order.get("customer", {})
        summary = order.get("summary", {})

        info_lines = [
            f"Customer: {customer.get('full_name', 'N/A')}",
            f"Phone: {customer.get('phone', 'N/A')}",
            f"Email: {customer.get('email', 'N/A')}",
            f"Address: {customer.get('address', 'N/A')}",
            f"Payment Method: {customer.get('payment_method', 'N/A')}",
            f"Date: {order.get('date', 'N/A')}",
            f"Status: {order.get('status', 'N/A')}",
            f"Notes: {order.get('notes', 'None')}",
        ]

        for line in info_lines:
            ctk.CTkLabel(body, text=line, anchor="w", justify="left", wraplength=680).pack(anchor="w", padx=10, pady=4)

        ctk.CTkLabel(body, text="Items", font=("Arial", 18, "bold")).pack(anchor="w", padx=10, pady=(12, 6))

        for item in order.get("items", []):
            card = ctk.CTkFrame(body, corner_radius=10)
            card.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(card, text=item.get("name", "Item"), font=("Arial", 15, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
            ctk.CTkLabel(
                card,
                text=f"Qty: {item.get('qty', 0)} | Price: ${item.get('price', 0):.2f} | Line Total: ${item.get('qty', 0) * item.get('price', 0):.2f}",
                text_color="gray"
            ).pack(anchor="w", padx=12, pady=(0, 10))

        totals = ctk.CTkFrame(body, corner_radius=10)
        totals.pack(fill="x", padx=10, pady=(10, 15))
        ctk.CTkLabel(totals, text=f"Subtotal: ${summary.get('subtotal', 0):.2f}").pack(anchor="w", padx=12, pady=(10, 4))
        ctk.CTkLabel(totals, text=f"Tax: ${summary.get('tax', 0):.2f}").pack(anchor="w", padx=12, pady=4)
        ctk.CTkLabel(totals, text=f"Total: ${summary.get('total', 0):.2f}", font=("Arial", 16, "bold")).pack(anchor="w", padx=12, pady=(4, 10))

    def save_receipt(self, order, kind):
        os.makedirs(RECEIPTS_DIR, exist_ok=True)
        purchase_id = order.get("purchase_id", "unknown")
        filename = f"{purchase_id}_{kind}.txt"
        path = os.path.join(RECEIPTS_DIR, filename)

        customer = order.get("customer", {})
        summary = order.get("summary", {})
        lines = [
            f"{kind.title()} Document",
            f"Purchase ID: {purchase_id}",
            f"Date: {order.get('date', 'N/A')}",
            f"Status: {order.get('status', 'N/A')}",
            "",
            f"Customer: {customer.get('full_name', 'N/A')}",
            f"Phone: {customer.get('phone', 'N/A')}",
            f"Email: {customer.get('email', 'N/A')}",
            f"Address: {customer.get('address', 'N/A')}",
            f"Payment Method: {customer.get('payment_method', 'N/A')}",
            "",
            "Items:",
        ]

        for item in order.get("items", []):
            lines.append(
                f"- {item.get('name', 'Item')} | Qty: {item.get('qty', 0)} | Price: ${item.get('price', 0):.2f} | Line Total: ${item.get('qty', 0) * item.get('price', 0):.2f}"
            )

        lines.extend([
            "",
            f"Subtotal: ${summary.get('subtotal', 0):.2f}",
            f"Tax: ${summary.get('tax', 0):.2f}",
            f"Total: ${summary.get('total', 0):.2f}",
            "",
            f"Notes: {order.get('notes', 'None')}",
        ])

        with open(path, "w", encoding="utf-8") as receipt_file:
            receipt_file.write("\n".join(lines))

        messagebox.showinfo("Saved", f"{kind.title()} saved to:\n{path}")

    def search_orders(self):
        query = self.search_entry.get().strip().lower()
        self.orders = [
            order for order in self.all_orders
            if query in order.get("purchase_id", "").lower()
            or query in order.get("customer", {}).get("full_name", "").lower()
        ]
        self.current_page = 0
        self.render_orders()

    def reset_orders(self):
        self.orders = self.all_orders[:]
        self.current_page = 0
        self.render_orders()

    def next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.orders):
            self.current_page += 1
            self.render_orders()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_orders()

    def open_dashboard(self):
        self.controller.show_page("dashboard")

    def open_orders(self):
        self.controller.show_page("orders")

    def open_inventory(self):
        self.controller.show_page("inventory")

    def open_employees(self):
        self.controller.show_page("employees")

    def open_history(self):
        pass


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("history")
