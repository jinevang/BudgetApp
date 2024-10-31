import json
import os
from datetime import datetime
import calendar
from collections import defaultdict


from helpers import parse_date, load_file, save_to_file, choose_from_array, ignore_field, get_category_icon, get_category_type

from operator import itemgetter

DATA_DIR = 'data'

expense_categories = []

settings = ["Add category", "Delete category", "Update category", "Change ratio targets", "Exit"]

options = ["Add income", "Add expense", "View balance", "See current month breakdown", "See current year breakdown"]

data = {
     "transactions": []
}

def add_reoccuring(name, type, amount, category, description='', date=''):
    print('Reoccuring transactions haven\'t been implemented yet')

def update_category(categoryname):
    print('Update category hasn\'t been implemented yet')

def delete_category(replacementcategory):
    print('Delete category hasn\'t been implemented yet')
    
def update_transaction(date, name):
    print('Updating transactions hasn\'t been implemented yet')

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

def add_category(category_name, type, icon='', ignore='N'):
    global expense_categories
    categories = load_file(DATA_DIR, 'categories')
    
    type = type.lower()
    ignore = ignore.lower()
    
    if category_name in expense_categories:
        print("This category is already in the category list")
        return
    
    if not type.startswith("w") and not type.startswith("n"):
        print("Type needs to be either want or need")
        return
    
    new_category = {
        "name": category_name,
        "type": "want" if type.startswith('w') else "need",
        "icon": icon,
        "ignore": True if ignore.startswith('Y') else False
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

def view_recent_transactions(number=5):
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
    
    print(f'{type.capitalize()} added! ({name} - ${amount} [{category}])')

# view monthly summary
def view_monthly_summary(month=''):
    now = datetime.now()
    year = str(now.year)
    if not month:
        month = now.month

    transactions_data = load_data(year)
    period_transactions = []
    
    categories = load_file(DATA_DIR, 'categories')
    
    if str(month) not in transactions_data:
        print(f'There are no transactions for {calendar.month_name[int(month)]}')
        return
    
    print(f'Transactions for: {calendar.month_name[int(month)]}')
    
    transactions_data[str(month)].sort(key=lambda x: datetime.strptime(x["date"], "%m/%d/%Y"))
        
    period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]
    period_income = [t for t in transactions_data[str(month)] if t['type'] == "income"]
    
    cumulative_by_name = defaultdict(int)
    cumulative_by_category = defaultdict(int)
    cumulative_need = 0
    cumulative_want = 0

    for obj in period_transactions:
        # Group by name
        if get_category_type(obj['category'], categories) == 'want':
            cumulative_want += obj['amount']
        elif obj['type'] != 'income':
            cumulative_need += obj['amount']
        if ignore_field(obj["category"], categories): continue
        cumulative_by_name[obj["name"]] += obj["amount"]
        # Group by category
        cumulative_by_category[obj["category"]] += obj["amount"]
        
        

    # Step 2: Find the name with the highest cumulative amount
    highest_name = max(cumulative_by_name, key=cumulative_by_name.get)
    highest_name_amount = cumulative_by_name[highest_name]

    # Step 3: Find the type with the highest cumulative amount
    highest_category = max(cumulative_by_category, key=cumulative_by_category.get)
    highest_category_amount = cumulative_by_category[highest_category]

    total_expense = 0
    total_income = 0
    print("\nTransactions:")
    for t in period_transactions:
        amount = t['amount']
        total_expense += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']} {get_category_icon(t['category'], categories)})")
    print("\nIncome:")
    for t in period_income:
        amount = t['amount']
        total_income += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']} {get_category_icon(t['category'], categories)})")

    print(f"\nTotal Expenses this month: ${total_expense:.2f}")
    print(f"Total Income this month: ${total_income:.2f}")
    print(f"Net for this month: ${total_income - total_expense:.2f}")
    
    print(f"\nLocation with highest amount: {highest_name} - ${highest_name_amount:.2f}")
    
    print(f"Category with highest amount: {highest_category} - ${highest_category_amount:.2f}")
    
    print(f"\nNeeds: ${cumulative_need:.2f}")
    print(f"Wants: ${cumulative_want:.2f}")
    
    if total_income > 0:
        print(f"\nNeeds % (target: 50): {(cumulative_need / total_income) * 100:.2f}%")
        print(f"Wants % (target: 30): {(cumulative_want / total_income) * 100:.2f}%")
    # print(f"\Savings % (target: 20): {(cumulative_want+cumulative_need / total_income) * 100:.2f}%")

