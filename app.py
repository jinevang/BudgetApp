import json
import os
from datetime import datetime
import calendar

from helpers import parse_date, load_file, save_to_file, choose_from_array

from operator import itemgetter

DATA_DIR = 'data'

expense_categories = []

settings = ["Set up reoccurring", "Add category", "Delete category", "Update Category", "Change ratio targets"]

options = ["Add income", "Add expense", "View balance", "See current month breakdown", "See current year breakdown"]

data = {
     "transactions": []
}

def choose_category():
    print("Please choose a category for the expense:")
    for idx, category in enumerate(expense_categories, start=1):
        print(f"{idx}) {category}")
    while True:
        try:
            choice = int(input("Enter the number of the category: "))
            if 1 <= choice <= len(expense_categories):
                return expense_categories[choice - 1]
            else:
                print("Invalid choice, please enter a valid number.")
        except ValueError:
            print("Invalid input, please enter a number.")
            
# def choose_settings():
#     print("Please make your selection:")
#     for idx, setting in enumerate(settings, start=1):
#         print(f"{idx}) {setting}")
#     while True:
#         try:
#             choice = int(input("Choice: "))
#             if choice == 'e': break
#             if 1 <= choice <= len(expense_categories):
#                 return expense_categories[choice - 1]
#             else:
#                 print("Invalid choice, please enter a valid number.")
#         except ValueError:
#             print("Invalid input, please enter a number.")

def load_data(year):
    file_name = os.path.join(DATA_DIR, f'{year}_budget_data.json')
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            return json.load(file)
    return {}

def load_categories():
    global expense_categories
    data = load_file(DATA_DIR, 'categories')

    if data["categories"]:
        expense_categories = [c["name"] for c in data["categories"]]

def add_category(category_name, type):
    global expense_categories
    categories = load_file(DATA_DIR, 'categories')
    
    type = type.lower()
    
    if category_name in expense_categories:
        print("This category is already in the category list")
        return
    
    if not type.startswith("w") and not type.startswith("n"):
        print("Type needs to be either want or need")
        return
    
    new_category = {
        "name": category_name,
        "type": "want" if type.startswith('w') else "need"
    }
    
    categories["categories"].append(new_category)
    
    save_categories(categories)

    load_categories()

def save_categories(data):
    file_name = os.path.join(DATA_DIR, 'categories.json')
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def save_data(year, data):
    file_name = os.path.join(DATA_DIR, f'{year}_budget_data.json')
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def view_recent_transactions(number):
    print('Viewing recent transactions')

def add_transaction(name, type, amount, category, description='', date=''):
    if not date:
        date = datetime.now().strftime('%m/%d/%Y')
        
    if date:
        date = parse_date(date)

    month, _, year = date.split('/')

    data = load_data(year)
    
    if month not in data:
        data[month] = []
    
    transaction = {
        "name": name,
        "type": type,
        "amount": amount,
        "description": description,
        "date": date,
        "category": category
    }
    
    # Append the transaction to the appropriate list
    data[month].append(transaction)
    
    # Save the updated data
    save_data(year, data)
    
def view_transactions(month=''):
    now = datetime.now()
    year = str(now.year)
    if not month:
        month = now.month

    transactions_data = load_data(year)
    period_transactions = []
    
    
    if str(month) not in transactions_data:
        print(f'There are no transactions for {calendar.month_name[int(month)]}')
        return
    
    print(f'Transactions for: {calendar.month_name[int(month)]}')
    
    transactions_data[str(month)].sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))
        
    period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]
    period_income = [t for t in transactions_data[str(month)] if t['type'] == "income"]

    total_expense = 0
    total_income = 0
    print("\nTransactions:")
    for t in period_transactions:
        amount = t['amount']
        total_expense += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']})")
    print("\nIncome:")
    for t in period_income:
        amount = t['amount']
        total_income += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']})")

    print(f"\nTotal Expenses this month: ${total_expense:.2f}")
    print(f"Total Income this month: ${total_income:.2f}")
    print(f"Net for this month: ${total_income - total_expense:.2f}")
    
    
def view_year_transactions(year=''):
    if not year:
        year = datetime.now().year
        
    print(f'\nViewing summary per month for {year}')
    transactions_data = load_data(year)
    
    period_transactions = [t for t in transactions_data]
    total_expenses = 0
    total_income = 0
    
    for t in period_transactions:
        print(calendar.month_name[int(t)])
        expenses = 0
        income = 0
        for i in transactions_data[str(t)]:
            amount = i['amount']
            if i['type'] == 'expense':
                expenses += amount
            elif i['type'] == 'income':
                income += amount
        
        total_expenses += expenses
        total_income += income
        print(f"Total Expenses: ${expenses:.2f}")
        print(f"Total Income: ${income:.2f}")
        print(f"Net: ${income-expenses:.2f}")
    
    print("\nSummary of full year:")
    print(f"Total Expenses: ${total_expenses:.2f}")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Net: ${total_income-total_expenses:.2f}")


def view_summary(month=''):
    if not month:
        month = datetime.now().month

def ensure_data_dir_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def choose_settings():
    chosensetting = choose_from_array(settings, "Which setting", True)
    print(settings[chosensetting])
    
    if chosensetting == 0:
        print('')
    if chosensetting == 1:
        category = input('Enter new category name: ')
        type = input('Want/Need?: ')
        emoji = input('Add custom emoji?: ')
        add_category(category, type)
    if chosensetting == 2:
        print()
    if chosensetting == 3:
        print()
    
    
    

def main():
    ensure_data_dir_exists()
    load_categories()
    load_data('2024')
    while True:
        # print_summary()
        print("\nBudgeting App")
        print("1) Add expense")
        print("2) Add income")
        print("3) View balance")
        print("4) View month breakdown")
        print("5) See current year breakdown")
        print("6) See breakdown by category")
        print("7) See breakdown by location")
        print("8) Settings")
        print("9) Exit")
        print("10) Help")


        
        choice = input("Choose an option: ")
        
        if choice == '1':
            print('\n---ADD NEW EXPENSE---')
            name = input("Enter name of expense: ")
            amount = float(input("Enter expense amount: "))
            category = choose_category()
            description = input("Enter description (optional): ")
            date = input("Enter date (MM/DD/YYYY) [if left empty, it will add the current day]: ")
            add_transaction(name, "expense", amount, category, description, date)
            print('Expense added!')

        elif choice == '2':
            print("\n---ADD NEW INCOME---")
            name = input("Enter name of income source: ")
            amount = float(input("Enter income amount: "))
            description = input("Enter description (optional): ")
            date = input("Enter date (MM/DD/YYYY) [if left empty, it will add the current day]: ")
            add_transaction(name, "income", amount, 'income', description, date)
            print("Income added!")
        elif choice == '4':
            print('\n---BREAKDOWN BY MONTH---')
            month = input('Enter month (as a number) [optional]: ')
            view_transactions(month)
        elif choice == '5':
            print('\n---BREAKDOWN OF THE CURRENT YEAR---')
            view_year_transactions()
        elif choice == '6':
            print("\n---BREAKDOWN BY CATEGORY---")
            category = choose_category()
            month = input('Enter month (as number): ')
            print('Category breakdown is not implemented yet.')
        elif choice =='7':
            print('\n---Breakdown by location---')
            location = input('Enter location name: ')
            print('Location breakdown is not implemented yet.')
        elif choice == '8':
            print('\n---Settings---')
            choose_settings()

        elif choice == '9':
            print("---Exiting the app---")
            break
        elif choice == '10':
            print('Help')
        else:
            print("Invalid option! Please try again.")

if __name__ == '__main__':
     main()
