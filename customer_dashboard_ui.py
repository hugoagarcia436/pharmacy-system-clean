import customtkinter as ctk
from PIL import Image
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CustomerDashboard(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Customer Dashboard")
        self.geometry("1350x800")

        base_path = os.path.dirname(os.path.realpath(__file__))
        img_path = os.path.join(base_path, "assets", "images")

        # ================= ROOT =================
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ================= HEADER =================
        header = ctk.CTkFrame(self, height=70)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Pharmacy+", font=("Arial", 20, "bold")).grid(row=0, column=0, padx=15)

        search = ctk.CTkEntry(header, placeholder_text="Search products...", height=40)
        search.grid(row=0, column=1, sticky="ew", padx=20)

        ctk.CTkButton(header, text="Orders").grid(row=0, column=2, padx=5)
        ctk.CTkButton(header, text="My Cart 🛒").grid(row=0, column=3, padx=5)
        ctk.CTkButton(header, text="Account").grid(row=0, column=4, padx=10)

        # ================= HERO =================
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

        ctk.CTkLabel(hero, image=promo_img, text="").grid(row=0, column=1, padx=20)

        # ================= GRID =================
        main = ctk.CTkFrame(self)
        main.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        for i in range(4):
            main.grid_columnconfigure(i, weight=1)

        # ---------- BOX FUNCTION ----------
        def create_box(parent, row, col, title, images):
            box = ctk.CTkFrame(parent, corner_radius=10)
            box.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            ctk.CTkLabel(
                box,
                text=title,
                font=("Arial", 16, "bold")
            ).pack(anchor="w", padx=10, pady=10)

            grid = ctk.CTkFrame(box, fg_color="transparent")
            grid.pack()

            # 2x2 image grid
            for i in range(2):
                grid.grid_rowconfigure(i, weight=1)
                grid.grid_columnconfigure(i, weight=1)

            idx = 0
            for r in range(2):
                for c in range(2):
                    if idx < len(images):
                        img = ctk.CTkImage(
                            light_image=Image.open(os.path.join(img_path, images[idx])),
                            size=(120, 90)
                        )
                        ctk.CTkLabel(grid, image=img, text="").grid(row=r, column=c, padx=5, pady=5)
                        idx += 1

        # ---------- ROW 1 ----------
        create_box(main, 0, 0, "Manage Prescriptions", [
            "banner_main.png", "info.png", "promo.png", "travel.png"
        ])

        create_box(main, 0, 1, "Health & Wellness", [
            "vaccine.png", "travel.png", "info.png", "promo.png"
        ])

        create_box(main, 0, 2, "Best Deals", [
            "promo.png", "vaccine.png", "banner_main.png", "info.png"
        ])

        # ---------- SIGN IN BOX ----------
        sign_box = ctk.CTkFrame(main, corner_radius=10)
        sign_box.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        ctk.CTkLabel(sign_box, text="Sign in for the best experience", font=("Arial", 16, "bold")).pack(pady=20)

        ctk.CTkButton(sign_box, text="Sign In Securely", width=200).pack(pady=10)

        # ---------- ROW 2 ----------
        create_box(main, 1, 0, "Seasonal Care", [
            "info.png", "vaccine.png", "travel.png", "promo.png"
        ])

        create_box(main, 1, 1, "Travel Essentials", [
            "travel.png", "banner_main.png", "info.png", "promo.png"
        ])

        create_box(main, 1, 2, "Pharmacy Picks", [
            "banner_main.png", "promo.png", "vaccine.png", "info.png"
        ])

        ad_box = ctk.CTkFrame(main, corner_radius=10)
        ad_box.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")

        ad_img = ctk.CTkImage(
            light_image=Image.open(os.path.join(img_path, "promo.png")),
            size=(250, 150)
        )

        ctk.CTkLabel(ad_box, image=ad_img, text="").pack(pady=10)


if __name__ == "__main__":
    app = CustomerDashboard()
    app.mainloop()