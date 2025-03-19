import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel
from db_manager import DBManager


def fetch_customers():
    """Fetch all customers from the database."""
    db = DBManager()
    customers = db.fetch_all("SELECT CustomerID, Name FROM Customer")
    db.close()
    return {customer[1]: customer[0] for customer in customers}  # {Name: CustomerID}

def update_customer_suggestions(event):
    """Updates the suggestion list based on the search query."""
    search_term = entry_customer_name.get().lower()
    listbox_customer.delete(0, tk.END)

    if not search_term:
        return

    for name in customer_data:
        if search_term in name.lower():
            listbox_customer.insert(tk.END, name)

def select_customer(event):
    """Selects a customer from the listbox."""
    selected_name = listbox_customer.get(listbox_customer.curselection())
    entry_customer_name.delete(0, tk.END)
    entry_customer_name.insert(0, selected_name)

    global selected_customer_id
    selected_customer_id = customer_data[selected_name]   

    listbox_customer.delete(0, tk.END)  # Hide suggestions

def fetch_menu_items():
    """Fetches available menu items from the database, marking low-stock items."""
    db = DBManager()
    items = db.fetch_all("SELECT ItemID, Name, Price, QuantityInStock FROM MenuItems WHERE QuantityInStock > 0")
    db.close()

    menu_dict = {}

    for item in items:
        item_id, name, price, stock = item

        display_name = f"{name} (Low Stock)" if stock <= 10 else name
        
        menu_dict[display_name] = (item_id, price, name)
    
    return menu_dict  # {Display Name: (ItemID, Price, Original Name)}

def add_item_to_order():
    """Adds an item to the order list while handling low-stock labels."""
    selected_display_name = menu_var.get()

    if selected_display_name not in menu_items:
        messagebox.showerror("Error", "Invalid menu item selected.")
        return

    item_id, price, original_name = menu_items[selected_display_name]  # Get actual name

    quantity = quantity_var.get()
    if quantity <= 0:
        messagebox.showerror("Error", "Quantity must be at least 1.")
        return

    subtotal = price * quantity
    order_items.append((item_id, original_name, quantity, subtotal))  # Use original name
    update_order_preview()


def update_order_preview():
    """Updates the order preview box."""
    text_order_preview.delete("1.0", tk.END)
    total_amount = sum(item[3] for item in order_items)
    
    for item in order_items:
        text_order_preview.insert(tk.END, f"{item[1]} - Qty: {item[2]}, Subtotal: ${item[3]:.2f}\n")
    
    text_order_preview.insert(tk.END, f"\nTotal: ${total_amount:.2f}")

def open_edit_popup():
    """Opens a popup window to edit or remove an item."""
    try:
        selected_index = text_order_preview.index(tk.INSERT).split(".")[0]  # Get selected line index
        selected_index = int(selected_index) - 1  # Convert to 0-based index

        if selected_index < 0 or selected_index >= len(order_items):
            return

        item_id, item_name, quantity, subtotal = order_items[selected_index]

        # Create popup window
        popup = Toplevel()
        popup.title("Edit Order Item")
        popup.geometry("300x200")

        tk.Label(popup, text=f"Editing: {item_name}").pack(pady=5)

        # Dropdown to change item
        new_item_var = tk.StringVar(popup)
        new_item_var.set(item_name)  # Default selection
        dropdown = tk.OptionMenu(popup, new_item_var, *menu_items.keys())
        dropdown.pack(pady=5)

        # Entry to update quantity
        quantity_var = tk.IntVar(popup, value=quantity)
        tk.Label(popup, text="New Quantity:").pack()
        quantity_entry = tk.Entry(popup, textvariable=quantity_var)
        quantity_entry.pack(pady=5)

        def save_changes():
            """Saves changes to the selected item."""
            new_item_name = new_item_var.get()
            if new_item_name not in menu_items:
                messagebox.showerror("Error", "Invalid item selected.")
                return

            new_quantity = quantity_var.get()
            if new_quantity <= 0:
                messagebox.showerror("Error", "Quantity must be at least 1.")
                return

            new_item_id, new_price = menu_items[new_item_name]
            new_subtotal = new_price * new_quantity
            order_items[selected_index] = (new_item_id, new_item_name, new_quantity, new_subtotal)

            update_order_preview()
            popup.destroy()

        def remove_item():
            """Removes the item from the order."""
            order_items.pop(selected_index)
            update_order_preview()
            popup.destroy()

        tk.Button(popup, text="Save Changes", command=save_changes).pack(pady=5)
        tk.Button(popup, text="Remove Item", command=remove_item, fg="red").pack(pady=5)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to edit item: {e}")


