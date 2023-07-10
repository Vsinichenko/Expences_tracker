import sqlite3

conn = sqlite3.connect("expenses.db")

cur = conn.cursor()

cur.execute(
    """CREATE TABLE IF NOT EXISTS expenses
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
            dt DATE NOT NULL,
            description TEXT,
            category TEXT NOT NULL,
            price Real NOT NULL)"""
)

conn.commit()
conn.close()
