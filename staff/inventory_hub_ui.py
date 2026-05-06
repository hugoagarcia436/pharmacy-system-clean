import sqlite3
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from catalog.category_utils import CATEGORY_DISPLAY_NAMES, INVENTORY_CATEGORIES, repair_inventory_categories
from shared.inventory_utils import (
    ensure_inventory_transaction_schema,
    inventory_status,
    inventory_status_color,
    receive_inventory,
    set_inventory_stock,
)
from shared.paths import DB_PATH
from staff.sidebar_ui import EmployeeSidebar


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


INVENTORY_COLUMNS = [
    ("Item", 230, "w"),
    ("Stock", 80, "center"),
    ("Price", 90, "center"),
    ("Updated", 110, "center"),
    ("Status", 110, "center"),
]

STOCK_ORDER_COLUMNS = [
    ("Item", 230, "w"),
    ("Stock", 80, "center"),
    ("Sold", 80, "center"),
    ("Status", 120, "center"),
    ("Action", 110, "center"),
]

HISTORY_COLUMNS = [
    ("Item", 300, "w"),
    ("Change", 130, "center"),
    ("Before", 90, "center"),
    ("After", 90, "center"),
    ("When", 190, "center"),
]


class InventoryHubUI(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Inventory Hub")
        self.controller.geometry("1320x760")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        ensure_inventory_transaction_schema(self.cursor)
        repair_inventory_categories(self.cursor)
        self.conn.commit()

        self.selected_inventory_item = None
        self.selected_order_item = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = EmployeeSidebar(self, self.controller, "inventory_hub")

        self.main = ctk.CTkFrame(self)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

        self.build_header()
        self.build_tabs()

    def build_header(self):
        header = ctk.CTkFrame(self.main)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Inventory Hub",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=(12, 2), sticky="w")

        ctk.CTkLabel(
            header,
            text="Manage inventory, restock items, and review stock history in one place.",
            text_color="gray",
            justify="left",
        ).grid(row=1, column=0, padx=15, pady=(0, 12), sticky="w")

    def build_tabs(self):
        self.tabs = ctk.CTkTabview(self.main)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        self.inventory_tab = self.tabs.add("Inventory List")
        self.orders_tab = self.tabs.add("Stock Orders")
        self.history_tab = self.tabs.add("History")

        self.build_inventory_tab()
        self.build_orders_tab()
        self.build_history_tab()

    def build_inventory_tab(self):
        tab = self.inventory_tab
        tab.grid_columnconfigure(0, weight=4)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        toolbar.grid_columnconfigure(0, weight=1)

        self.inventory_search = ctk.CTkEntry(toolbar, placeholder_text="Search item name or ID...")
        self.inventory_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.inventory_search.bind("<Return>", lambda event: self.refresh_inventory_list())
        self.inventory_search.bind("<KeyRelease>", lambda event: self.refresh_inventory_list())

        ctk.CTkButton(toolbar, text="Refresh", width=90, command=self.refresh_all).grid(row=0, column=1)

        list_panel = ctk.CTkFrame(tab)
        list_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=(0, 10))
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            list_panel,
            text="Inventory List",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        self.inventory_list = ctk.CTkScrollableFrame(list_panel)
        self.inventory_list.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.inventory_list.grid_columnconfigure(0, weight=1)

        detail = ctk.CTkFrame(tab)
        detail.grid(row=1, column=1, sticky="nsew", padx=(6, 10), pady=(0, 10))
        detail.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            detail,
            text="Item Details",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(14, 8))

        self.inventory_detail_title = ctk.CTkLabel(detail, text="Select an item to view or edit.", text_color="gray")
        self.inventory_detail_title.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        self.name_entry = ctk.CTkEntry(detail, placeholder_text="Display Name")
        self.name_entry.grid(row=2, column=0, sticky="ew", padx=14, pady=6)

        self.category_menu = ctk.CTkOptionMenu(
            detail,
            values=[CATEGORY_DISPLAY_NAMES[value] for value in INVENTORY_CATEGORIES],
        )
        self.category_menu.grid(row=3, column=0, sticky="ew", padx=14, pady=6)

        self.price_entry = ctk.CTkEntry(detail, placeholder_text="Price")
        self.price_entry.grid(row=4, column=0, sticky="ew", padx=14, pady=6)

        self.stock_entry = ctk.CTkEntry(detail, placeholder_text="Stock Quantity")
        self.stock_entry.grid(row=5, column=0, sticky="ew", padx=14, pady=6)

        ctk.CTkButton(detail, text="Save Item", command=self.save_selected_inventory_item).grid(
            row=6, column=0, sticky="ew", padx=14, pady=(12, 6)
        )

        self.inventory_status_label = ctk.CTkLabel(detail, text="", text_color="#167a3f", justify="left")
        self.inventory_status_label.grid(row=7, column=0, sticky="w", padx=14, pady=(0, 14))

        self.refresh_inventory_list()

    def build_orders_tab(self):
        tab = self.orders_tab
        tab.grid_columnconfigure(0, weight=4)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            tab,
            text="Restock items without opening a separate Orders table.",
            text_color="gray",
            justify="left",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=10)

        list_panel = ctk.CTkFrame(tab)
        list_panel.grid(row=1, column=0, sticky="nsew", padx=(10, 6), pady=(0, 10))
        list_panel.grid_columnconfigure(0, weight=1)
        list_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_panel, text="Stock Order List", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 8)
        )
        self.stock_order_list = ctk.CTkScrollableFrame(list_panel)
        self.stock_order_list.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.stock_order_list.grid_columnconfigure(0, weight=1)

        restock_panel = ctk.CTkFrame(tab)
        restock_panel.grid(row=1, column=1, sticky="nsew", padx=(6, 10), pady=(0, 10))
        restock_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(restock_panel, text="Restock Selected Item", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=14, pady=(14, 8)
        )
        self.order_detail_label = ctk.CTkLabel(restock_panel, text="Select an item from the list.", text_color="gray", justify="left")
        self.order_detail_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        self.restock_qty = ctk.CTkEntry(restock_panel, placeholder_text="Quantity to receive")
        self.restock_qty.grid(row=2, column=0, sticky="ew", padx=14, pady=6)

        ctk.CTkButton(restock_panel, text="Receive Stock", command=self.receive_selected_stock).grid(
            row=3, column=0, sticky="ew", padx=14, pady=(12, 6)
        )

        self.order_status_label = ctk.CTkLabel(restock_panel, text="", text_color="#167a3f", justify="left")
        self.order_status_label.grid(row=4, column=0, sticky="w", padx=14, pady=(0, 14))

        self.refresh_stock_orders()

    def build_history_tab(self):
        tab = self.history_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        toolbar = ctk.CTkFrame(tab, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        toolbar.grid_columnconfigure(0, weight=1)

        self.history_search = ctk.CTkEntry(toolbar, placeholder_text="Filter by item name, ID, or change type...")
        self.history_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.history_search.bind("<Return>", lambda event: self.refresh_history())
        self.history_search.bind("<KeyRelease>", lambda event: self.refresh_history())

        ctk.CTkButton(toolbar, text="Refresh", width=90, command=self.refresh_history).grid(row=0, column=1)

        ctk.CTkLabel(
            tab,
            text="Recent Inventory Changes",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))

        self.history_list = ctk.CTkScrollableFrame(tab)
        self.history_list.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.history_list.grid_columnconfigure(0, weight=1)

        self.refresh_history()

    def fetch_inventory_rows(self, query=""):
        query = query.strip()
        params = []
        where = ""
        if query:
            if query.upper().startswith(("ID-", "ORD-")):
                query = query[3:]
            where = "WHERE name LIKE ? OR CAST(id AS TEXT) LIKE ?"
            params = [f"%{query}%", f"%{query}%"]

        self.cursor.execute(
            f"""
            SELECT id, name, price, stock, sold, total_stock, updated, status, category
            FROM inventory
            {where}
            ORDER BY name
            """,
            params,
        )
        return self.cursor.fetchall()

    def refresh_inventory_list(self):
        for widget in self.inventory_list.winfo_children():
            widget.destroy()

        rows = self.fetch_inventory_rows(self.inventory_search.get())
        self.create_table_header(self.inventory_list, INVENTORY_COLUMNS)

        if not rows:
            ctk.CTkLabel(self.inventory_list, text="No inventory items found.", text_color="gray").grid(
                row=1, column=0, sticky="w", padx=10, pady=10
            )
            return

        for row_index, item in enumerate(rows, start=1):
            self.create_inventory_row(self.inventory_list, row_index, item, self.select_inventory_item)

    def refresh_stock_orders(self):
        for widget in self.stock_order_list.winfo_children():
            widget.destroy()

        rows = self.fetch_inventory_rows()
        self.create_table_header(self.stock_order_list, STOCK_ORDER_COLUMNS)

        for row_index, item in enumerate(rows, start=1):
            item_id, name, _, stock, sold, _, _, _, _ = item
            status = inventory_status(stock)
            row = self.basic_row(self.stock_order_list, row_index, STOCK_ORDER_COLUMNS)
            values = [f"ORD-{item_id}  {name}", str(stock), str(sold or 0), status]
            for col, value in enumerate(values):
                _, _, anchor = STOCK_ORDER_COLUMNS[col]
                color = inventory_status_color(status) if col == 3 else "#263238"
                ctk.CTkLabel(row, text=value, text_color=color, anchor=anchor).grid(
                    row=0, column=col, sticky="ew", padx=10, pady=9
                )
            ctk.CTkButton(row, text="Restock", width=86, command=lambda current=item: self.select_order_item(current)).grid(
                row=0, column=4, padx=10, pady=7
            )

    def create_table_header(self, parent, columns):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        for col, (text, width, anchor) in enumerate(columns):
            header.grid_columnconfigure(col, minsize=width, weight=0)
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(weight="bold"), anchor=anchor).grid(
                row=0, column=col, sticky="ew", padx=10, pady=6
            )

    def basic_row(self, parent, row_index, columns):
        row = ctk.CTkFrame(parent, fg_color="#ffffff" if row_index % 2 else "#edf8f4", corner_radius=8)
        row.grid(row=row_index, column=0, sticky="ew", pady=3)
        for col, (_, width, _) in enumerate(columns):
            row.grid_columnconfigure(col, minsize=width, weight=0)
        return row

    def create_inventory_row(self, parent, row_index, item, command):
        item_id, name, price, stock, _, _, updated, _, _ = item
        status = inventory_status(stock)
        row = self.basic_row(parent, row_index, INVENTORY_COLUMNS)

        values = [
            f"ID-{item_id}  {name}",
            str(stock),
            f"${price:.2f}",
            updated or "N/A",
            status,
        ]

        for col, value in enumerate(values):
            _, _, anchor = INVENTORY_COLUMNS[col]
            color = inventory_status_color(status) if col == 4 else "#263238"
            ctk.CTkLabel(row, text=value, text_color=color, anchor=anchor).grid(
                row=0, column=col, sticky="ew", padx=10, pady=9
            )

        row.bind("<Button-1>", lambda event: command(item))
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda event: command(item))

    def select_inventory_item(self, item):
        self.selected_inventory_item = item
        item_id, name, price, stock, _, _, updated, _, category = item
        status = inventory_status(stock)

        self.inventory_detail_title.configure(
            text=f"ID-{item_id} | {status} | Updated {updated or 'N/A'}",
            text_color=inventory_status_color(status),
        )
        self.set_entry(self.name_entry, name)
        self.set_entry(self.price_entry, f"{price:.2f}")
        self.set_entry(self.stock_entry, str(stock))
        self.category_menu.set(CATEGORY_DISPLAY_NAMES.get(category, "Medicine"))
        self.inventory_status_label.configure(text="")

    def save_selected_inventory_item(self):
        if self.selected_inventory_item is None:
            self.inventory_status_label.configure(text="Select an item first.", text_color="#c62828")
            return

        item_id = self.selected_inventory_item[0]
        name = self.name_entry.get().strip()
        price_text = self.price_entry.get().strip()
        stock_text = self.stock_entry.get().strip()
        category_label = self.category_menu.get()
        category = next((key for key, label in CATEGORY_DISPLAY_NAMES.items() if label == category_label), category_label)

        try:
            price = float(price_text)
            stock = int(stock_text)
        except ValueError:
            self.inventory_status_label.configure(text="Enter a valid price and stock quantity.", text_color="#c62828")
            return

        if not name or price < 0 or stock < 0:
            self.inventory_status_label.configure(text="Name is required. Price and stock cannot be negative.", text_color="#c62828")
            return

        self.cursor.execute(
            "UPDATE inventory SET name=?, price=?, category=?, updated=? WHERE id=?",
            (name, price, category, datetime.now().strftime("%Y-%m-%d"), item_id),
        )
        set_inventory_stock(self.cursor, item_id, stock, "Inventory Hub update")
        self.conn.commit()
        self.inventory_status_label.configure(text="Item saved successfully.", text_color="#167a3f")
        self.refresh_all()

    def select_order_item(self, item):
        self.selected_order_item = item
        item_id, name, _, stock, sold, total_stock, updated, _, _ = item
        status = inventory_status(stock)
        self.order_detail_label.configure(
            text=(
                f"ORD-{item_id} | {name}\n"
                f"Current stock: {stock} | Sold: {sold or 0} | Total received: {total_stock or stock}\n"
                f"Status: {status} | Updated: {updated or 'N/A'}"
            ),
            text_color=inventory_status_color(status),
        )
        self.restock_qty.delete(0, "end")
        self.order_status_label.configure(text="")

    def receive_selected_stock(self):
        if self.selected_order_item is None:
            self.order_status_label.configure(text="Select an item to restock first.", text_color="#c62828")
            return

        try:
            quantity = int(self.restock_qty.get())
        except ValueError:
            self.order_status_label.configure(text="Enter a valid quantity.", text_color="#c62828")
            return

        if quantity <= 0:
            self.order_status_label.configure(text="Quantity must be greater than zero.", text_color="#c62828")
            return

        item_id = self.selected_order_item[0]
        receive_inventory(self.cursor, item_id, quantity, "Inventory Hub stock receipt")
        self.conn.commit()
        self.order_status_label.configure(text=f"Received {quantity} units.", text_color="#167a3f")
        self.restock_qty.delete(0, "end")
        self.refresh_all()

    def refresh_history(self):
        for widget in self.history_list.winfo_children():
            widget.destroy()

        query = self.history_search.get().strip()
        where = ""
        params = []
        if query:
            where = """
            WHERE item_name LIKE ?
            OR change_type LIKE ?
            OR CAST(inventory_id AS TEXT) LIKE ?
            """
            params = [f"%{query}%", f"%{query}%", f"%{query}%"]

        self.cursor.execute(
            f"""
            SELECT inventory_id, item_name, change_type, quantity, stock_before, stock_after, reference, created_at
            FROM inventory_transactions
            {where}
            ORDER BY id DESC
            LIMIT 80
            """,
            params,
        )
        rows = self.cursor.fetchall()

        self.create_table_header(self.history_list, HISTORY_COLUMNS)
        if not rows:
            ctk.CTkLabel(self.history_list, text="No inventory changes recorded yet.", text_color="gray").grid(
                row=1, column=0, sticky="w", padx=10, pady=10
            )
            return

        for row_index, row_data in enumerate(rows, start=1):
            item_id, name, change_type, quantity, before, after, reference, created_at = row_data
            row = self.basic_row(self.history_list, row_index, HISTORY_COLUMNS)
            values = [
                f"ID-{item_id}  {name}",
                f"{change_type.title()} {quantity}",
                str(before),
                str(after),
                created_at or reference or "N/A",
            ]
            for col, value in enumerate(values):
                _, _, anchor = HISTORY_COLUMNS[col]
                ctk.CTkLabel(row, text=value, anchor=anchor).grid(
                    row=0, column=col, sticky="ew", padx=10, pady=9
                )

    def refresh_all(self):
        self.refresh_inventory_list()
        self.refresh_stock_orders()
        self.refresh_history()

    def set_entry(self, entry, value):
        entry.delete(0, "end")
        entry.insert(0, str(value))

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("inventory_hub")
