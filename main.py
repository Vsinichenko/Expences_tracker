import sqlite3
import datetime
from tabulate import tabulate


class ExpenseTracker:
    """Track personal expenses and view summaries by category and month"""

    fixed_price_categories = {
        "Therapy": 45,
        "Rent": 655,
        "Internet": 24.9,
        "Phone": 15,
        "Electricity": 40,
        "Youtube": 4.5,
        "Entgeltabrechnung": 3.9,
        "Birthday quarks": 2.45,
        "Washing machine": 2.5,
        "Health insurance": 127.65,
    }
    db_filename = "expenses.db"

    def __init__(self):
        self.conn = None
        self.cur = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_filename)
        self.cur = self.conn.cursor()
        return self

    def execute_and_print(self, title, query):
        """Execute the query and print the results in a prettified table"""
        print(title.upper())
        self.cur.execute(query)
        column_names = [description[0] for description in self.cur.description]
        expenses = self.cur.fetchall()
        print(tabulate(expenses, headers=column_names, tablefmt="pretty"))

    def get_dt(self):
        """Get the date of the expense or income"""
        print("Is it current date? Print 1 for yes, 2 - previous month is assumed")
        date_choice = int(input())
        if date_choice == 1:
            # first day ot the current month
            date = datetime.date.today()
        else:
            # first day of the previous month
            now = datetime.date.today()
            first_day_of_current_month = now.replace(day=1)
            last_day_of_previous_month = first_day_of_current_month - datetime.timedelta(days=1)
            date = last_day_of_previous_month.replace(day=1)
        return date

    def get_price(self):
        user_input = input("Enter amount: \n Allowed inputs: 10 | 10,5 | 10.5 | 500/41,5 | ... \n")
        if "/" in user_input:
            # parse the string and execute the division
            numerator, denominator = user_input.split("/")
            price = float(numerator.replace(",", ".")) / float(denominator.replace(",", "."))
            price = round(price, 2)
        else:
            price = float(user_input.replace(",", "."))
        return price

    def get_expense_category(self):
        """Obtain expense category from user"""
        print("Select a category by number:")
        self.cur.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
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

        if category in self.fixed_price_categories:
            price = self.fixed_price_categories[category]
            description = ""
        else:
            price = self.get_price()
            description = input("Enter description or leave empty: ")

        self.cur.execute(
            """INSERT INTO expenses (dt, description, category, price)
                                VALUES (?, ?, ?, ?)""",
            (dt, description, category, price),
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
            print("5. View expenses by month")
            print("6. List all expenses")
            print("7. List all income sources")
            print("8. Exit")

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
                self.execute_and_print(
                    title="SUMMARY BY CATEGORY:",
                    query="""SELECT strftime('%Y', dt) as year, 
                    strftime('%m', dt) as month, 
                    category, 
                    CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2, 3
                ORDER BY 1, 2, 4 desc""",
                )

            elif choice == 4:
                self.execute_and_print(
                    title="SUMMARY BY MAJOR CATEGORY:",
                    query="""SELECT strftime('%Y', dt) as year, 
                    strftime('%m', dt) as month, 
                    CASE WHEN category='Rent' then 'Housing'
                        WHEN category='Washing machine' then 'Housing'
                        WHEN category='Phone' then 'Housing'
                        WHEN category='Health insurance' then 'Housing'
                        WHEN category='Internet' then 'Housing'
                        WHEN category='Electricity' then 'Housing' 
                        WHEN category='Youtube' then 'Comfort (Tech / Furniture / Subscriptions)'
                        WHEN category='Birthday quarks' then 'Other'
                        WHEN category='Entgeltabrechnung' then 'Other'
                        WHEN category='Entertainment' then 'Luxury (Eating out, entertainment)'
                        WHEN category='Eating out' then 'Luxury (Eating out, entertainment)'
                        else category end as major_category, 
                    CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses
                GROUP BY 1, 2, 3 
                ORDER BY 1, 2, CAST(ROUND(sum(price)) AS INTEGER) desc""",
                )

            elif choice == 5:
                self.execute_and_print(
                    title="SUMMARY BY MONTH:",
                    query="""SELECT strftime('%Y', dt) as year, strftime('%m', dt) as month, CAST(ROUND(sum(price)) AS INTEGER) as total
                FROM expenses 
                GROUP BY 1, 2
                ORDER BY 1 desc, 2 desc""",
                )

            elif choice == 6:
                self.execute_and_print(
                    title="ALL EXPENSES:",
                    query="""SELECT description, dt, category, price FROM expenses
                            ORDER BY dt""",
                )

            elif choice == 7:
                self.execute_and_print(
                    title="ALL INCOME SOURCES:",
                    query="""SELECT description, dt, amount FROM income
                                            ORDER BY dt""",
                )

            elif choice == 8:
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
