import customtkinter as ctk
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AdminHistoryUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Admin Dashboard")
        self.geometry("1300x700")  # 🔥 slightly bigger for proper fit

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 🔥 FIXED COLUMN WIDTHS (WIDER)
        self.column_specs = [
            ("ID", 100),
            ("Name", 220),
            ("Payment", 140),
            ("Time", 120),
            ("Type", 140),
            ("Status", 160),
            ("Total", 120),
            ("Action", 140),
        ]

        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color="#161b31")
        self.sidebar.grid(row=0, column=0, sticky="nsw")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Pharmacy",
                     font=("Arial", 20, "bold")).pack(pady=(30, 20))

        self.create_sidebar_button("Dashboard")
        self.create_sidebar_button("Orders")
        self.create_sidebar_button("Inventory")
        self.create_sidebar_button("History", active=True)

        # ================= MAIN =================
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.grid(row=0, column=1, sticky="nsew")

        self.main.grid_rowconfigure(3, weight=1)
        self.main.grid_columnconfigure(0, weight=1)

        self.orders = self.mock_data()
        self.current_page = 0
        self.rows_per_page = 5

        self.build_ui()

    # ================= SIDEBAR =================
    def create_sidebar_button(self, text, active=False):
        color = "#4b83e7" if active else "#2f66db"

        ctk.CTkButton(
            self.sidebar,
            text=text,
            height=42,
            fg_color=color,
            hover_color="#3a73e3",
            corner_radius=8
        ).pack(fill="x", padx=20, pady=8)

    # ================= UI =================
    def build_ui(self):

        # ===== TOP BAR =====
        top_bar = ctk.CTkFrame(self.main, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(top_bar, text="Order History",
                     font=("Arial", 26, "bold")).pack(side="left")

        right = ctk.CTkFrame(top_bar, fg_color="transparent")
        right.pack(side="right")

        self.search_entry = ctk.CTkEntry(right, width=320)
        self.search_entry.pack(side="left", padx=10)

        ctk.CTkButton(right, text="Search",
                      command=self.search_orders).pack(side="left", padx=5)

        ctk.CTkButton(right, text="Reset",
                      command=self.reset_orders).pack(side="left", padx=5)

        # ===== HEADER =====
        self.header = ctk.CTkFrame(self.main, fg_color="#1c2d4a", height=50)
        self.header.grid(row=1, column=0, sticky="ew", padx=20)
        self.header.grid_propagate(False)

        self.build_header()

        # ===== SCROLL =====
        self.scroll = ctk.CTkScrollableFrame(self.main)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # ===== PAGINATION =====
        bottom = ctk.CTkFrame(self.main, fg_color="transparent")
        bottom.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        self.page_label = ctk.CTkLabel(bottom, text="")
        self.page_label.pack(side="left")

        ctk.CTkButton(bottom, text="Previous",
                      command=self.prev_page).pack(side="right", padx=5)

        ctk.CTkButton(bottom, text="Next",
                      command=self.next_page).pack(side="right", padx=5)

        self.render_orders()

    def build_header(self):
        x = 0
        for col, width in self.column_specs:
            frame = ctk.CTkFrame(self.header, width=width, height=50, fg_color="transparent")
            frame.place(x=x, y=0)
            frame.pack_propagate(False)

            ctk.CTkLabel(frame, text=col,
                         font=("Arial", 12, "bold")).pack(anchor="w", padx=10)

            x += width

    # ================= DATA =================
    def mock_data(self):
        return [
            {"id": f"#{2630+i}", "name": f"Customer {i}",
             "payment": "Cash", "time": f"{10+i} min",
             "type": "Delivery",
             "status": "Delivered" if i % 2 == 0 else "Canceled",
             "total": f"${10+i}.00"}
            for i in range(15)
        ]

    def status_color(self, status):
        return "#16e06e" if status == "Delivered" else "#ff4d4f"

    # ================= PAGINATION =================
    def render_orders(self):

        for w in self.scroll.winfo_children():
            w.destroy()

        start = self.current_page * self.rows_per_page
        end = start + self.rows_per_page

        data = self.orders[start:end]

        for i, order in enumerate(data):
            self.create_row(order, i)

        total_pages = (len(self.orders) - 1) // self.rows_per_page + 1
        self.page_label.configure(text=f"Page {self.current_page+1} of {total_pages}")

    def next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.orders):
            self.current_page += 1
            self.render_orders()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.render_orders()

    # ================= ROW =================
    def create_row(self, order, index):

        color = "#000000" if index % 2 == 0 else "#2f2f2f"

        row = ctk.CTkFrame(self.scroll, fg_color=color, height=55)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        values = [
            order["id"], order["name"], order["payment"],
            order["time"], order["type"], order["status"], order["total"]
        ]

        x = 0
        for i, ((_, width), val) in enumerate(zip(self.column_specs[:-1], values)):
            cell = ctk.CTkFrame(row, width=width, height=55, fg_color="transparent")
            cell.place(x=x, y=0)
            cell.pack_propagate(False)

            txt = f"• {val}" if i == 5 else val

            ctk.CTkLabel(
                cell,
                text=txt,
                text_color=self.status_color(val) if i == 5 else "white"
            ).pack(anchor="w", padx=10)

            x += width

        # ===== ACTION BUTTON =====
        action_width = self.column_specs[-1][1]

        action_cell = ctk.CTkFrame(row, width=action_width, height=55, fg_color="transparent")
        action_cell.place(x=x, y=0)
        action_cell.pack_propagate(False)

        btn = ctk.CTkButton(action_cell, text="Actions", width=90)
        btn.pack(padx=10, pady=10)

        btn.configure(command=lambda o=order, b=btn: self.show_menu(o, b))

    # ================= MENU =================
    def show_menu(self, order, button):
        menu = tk.Menu(self, tearoff=0)

        menu.add_command(label="View Order", command=lambda: print("View", order["id"]))
        menu.add_command(label="Refund", command=lambda: print("Refund", order["id"]))
        menu.add_command(label="Print Receipt", command=lambda: print("Print", order["id"]))

        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()

        menu.tk_popup(x, y)

    # ================= SEARCH =================
    def search_orders(self):
        query = self.search_entry.get().lower()

        self.orders = [o for o in self.mock_data()
                       if query in o["name"].lower() or query in o["id"].lower()]

        self.current_page = 0
        self.render_orders()

    def reset_orders(self):
        self.orders = self.mock_data()
        self.current_page = 0
        self.render_orders()


if __name__ == "__main__":
    app = AdminHistoryUI()
    app.mainloop()