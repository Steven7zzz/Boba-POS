import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db_manager import DBManager

def add_customer():
    """Inserts a new customer"""
    name = entry_name.get()
    contact = entry_contact.get()

    if not name or not contact:
        messagebox.showerror("Error", "All fields are required!")
        return

    db = DBManager()
    db.execute_query("INSERT INTO Customer (Name, ContactInfo) VALUES (%s, %s)", (name, contact))
    db.close()
    messagebox.showinfo("Success", "Customer added!")

    entry_name.delete(0, tk.END)
    entry_contact.delete(0, tk.END)
    show_customers()

def update_customer():
    """Updates customer details dynamically"""
    selected_item = customer_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a customer to update!")
        return

    customer_id = customer_tree.item(selected_item, "values")[0]
    name = entry_name.get()
    contact = entry_contact.get()

    updates = []
    values = []

    if name:
        updates.append("Name = %s")
        values.append(name)
    if contact:
        updates.append("ContactInfo = %s")
        values.append(contact)

    if not updates:
        messagebox.showerror("Error", "No fields to update!")
        return

    values.append(customer_id)
    query = f"UPDATE Customer SET {', '.join(updates)} WHERE CustomerID = %s"

    db = DBManager()
    db.execute_query(query, tuple(values))
    db.close()

    messagebox.showinfo("Success", "Customer updated!")
    entry_name.delete(0, tk.END)
    entry_contact.delete(0, tk.END)
    show_customers()

def delete_customer():
    """Deletes a customer"""
    selected_item = customer_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select a customer to delete!")
        return

    customer_id = customer_tree.item(selected_item, "values")[0]

    db = DBManager()
    db.execute_query("DELETE FROM Customer WHERE CustomerID = %s", (customer_id,))
    db.close()
    
    messagebox.showinfo("Success", "Customer deleted!")
    show_customers()

def show_customers(filter_text=""):
    """Displays all customers or filters based on search"""
    db = DBManager()

    if filter_text:
        query = "SELECT * FROM Customer WHERE Name LIKE %s OR ContactInfo LIKE %s"
        customers = db.fetch_all(query, (f"%{filter_text}%", f"%{filter_text}%"))
    else:
        customers = db.fetch_all("SELECT * FROM Customer")

    db.close()

    customer_tree.delete(*customer_tree.get_children())
    for customer in customers:
        customer_tree.insert("", "end", values=customer)

def on_row_select(event):
    """Populates entry fields when a row is selected"""
    selected_item = customer_tree.selection()
    if selected_item:
        item = customer_tree.item(selected_item, "values")
        entry_name.delete(0, tk.END)
        entry_name.insert(0, item[1])

        entry_contact.delete(0, tk.END)
        entry_contact.insert(0, item[2])

def search_customers():
    """Filters the customer list based on the search input"""
    search_text = entry_search.get().strip()
    show_customers(search_text)

def customer_ui():
    """Creates the customer UI in a new window"""
    global entry_name, entry_contact, customer_tree, entry_search

    customer_window = tk.Toplevel()
    customer_window.title("Customer Management")

    frame = tk.Frame(customer_window)
    frame.grid(pady=10, padx=20)

    tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="e", padx=5)
    entry_name = tk.Entry(frame, width=30)
    entry_name.grid(row=0, column=1, columnspan=2, sticky="ew", padx=5)

    tk.Label(frame, text="Contact:").grid(row=1, column=0, sticky="e", padx=5)
    entry_contact = tk.Entry(frame, width=30)
    entry_contact.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)

    tk.Button(frame, text="Add Customer", command=add_customer).grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
    tk.Button(frame, text="Update Customer", command=update_customer).grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
    tk.Button(frame, text="Delete Customer", command=delete_customer).grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")

    search_frame = tk.Frame(customer_window)
    search_frame.grid(row=5, column=0, columnspan=3, pady=10, padx=20, sticky="ew")

    tk.Label(search_frame, text="Search:").grid(row=0, column=0, sticky="w", padx=5)
    entry_search = tk.Entry(search_frame, width=40)
    entry_search.grid(row=0, column=1, sticky="ew", padx=5)
    tk.Button(search_frame, text="Search", command=search_customers).grid(row=0, column=2, padx=5)

    tk.Label(customer_window, text="Customers:").grid(row=6, column=0, sticky="w", padx=20)

    columns = ("ID", "Name", "Contact")
    customer_tree = ttk.Treeview(customer_window, columns=columns, show="headings")
    customer_tree.heading("ID", text="ID")
    customer_tree.heading("Name", text="Name")
    customer_tree.heading("Contact", text="Contact")
    customer_tree.grid(row=7, column=0, columnspan=3, pady=5, padx=20, sticky="ew")

    customer_tree.bind("<<TreeviewSelect>>", on_row_select)

    tk.Button(customer_window, text="Refresh List", command=lambda: show_customers("")).grid(
        row=8, column=0, columnspan=3, pady=10, sticky="ew"
    )

    show_customers()