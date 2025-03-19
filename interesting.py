import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DBManager  

def fetch_query_results(query):
    """Fetch results from the database using DBManager."""
    try:
        db = DBManager()
        results = db.fetch_all(query)
        db.close()
        return results
    except Exception as e:
        messagebox.showerror("Database Error", str(e))
        return []

def display_results(tree, query, column_names):
    """Fetch and display query results in the Treeview table."""
    results = fetch_query_results(query)

    tree.delete(*tree.get_children())
    tree["columns"] = column_names

    for col in column_names:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    for row in results:
        tree.insert("", tk.END, values=row)

def interesting_ui():
    """Create the UI for interesting queries."""
    root = tk.Toplevel()
    root.title("Interesting Queries")

    query_options = [
        "Top 5 Best-Selling Items",
        "Loyal Customers (Most Spent)",
        "Customers with No Orders",
        "Monthly Revenue Trends",
        "Average Order Value",
        "Most Recent Order per Customer"
    ]

    queries = {
        query_options[0]: {
            "query": """
                SELECT mi.Name AS ItemName, SUM(od.Quantity) AS TotalSold
                FROM OrderDetails od
                JOIN MenuItems mi ON od.ItemID = mi.ItemID
                GROUP BY mi.Name
                ORDER BY TotalSold DESC
                LIMIT 5;
            """,
            "columns": ["Item Name", "Total Sold"]
        },
        query_options[1]: {
            "query": """
                SELECT c.CustomerID, c.Name AS CustomerName, SUM(o.TotalAmount) AS TotalSpent
                FROM Customer c
                JOIN `Order` o ON c.CustomerID = o.CustomerID
                GROUP BY c.CustomerID, c.Name
                ORDER BY TotalSpent DESC
                LIMIT 5;
            """,
            "columns": ["Customer ID", "Customer Name", "Total Spent"]
        },
        query_options[2]: {
            "query": """
                SELECT c.CustomerID, c.Name AS CustomerName
                FROM Customer c
                LEFT JOIN `Order` o ON c.CustomerID = o.CustomerID
                WHERE o.OrderID IS NULL;
            """,
            "columns": ["Customer ID", "Customer Name"]
        },
        query_options[3]: {
            "query": """
                SELECT DATE_FORMAT(OrderDate, '%Y-%m') AS Month, SUM(TotalAmount) AS MonthlyRevenue
                FROM `Order`
                GROUP BY Month
                ORDER BY Month DESC;
            """,
            "columns": ["Month", "Monthly Revenue"]
        },
        query_options[4]: {
            "query": """
                SELECT AVG(TotalAmount) AS AvgOrderValue FROM `Order`;
            """,
            "columns": ["Average Order Value"]
        },
        query_options[5] : {
            "query": """
                WITH ranked_orders AS (
                    SELECT o.CustomerID, o.OrderID, o.OrderDate, o.TotalAmount,
                        RANK() OVER (PARTITION BY o.CustomerID ORDER BY o.OrderDate DESC) AS rnk
                    FROM `Order` o
                    WHERE o.CustomerID IS NOT NULL
                )
                SELECT c.CustomerID, c.Name AS CustomerName, r.OrderID, r.OrderDate, r.TotalAmount
                FROM ranked_orders r
                JOIN Customer c ON r.CustomerID = c.CustomerID
                WHERE r.rnk = 1;
            """,
            "columns": ["Customer ID", "Customer Name", "Order ID", "Order Date", "Total Amount"]
        }
    }

    # Dropdown selection
    tk.Label(root, text="Select a Query:", font=("Arial", 12)).pack(pady=5)
    selected_query = tk.StringVar(root)
    selected_query.set(query_options[0])

    dropdown = tk.OptionMenu(root, selected_query, *query_options)
    dropdown.pack(pady=5)

    # Treeview table setup
    tree = ttk.Treeview(root, show="headings")
    tree.pack(pady=10, fill=tk.BOTH, expand=True)

    # Fetch and display results when query is selected
    def run_query():
        query_info = queries[selected_query.get()]
        display_results(tree, query_info["query"], query_info["columns"])

    tk.Button(root, text="Run Query", command=run_query).pack(pady=10)

    root.mainloop()