def place_order():
    """Places a new order, handles payment, and updates inventory."""
    global order_items  # Ensure order_items is accessible
    global selected_customer_id  # Get the selected customer

    customer_id = selected_customer_id  # Use selected customer ID
    if not customer_id:
        customer_id = None  # Allow guest checkout

    if not order_items:
        messagebox.showerror("Error", "No items added to the order.")
        return

    db = DBManager()

    try:
        # Create the order
        db.execute_query("INSERT INTO `Order` (CustomerID, OrderDate, TotalAmount) VALUES (%s, NOW(), 0.00)", (customer_id,))
        order_id = db.fetch_one("SELECT LAST_INSERT_ID()")[0]

        # Insert order details and update inventory
        for item_id, _, quantity, subtotal in order_items:
            db.execute_query("INSERT INTO OrderDetails (OrderID, ItemID, Quantity, SubTotal) VALUES (%s, %s, %s, %s)",
                           (order_id, item_id, quantity, subtotal))
            db.execute_query("UPDATE MenuItems SET QuantityInStock = QuantityInStock - %s WHERE ItemID = %s", (quantity, item_id))

        total_amount = float(sum(item[3] for item in order_items))

        # Ask for payment (can be 0)
        remaining_amount = total_amount
        payments = []
        while remaining_amount > 0:
            payment_method = simpledialog.askstring("Payment", "Enter card to pay with card or leave blank for unpaid:")
            if not payment_method:
                payments.append((order_id, 0.00, None))  # Unpaid order
                remaining_amount = 0
                break

            amount = simpledialog.askfloat("Payment", f"Remaining: ${remaining_amount:.2f}\n fEnter amount for {payment_method}:")
            if amount < 0 or amount > remaining_amount:
                messagebox.showerror("Error", "Invalid amount entered.")
                continue

            card_number = None
            if payment_method.lower() == "card":
                card_number = simpledialog.askstring("Payment", "Enter at most 16 digits of card number:")
                if not card_number or len(card_number) >= 16:
                    messagebox.showerror("Error", "Invalid card number.")
                    continue

            payments.append((order_id, amount, card_number))
            remaining_amount -= amount

        # Save payments
        for order_id, amount, card_number in payments:
            db.execute_query("INSERT INTO Payment (OrderID, AmountPaid, CardNumber) VALUES (%s, %s, %s)", (order_id, amount, card_number))

        # Update total amount in Order table
        db.execute_query("UPDATE `Order` SET TotalAmount = %s WHERE OrderID = %s", (total_amount, order_id))

        messagebox.showinfo("Success", f"Order placed successfully! Total: ${total_amount:.2f}")

        order_items.clear()
        update_order_preview()
        show_orders()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to place order: {e}")
    finally:
        db.close()

def show_orders():
    """Displays all orders with customer names and binds a click event to show order details."""
    global text_orders, orders_data
    db = DBManager()

    orders = db.fetch_all("""
        SELECT o.OrderID, COALESCE(c.Name, 'Guest') AS CustomerName, o.OrderDate, o.TotalAmount
        FROM `Order` o
        LEFT JOIN Customer c ON o.CustomerID = c.CustomerID
        ORDER BY o.OrderID DESC
    """)

    db.close()

    # Store orders globally
    orders_data = orders

    # Clear the text box and display orders
    text_orders.delete("1.0", tk.END)
    for order in orders:
        text_orders.insert(tk.END, f"ID: {order[0]}, Customer: {order[1]}, Date: {order[2]}, Total: ${order[3]:.2f}\n")

    # Bind click event to show order details
    text_orders.bind("<ButtonRelease-1>", lambda event: show_order_details(event, orders_data))