def category_breakdown(month=''):
    if not month:
        month = datetime.now().month
    
    print(f'\nViewing summary for categories for {calendar.month_name[int(month)]}')
    transactions_data = load_data(datetime.now().year)
    
    period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]

    cumulative_by_category = defaultdict(int)
    
    for obj in period_transactions:
        cumulative_by_category[obj["category"]] += obj["amount"]
        
    for category, amount in cumulative_by_category.items():
        print(f"{category}: ${amount:.2f}")

def location_breakdown(month=''):
    if not month:
        month = datetime.now().month
    
    print(f'\nViewing summary for location for {calendar.month_name[int(month)]}')
    transactions_data = load_data(datetime.now().year)
    
    period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]

    cumulative_by_name = defaultdict(int)
    
    for obj in period_transactions:
        cumulative_by_name[obj["name"]] += obj["amount"]
        
    for name, amount in cumulative_by_name.items():
        print(f"{name}: ${amount:.2f}")

def view_year_transactions(year=''):
    if not year:
        year = datetime.now().year
        
    print(f'\nViewing summary per month for {year}')
    transactions_data = load_data(year)
    
    period_transactions = [t for t in transactions_data]
    period_transactions = dict(sorted(transactions_data.items(), key=lambda item: int(item[0])))

    total_expenses = 0
    total_income = 0
    
    for t in period_transactions:
        print(f'\n{calendar.month_name[int(t)]}')
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
        print(f"Expenses: ${expenses:.2f}")
        print(f"Income: ${income:.2f}")
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
        # new category
        category = input('Enter new category name: ')
        type = input('Want/Need?: ')
        icon = input('Add custom icon?: ')
        ignore = input('Should this category be ignored in top category summaries?: (Y/N)')
        add_category(category, type, icon, ignore)
    if chosensetting == 1:
        # delete category
        print()
    if chosensetting == 2:
        # update category
        print()
    if chosensetting == 3:
        # change ratio targets
        print()
    if chosensetting == 4:
        return


def main():
    ensure_data_dir_exists()
    load_categories()
    load_data('2024')
    while True:
        # print_summary()
        print("\nBudgeting App")
        print("1) Add expense")
        print("2) Add income")
        print("3) View month breakdown")
        print("4) See current year breakdown")
        print("5) See breakdown by category")
        print("6) See breakdown by location")
        print("7) Settings")
        print("8) Exit")
        print("9) Help")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            print('\n---ADD NEW EXPENSE---')
            name = input("Enter name of expense: ")
            amount = float(input("Enter expense amount: "))
            category = choose_from_array(expense_categories, 'Choose category')
            date = input("Enter date (MM/DD/YYYY) [if left empty, it will add the current day]: ")
            description = input("Enter description (optional): ")
            add_transaction(name, "expense", amount, category, description, date)
        elif choice == '2':
            print("\n---ADD NEW INCOME---")
            name = input("Enter name of income source: ")
            amount = float(input("Enter income amount: "))
            date = input("Enter date (MM/DD/YYYY) [if left empty, it will add the current day]: ")
            description = input("Enter description (optional): ")
            add_transaction(name, "income", amount, 'Income', description, date)
        elif choice == '3':
            print('\n---BREAKDOWN BY MONTH---')
            month = input('Enter month (as a number) [optional]: ')
            view_monthly_summary(month)
        elif choice == '4':
            print('\n---BREAKDOWN OF THE CURRENT YEAR---')
            view_year_transactions()
        elif choice == '5':
            print("\n---BREAKDOWN BY CATEGORY---")
            month = input('Enter month (as number): ')
            category_breakdown(month)
        elif choice =='6':
            print('\n---BREAKDOWN BY LOCATION---')
            month = input('Enter month (as number): ')
            location_breakdown(month)
        elif choice == '7':
            print('\n---SETTINGS---')
            choose_settings()

        elif choice == '8':
            print("---EXITING THE APP: bye bye!---")
            break
        elif choice == '9':
            print('This is a lightweight budgeting app built in Python!')
            print('© Evan Jin 2024')
        else:
            print("Invalid option! Please try again.")

if __name__ == '__main__':
     main()
