import customtkinter as ctk

from staff.employee_dashboard_ui import EmployeeDashboard
from staff.employee_history_ui import EmployeeHistoryUI
from staff.employees_ui import EmployeesUI
from staff.customer_records_ui import CustomerRecordsUI
from staff.inventory_ui import InventoryUI
from staff.order_ui import Order
from staff.process_sales_ui import ProcessSalesUI


class StaffApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.current_page = None
        self.pages = {
            "dashboard": EmployeeDashboard,
            "sales": ProcessSalesUI,
            "inventory": InventoryUI,
            "orders": Order,
            "customers": CustomerRecordsUI,
            "employees": EmployeesUI,
            "history": EmployeeHistoryUI,
        }

    def show_page(self, page_name):
        page_class = self.pages[page_name]
        if self.current_page is not None:
            self.current_page.destroy()

        self.current_page = page_class(self, self)
        self.current_page.grid(row=0, column=0, sticky="nsew")


def launch_staff_app(start_page="dashboard"):
    app = StaffApp()
    app.show_page(start_page)
    app.mainloop()


if __name__ == "__main__":
    launch_staff_app()
