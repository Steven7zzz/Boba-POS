## Installation

### Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **MySQL Server**
- **MySQL Connector for Python**
- **Faker** (for generating fake data)
- **Tkinter** (comes with Python by default)


### Step 1: Set Up Database
Open MySQL and create the database and tables:

```sh
​​CREATE SCHEMA `BobaShopPOS`;
USE BobaShopPOS;

CREATE TABLE Customer (
    CustomerID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    ContactInfo VARCHAR(255) NOT NULL
);

CREATE TABLE MenuItems (
    ItemID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Price DECIMAL(10,2) NOT NULL,
    QuantityInStock INT NOT NULL
);

CREATE TABLE `Order` (
    OrderID INT AUTO_INCREMENT PRIMARY KEY,
    CustomerID INT NULL, (allow guest checkout)
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    TotalAmount DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE
);

CREATE TABLE OrderDetails (
    OrderID INT NOT NULL,
    ItemID INT NOT NULL,
    Quantity INT NOT NULL,
    SubTotal DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (OrderID, ItemID),
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES MenuItems(ItemID) ON DELETE CASCADE
);

CREATE TABLE Payment (
    PaymentID INT AUTO_INCREMENT PRIMARY KEY,
    OrderID INT NOT NULL,
    AmountPaid DECIMAL(10,2) NOT NULL,
    CardNumber VARCHAR(16) NULL,
    FOREIGN KEY (OrderID) REFERENCES `Order`(OrderID) ON DELETE CASCADE
)
```

### Step 2: Clone the Repository
```sh
git clone https://github.com/Steven7zzz/Boba-POS.git
cd BobaS-POS
```

### Step 3: Configure Database Connection
Edit the **DB_CONFIG** in **db_manager.py** and **create_data.py** (if you want some sample data):

```sh
DB_CONFIG = {
    "host": "localhost",
    "user": "...",
    "password": "...",
    "database": "BobaShopPOS"
}
```
Replace "user" and "yourpassword" with your actual MySQL user and password.

### Step 4: Run the GUI Application
create randon data (not reuired)
```sh
python create_data.py
```
Start the POS system with:
```sh
python main.py
```
