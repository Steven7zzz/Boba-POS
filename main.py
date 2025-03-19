import tkinter as tk
from customer import customer_ui
from menu import menu_ui
from order import order_ui
from interesting import interesting_ui

def open_customer():
    customer_ui()

def open_menu():
    menu_ui()

def open_order():
    order_ui()

def open_interesting():
    interesting_ui()


root = tk.Tk()
root.title("Boba POS System")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

tk.Label(frame, text="Boba Shop POS System", font=("Arial", 16, "bold")).pack(pady=10)

tk.Button(frame, text="Manage Customers", command=open_customer).pack(fill=tk.X, pady=5)
tk.Button(frame, text="Manage Menu Items", command=open_menu).pack(fill=tk.X, pady=5)
tk.Button(frame, text="Manage Orders", command=open_order).pack(fill=tk.X, pady=5)
tk.Button(frame, text="Interesting Queries", command=open_interesting).pack(fill=tk.X, pady=5) 

root.mainloop()
