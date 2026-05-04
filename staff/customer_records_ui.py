import sqlite3
import os

import customtkinter as ctk

from shared.paths import DB_PATH, RECEIPTS_DIR
from shared.session_utils import load_all_orders
from staff.sidebar_ui import EmployeeSidebar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

MULTIPLE_RECORD_WARNING_LIMIT = 5


class CustomerRecordsUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Customer Records")
        self.controller.geometry("1320x760")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.orders = load_all_orders()
        self.customers = self.load_customer_records()
        self.filtered_customers = self.customers[:]
        self.selected_customer = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = EmployeeSidebar(self, self.controller, "customers")

        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_columnconfigure(1, weight=2)
        self.main.grid_rowconfigure(1, weight=1)

        self.build_header()
        self.build_customer_list()
        self.build_detail_panel()
        self.render_customer_list()
        self.render_customer_detail()

    def load_customer_records(self):
        records = {}

        try:
            self.cursor.execute("""
                SELECT name, email, username
                FROM users
                WHERE role='customer'
                ORDER BY name
            """)
            for name, email, username in self.cursor.fetchall():
                key = self.record_key(username, email, name)
                records[key] = {
                    "customer_id": username or email or name,
                    "name": name or "Unknown",
                    "email": email or "",
                    "username": username or "",
                    "phone": "",
                    "city": "",
                    "address": "",
                    "orders": [],
                }
        except sqlite3.Error:
            pass

        for order in self.orders:
            customer = order.get("customer", {})
            name = customer.get("full_name", "Unknown")
            email = customer.get("email", "")
            username = customer.get("username", "")
            key = self.record_key(username, email, name)

            if key not in records:
                records[key] = {
                    "customer_id": username or email or name,
                    "name": name,
                    "email": email,
                    "username": username,
                    "phone": "",
                    "city": "",
                    "address": "",
                    "orders": [],
                }

            record = records[key]
            record["customer_id"] = record.get("customer_id") or username or email or name
            record["name"] = record["name"] or name
            record["email"] = record["email"] or email
            record["username"] = record["username"] or username
            record["phone"] = customer.get("phone", "") or record["phone"]
            record["city"] = customer.get("city", "") or record["city"]
            record["address"] = customer.get("address", "") or record["address"]
            record["orders"].append(order)

        return sorted(records.values(), key=lambda record: record["name"].lower())

    def record_key(self, username, email, name):
        if username:
            return f"username:{username.lower()}"
        if email:
            return f"email:{email.lower()}"
        return f"name:{name.lower()}"

    def build_header(self):
        header = ctk.CTkFrame(self.main)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 8))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Customer Records",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=12)

        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search name, email, or customer ID...")
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=12)
        self.search_entry.bind("<KeyRelease>", lambda event: self.search_customers())

        ctk.CTkButton(
            header,
            text="Reset",
            width=90,
            command=self.reset_search
        ).grid(row=0, column=2, padx=(5, 15), pady=12)

    def build_customer_list(self):
        self.list_panel = ctk.CTkFrame(self.main)
        self.list_panel.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=(0, 15))
        self.list_panel.grid_columnconfigure(0, weight=1)
        self.list_panel.grid_rowconfigure(1, weight=1)

        self.list_count_label = ctk.CTkLabel(
            self.list_panel,
            text="Customers",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.list_count_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

        self.customer_list = ctk.CTkScrollableFrame(self.list_panel)
        self.customer_list.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.customer_list.grid_columnconfigure(0, weight=1)

        self.search_message_label = ctk.CTkLabel(self.list_panel, text="", text_color="#ffb300", wraplength=420, justify="left")
        self.search_message_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 12))

    def build_detail_panel(self):
        self.detail_panel = ctk.CTkFrame(self.main)
        self.detail_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 15), pady=(0, 15))
        self.detail_panel.grid_columnconfigure(0, weight=1)
        self.detail_panel.grid_rowconfigure(1, weight=1)

    def search_customers(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.filtered_customers = self.customers[:]
        else:
            self.filtered_customers = [
                customer for customer in self.customers
                if query in customer.get("name", "").lower()
                or query in customer.get("email", "").lower()
                or query in customer.get("phone", "").lower()
                or query in customer.get("username", "").lower()
                or query in customer.get("customer_id", "").lower()
            ]
        self.render_customer_list()

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.filtered_customers = self.customers[:]
        self.render_customer_list()

    def render_customer_list(self):
        for widget in self.customer_list.winfo_children():
            widget.destroy()

        self.list_count_label.configure(text=f"Customers ({len(self.filtered_customers)})")
        self.search_message_label.configure(text="")

        if not self.filtered_customers:
            ctk.CTkLabel(
                self.customer_list,
                text="Customer record not found.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            return

        query = self.search_entry.get().strip()
        if query and len(self.filtered_customers) > MULTIPLE_RECORD_WARNING_LIMIT:
            self.search_message_label.configure(
                text="Multiple customer records found. Please refine your search."
            )

        for row_index, customer in enumerate(self.filtered_customers):
            self.create_customer_card(row_index, customer)

    def create_customer_card(self, row_index, customer):
        card = ctk.CTkFrame(self.customer_list)
        card.grid(row=row_index, column=0, sticky="ew", pady=5)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=customer.get("name", "Unknown"),
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        contact = customer.get("email") or customer.get("phone") or "No contact saved"
        ctk.CTkLabel(
            card,
            text=f"Customer ID: {customer.get('customer_id', 'N/A')} | {contact}",
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", padx=12, pady=2)

        ctk.CTkLabel(
            card,
            text=f"Purchases: {len(customer.get('orders', []))}",
            text_color="#7ddc7a"
        ).grid(row=2, column=0, sticky="w", padx=12, pady=(2, 10))

        ctk.CTkButton(
            card,
            text="View",
            width=80,
            command=lambda selected=customer: self.select_customer(selected)
        ).grid(row=0, column=1, rowspan=3, padx=12, pady=10)

    def select_customer(self, customer):
        self.selected_customer = customer
        self.render_customer_detail()

    def render_customer_detail(self):
        for widget in self.detail_panel.winfo_children():
            widget.destroy()

        if self.selected_customer is None:
            ctk.CTkLabel(
                self.detail_panel,
                text="Select a customer to view their details.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=20, pady=20)
            return

        customer = self.selected_customer
        orders = sorted(customer.get("orders", []), key=lambda order: order.get("purchase_id", ""), reverse=True)

        ctk.CTkLabel(
            self.detail_panel,
            text=customer.get("name", "Unknown"),
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        body = ctk.CTkScrollableFrame(self.detail_panel)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(0, weight=1)

        self.add_detail_label(body, 0, f"Customer ID: {customer.get('customer_id') or 'N/A'}")
        self.add_detail_label(body, 1, f"Username: {customer.get('username') or 'N/A'}")
        self.add_detail_label(body, 2, f"Email: {customer.get('email') or 'N/A'}")
        self.add_detail_label(body, 3, f"Phone: {customer.get('phone') or 'N/A'}")
        self.add_detail_label(body, 4, f"City: {customer.get('city') or 'N/A'}")
        self.add_detail_label(body, 5, f"Address: {customer.get('address') or 'N/A'}")
        self.add_detail_label(body, 6, f"Total Purchases: {len(orders)}")
        self.add_detail_label(body, 7, f"Total Spent: ${self.customer_total_spent(orders):.2f}")

        receipt_row = 8
        ctk.CTkLabel(
            body,
            text="Saved Receipts",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=receipt_row, column=0, sticky="w", padx=10, pady=(10, 8))

        saved_receipts = self.saved_receipts_for_orders(orders)
        if saved_receipts:
            for offset, (order, receipt_path) in enumerate(saved_receipts, start=1):
                self.create_receipt_card(body, receipt_row + offset, order, receipt_path)
            purchase_start_row = receipt_row + len(saved_receipts) + 1
        else:
            ctk.CTkLabel(
                body,
                text="No saved receipts found for this customer.",
                text_color="gray"
            ).grid(row=receipt_row + 1, column=0, sticky="w", padx=10, pady=8)
            purchase_start_row = receipt_row + 2

        ctk.CTkLabel(
            body,
            text="Purchase History",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=purchase_start_row, column=0, sticky="w", padx=10, pady=(18, 8))

        if not orders:
            ctk.CTkLabel(
                body,
                text="No purchase history found.",
                text_color="gray"
            ).grid(row=purchase_start_row + 1, column=0, sticky="w", padx=10, pady=8)
            return

        for index, order in enumerate(orders, start=purchase_start_row + 1):
            self.create_order_card(body, index, order)

    def add_detail_label(self, parent, row, text):
        ctk.CTkLabel(parent, text=text, anchor="w", wraplength=700, justify="left").grid(
            row=row,
            column=0,
            sticky="w",
            padx=10,
            pady=3,
        )

    def create_order_card(self, parent, row, order):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text=f"{order.get('purchase_id', 'N/A')} | {order.get('date', 'N/A')}",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 3))

        items_text = ", ".join(item.get("name", "Item") for item in order.get("items", []))
        ctk.CTkLabel(
            card,
            text=f"Status: {order.get('status', 'N/A')} | Total: ${order.get('summary', {}).get('total', 0):.2f}",
            text_color="#7ddc7a"
        ).grid(row=1, column=0, sticky="w", padx=12, pady=3)

        ctk.CTkLabel(
            card,
            text=f"Items: {items_text or 'N/A'}",
            text_color="gray",
            wraplength=640,
            justify="left"
        ).grid(row=2, column=0, sticky="w", padx=12, pady=(3, 10))

        ctk.CTkButton(
            card,
            text="Open",
            width=80,
            command=lambda current_order=order: self.show_order_detail(current_order)
        ).grid(row=0, column=1, rowspan=3, padx=12, pady=10)

    def saved_receipts_for_orders(self, orders):
        receipts = []
        for order in orders:
            for receipt_path in self.receipt_paths_for_order(order):
                if os.path.exists(receipt_path):
                    receipts.append((order, receipt_path))
        return receipts

    def receipt_paths_for_order(self, order):
        purchase_id = order.get("purchase_id")
        if not purchase_id:
            return []

        filenames = [
            f"{purchase_id}_receipt.txt",
            f"{purchase_id}_verification.txt",
        ]
        return [os.path.join(RECEIPTS_DIR, filename) for filename in filenames]

    def create_receipt_card(self, parent, row, order, receipt_path):
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=6)
        card.grid_columnconfigure(0, weight=1)

        purchase_id = order.get("purchase_id", "N/A")
        ctk.CTkLabel(
            card,
            text=f"{purchase_id} | {os.path.basename(receipt_path)}",
            font=ctk.CTkFont(size=15, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 3))

        ctk.CTkLabel(
            card,
            text=f"Date: {order.get('date', 'N/A')} | Total: ${order.get('summary', {}).get('total', 0):.2f}",
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(3, 10))

        ctk.CTkButton(
            card,
            text="View Receipt",
            width=110,
            command=lambda current_path=receipt_path, current_order=order: self.show_saved_receipt(current_path, current_order)
        ).grid(row=0, column=1, rowspan=2, padx=12, pady=10)

    def show_saved_receipt(self, receipt_path, order):
        receipt_window = ctk.CTkToplevel(self)
        receipt_window.title(f"Receipt {order.get('purchase_id', '')}")
        receipt_window.geometry("640x700")
        receipt_window.grid_columnconfigure(0, weight=1)
        receipt_window.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            receipt_window,
            text=f"Saved Receipt: {order.get('purchase_id', 'N/A')}",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        receipt_box = ctk.CTkTextbox(receipt_window, font=ctk.CTkFont(family="Consolas", size=13))
        receipt_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))

        try:
            with open(receipt_path, "r", encoding="utf-8") as receipt_file:
                receipt_text = receipt_file.read()
        except OSError:
            receipt_text = "Unable to retrieve saved receipt."

        receipt_box.insert("1.0", receipt_text)
        receipt_box.configure(state="disabled")

        ctk.CTkButton(
            receipt_window,
            text="Close",
            command=receipt_window.destroy
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

    def show_order_detail(self, order):
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(order.get("purchase_id", "Order"))
        detail_window.geometry("800x760")
        detail_window.grid_columnconfigure(0, weight=1)
        detail_window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(detail_window)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Pharmacy+",
            font=ctk.CTkFont(size=28, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 2))

        ctk.CTkLabel(
            header,
            text="Customer Receipt",
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 12))

        body = ctk.CTkScrollableFrame(detail_window)
        body.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        body.grid_columnconfigure(0, weight=1)

        customer = order.get("customer", {})
        summary = order.get("summary", {})

        receipt_meta = ctk.CTkFrame(body, corner_radius=10)
        receipt_meta.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        receipt_meta.grid_columnconfigure(0, weight=1)
        receipt_meta.grid_columnconfigure(1, weight=1)

        self.add_receipt_pair(receipt_meta, 0, 0, "Receipt No.", order.get("purchase_id", "N/A"))
        self.add_receipt_pair(receipt_meta, 1, 0, "Date", order.get("date", "N/A"))
        self.add_receipt_pair(receipt_meta, 0, 1, "Status", order.get("status", "N/A"))
        self.add_receipt_pair(receipt_meta, 1, 1, "Processed By", order.get("processed_by", "Online checkout"))

        details = ctk.CTkFrame(body, corner_radius=10)
        details.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
        details.grid_columnconfigure(0, weight=1)
        details.grid_columnconfigure(1, weight=1)

        customer_block = ctk.CTkFrame(details, fg_color="transparent")
        customer_block.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)
        customer_block.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(customer_block, text="Customer", font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.add_block_line(customer_block, 1, customer.get("full_name", "N/A"))
        self.add_block_line(customer_block, 2, f"Phone: {customer.get('phone') or 'N/A'}")
        self.add_block_line(customer_block, 3, f"Email: {customer.get('email') or 'N/A'}")
        self.add_block_line(customer_block, 4, f"Address: {customer.get('address') or 'N/A'}")

        payment_block = ctk.CTkFrame(details, fg_color="transparent")
        payment_block.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)
        payment_block.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(payment_block, text="Payment", font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 8)
        )
        self.add_block_line(payment_block, 1, f"Method: {customer.get('payment_method') or 'N/A'}")
        self.add_block_line(payment_block, 2, f"Card Name: {customer.get('card_name') or 'N/A'}")
        self.add_block_line(payment_block, 3, f"Notes: {order.get('notes') or 'None'}")

        items_card = ctk.CTkFrame(body, corner_radius=10)
        items_card.grid(row=2, column=0, sticky="ew", padx=10, pady=8)
        items_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(items_card, text="Items Purchased", font=ctk.CTkFont(size=17, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 8)
        )

        table = ctk.CTkFrame(items_card, fg_color="transparent")
        table.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))
        table.grid_columnconfigure(0, weight=3)
        table.grid_columnconfigure((1, 2, 3), weight=1)

        headers = ["Item", "Qty", "Price", "Line Total"]
        for col, text in enumerate(headers):
            ctk.CTkLabel(table, text=text, font=ctk.CTkFont(weight="bold"), anchor="w").grid(
                row=0, column=col, sticky="ew", padx=6, pady=(0, 6)
            )

        for index, item in enumerate(order.get("items", []), start=1):
            qty = item.get("qty", 0)
            price = item.get("price", 0)
            line_total = qty * price
            values = [item.get("name", "Item"), str(qty), f"${price:.2f}", f"${line_total:.2f}"]
            for col, value in enumerate(values):
                ctk.CTkLabel(table, text=value, anchor="w").grid(
                    row=index,
                    column=col,
                    sticky="ew",
                    padx=6,
                    pady=4,
                )

        totals_card = ctk.CTkFrame(body, corner_radius=10)
        totals_card.grid(row=3, column=0, sticky="e", padx=10, pady=(8, 14))
        totals_card.grid_columnconfigure(0, weight=1)
        totals_card.grid_columnconfigure(1, weight=1)

        self.add_total_line(totals_card, 0, "Subtotal", summary.get("subtotal", 0))
        self.add_total_line(totals_card, 1, "Tax", summary.get("tax", 0))
        self.add_total_line(totals_card, 2, "Total", summary.get("total", 0), bold=True)

        ctk.CTkButton(
            detail_window,
            text="Close",
            command=detail_window.destroy
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))

    def add_receipt_pair(self, parent, row, column, label, value):
        holder = ctk.CTkFrame(parent, fg_color="transparent")
        holder.grid(row=row, column=column, sticky="ew", padx=14, pady=8)
        holder.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(holder, text=label, text_color="gray").grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(holder, text=value, font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w")

    def add_block_line(self, parent, row, text):
        ctk.CTkLabel(parent, text=text, wraplength=320, justify="left", anchor="w").grid(
            row=row,
            column=0,
            sticky="w",
            pady=3,
        )

    def add_total_line(self, parent, row, label, amount, bold=False):
        font = ctk.CTkFont(size=16, weight="bold") if bold else None
        ctk.CTkLabel(parent, text=f"{label}:", font=font).grid(row=row, column=0, sticky="e", padx=(18, 8), pady=5)
        ctk.CTkLabel(parent, text=f"${amount:.2f}", font=font).grid(row=row, column=1, sticky="e", padx=(8, 18), pady=5)

    def customer_total_spent(self, orders):
        return sum(order.get("summary", {}).get("total", 0) for order in orders)

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("customers")