def show_unpaid_orders():
    """Displays all unpaid orders and allows updating their payment."""
    global text_orders
    db = DBManager()
    
    orders = db.fetch_all("""
        SELECT o.OrderID, COALESCE(c.Name, 'Guest') AS CustomerName, o.OrderDate, o.TotalAmount,
               COALESCE(SUM(p.AmountPaid), 0) AS AmountPaid
        FROM `Order` o
        LEFT JOIN Customer c ON o.CustomerID = c.CustomerID
        LEFT JOIN Payment p ON o.OrderID = p.OrderID
        GROUP BY o.OrderID, c.Name, o.OrderDate, o.TotalAmount
        HAVING TotalAmount > AmountPaid
        ORDER BY o.OrderID DESC
    """)
    
    db.close()

    # Clear text_orders and display unpaid orders
    text_orders.delete("1.0", tk.END)
    for order in orders:
        remaining_balance = order[3] - order[4]  # TotalAmount - AmountPaid
        text_orders.insert(tk.END, f"ID: {order[0]}, Customer: {order[1]}, Date: {order[2]}, Due: ${remaining_balance:.2f}\n")

    # Bind click event to update payment
    text_orders.bind("<ButtonRelease-1>", lambda event: open_update_payment_popup(event, orders))

def open_update_payment_popup(event, orders):
    """Opens a popup window to update payment for a selected unpaid order."""
    try:
        index = text_orders.index(tk.INSERT).split(".")[0]  # Get clicked line index
        index = int(index) - 1  # Convert to 0-based index

        if index < 0 or index >= len(orders):
            return

        order_id, customer_name, order_date, total_amount, amount_paid = orders[index]
        remaining_balance = total_amount - amount_paid 

        # Create popup window
        popup = Toplevel()
        popup.title(f"Update Payment - Order {order_id}")
        popup.geometry("300x250")

        tk.Label(popup, text=f"Customer: {customer_name}").pack(pady=5)
        tk.Label(popup, text=f"Total: ${total_amount:.2f}, Paid: ${amount_paid:.2f}, Due: ${remaining_balance:.2f}").pack()

        # Payment method entry
        tk.Label(popup, text="Card Number:").pack()
        payment_method_var = tk.StringVar()
        tk.Entry(popup, textvariable=payment_method_var).pack(pady=5)

        # Amount paid entry
        tk.Label(popup, text="Amount Paid:").pack()
        amount_paid_var = tk.DoubleVar()
        tk.Entry(popup, textvariable=amount_paid_var).pack(pady=5)

        def save_payment():
            """Updates the payment in the database."""
            payment_method = payment_method_var.get().strip()
            amount = amount_paid_var.get()

            if not payment_method:
                messagebox.showerror("Error", "Please enter a payment method.")
                return

            if amount <= 0 or amount > remaining_balance:
                messagebox.showerror("Error", "Invalid payment amount.")
                return

            db = DBManager()
            try:
                # Delete old payment, should use update if we each order can have only one payment. 
                db.execute_query("DELETE FROM Payment WHERE OrderID = %s AND AmountPaid = 0.00", (order_id,))

                # Insert new payment (allows split payments)
                db.execute_query("INSERT INTO Payment (OrderID, AmountPaid, CardNumber) VALUES (%s, %s, %s)", (order_id, amount, payment_method))

                # Check total paid after update
                new_total_paid = db.fetch_one("SELECT COALESCE(SUM(AmountPaid), 0) FROM Payment WHERE OrderID = %s", (order_id,))[0]

                # If fully paid, mark as complete
                if new_total_paid >= total_amount:
                    messagebox.showinfo("Success", f"Order {order_id} is now fully paid!")

                popup.destroy()
                show_unpaid_orders() 

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update payment: {e}")

            finally:
                db.close()

        tk.Button(popup, text="Save Payment", command=save_payment).pack(pady=5)
        tk.Button(popup, text="Cancel", command=popup.destroy).pack(pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to update payment: {e}")

def show_order_details(event, orders):
    """Opens a popup showing details of the clicked order."""
    try:
        index = text_orders.index(tk.INSERT).split(".")[0]  # Get clicked line index
        index = int(index) - 1  # Convert to 0-based index

        if index < 0 or index >= len(orders):
            return

        order_id, customer_name, order_date, total_amount = orders[index]

        db = DBManager()
        order_details = db.fetch_all("""
            SELECT mi.Name, od.Quantity, od.SubTotal
            FROM OrderDetails od
            JOIN MenuItems mi ON od.ItemID = mi.ItemID
            WHERE od.OrderID = %s
        """, (order_id,))
        db.close()

        popup = Toplevel()
        popup.title(f"Order Details - {order_id}")
        popup.geometry("350x300")

        tk.Label(popup, text=f"Customer: {customer_name}").pack(pady=5)
        tk.Label(popup, text=f"Order Date: {order_date}").pack()
        tk.Label(popup, text=f"Total Amount: ${total_amount:.2f}").pack(pady=5)

        text_details = tk.Text(popup, height=10, width=50)
        text_details.pack(pady=5)

        for item in order_details:
            text_details.insert(tk.END, f"{item[0]} - Qty: {item[1]}, Subtotal: ${item[2]:.2f}\n")

        tk.Button(popup, text="Close", command=popup.destroy).pack(pady=5)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch order details: {e}")


def order_ui():
    """Creates the order UI in a new window"""
    global entry_customer_name, listbox_customer, text_orders, text_order_preview, menu_var, quantity_var, order_items, menu_items, customer_data, selected_customer_id

    order_window = tk.Toplevel()
    order_window.title("Order Management")

    frame = tk.Frame(order_window)
    frame.grid(pady=10)

    customer_data = fetch_customers()
    selected_customer_id = None  # Store selected customer

    tk.Label(frame, text="Search customer name, leave blank for guest checkout").grid(row=0, column=0, sticky="w")
    entry_customer_name = tk.Entry(frame)
    entry_customer_name.grid(row=0, column=1)
    entry_customer_name.bind("<KeyRelease>", update_customer_suggestions)

    listbox_customer = tk.Listbox(frame, height=5)
    listbox_customer.grid(row=1, column=1)
    listbox_customer.bind("<ButtonRelease-1>", select_customer)

    menu_items = fetch_menu_items()
    menu_var = tk.StringVar(order_window)
    menu_var.set(next(iter(menu_items)))  # Default to first item

    tk.Label(frame, text="Select Item:").grid(row=2, column=0, sticky="w")
    dropdown_menu = tk.OptionMenu(frame, menu_var, *menu_items.keys())
    dropdown_menu.grid(row=2, column=1)

    tk.Label(frame, text="Quantity:").grid(row=3, column=0, sticky="w")
    quantity_var = tk.IntVar(order_window, value=1)
    tk.Entry(frame, textvariable=quantity_var).grid(row=3, column=1)

    tk.Button(frame, text="Add Item", command=add_item_to_order).grid(row=4, columnspan=2, pady=5)

    tk.Label(order_window, text="Order Preview (Click to Edit):").grid(row=5, column=0, sticky="w")
    text_order_preview = tk.Text(order_window, height=5, width=60)
    text_order_preview.grid(row=6, column=0, columnspan=2)
    text_order_preview.bind("<ButtonRelease-1>", lambda event: open_edit_popup())  # Enable editing


    tk.Button(order_window, text="Place Order", command=place_order).grid(row=7, column=0, columnspan=2, pady=5)


    button_frame = tk.Frame(order_window)
    button_frame.grid(row=8, column=0, columnspan=2, pady=5)

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    tk.Button(button_frame, text="Unpaid Orders", command=show_unpaid_orders).grid(row=0, column=0, padx=5, sticky="ew")
    tk.Button(button_frame, text="Refresh Orders", command=show_orders).grid(row=0, column=1, padx=5, sticky="ew")


    tk.Label(order_window, text="Newest Orders:").grid(row=9, column=0, sticky="w")
    text_orders = tk.Text(order_window, height=10, width=80)
    text_orders.grid(row=10, column=0, columnspan=2)

    order_items = []
    show_orders()





