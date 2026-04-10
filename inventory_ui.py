import customtkinter as ctk
from datetime import datetime
import os
import sqlite3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


class InventoryUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Employee Dashboard")
        self.geometry("1200x700")

        self.conn = sqlite3.connect("app_data.db")
        self.cursor = self.conn.cursor()

        self.current_page = 1
        self.items_per_page = 25

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=240, fg_color=SIDEBAR_COLOR)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="EMPLOYEE",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(28, 28))

        self.create_sidebar_button(sidebar, "Dashboard", self.open_dashboard)
        self.create_sidebar_button(sidebar, "Inventory", active=True)
        self.create_sidebar_button(sidebar, "Orders", self.open_orders)
        self.create_sidebar_button(sidebar, "Employees", self.open_employees)
        self.create_sidebar_button(sidebar, "History", self.open_history)

        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew")

        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(main)
        topbar.grid(row=0, column=0, sticky="ew", padx=15, pady=8)

        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(topbar, text="Inventory Check",
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

        display_entry = ctk.CTkEntry(detail, placeholder_text="Display Name", width=120)
        display_entry.grid(row=0, column=0, padx=6, pady=4, sticky="ew")

        dept_menu = ctk.CTkOptionMenu(detail, values=["Cosmetic", "Medicine"], width=120)
        dept_menu.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        cost_entry = ctk.CTkEntry(detail, placeholder_text="Cost", width=100)
        cost_entry.grid(row=0, column=2, padx=6, pady=4, sticky="ew")

        barcode_entry = ctk.CTkEntry(detail, placeholder_text="Barcode", width=120)
        barcode_entry.grid(row=0, column=3, padx=6, pady=4, sticky="ew")

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
        ).grid(row=0, column=4, padx=6, pady=4)

        self.detail_frame = detail

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
        self.cursor.execute("SELECT COUNT(*) FROM inventory")
        total_items = self.cursor.fetchone()[0]

        total_pages = max(1, (total_items // self.items_per_page) +
                          (1 if total_items % self.items_per_page else 0))

        if self.current_page > total_pages:
            self.current_page = total_pages

        start = (self.current_page - 1) * self.items_per_page + 1
        end = min(self.current_page * self.items_per_page, total_items)

        self.page_label.configure(text=f"Showing {start}-{end} of {total_items} items  |  Page {self.current_page} of {total_pages}")

        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

        if hasattr(self, "search_entry") and self.search_entry.get():
            self.populate_rows(search=True)
        else:
            self.populate_rows()

    def remove_details(self):
        if hasattr(self, "detail_frame"):
            self.detail_frame.destroy()
            
    
    def search_inventory(self, event=None):
        self.current_page = 1
        self.populate_rows(search=True)

    def open_dashboard(self):
        self.destroy()
        os.system("python admin_dashboard_view_ui.py")

    def open_orders(self):
        self.destroy()
        os.system("python order_ui.py")

    def open_employees(self):
        self.destroy()
        os.system("python employees_ui.py")

    def open_history(self):
        self.destroy()
        os.system("python admin_history_ui.py")


if __name__ == "__main__":
    app = InventoryUI()
    app.mainloop()
