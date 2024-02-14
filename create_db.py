import sqlite3

conn = sqlite3.connect("expenses.db")

cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS expenses
                (
            dt DATE NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            price Real NOT NULL)"""
)


cur.execute(
    """CREATE TABLE IF NOT EXISTS income
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
            dt DATE NOT NULL,
            description TEXT NOT NULL,
            amount Real NOT NULL)"""
)

cur.execute(
    """CREATE TABLE IF NOT EXISTS fixed_price_categories
                (
            category TEXT UNIQUE NOT NULL,
            price Real NOT NULL)"""
)


conn.commit()
conn.close()
