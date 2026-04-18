import customtkinter as ctk
from datetime import datetime
import sqlite3
from tkinter import messagebox
from catalog.category_utils import (
    CATEGORY_DISPLAY_NAMES,
    INVENTORY_CATEGORIES,
    repair_inventory_categories,
)
from shared.inventory_utils import set_inventory_stock
from shared.paths import DB_PATH
from staff.sidebar_ui import EmployeeSidebar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class InventoryUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Employee Dashboard")
        self.controller.geometry("1200x700")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        repair_inventory_categories(self.cursor)
        self.conn.commit()

        self.current_page = 1
        self.items_per_page = 25

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = EmployeeSidebar(self, self.controller, "inventory")

        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew")

        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(main)
        topbar.grid(row=0, column=0, sticky="ew", padx=15, pady=8)

        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(topbar, text="View Inventory",
                     font=ctk.CTkFont(size=20, weight="bold"))\
            .grid(row=0, column=0, padx=15, sticky="w")

        ctk.CTkLabel(topbar, text="Employee").grid(row=0, column=1, padx=15)

        self.frame = ctk.CTkFrame(main)
        self.frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=8)

        self.frame.grid_columnconfigure(0, weight=1)

        self.expanded_row = None

        self.setup_inventory()

    def setup_inventory(self):
        frame = self.frame

        top_bar = ctk.CTkFrame(frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(top_bar, placeholder_text="Search inventory...", width=220)
        self.search_entry.grid(row=0, column=1, padx=8, pady=6, sticky="e")

        # trigger search when pressing Enter
        self.search_entry.bind("<Return>", self.search_inventory)
        self.search_entry.bind("<KeyRelease>", self.search_inventory)

        self.table = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            height=450
        )
        self.table.grid(row=1, column=0, sticky="nsew")

        headers = ["Item ID", "Item Name", "Stock", "Price", "Updated", "Status"]

        header_row = ctk.CTkFrame(self.table, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=6, sticky="ew")

        # SAME structure as create_row()
        header_row.grid_columnconfigure(0, weight=1, minsize=100)
        header_row.grid_columnconfigure(1, weight=2, minsize=180)
        header_row.grid_columnconfigure(2, weight=1, minsize=80)
        header_row.grid_columnconfigure(3, weight=1, minsize=80)
        header_row.grid_columnconfigure(4, weight=1, minsize=120)
        header_row.grid_columnconfigure(5, weight=1, minsize=100)

        for col, h in enumerate(headers):
            ctk.CTkLabel(
                header_row,
                text=h,
                font=ctk.CTkFont(weight="bold", size=12),
                anchor="w"
            ).grid(row=0, column=col, padx=10, pady=6, sticky="w")
        
        self.table.grid_columnconfigure(0, weight=1, minsize=100)
        self.table.grid_columnconfigure(1, weight=2, minsize=180)
        self.table.grid_columnconfigure(2, weight=1, minsize=80)
        self.table.grid_columnconfigure(3, weight=1, minsize=80)
        self.table.grid_columnconfigure(4, weight=1, minsize=120)
        self.table.grid_columnconfigure(5, weight=1, minsize=100)

        ctk.CTkFrame(self.table, height=1, fg_color="#888")\
            .grid(row=1, column=0, columnspan=6, sticky="ew")

        self.table.grid_columnconfigure(0, weight=1, minsize=100)
        self.table.grid_columnconfigure(1, weight=2, minsize=180)
        self.table.grid_columnconfigure(2, weight=1, minsize=80)
        self.table.grid_columnconfigure(3, weight=1, minsize=80)
        self.table.grid_columnconfigure(4, weight=1, minsize=120)
        self.table.grid_columnconfigure(5, weight=1, minsize=100)

        self.pagination_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.pagination_frame.grid(row=2, column=0, pady=10)
        self.pagination_frame.grid_columnconfigure((0, 1, 2), weight=0)

        self.prev_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Previous",
            width=120,
            command=self.prev_page
        )
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.page_label = ctk.CTkLabel(
            self.pagination_frame,
            text="Page 1"
        )
        self.page_label.grid(row=0, column=1, padx=10)

        self.next_btn = ctk.CTkButton(
            self.pagination_frame,
            text="Next",
            width=120,
            command=self.next_page
        )
        self.next_btn.grid(row=0, column=2, padx=5)

        self.refresh_table()

    def populate_rows(self, search=False):
        for widget in self.table.winfo_children()[2:]:
            widget.destroy()

        offset = (self.current_page - 1) * self.items_per_page

        if search:
            query = self.search_entry.get().strip()

            # remove "ID-" if user types it
            if query.upper().startswith("ID-"):
                query = query[3:]

            self.cursor.execute(
                "SELECT * FROM inventory WHERE name LIKE ? OR id LIKE ?",
                (f"%{query}%", f"%{query}%")
            )
        else:
            self.cursor.execute(
                "SELECT * FROM inventory LIMIT ? OFFSET ?",
                (self.items_per_page, offset)
            )

        rows = self.cursor.fetchall()

        if not rows:
            message = "Product not found." if search else "No inventory items available."
            ctk.CTkLabel(
                self.table,
                text=message,
                text_color="gray"
            ).grid(row=2, column=0, columnspan=6, sticky="w", padx=10, pady=12)
            return

        for i, row_data in enumerate(rows):
            self.create_row(i, row_data)

    def create_row(self, i, data):
        product_id = f"ID-{data[0]}"
        name = data[1]
        price = f"${data[2]}"
        stock = data[3]
        updated = data[6]
        status = data[7]

        values = [product_id, name, stock, price, updated, status]

        bg = "#2b2b2b" if i % 2 == 0 else "#242424"

        row = ctk.CTkFrame(self.table, fg_color=bg)
        row.grid(row=i*2+2, column=0, columnspan=6, sticky="ew", pady=2)

        # ðŸ”¥ FIX ADDED (restores layout)
        row.grid_columnconfigure(0, weight=1, minsize=100)
        row.grid_columnconfigure(1, weight=2, minsize=180)
        row.grid_columnconfigure(2, weight=1, minsize=80)
        row.grid_columnconfigure(3, weight=1, minsize=80)
        row.grid_columnconfigure(4, weight=1, minsize=120)
        row.grid_columnconfigure(5, weight=1, minsize=100)

        for col, val in enumerate(values):
            color = "#00c853" if col == 5 else "white"

            ctk.CTkLabel(
                row,
                text=val,
                text_color=color,
                anchor="w"
            ).grid(row=0, column=col, padx=10, pady=8, sticky="w")

        row.bind("<Button-1>", lambda e, r=i, d=data: self.toggle_expand(r, d))
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda e, r=i, d=data: self.toggle_expand(r, d))

    def toggle_expand(self, index, data):
        if self.expanded_row == index:
            self.remove_details()
            self.expanded_row = None
            return

        self.remove_details()
        self.expanded_row = index

        detail = ctk.CTkFrame(self.table, fg_color="#1f1f1f")
        detail.grid(row=index*2+3, column=0, columnspan=6, sticky="ew", pady=3)

        detail.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        detail_lines = [
            f"Product ID: ID-{data[0]}",
            f"Name: {data[1]}",
            f"Price: ${data[2]:.2f}",
            f"Current Stock: {data[3]}",
            f"Sold: {data[4] or 0}",
            f"Total Stock: {data[5] or data[3]}",
            f"Updated: {data[6]}",
            f"Status: {data[7]}",
            f"Category: {CATEGORY_DISPLAY_NAMES.get(data[8], data[8])}",
        ]

        detail_info = ctk.CTkFrame(detail, fg_color="transparent")
        detail_info.grid(row=0, column=0, columnspan=5, sticky="ew", padx=8, pady=(8, 4))
        detail_info.grid_columnconfigure((0, 1, 2), weight=1)

        for line_index, line in enumerate(detail_lines):
            ctk.CTkLabel(
                detail_info,
                text=line,
                anchor="w"
            ).grid(
                row=line_index // 3,
                column=line_index % 3,
                padx=6,
                pady=3,
                sticky="w"
            )

        display_entry = ctk.CTkEntry(detail, placeholder_text="Display Name", width=120)
        display_entry.grid(row=1, column=0, padx=6, pady=4, sticky="ew")

        dept_menu = ctk.CTkOptionMenu(
            detail,
            values=[CATEGORY_DISPLAY_NAMES[value] for value in INVENTORY_CATEGORIES],
            width=120
        )
        dept_menu.grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        if data[8] in CATEGORY_DISPLAY_NAMES:
            dept_menu.set(CATEGORY_DISPLAY_NAMES[data[8]])

        cost_entry = ctk.CTkEntry(detail, placeholder_text="Cost", width=100)
        cost_entry.grid(row=1, column=2, padx=6, pady=4, sticky="ew")

        barcode_entry = ctk.CTkEntry(detail, placeholder_text="Barcode", width=120)
        barcode_entry.grid(row=1, column=3, padx=6, pady=4, sticky="ew")

        ctk.CTkButton(
            detail,
            text="Save",
            width=90,
            command=lambda: self.save_changes(
                data[0],
                display_entry.get(),
                dept_menu.get(),
                cost_entry.get(),
                barcode_entry.get()
            )
        ).grid(row=1, column=4, padx=6, pady=4)

        stock_update_frame = ctk.CTkFrame(detail, fg_color="transparent")
        stock_update_frame.grid(row=2, column=0, columnspan=5, sticky="ew", padx=8, pady=(4, 8))
        stock_update_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            stock_update_frame,
            text="Updated Stock Quantity"
        ).grid(row=0, column=0, padx=6, pady=4, sticky="w")

        stock_entry = ctk.CTkEntry(stock_update_frame, placeholder_text="Enter updated stock quantity")
        stock_entry.insert(0, str(data[3]))
        stock_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        ctk.CTkButton(
            stock_update_frame,
            text="Update Stock",
            width=120,
            command=lambda: self.update_stock_quantity(data[0], stock_entry.get())
        ).grid(row=0, column=2, padx=6, pady=4)

        self.detail_frame = detail

    def update_stock_quantity(self, item_id, quantity_value):
        try:
            updated_stock = int(quantity_value)
        except ValueError:
            messagebox.showerror("Invalid Quantity", "Invalid quantity entered.")
            return

        if updated_stock < 0:
            messagebox.showerror("Invalid Quantity", "Quantity cannot be negative.")
            return

        set_inventory_stock(self.cursor, item_id, updated_stock, "Employee inventory update")
        self.conn.commit()
        messagebox.showinfo("Inventory Updated", "Inventory has been successfully updated.")
        self.refresh_table()
        self.remove_details()

    def save_changes(self, item_id, name, dept, cost, barcode):

        # get today's date
        today = datetime.now().strftime("%Y-%m-%d")

        if name:
            self.cursor.execute(
                "UPDATE inventory SET name=?, updated=? WHERE id=?",
                (name, today, item_id)
            )

        if cost:
            try:
                self.cursor.execute(
                    "UPDATE inventory SET price=?, updated=? WHERE id=?",
                    (float(cost), today, item_id)
                )
            except ValueError:
                print("Invalid cost value")

        if dept:
            normalized_dept = next(
                (key for key, label in CATEGORY_DISPLAY_NAMES.items() if label == dept),
                dept
            )
            self.cursor.execute(
                "UPDATE inventory SET category=?, updated=? WHERE id=?",
                (normalized_dept, today, item_id)
            )

        self.conn.commit()

        self.refresh_table()
        self.remove_details()

    def next_page(self):
        self.current_page += 1
        self.refresh_table()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_table()

    def refresh_table(self):
        is_searching = hasattr(self, "search_entry") and bool(self.search_entry.get().strip())

        if is_searching:
            query = self.search_entry.get().strip()
            if query.upper().startswith("ID-"):
                query = query[3:]
            self.cursor.execute(
                "SELECT COUNT(*) FROM inventory WHERE name LIKE ? OR id LIKE ?",
                (f"%{query}%", f"%{query}%")
            )
        else:
            self.cursor.execute("SELECT COUNT(*) FROM inventory")

        total_items = self.cursor.fetchone()[0]

        total_pages = max(1, (total_items // self.items_per_page) +
                          (1 if total_items % self.items_per_page else 0))

        if self.current_page > total_pages:
            self.current_page = total_pages

        if total_items == 0:
            start = 0
            end = 0
        else:
            start = (self.current_page - 1) * self.items_per_page + 1
            end = min(self.current_page * self.items_per_page, total_items)

        self.page_label.configure(text=f"Showing {start}-{end} of {total_items} items  |  Page {self.current_page} of {total_pages}")

        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

        self.populate_rows(search=is_searching)

    def remove_details(self):
        if hasattr(self, "detail_frame"):
            self.detail_frame.destroy()
            
    
    def search_inventory(self, event=None):
        self.current_page = 1
        self.refresh_table()

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("inventory")
