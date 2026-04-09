import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CartUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Shopping Cart")
        self.geometry("1350x850")

        # 🔥 IMPORTANT: allow window to expand
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        base_path = os.path.dirname(os.path.realpath(__file__))
        img_path = os.path.join(base_path, "assets", "images")

        # ================= HEADER =================
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold"))\
            .grid(row=0, column=0, padx=15)

        search = ctk.CTkEntry(header, placeholder_text="Search medications...", height=40)
        search.grid(row=0, column=1, sticky="ew", padx=20)

        ctk.CTkButton(header, text="Orders").grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Cart 🛒").grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="Account").grid(row=0, column=4, padx=10)

        # ================= MAIN =================
        main = ctk.CTkFrame(self)
        main.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # 🔥 allow full expansion
        main.grid_columnconfigure(0, weight=3)
        main.grid_columnconfigure(1, weight=1)
        main.grid_rowconfigure(0, weight=1)

        # ================= LEFT =================
        scroll = ctk.CTkScrollableFrame(main)
        scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        scroll.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(scroll, text="Your Cart", font=("Arial", 26, "bold"))\
            .grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # ---------- ITEM ----------
        def create_item(row, title, price, image_file):
            card = ctk.CTkFrame(scroll, corner_radius=12)
            card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)

            card.grid_columnconfigure(1, weight=1)

            # IMAGE
            img = ctk.CTkImage(
                light_image=Image.open(os.path.join(img_path, image_file)),
                size=(110, 80)
            )
            ctk.CTkLabel(card, image=img, text="")\
                .grid(row=0, column=0, rowspan=3, padx=10, pady=10)

            # INFO
            ctk.CTkLabel(card, text=title, font=("Arial", 15, "bold"))\
                .grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(card, text="In Stock ✔", text_color="green")\
                .grid(row=1, column=1, sticky="w")

            ctk.CTkLabel(card, text="Free delivery", text_color="gray")\
                .grid(row=2, column=1, sticky="w")

            # RIGHT SIDE
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.grid(row=0, column=2, rowspan=3, padx=10)

            ctk.CTkLabel(right, text=f"${price}", font=("Arial", 16, "bold"))\
                .pack()

            qty = ctk.CTkFrame(right, fg_color="transparent")
            qty.pack(pady=5)

            ctk.CTkButton(qty, text="-", width=30).pack(side="left", padx=2)
            ctk.CTkLabel(qty, text="1").pack(side="left", padx=5)
            ctk.CTkButton(qty, text="+", width=30).pack(side="left", padx=2)

            ctk.CTkButton(right, text="Remove", width=80).pack(pady=2)
            ctk.CTkButton(right, text="Save", width=80).pack(pady=2)

        # ITEMS
        create_item(1, "Pain Relief Tablets", "12.99", "promo.png")
        create_item(2, "Vitamin C Supplements", "8.49", "vaccine.png")
        create_item(3, "Travel Health Kit", "25.00", "travel.png")
        create_item(4, "Allergy Relief Medicine", "18.50", "info.png")
        create_item(5, "Cold & Flu Kit", "22.00", "promo.png")

        # ================= RIGHT =================
        summary = ctk.CTkFrame(main, corner_radius=12)
        summary.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        ctk.CTkLabel(summary, text="Order Summary", font=("Arial", 20, "bold"))\
            .pack(pady=20)

        ctk.CTkLabel(summary, text="Items (5): $86.98").pack(pady=5)
        ctk.CTkLabel(summary, text="Shipping: Free").pack(pady=5)
        ctk.CTkLabel(summary, text="Tax: $6.00").pack(pady=5)

        ctk.CTkLabel(summary, text="Total: $92.98", font=("Arial", 18, "bold"))\
            .pack(pady=10)

        ctk.CTkButton(summary, text="Proceed to Checkout", height=50)\
            .pack(pady=20)


if __name__ == "__main__":
    app = CartUI()
    app.mainloop()