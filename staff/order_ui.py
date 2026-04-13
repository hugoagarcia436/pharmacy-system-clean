import customtkinter as ctk
import sqlite3
from datetime import datetime
from shared.paths import DB_PATH

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR = "#161b31"
BUTTON_COLOR = "#2f66db"
BUTTON_HOVER = "#3a73e3"
ACTIVE_BUTTON = "#4b83e7"


class Order(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Employee Dashboard")
        self.controller.geometry("1200x700")

        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ===== SIDEBAR =====
        sidebar = ctk.CTkFrame(self, width=240, fg_color=SIDEBAR_COLOR)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="EMPLOYEE",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(28, 28))

        self.create_sidebar_button(sidebar, "Dashboard", self.open_dashboard)
        self.create_sidebar_button(sidebar, "Inventory", self.show_inventory)
        self.create_sidebar_button(sidebar, "Orders", active=True)
        self.create_sidebar_button(sidebar, "Employees", self.open_employees)
        self.create_sidebar_button(sidebar, "History", self.open_history)

        # ===== MAIN =====
        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        topbar = ctk.CTkFrame(main)
        topbar.grid(row=0, column=0, sticky="ew", padx=15, pady=8)
        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topbar,
            text="Employee Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        ).grid(row=0, column=0, padx=15, sticky="w")

        # ===== CONTENT =====
        self.content = ctk.CTkFrame(main)
        self.content.grid(row=1, column=0, sticky="nsew", padx=15, pady=8)
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        self.detail_frame = None
        self.detail_host = None

        self.show_orders()

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

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()
        self.detail_frame = None
        self.detail_host = None

    def remove_details(self):
        if self.detail_frame is not None and self.detail_frame.winfo_exists():
            self.detail_frame.destroy()
            self.detail_frame = None

    def delete_item(self, data):
        self.cursor.execute("DELETE FROM inventory WHERE id=?", (data[0],))
        self.conn.commit()
        self.show_orders()

    def show_inventory(self):
        self.controller.show_page("inventory")

    def show_orders(self):
        self.clear_content()

        container = ctk.CTkScrollableFrame(self.content)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            container,
            text="Stock Orders",
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # ===== DETAIL AREA UNDER TITLE =====
        self.detail_host = ctk.CTkFrame(container, fg_color="transparent")
        self.detail_host.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
        self.detail_host.grid_columnconfigure(0, weight=1)

        # ===== TABLE =====
        table_wrap = ctk.CTkFrame(container, fg_color="transparent")
        table_wrap.grid(row=2, column=0, sticky="ew", padx=10)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.table = ctk.CTkFrame(table_wrap, fg_color="transparent")
        self.table.grid(row=0, column=0, sticky="ew")
        self.table.grid_columnconfigure(0, weight=1)

        headers = ["Order ID", "Item Name", "Stock", "Price", "Updated", "Status", "Actions"]
        col_widths = [100, 220, 100, 100, 150, 120, 190]

        header = ctk.CTkFrame(self.table, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")

        for i, w in enumerate(col_widths):
            header.grid_columnconfigure(i, minsize=w, weight=1 if i in [1, 6] else 0)

        for col, text in enumerate(headers):
            anchor = "w" if col in [0, 1, 6] else "center"
            ctk.CTkLabel(
                header,
                text=text,
                font=ctk.CTkFont(weight="bold"),
                anchor=anchor
            ).grid(row=0, column=col, padx=10, pady=8, sticky="ew")

        self.cursor.execute("SELECT * FROM inventory")
        rows = self.cursor.fetchall()

        for i, data in enumerate(rows, start=1):
            bg = "#2b2b2b" if (i - 1) % 2 == 0 else "#242424"

            row = ctk.CTkFrame(self.table, fg_color=bg, corner_radius=8)
            row.grid(row=i, column=0, sticky="ew", pady=3)

            for j, w in enumerate(col_widths):
                row.grid_columnconfigure(j, minsize=w, weight=1 if j in [1, 6] else 0)

            values = [
                f"ORD-{data[0]}",
                data[1],
                str(data[3]),
                f"${data[2]}",
                data[6],
                data[7]
            ]

            for col, val in enumerate(values):
                anchor = "w" if col in [0, 1] else "center"
                color = "#00c853" if col == 5 else "white"

                ctk.CTkLabel(
                    row,
                    text=val,
                    text_color=color,
                    anchor=anchor
                ).grid(row=0, column=col, padx=10, pady=10, sticky="ew")

            actions = ctk.CTkFrame(row, fg_color="transparent")
            actions.grid(row=0, column=6, padx=8, pady=6, sticky="e")

            ctk.CTkButton(
                actions,
                text="View",
                width=50,
                command=lambda d=data: self.show_detail(d, "view")
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                actions,
                text="+",
                width=40,
                command=lambda d=data: self.show_detail(d, "order")
            ).pack(side="left", padx=3)

            ctk.CTkButton(
                actions,
                text="Del",
                width=50,
                fg_color="#8b0000",
                hover_color="#a00000",
                command=lambda d=data: self.delete_item(d)
            ).pack(side="left", padx=3)

    def show_detail(self, data, mode):
        self.remove_details()

        if self.detail_host is None:
            return

        self.detail_frame = ctk.CTkFrame(self.detail_host, fg_color="#1f1f1f", corner_radius=10)
        self.detail_frame.grid(row=0, column=0, sticky="ew")
        self.detail_frame.grid_columnconfigure((0, 1, 2), weight=1)

        if mode == "view":
            storage = int(data[3] * 0.6)
            floor = int(data[3] * 0.4)
            sold = data[3] - floor

            ctk.CTkLabel(
                self.detail_frame,
                text=f"Item: {data[1]}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 8), sticky="w")

            ctk.CTkLabel(
                self.detail_frame,
                text=f"Storage Stock: {storage}"
            ).grid(row=1, column=0, padx=15, pady=8, sticky="w")

            ctk.CTkLabel(
                self.detail_frame,
                text=f"Sales Floor: {floor}"
            ).grid(row=1, column=1, padx=15, pady=8, sticky="w")

            ctk.CTkLabel(
                self.detail_frame,
                text=f"Sold: {sold}"
            ).grid(row=1, column=2, padx=15, pady=8, sticky="w")

            ctk.CTkButton(
                self.detail_frame,
                text="Close",
                width=90,
                command=self.remove_details
            ).grid(row=2, column=2, padx=15, pady=(8, 12), sticky="e")

        elif mode == "order":
            ctk.CTkLabel(
                self.detail_frame,
                text=f"Add Order for: {data[1]}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 8), sticky="w")

            qty_entry = ctk.CTkEntry(self.detail_frame, placeholder_text="Quantity")
            qty_entry.grid(row=1, column=0, padx=15, pady=8, sticky="w")

            def add():
                try:
                    qty = int(qty_entry.get())
                    self.cursor.execute("SELECT stock FROM inventory WHERE id=?", (data[0],))
                    current = self.cursor.fetchone()[0]

                    new_stock = current + qty
                    today = datetime.now().strftime("%Y-%m-%d")

                    self.cursor.execute(
                        "UPDATE inventory SET stock=?, updated=? WHERE id=?",
                        (new_stock, today, data[0])
                    )
                    self.conn.commit()
                    self.show_orders()
                except:
                    print("Invalid input")

            ctk.CTkButton(
                self.detail_frame,
                text="Submit",
                width=90,
                command=add
            ).grid(row=1, column=1, padx=10, pady=8, sticky="w")

            ctk.CTkButton(
                self.detail_frame,
                text="Close",
                width=90,
                command=self.remove_details
            ).grid(row=1, column=2, padx=15, pady=8, sticky="e")

    def open_dashboard(self):
        self.controller.show_page("dashboard")

    def open_employees(self):
        self.controller.show_page("employees")

    def open_history(self):
        self.controller.show_page("history")

    def destroy(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass
        super().destroy()


if __name__ == "__main__":
    from app.staff_app import launch_staff_app

    launch_staff_app("orders")
