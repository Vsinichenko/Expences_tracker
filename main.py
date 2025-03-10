import sqlite3
import datetime
from dateutil.relativedelta import relativedelta
from tabulate import tabulate
from sympy import sympify


class ExpenseTracker:
    """Track personal expenses and view summaries by category and month"""

    db_filename = "/Users/v.sinichenko/Library/Mobile Documents/com~apple~CloudDocs/MyFiles/Python/Expenses/expenses.db"
    no_description_categories = ["Mensa", "Groceries"]

    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_filename)
        self.cur = self.conn.cursor()
        return self

    def select_and_print_pretty(self, title, query):
        """Execute the query and print the results in a prettified table"""
        print(title)
        self.cur.execute(query)
        column_names = [description[0] for description in self.cur.description]
        expenses = self.cur.fetchall()
        print(tabulate(expenses, headers=column_names, tablefmt="psql", floatfmt=",.0f"))

    def get_dt(self):
        """Get the date of the expense or income"""
        while True:
            print(
                """Select date: 
                1 - current date
                2 - last day of previous month is assumed 
                3 - last day of the month before last"""
            )
            try:
                date_choice = int(input())
            except ValueError:
                print("Invalid choice")
                continue

            if date_choice == 1:
                # first day ot the current month
                date = datetime.date.today()
                break
            elif date_choice == 2:
                # last day of the previous month
                date = (datetime.date.today() - relativedelta(months=1)).replace(day=1)
                break
            elif date_choice == 3:
                # last day of the month before last
                date = (datetime.date.today() - relativedelta(months=2)).replace(day=1)
                break
            else:
                print("Invalid number")
                continue

        return date

    def float_from_string(self, string):
        return float(string.replace(",", "."))

    def get_price(self):
        user_input = input(
            "Enter amount: \n Allowed inputs: 10 | 10,5 | 10.5 | 500/41,5 | 5,3+10,1 | (10+100)/42,8 |... \n"
        )
        user_input = user_input.replace(",", ".")
        price = float(sympify(user_input))
        price = round(price, 2)

        return price

    def get_expense_category(self):
        """Obtain expense category from user"""
        print("Select a category by number:")
        self.cur.execute(
            """SELECT DISTINCT e.category
        FROM expenses e
                 LEFT JOIN outdated_categories oc ON oc.category = e.category
        WHERE oc.category IS NULL
        ORDER BY e.category """
        )
        categories = self.cur.fetchall()
        for i, category in enumerate(categories):
            print(f"{i + 1}. {category[0]}")
        print(len(categories) + 1, "Add a new category")
        category_idx = int(input())
        if category_idx == len(categories) + 1:
            category = input("Enter the new category name: ")
        else:
            category = categories[category_idx - 1][0]
        return category

    def get_income_description(self):
        """Obtain income category from user"""
        print("Select a description by number:")
        self.cur.execute("SELECT DISTINCT description FROM income ORDER BY description")
        descriptions = self.cur.fetchall()
        for i, description in enumerate(descriptions):
            print(f"{i + 1}. {description[0]}")
        print(len(descriptions) + 1, "Add a new description")
        description_idx = int(input())
        if description_idx == len(descriptions) + 1:
            description = input("Enter the new description name: ")
        else:
            description = descriptions[description_idx - 1][0]
        return description

    def add_expense(self):
        dt = self.get_dt()
        category = self.get_expense_category()

        self.cur.execute("SELECT category FROM fixed_price_categories ORDER BY category")
        fixed_price_categories = self.cur.fetchall()
        fixed_price_categories = [el[0] for el in fixed_price_categories]

        if category in fixed_price_categories:
            self.cur.execute("SELECT price FROM fixed_price_categories WHERE category=?", (category,))
            price = self.cur.fetchall()[0][0]
            print(price)
            description = ""
        elif category in self.no_description_categories:
            price = self.get_price()
            description = ""
        else:
            price = self.get_price()
            description = input("Enter description or leave empty: ")

        self.cur.execute(
            """INSERT INTO expenses (dt, description, category, price, insert_dt)
                                VALUES (?, ?, ?, ?, ?)""",
            (dt, description, category, price, datetime.datetime.now()),
        )
        self.conn.commit()

    def add_income(self):
        dt = self.get_dt()
        description = self.get_income_description()
        amount = self.get_price()
        self.cur.execute(
            """INSERT INTO income (dt, description, amount)
                                VALUES (?, ?, ?)""",
            (dt, description, amount),
        )
        self.conn.commit()

    def main(self):
        """Get user input and execute the corresponding function"""
        while True:
            print("\nSelect an option:")
            print("1. Add expense")
            print("2. Add income")
            print("3. View expenses by category")
            print("4. View expenses by major category")
            print("5. View summary by month")
            print("6. List recent expenses")
            print("7. List all income sources")
            print("8. Remove last expense")
            print("9. Exit")

            try:
                choice = int(input())
            except ValueError:
                print("Invalid choice")
                continue

            if choice == 1:
                self.add_expense()

            elif choice == 2:
                self.add_income()

            elif choice == 3:
                self.select_and_print_pretty(
                    title="SUMMARY BY CATEGORY:",
                    query="""SELECT strftime('%Y', dt) as year, 
                    strftime('%m', dt) as month, 
                    category, 
                    CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2, 3
                UNION ALL 
                SELECT strftime('%Y', dt) as year,
                strftime('%m', dt) as month, 
                '__________________'  as category,
                CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2, 3
                ORDER BY 1, 2, 4 desc""",
                )

            elif choice == 4:
                self.select_and_print_pretty(
                    title="SUMMARY BY MAJOR CATEGORY:",
                    query="""
                SELECT STRFTIME('%Y', dt)                 AS year,
                       STRFTIME('%m', dt)                 AS month,
                       IFNULL(mcg.major_category, e.category),
                       CAST(ROUND(SUM(price)) AS INTEGER) AS total
                FROM expenses e
                         LEFT JOIN major_category_groupings mcg ON e.category = mcg.category
                GROUP BY 1, 2, 3
                UNION ALL
                SELECT STRFTIME('%Y', dt)                 AS year,
                       STRFTIME('%m', dt)                 AS month,
                       '__________________'               AS major_category,
                       CAST(ROUND(SUM(price)) AS INTEGER) AS total
                FROM expenses
                GROUP BY 1, 2, 3
                ORDER BY year, month, total DESC
                    """,
                )

            elif choice == 5:
                self.select_and_print_pretty(
                    title="SUMMARY BY MONTH:",
                    query="""
                SELECT e.year,
                       e.month,
                       COALESCE(i.total_income, 0)                     total_income,
                       e.total_expenses,
                       COALESCE(i.total_income, 0) - total_expenses AS diff
                FROM (SELECT STRFTIME('%Y', dt) AS year, STRFTIME('%m', dt) AS month, ROUND(SUM(price)) AS total_expenses
                      FROM expenses
                      GROUP BY 1, 2
                      ORDER BY 1, 2) e
                         LEFT JOIN
                     (SELECT STRFTIME('%Y', dt) AS year, STRFTIME('%m', dt) AS month, ROUND(SUM(amount)) AS total_income
                      FROM income
                      GROUP BY 1, 2) i ON i.month = e.month AND i.year = e.year
                """,
                )

            elif choice == 6:
                self.select_and_print_pretty(
                    title="RECENT EXPENSES:",
                    query="""
                        SELECT description, dt, category, price, insert_dt
                        FROM (SELECT description, dt, category, price, insert_dt
                              FROM expenses
                              ORDER BY insert_dt DESC
                              LIMIT 50) sub
                        ORDER BY insert_dt
                    """,
                )

            elif choice == 7:
                self.select_and_print_pretty(
                    title="ALL INCOME SOURCES:",
                    query="""SELECT description, dt, amount FROM income
                                            ORDER BY dt""",
                )

            elif choice == 8:
                print("Most recent expense has been removed")
                self.cur.execute(
                    """DELETE FROM expenses
                        WHERE insert_dt = (SELECT MAX(insert_dt) FROM expenses)"""
                )

            elif choice == 9:
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
