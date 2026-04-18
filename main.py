#Start the app, and open the login page first.
#Go into the app folder
#Open/use customer_app.py
#Find the function called launch_customer_app
#Bring that function into main.py

# Import the function that starts the customer-facing application.
# This function is defined in app/customer_app.py.
from app.customer_app import launch_customer_app

## If another file imports main.py, this block will not automatically run.
# If another file imports main.py, this block will not automatically run.
if __name__ == "__main__":
    #Start the application on the login page.
    # The word "login" matches a page name registered inside CustomerApp.
    launch_customer_app("login")
