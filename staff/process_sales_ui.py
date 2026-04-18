import os
import sqlite3
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from shared.inventory_utils import ensure_inventory_transaction_schema, sell_inventory, validate_cart_stock
from shared.image_utils import product_image_name
from shared.paths import DB_PATH, RECEIPTS_DIR
from shared.session_utils import get_current_user, load_all_orders, save_all_orders
from staff.sidebar_ui import EmployeeSidebar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class ProcessSalesUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Process Sale")
        self.controller.geometry("1320x760")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        ensure_inventory_transaction_schema(self.cursor)
        self.conn.commit()

        self.sale_cart = {}
        self.current_user = get_current_user()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = EmployeeSidebar(self, self.controller, "sales")

        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=3)
        self.main.grid_columnconfigure(1, weight=2)
        self.main.grid_rowconfigure(1, weight=1)

        self.build_header()
        self.build_product_panel()
        self.build_sale_panel()
        self.load_products()

    def build_header(self):
        header = ctk.CTkFrame(self.main)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=(15, 8))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Process Sale",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, padx=15, pady=12, sticky="w")

        self.search_entry = ctk.CTkEntry(header, placeholder_text="Search item name or ID...")
        self.search_entry.grid(row=0, column=1, padx=10, pady=12, sticky="ew")
        self.search_entry.bind("<Return>", lambda event: self.load_products())

        ctk.CTkButton(
            header,
            text="Search",
            width=90,
            command=self.load_products
        ).grid(row=0, column=2, padx=5, pady=12)

        ctk.CTkButton(
            header,
            text="Reset",
            width=90,
            command=self.reset_search
        ).grid(row=0, column=3, padx=(5, 15), pady=12)

    def build_product_panel(self):
        product_panel = ctk.CTkFrame(self.main)
        product_panel.grid(row=1, column=0, sticky="nsew", padx=(15, 8), pady=(0, 15))
        product_panel.grid_columnconfigure(0, weight=1)
        product_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            product_panel,
            text="Available Inventory",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

        self.product_list = ctk.CTkScrollableFrame(product_panel)
        self.product_list.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.product_list.grid_columnconfigure(0, weight=1)

    def build_sale_panel(self):
        sale_panel = ctk.CTkFrame(self.main)
        sale_panel.grid(row=1, column=1, sticky="nsew", padx=(8, 15), pady=(0, 15))
        sale_panel.grid_columnconfigure(0, weight=1)
        sale_panel.grid_rowconfigure(7, weight=1)

        ctk.CTkLabel(
            sale_panel,
            text="Customer Transaction",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

        self.customer_name = ctk.CTkEntry(sale_panel, placeholder_text="Customer name")
        self.customer_name.grid(row=1, column=0, sticky="ew", padx=15, pady=6)

        self.customer_phone = ctk.CTkEntry(sale_panel, placeholder_text="Phone number")
        self.customer_phone.grid(row=2, column=0, sticky="ew", padx=15, pady=6)

        self.customer_email = ctk.CTkEntry(sale_panel, placeholder_text="Email optional")
        self.customer_email.grid(row=3, column=0, sticky="ew", padx=15, pady=6)

        self.payment_method = ctk.CTkOptionMenu(
            sale_panel,
            values=["Cash", "Credit Card", "Debit Card", "GCash"]
        )
        self.payment_method.grid(row=4, column=0, sticky="w", padx=15, pady=6)
        self.payment_method.set("Cash")

        self.notes = ctk.CTkTextbox(sale_panel, height=70)
        self.notes.grid(row=5, column=0, sticky="ew", padx=15, pady=6)
        self.notes.insert("1.0", "Transaction notes")

        ctk.CTkLabel(
            sale_panel,
            text="Sale Items",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=6, column=0, sticky="w", padx=15, pady=(12, 4))

        self.cart_list = ctk.CTkScrollableFrame(sale_panel)
        self.cart_list.grid(row=7, column=0, sticky="nsew", padx=15, pady=6)
        self.cart_list.grid_columnconfigure(0, weight=1)

        self.total_label = ctk.CTkLabel(sale_panel, text="Total: $0.00", font=ctk.CTkFont(size=18, weight="bold"))
        self.total_label.grid(row=8, column=0, sticky="w", padx=15, pady=(8, 4))

        self.status_label = ctk.CTkLabel(sale_panel, text="", text_color="#7ddc7a", wraplength=430, justify="left")
        self.status_label.grid(row=9, column=0, sticky="w", padx=15, pady=4)

        ctk.CTkButton(
            sale_panel,
            text="Complete Sale",
            height=42,
            command=self.complete_sale
        ).grid(row=10, column=0, sticky="ew", padx=15, pady=(8, 15))

    def reset_search(self):
        self.search_entry.delete(0, "end")
        self.load_products()

    def load_products(self):
        for widget in self.product_list.winfo_children():
            widget.destroy()

        query = self.search_entry.get().strip()
        if query.upper().startswith("ID-"):
            query = query[3:]

        if query:
            self.cursor.execute(
                """
                SELECT id, name, price, stock, status, category
                FROM inventory
                WHERE name LIKE ? OR CAST(id AS TEXT) LIKE ?
                ORDER BY name
                """,
                (f"%{query}%", f"%{query}%")
            )
        else:
            self.cursor.execute(
                """
                SELECT id, name, price, stock, status, category
                FROM inventory
                ORDER BY name
                """
            )

        products = self.cursor.fetchall()
        if not products:
            ctk.CTkLabel(
                self.product_list,
                text="No matching inventory items.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            return

        for row_index, product in enumerate(products):
            self.create_product_row(row_index, product)

    def create_product_row(self, row_index, product):
        item_id, name, price, stock, status, category = product
        row = ctk.CTkFrame(self.product_list)
        row.grid(row=row_index, column=0, sticky="ew", pady=4)
        row.grid_columnconfigure(0, weight=1)

        info = ctk.CTkFrame(row, fg_color="transparent")
        info.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info,
            text=f"ID-{item_id}  {name}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            info,
            text=f"${price:.2f} | Stock: {stock} | {status} | {category}",
            text_color="gray"
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        qty_entry = ctk.CTkEntry(row, width=70)
        qty_entry.insert(0, "1")
        qty_entry.grid(row=0, column=1, padx=8, pady=8)

        ctk.CTkButton(
            row,
            text="Add",
            width=70,
            state="normal" if stock > 0 else "disabled",
            command=lambda p=product, q=qty_entry: self.add_to_sale(p, q)
        ).grid(row=0, column=2, padx=(0, 10), pady=8)

    def add_to_sale(self, product, qty_entry):
        item_id, name, price, stock, status, category = product
        try:
            quantity = int(qty_entry.get())
        except ValueError:
            self.status_label.configure(text="Enter a valid quantity.")
            return

        if quantity <= 0:
            self.status_label.configure(text="Quantity must be greater than zero.")
            return

        current_quantity = self.sale_cart.get(item_id, {}).get("qty", 0)
        if current_quantity + quantity > stock:
            self.status_label.configure(text=f"Only {stock} available for {name}.")
            return

        self.sale_cart[item_id] = {
            "id": item_id,
            "name": name,
            "price": price,
            "qty": current_quantity + quantity,
            "image": product_image_name(name),
        }
        self.render_cart()
        self.status_label.configure(text=f"Added {quantity} {name}.")

    def render_cart(self):
        for widget in self.cart_list.winfo_children():
            widget.destroy()

        if not self.sale_cart:
            ctk.CTkLabel(
                self.cart_list,
                text="No items added yet.",
                text_color="gray"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            self.total_label.configure(text="Total: $0.00")
            return

        for row_index, item in enumerate(self.sale_cart.values()):
            row = ctk.CTkFrame(self.cart_list)
            row.grid(row=row_index, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=item["name"],
                font=ctk.CTkFont(weight="bold")
            ).grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                row,
                text=f"Qty: {item['qty']} | ${item['price']:.2f} each",
                text_color="gray"
            ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

            ctk.CTkButton(
                row,
                text="Remove",
                width=80,
                fg_color="#8b0000",
                hover_color="#a00000",
                command=lambda item_id=item["id"]: self.remove_from_sale(item_id)
            ).grid(row=0, column=1, rowspan=2, padx=10, pady=8)

        self.total_label.configure(text=f"Total: ${self.calculate_total():.2f}")

    def remove_from_sale(self, item_id):
        self.sale_cart.pop(item_id, None)
        self.render_cart()

    def calculate_total(self):
        return sum(item["price"] * item["qty"] for item in self.sale_cart.values())

    def complete_sale(self):
        if not self.sale_cart:
            self.status_label.configure(text="Add at least one item before completing the sale.")
            return

        if not self.customer_name.get().strip():
            self.status_label.configure(text="Enter the customer name.")
            return

        shortages = validate_cart_stock(self.cursor, self.sale_cart)
        if shortages:
            self.status_label.configure(text="Not enough stock for: " + "; ".join(shortages))
            self.load_products()
            return

        orders = load_all_orders()
        purchase_id = f"STAFF-{1000 + len(orders) + 1}"
        subtotal = self.calculate_total()
        tax = round(subtotal * 0.07, 2)
        total = subtotal + tax
        employee_name = self.current_user.get("name", "Employee")

        order_record = {
            "purchase_id": purchase_id,
            "status": "Completed",
            "date": datetime.now().strftime("%B %d, %Y"),
            "processed_by": employee_name,
            "customer": {
                "full_name": self.customer_name.get().strip(),
                "phone": self.customer_phone.get().strip(),
                "email": self.customer_email.get().strip(),
                "city": "",
                "address": "In-store sale",
                "payment_method": self.payment_method.get(),
                "card_name": "",
                "username": "",
            },
            "notes": self.notes.get("1.0", "end").strip(),
            "items": list(self.sale_cart.values()),
            "summary": {
                "subtotal": subtotal,
                "tax": tax,
                "total": total,
            },
        }

        try:
            for item in self.sale_cart.values():
                sell_inventory(self.cursor, item["id"], item["qty"], purchase_id)
            self.conn.commit()
        except ValueError as error:
            self.conn.rollback()
            self.status_label.configure(text=str(error))
            self.load_products()
            return

        orders.append(order_record)
        save_all_orders(orders)
        receipt_text = self.build_receipt_text(order_record)
        receipt_path = self.save_receipt(order_record, receipt_text)

        self.sale_cart = {}
        self.render_cart()
        self.clear_customer_fields()
        self.load_products()
        self.show_receipt_preview(order_record, receipt_text, receipt_path)

    def build_receipt_text(self, order):
        customer = order.get("customer", {})
        summary = order.get("summary", {})
        purchase_id = order.get("purchase_id", "N/A")

        lines = [
            "Sales Receipt",
            f"Purchase ID: {purchase_id}",
            f"Date: {order.get('date', 'N/A')}",
            f"Status: {order.get('status', 'N/A')}",
            f"Processed By: {order.get('processed_by', 'Employee')}",
            "",
            f"Customer: {customer.get('full_name', 'N/A')}",
            f"Phone: {customer.get('phone', 'N/A')}",
            f"Email: {customer.get('email', 'N/A')}",
            f"Payment Method: {customer.get('payment_method', 'N/A')}",
            "",
            "Items:",
        ]

        for item in order.get("items", []):
            qty = item.get("qty", 0)
            price = item.get("price", 0)
            lines.append(
                f"- {item.get('name', 'Item')} | Qty: {qty} | Price: ${price:.2f} | Line Total: ${qty * price:.2f}"
            )

        lines.extend([
            "",
            f"Subtotal: ${summary.get('subtotal', 0):.2f}",
            f"Tax: ${summary.get('tax', 0):.2f}",
            f"Total: ${summary.get('total', 0):.2f}",
            "",
            f"Notes: {order.get('notes', 'None')}",
        ])

        return "\n".join(lines)

    def save_receipt(self, order, receipt_text=None):
        os.makedirs(RECEIPTS_DIR, exist_ok=True)

        purchase_id = order.get("purchase_id", "unknown")
        path = os.path.join(RECEIPTS_DIR, f"{purchase_id}_receipt.txt")
        if receipt_text is None:
            receipt_text = self.build_receipt_text(order)

        with open(path, "w", encoding="utf-8") as receipt_file:
            receipt_file.write(receipt_text)

        return path

    def show_receipt_preview(self, order, receipt_text, receipt_path):
        preview = ctk.CTkToplevel(self)
        preview.title(f"Receipt {order.get('purchase_id', '')}")
        preview.geometry("620x700")
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            preview,
            text="Receipt Preview",
            font=ctk.CTkFont(size=24, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 10))

        receipt_box = ctk.CTkTextbox(preview, font=ctk.CTkFont(family="Consolas", size=13))
        receipt_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        receipt_box.insert("1.0", receipt_text)
        receipt_box.configure(state="disabled")

        button_bar = ctk.CTkFrame(preview, fg_color="transparent")
        button_bar.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        button_bar.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            button_bar,
            text="Print Receipt",
            command=lambda: self.print_receipt(receipt_path)
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            button_bar,
            text="Save Receipt",
            command=lambda: messagebox.showinfo("Receipt Saved", f"Receipt saved to:\n{receipt_path}")
        ).grid(row=0, column=1, padx=6, sticky="ew")

        ctk.CTkButton(
            button_bar,
            text="Cancel",
            fg_color="gray",
            hover_color="#555555",
            command=preview.destroy
        ).grid(row=0, column=2, padx=(6, 0), sticky="ew")

    def print_receipt(self, receipt_path):
        try:
            if os.name == "nt":
                os.startfile(receipt_path, "print")
            else:
                raise OSError("Printing is not configured for this operating system.")
        except OSError:
            messagebox.showerror("Printer", "Printer not available.")
            return

        messagebox.showinfo("Print Receipt", "Receipt sent to printer.")

    def clear_customer_fields(self):
        self.customer_name.delete(0, "end")
        self.customer_phone.delete(0, "end")
        self.customer_email.delete(0, "end")
        self.payment_method.set("Cash")
        self.notes.delete("1.0", "end")
        self.notes.insert("1.0", "Transaction notes")
        self.status_label.configure(text="")

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("sales")
