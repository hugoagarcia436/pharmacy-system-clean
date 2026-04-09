import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AdminDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Admin Dashboard")
        self.geometry("1200x700")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR
        sidebar = ctk.CTkFrame(self, width=200)
        sidebar.grid(row=0, column=0, sticky="ns")

        ctk.CTkLabel(sidebar, text="Pharmacy",
                     font=ctk.CTkFont(size=18, weight="bold")).grid(pady=15)

        for i, name in enumerate(["Dashboard", "Orders", "Inventory", "History"]):
            ctk.CTkButton(sidebar, text=name)\
                .grid(row=i+1, column=0, padx=15, pady=6, sticky="ew")

        # MAIN
        main = ctk.CTkFrame(self)
        main.grid(row=0, column=1, sticky="nsew")

        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        # TOP BAR
        topbar = ctk.CTkFrame(main)
        topbar.grid(row=0, column=0, sticky="ew", padx=15, pady=8)

        topbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(topbar, text="Inventory Check",
                     font=ctk.CTkFont(size=20, weight="bold"))\
            .grid(row=0, column=0, padx=15, sticky="w")

        ctk.CTkLabel(topbar, text="Admin").grid(row=0, column=1, padx=15)

        # CONTENT
        self.frame = ctk.CTkFrame(main)
        self.frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=8)

        self.frame.grid_columnconfigure(0, weight=1)

        self.expanded_row = None

        self.setup_inventory()

    def setup_inventory(self):
        frame = self.frame

        # SEARCH
        top_bar = ctk.CTkFrame(frame, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkEntry(top_bar, placeholder_text="Search inventory...", width=220)\
            .grid(row=0, column=1, padx=8, pady=6, sticky="e")

        # TABLE
        self.table = ctk.CTkFrame(frame, fg_color="transparent")
        self.table.grid(row=1, column=0, sticky="nsew")

        headers = ["Item ID", "Item Name", "Stock", "Price", "Updated", "Status"]

        for col, h in enumerate(headers):
            ctk.CTkLabel(
                self.table,
                text=h,
                font=ctk.CTkFont(weight="bold", size=12)
            ).grid(row=0, column=col, padx=15, pady=6, sticky="w")

        ctk.CTkFrame(self.table, height=1, fg_color="#888")\
            .grid(row=1, column=0, columnspan=6, sticky="ew")

        for col in range(6):
            self.table.grid_columnconfigure(col, weight=1)

        self.populate_rows()

    def populate_rows(self):
        for i in range(10):
            self.create_row(i)

    def create_row(self, i):
        values = [
            f"ID-{i}",
            "Medicine A",
            "150",
            "$20",
            "2026-04-08",
            "In Stock"
        ]

        row = ctk.CTkFrame(self.table, fg_color="#2b2b2b")
        row.grid(row=i*2+2, column=0, columnspan=6, sticky="ew", pady=2)

        for col in range(6):
            row.grid_columnconfigure(col, weight=1)

        for col, val in enumerate(values):
            color = "#00c853" if col == 5 else "white"

            ctk.CTkLabel(
                row,
                text=val,
                text_color=color,
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=col, padx=15, pady=8, sticky="w")

        row.bind("<Button-1>", lambda e, r=i: self.toggle_expand(r))
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda e, r=i: self.toggle_expand(r))

    def toggle_expand(self, index):
        if self.expanded_row == index:
            self.remove_details()
            self.expanded_row = None
            return

        self.remove_details()
        self.expanded_row = index

        detail = ctk.CTkFrame(self.table, fg_color="#1f1f1f")
        detail.grid(row=index*2+3, column=0, columnspan=6, sticky="ew", pady=3)

        detail.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # compact inputs
        ctk.CTkEntry(detail, placeholder_text="Display Name")\
            .grid(row=0, column=0, padx=8, pady=4, sticky="ew")

        ctk.CTkOptionMenu(detail, values=["Cosmetic", "Medicine"])\
            .grid(row=0, column=1, padx=8, pady=4, sticky="ew")

        ctk.CTkEntry(detail, placeholder_text="Cost")\
            .grid(row=0, column=2, padx=8, pady=4, sticky="ew")

        ctk.CTkEntry(detail, placeholder_text="Barcode")\
            .grid(row=0, column=3, padx=8, pady=4, sticky="ew")

        ctk.CTkLabel(detail, text="In Stock: 174", font=ctk.CTkFont(size=11))\
            .grid(row=1, column=0, pady=4)

        ctk.CTkLabel(detail, text="Sold: 226", font=ctk.CTkFont(size=11))\
            .grid(row=1, column=1)

        ctk.CTkLabel(detail, text="Total Stock: 400", font=ctk.CTkFont(size=11))\
            .grid(row=1, column=2)

        ctk.CTkButton(detail, text="Save", width=90)\
            .grid(row=1, column=3, pady=4)

        self.detail_frame = detail

    def remove_details(self):
        if hasattr(self, "detail_frame"):
            self.detail_frame.destroy()


if __name__ == "__main__":
    app = AdminDashboard()
    app.mainloop()