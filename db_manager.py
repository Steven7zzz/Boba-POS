import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "BobaShopPOS"
}

class DBManager:
    def __init__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        """Executes a SQL query (INSERT, UPDATE, DELETE)"""
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def fetch_all(self, query, params=None):
        """Executes a SELECT query and returns all results"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        """Executes a SELECT query and returns one result"""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()
