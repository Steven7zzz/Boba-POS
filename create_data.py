import mysql.connector
import random
from faker import Faker
from datetime import datetime, timedelta

DB_CONFIG = {
    "host": "localhost",
    "user": "root",  
    "password": "password", 
    "database": "BobaShopPOS"
}

fake = Faker()

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

def clear_tables():
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")  
    cursor.execute("TRUNCATE TABLE Payment;")
    cursor.execute("TRUNCATE TABLE OrderDetails;")
    cursor.execute("TRUNCATE TABLE `Order`;")
    cursor.execute("TRUNCATE TABLE Customer;")
    cursor.execute("TRUNCATE TABLE MenuItems;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")  
    conn.commit()
    print("All tables cleared.")

clear_tables()


def generate_customers(n):
    customers = []
    for _ in range(n):
        name = fake.name()
        email = fake.email()
        customers.append((name, email))

    cursor.executemany("INSERT INTO Customer (Name, ContactInfo) VALUES (%s, %s)", customers)
    conn.commit()
    print(f"Inserted {n} customers.")


def generate_menu_items():
    items = [
        ("Milk Tea", 5.50, 100),
        ("Taro Smoothie", 6.00, 50),
        ("Matcha Latte", 6.50, 80),
        ("Brown Sugar Boba", 6.75, 60),
        ("Strawberry Slush", 6.25, 70),
        ("Coconut Shake", 7.00, 50),
        ("Thai Tea", 5.75, 90),
        ("Oolong Milk Tea", 5.95, 85),
        ("Wintermelon Tea", 5.25, 95),
        ("Coffee Jelly Milk Tea", 6.80, 75)
    ]
    cursor.executemany("INSERT INTO MenuItems (Name, Price, QuantityInStock) VALUES (%s, %s, %s)", items)
    conn.commit()
    print(f"Inserted {len(items)} menu items.")


def generate_orders(n):
    orders = []
    
    start_date = datetime.now() - timedelta(days=180)  
    
    for _ in range(n):
        customer_id = random.randint(1, 500)  

        random_days = random.randint(0, 180)  
        random_time = timedelta(hours=random.randint(11, 20), minutes=random.randint(0, 59))
        order_date = start_date + timedelta(days=random_days) + random_time
        order_date_str = order_date.strftime('%Y-%m-%d %H:%M:%S')

        orders.append((customer_id, order_date_str, 0.00))  

    cursor.executemany("INSERT INTO `Order` (CustomerID, OrderDate, TotalAmount) VALUES (%s, %s, %s)", orders)
    conn.commit()
    print(f"Inserted {n} orders. TotalAmount will be updated after OrderDetails generation.")



def generate_order_details():
    cursor.execute("SELECT OrderID FROM `Order`")
    order_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT ItemID, Price FROM MenuItems")
    menu_items = {row[0]: row[1] for row in cursor.fetchall()}  # {ItemID: Price}
    
    order_details = []
    order_totals = {}

    for order_id in order_ids:
        num_items = random.randint(1, 3)  # Each order has 1-3 items
        selected_items = random.sample(menu_items.keys(), num_items)
        
        total_amount = 0  

        for item_id in selected_items:
            quantity = random.randint(1, 5)  
            price = menu_items[item_id]
            subtotal = round(price * quantity, 2)  
            order_details.append((order_id, item_id, quantity, subtotal))
            total_amount += subtotal  

        order_totals[order_id] = round(total_amount, 2)

    # Insert OrderDetails data
    cursor.executemany("INSERT INTO OrderDetails (OrderID, ItemID, Quantity, SubTotal) VALUES (%s, %s, %s, %s)", order_details)
    conn.commit()
    print(f"Inserted {len(order_details)} order details.")

    # Update Order table with correct TotalAmount
    update_orders = [(total, order_id) for order_id, total in order_totals.items()]
    cursor.executemany("UPDATE `Order` SET TotalAmount = %s WHERE OrderID = %s", update_orders)
    conn.commit()
    print("Updated TotalAmount in Orders based on OrderDetails.")


def generate_payments(n):
    payments = []
    
    cursor.execute("SELECT OrderID, TotalAmount FROM `Order`")
    orders = cursor.fetchall()  # List of (OrderID, TotalAmount)

    for order_id, total_amount in orders[:n]:  # Limit to 'n' payments
        total_amount = float(total_amount) 

        if total_amount == 0 or random.random() < 0.1:  
            # 10% of orders remain unpaid (AmountPaid = 0)
            payments.append((order_id, 0.00, None))  # No card number for unpaid orders
        else:
            # Split only if > $10
            num_payments = random.choice([1, 2, 3]) if total_amount > 10 else 1  
            
            amounts = []
            remaining_amount = total_amount
            
            if num_payments == 1:
                amounts.append(total_amount)
            else:
                # Generate random split payments ensuring the total adds up
                for _ in range(num_payments - 1):
                    split = round(random.uniform(1, remaining_amount / 2), 2) 
                    amounts.append(split)
                    remaining_amount -= split
                
                amounts.append(round(remaining_amount, 2)) 

            # Insert multiple payments per order
            for amount in amounts:
                card_number = fake.credit_card_number()[:16]  
                payments.append((order_id, amount, card_number))

    cursor.executemany("INSERT INTO Payment (OrderID, AmountPaid, CardNumber) VALUES (%s, %s, %s)", payments)
    conn.commit()
    print(f"Inserted {len(payments)} payments across {n} orders.")



generate_customers(500)
generate_menu_items()
generate_orders(1000)
generate_order_details()
generate_payments(1000)


cursor.close()
conn.close()
print("Data generation completed successfully.")
