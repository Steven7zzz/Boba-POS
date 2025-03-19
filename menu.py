import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from db_manager import DBManager

def add_menu_item():
    """Inserts a new menu item"""
    name = entry_name.get()
    price = entry_price.get()
    quantity = entry_quantity.get()

    if not name or not price or not quantity:
        messagebox.showerror("Error", "All fields are required!")
        return

    db = DBManager()
    db.execute_query("INSERT INTO MenuItems (Name, Price, QuantityInStock) VALUES (%s, %s, %s)",
                     (name, price, quantity))
    db.close()

    messagebox.showinfo("Success", "Menu item added!")
    entry_name.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    show_menu_items()

def delete_menu_item():
    """Deletes a selected menu item"""
    selected_item = menu_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select an item to delete!")
        return

    item_id = menu_tree.item(selected_item, "values")[0]

    db = DBManager()
    db.execute_query("DELETE FROM MenuItems WHERE ItemID = %s", (item_id,))
    db.close()

    messagebox.showinfo("Success", "Menu item deleted!")
    show_menu_items()

def update_menu_item():
    """Updates menu item details dynamically"""
    selected_item = menu_tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Select an item to update!")
        return

    item_id = menu_tree.item(selected_item, "values")[0]
    name = entry_name.get()
    price = entry_price.get()
    quantity = entry_quantity.get()

    updates = []
    values = []

    if name:
        updates.append("Name = %s")
        values.append(name)
    if price:
        updates.append("Price = %s")
        values.append(price)
    if quantity:
        updates.append("QuantityInStock = %s")
        values.append(quantity)

    if not updates:
        messagebox.showerror("Error", "No fields to update!")
        return

    values.append(item_id)
    query = f"UPDATE MenuItems SET {', '.join(updates)} WHERE ItemID = %s"

    db = DBManager()
    db.execute_query(query, tuple(values))
    db.close()

    messagebox.showinfo("Success", "Menu item updated!")
    show_menu_items()

def show_menu_items():
    """Displays all menu items in the treeview"""
    db = DBManager()
    items = db.fetch_all("SELECT * FROM MenuItems")
    db.close()

    menu_tree.delete(*menu_tree.get_children())
    for item in items:
        menu_tree.insert("", "end", values=item)

def on_row_select(event):
    """Populates entry fields when a row is selected"""
    selected_item = menu_tree.selection()
    if selected_item:
        item = menu_tree.item(selected_item, "values")
        entry_name.delete(0, tk.END)
        entry_name.insert(0, item[1])

        entry_price.delete(0, tk.END)
        entry_price.insert(0, item[2])

        entry_quantity.delete(0, tk.END)
        entry_quantity.insert(0, item[3])

def menu_ui():
    """Creates the menu UI in a new window"""
    global entry_name, entry_price, entry_quantity, menu_tree
    
    menu_window = tk.Toplevel()
    menu_window.title("Menu Management")

    frame = tk.Frame(menu_window)
    frame.grid(pady=10)

    tk.Label(frame, text="Name:").grid(row=0, column=0, sticky="w")
    entry_name = tk.Entry(frame)
    entry_name.grid(row=0, column=1)

    tk.Label(frame, text="Price:").grid(row=1, column=0, sticky="w")
    entry_price = tk.Entry(frame)
    entry_price.grid(row=1, column=1)

    tk.Label(frame, text="Stock:").grid(row=2, column=0, sticky="w")
    entry_quantity = tk.Entry(frame)
    entry_quantity.grid(row=2, column=1)

    tk.Button(frame, text="Add Item", command=add_menu_item).grid(row=3, columnspan=2, pady=5)
    tk.Button(frame, text="Update Item", command=update_menu_item).grid(row=4, columnspan=2, pady=5)
    tk.Button(frame, text="Delete Item", command=delete_menu_item).grid(row=5, columnspan=2, pady=5)

    tk.Label(menu_window, text="Menu Items:").grid(row=6, column=0, sticky="w")

    columns = ("ID", "Name", "Price", "Stock")
    menu_tree = ttk.Treeview(menu_window, columns=columns, show="headings")
    menu_tree.heading("ID", text="ID")
    menu_tree.heading("Name", text="Name")
    menu_tree.heading("Price", text="Price")
    menu_tree.heading("Stock", text="Stock")
    menu_tree.grid(row=7, column=0, columnspan=2, pady=5)

    menu_tree.bind("<<TreeviewSelect>>", on_row_select)

    tk.Button(menu_window, text="Refresh List", command=show_menu_items).grid(row=8, column=0, columnspan=2)

    show_menu_items()
