import json
import os
from datetime import datetime
import calendar

from helpers import parse_date, load_file, save_to_file

from operator import itemgetter

DATA_DIR = 'data'

expense_categories = ["Food/Dining", "Drink/Dessert", "Personal Care", "Transportation", "Utilities", "Shopping", "Income", "Health", "Groceries", "Entertainment", "Donation"]

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
            
def choose_settings():
    print("Please make your selection:")
    for idx, setting in enumerate(settings, start=1):
        print(f"{idx}) {setting}")
    while True:
        try:
            choice = int(input("Choice: "))
            if choice == 'e': break
            if 1 <= choice <= len(expense_categories):
                return expense_categories[choice - 1]
            else:
                print("Invalid choice, please enter a valid number.")
        except ValueError:
            print("Invalid input, please enter a number.")

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
    
    print('Expense added!')

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

    # Calculate totals and display
    total_expense = 0

    for t in period_transactions:
        amount = t['amount']
        total_expense += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']})")

    print(f"\nTotal Expenses this month: ${total_expense:.2f}")
    
def view_year_transactions(year=''):
    if not year:
        year = datetime.now().year
    
    print(f'Viewing summary per month for {year}')
    transactions_data = load_data(year)
    period_transactions = []
    
    period_transactions = [t for t in transactions_data]
    

def view_summary(month=''):
    if not month:
        month = datetime.now().month

def ensure_data_dir_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

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
        print("ac) add category")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            name = input("Enter name of expense: ")
            amount = float(input("Enter expense amount: "))
            category = choose_category()
            description = input("Enter description (optional): ")
            date = input("Enter date (MM/DD/YYYY) (if left empty, it will add the current day): ")
            add_transaction(name, "expense", amount, category, description, date)
        elif choice == '2':
            name = input("Enter name of income source: ")
            amount = float(input("Enter income amount: "))
            description = input("Enter description (optional): ")
            date = input("Enter date (MM/DD/YYYY) (if left empty, it will add the current day): ")
            add_transaction(name, "income", amount, 'income', description, date)
            print("Income added.")
        elif choice == '4':
            month = input('Enter month (as a number) (blank=current): ')
            view_transactions(month)
        elif choice == '5':
            print("Current year transactions:")
            print('year not currently implemented')
        elif choice == '6':
            print("Breakdown by category:")
            category = choose_category()
            month = input('Enter month (as number): ')
        elif choice =='7':
            print('Breakdown by location')
            location = input('Enter location name: ')
        elif choice == '8':
            print('settings')
            choose_settings()
        elif choice == '9':
            print("Exiting the app")
            break
        elif choice == '10':
            print('Help')
        elif choice == 'ac':
            category = input('Enter new category name: ')
            type = input('Want/Need? ')
            add_category(category, type)
            
        else:
            print("Invalid option! Please try again.")

if __name__ == '__main__':
     main()
