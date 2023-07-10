import sqlite3
import datetime
from tabulate import tabulate


class ExpenseTracker:
    """Track personal expenses and view summaries by category and month"""

    FIXED_PRICE_CATEGORIES = {
        "Therapy": 45,
        "Rent": 655,
        "Internet": 24.9,
        "Phone": 15,
        "Electricity": 40,
        "Youtube": 4.5,
        "Entgeltabrechnung": 3.9,
    }
    DB_FILENAME = "expenses.db"

    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.DB_FILENAME)
        self.cur = self.conn.cursor()
        return self

    def execute_and_print(self, title, query):
        """Execute the query and print the results in a prettified table"""
        print(title.upper())
        self.cur.execute(query)
        column_names = [description[0] for description in self.cur.description]
        expenses = self.cur.fetchall()
        print(tabulate(expenses, headers=column_names, tablefmt="pretty"))

    def get_date(self):
        """Get the date of the expense"""
        print(
            "Is it current month's expense? Print 1 for yes, 2 - for previous month is assumed"
        )
        date_choice = int(input())
        if date_choice == 1:
            # first day ot the current month
            date = datetime.date.today()
        else:
            # first day of the previous month
            now = datetime.date.today()
            first_day_of_current_month = now.replace(day=1)
            last_day_of_previous_month = (
                first_day_of_current_month - datetime.timedelta(days=1)
            )
            date = last_day_of_previous_month.replace(day=1)
        return date

    def add_expense(self):
        date = self.get_date()

        self.cur.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
        categories = self.cur.fetchall()
        print("Select a category by number:")
        for i, category in enumerate(categories):
            print(f"{i + 1}. {category[0]}")
        print(len(categories) + 1, "Add a new category")
        category_idx = int(input())
        if category_idx == len(categories) + 1:
            category = input("Enter the new category name: ")
        else:
            category = categories[category_idx - 1][0]

        if category in self.FIXED_PRICE_CATEGORIES:
            price = self.FIXED_PRICE_CATEGORIES[category]
            description = ""
        else:
            price = float(input("Enter price: ").replace(",", "."))
            description = input("Enter description or leave empty: ")

        self.cur.execute(
            """INSERT INTO expenses (dt, description, category, price)
                                VALUES (?, ?, ?, ?)""",
            (date, description, category, price),
        )
        self.conn.commit()

    def main(self):
        """Get user input and execute the corresponding function"""
        while True:
            print("\nSelect an option:")
            print("1. Add expense")
            print("2. View summary by category")
            print("3. View summary by major category")
            print("4. View summary by month")
            print("5. List all expenses")
            print("6. Exit")

            try:
                choice = int(input())
            except ValueError:
                print("Invalid choice")
                continue

            if choice == 1:
                self.add_expense()

            elif choice == 2:
                self.execute_and_print(
                    title="SUMMARY BY CATEGORY:",
                    query="""SELECT strftime('%Y', dt) as year, 
                    strftime('%m', dt) as month, 
                    category, 
                    CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2, 3
                ORDER BY 1 desc, 2 desc, 4 desc""",
                )

            elif choice == 3:
                self.execute_and_print(
                    title="SUMMARY BY MAJOR CATEGORY:",
                    query="""SELECT strftime('%Y', dt) as year, 
                    strftime('%m', dt) as month, 
                    CASE WHEN category='Rent' then 'Housing'
                        WHEN category='Internet' then 'Housing'
                        WHEN category='Electricity' then 'Housing' 
                        WHEN category='Youtube' then 'Comfort (Tech / Furniture / Subscriptions)'
                        else category end as category, 
                    CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses
                GROUP BY 1, 2, 3
                ORDER BY 1 desc, 2 desc, 4 desc""",
                )

            elif choice == 4:
                self.execute_and_print(
                    title="SUMMARY BY MONTH:",
                    query="""SELECT strftime('%Y', dt) as year, strftime('%m', dt) as month, CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2
                ORDER BY 1 desc, 2 desc""",
                )

            elif choice == 5:
                self.execute_and_print(
                    title="ALL EXPENSES:",
                    query="""SELECT description, dt, category, price FROM expenses
                            ORDER BY dt desc""",
                )

            elif choice == 6:
                break
            else:
                print("Invalid choice")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close the connection to the database"""
        print("Exiting...")
        self.conn.close()


if __name__ == "__main__":
    with ExpenseTracker() as tracker:
        tracker.main()
