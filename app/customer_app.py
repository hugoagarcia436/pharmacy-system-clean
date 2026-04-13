import customtkinter as ctk

from auth.login_ui import LoginUI
from auth.sign_up_ui import SignUpUI
from app.staff_app import launch_staff_app
from catalog.cosmetic_ui import CosmeticUI
from catalog.firstaid_ui import FirstAidUI
from catalog.medicine_ui import medicineUI
from catalog.personal_ui import PersonalUI
from catalog.travel_ui import TravelUI
from customer.cart_ui import CartUI
from customer.checkout_ui import CheckoutUI
from customer.customer_account_ui import CustomerAccountUI
from customer.customer_dashboard_ui import CustomerDashboard
from customer.customer_orders_ui import CustomerOrdersUI
from customer.customer_payment_methods_ui import CustomerPaymentMethodsUI
from customer.customer_security_ui import CustomerSecurityUI


class CustomerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.current_page = None
        self.pages = {
            "login": LoginUI,
            "signup": SignUpUI,
            "customer_dashboard": CustomerDashboard,
            "customer_orders": CustomerOrdersUI,
            "customer_account": CustomerAccountUI,
            "customer_payments": CustomerPaymentMethodsUI,
            "customer_security": CustomerSecurityUI,
            "cart": CartUI,
            "checkout": CheckoutUI,
            "medicine": medicineUI,
            "cosmetic": CosmeticUI,
            "personal": PersonalUI,
            "firstaid": FirstAidUI,
            "travel": TravelUI,
        }

    def show_page(self, page_name):
        page_class = self.pages[page_name]
        if self.current_page is not None:
            self.current_page.destroy()

        self.current_page = page_class(self, self)
        self.current_page.grid(row=0, column=0, sticky="nsew")

    def open_staff_dashboard(self):
        launch_staff_app("dashboard")
        self.destroy()


def launch_customer_app(start_page="login"):
    app = CustomerApp()
    app.show_page(start_page)
    app.mainloop()


if __name__ == "__main__":
    launch_customer_app()
