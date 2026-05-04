# Pharmacy+ Project

This project is a pharmacy management and shopping system built with Python, `customtkinter`, saved data files, and SQLite.

It includes:
- customer shopping interfaces
- cart and checkout flow
- customer order history
- employee dashboard, sales, inventory, customer records, and employee records

## Project Files

### Core Files

- `main.py`
  Main entry file used to launch the application flow.

- `login_ui.py`
  Login screen for customers and employees to access the system.

- `sign_up_ui.py`
  Signup screen for creating customer or employee accounts.

- `session_utils.py`
  Helper functions for handling user session data, carts, saved checkout info, payment methods, and account-based storage.

### Database And Setup

- `data/app_data.db`
  Main SQLite database containing inventory, product information, and user records.

- `database_setup.py`
  Creates and initializes the main database tables and starter data.

- `fix_database.py`
  Utility script used to correct or update database data when needed.

### Customer Interfaces

- `customer_dashboard_ui.py`
  Main customer dashboard with category navigation to shopping sections.

- `category_ui.py`
  Shared customer category interface used for medicine, travel, cosmetic, personal care, and first aid. The dashboard passes the selected category, and this screen filters the inventory data.

- `cart_ui.py`
  Customer cart screen for reviewing items, changing quantity, removing items, and proceeding to checkout.

- `checkout_ui.py`
  Customer checkout screen for entering delivery and payment details, saving payment methods, and placing an order.

- `customer_orders_ui.py`
  Customer orders screen for viewing purchase history and order details.

- `customer_account_ui.py`
  Customer account screen for viewing account-related personal information.

### Employee Interfaces

- `employee_dashboard_ui.py`
  Main employee dashboard showing summary stats and recent customer orders.

- `inventory_hub_ui.py`
  Employee inventory workspace for checking stock, restocking items, updating inventory details, and reviewing stock history.

- `employees_ui.py`
  Employee management screen for viewing employee records, employee details, and staff-related actions.

### Saved Data Files

- `cart_data.json`
  Stores the current shopping cart data for the logged-in customer.

- `current_user.json`
  Stores the currently logged-in user session.

- `customer_checkout_data.json`
  Stores saved checkout details for each customer account.

- `customer_orders_data.json`
  Stores placed customer orders and their purchase history.

- `customer_payment_methods.json`
  Stores saved named payment methods for each customer.

### Assets And Generated Files

- `assets/images/`
  Stores the image files used by the interfaces.

- `__pycache__/`
  Python cache folder automatically created when files run.

- `receipts/`
  Stores generated receipt and verification text files created from employee order history.

## Notes

- Customer data is scoped by the currently logged-in account.
- Orders placed in checkout are saved and shown in customer and employee history screens.
- Employee screens are separate from the customer flow and are used for stock, inventory, staff, and order history management.
