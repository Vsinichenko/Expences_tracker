import sqlite3

conn = sqlite3.connect("expenses.db")

cur = conn.cursor()

cur.execute(
    """UPDATE expenses
    SET dt = '2023-07-01'
    where dt = '2023-01-01'
    """
)

conn.commit()
conn.close()
