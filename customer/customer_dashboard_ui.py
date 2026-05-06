import customtkinter as ctk
from PIL import Image
import os
from shared.paths import IMAGES_DIR

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CustomerDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.controller.title("Customer Dashboard")
        self.controller.geometry("1350x800")
        self.image_refs = []
        img_path = IMAGES_DIR

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)
        ctk.CTkEntry(header, placeholder_text="Search products...", height=40).grid(row=0, column=1, sticky="ew", padx=20)
        ctk.CTkButton(header, text="Dashboard", command=self.open_dashboard).grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="Orders", command=self.open_orders).grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="My Cart", command=self.open_cart).grid(row=0, column=4, padx=5)
        ctk.CTkButton(header, text="Account", command=self.open_account).grid(row=0, column=5, padx=10)

        hero = ctk.CTkFrame(self, height=180, fg_color="#1f6feb")
        hero.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        hero.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            hero,
            text="Fast, reliable healthcare\nand savings",
            font=("Arial", 28, "bold"),
            text_color="white"
        ).grid(row=0, column=0, padx=30, pady=30, sticky="w")

        promo_img = ctk.CTkImage(
            light_image=Image.open(os.path.join(img_path, "promo.png")),
            size=(300, 120)
        )
        self.image_refs.append(promo_img)
        ctk.CTkLabel(hero, image=promo_img, text="").grid(row=0, column=1, padx=20)

        main = ctk.CTkScrollableFrame(self)
        main.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(3):
            main.grid_columnconfigure(i, weight=1)

        def create_box(parent, row, col, title, image_file, command=None, subtitle=None):
            box = ctk.CTkFrame(parent, corner_radius=10)
            box.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            box.grid_columnconfigure(0, weight=1)

            title_label = ctk.CTkLabel(box, text=title, font=("Arial", 16, "bold"))
            title_label.pack(anchor="w", padx=10, pady=(10, 6))

            subtitle_label = None
            if subtitle:
                subtitle_label = ctk.CTkLabel(
                    box,
                    text=subtitle,
                    text_color="gray",
                    justify="left",
                    wraplength=250
                )
                subtitle_label.pack(anchor="w", padx=10, pady=(0, 8))

            img = ctk.CTkImage(
                light_image=Image.open(os.path.join(img_path, image_file)),
                size=(290, 185)
            )
            self.image_refs.append(img)
            image_label = ctk.CTkLabel(box, image=img, text="")
            image_label.pack(padx=10, pady=(0, 10))

            if command is not None:
                widgets = [box, title_label, image_label]
                if subtitle_label is not None:
                    widgets.append(subtitle_label)

                for widget in widgets:
                    widget.bind("<Button-1>", lambda event, action=command: action())
                    widget.configure(cursor="hand2")

        ctk.CTkLabel(
            main,
            text="Shop by Category",
            font=("Arial", 22, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        create_box(
            main, 1, 0, "Medicine", "info.png",
            command=lambda: self.open_section("medicine"),
            subtitle="Prescription support and everyday medicines."
        )
        create_box(
            main, 1, 1, "Travel", "travel.png",
            command=lambda: self.open_section("travel"),
            subtitle="Travel-size products and on-the-go essentials."
        )
        create_box(
            main, 1, 2, "Cosmetic", "promo.png",
            command=lambda: self.open_section("cosmetic"),
            subtitle="Skin care and beauty picks for daily use."
        )
        create_box(
            main, 2, 0, "Personal Care", "banner_main.png",
            command=lambda: self.open_section("personal"),
            subtitle="Hygiene and self-care products in one place."
        )
        create_box(
            main, 2, 1, "First Aid", "vaccine.png",
            command=lambda: self.open_section("firstaid"),
            subtitle="Quick-access first aid basics for home and travel."
        )

    def open_section(self, page_name):
        self.controller.show_page(page_name)

    def open_orders(self):
        self.controller.show_page("customer_orders")

    def open_dashboard(self):
        pass

    def open_cart(self):
        self.controller.show_page("cart")

    def open_account(self):
        self.controller.show_page("customer_account")


if __name__ == "__main__":
    from app.customer_app import launch_customer_app

    launch_customer_app("customer_dashboard")
