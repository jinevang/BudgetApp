import json
import os
from datetime import datetime

DATA_DIR = 'data'

expense_categories = ["Food/Dining", "Drink/Dessert", "Personal Care", "Transportation", "Utilities", "Shopping", "Income", "Health", "Groceries", "Entertainment", "Donation"]

settings = ["Add category", "Delete category", "Change ratio targets"]

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
    return {}  # Return an empty dictionary if no data exists

def save_data(year, data):
    file_name = os.path.join(DATA_DIR, f'{year}_budget_data.json')
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)

def view_recent_transactions():
    print('Viewing recent transactions')

def add_transaction(name, type, amount, category, description='', date=''):
    if not date:
        date = datetime.now().strftime('%m/%d/%Y')
    print(date)
    try:
        month, _, year = date.split('/')
    except ValueError:
        print("Error: Date must be in MM/DD/YYYY format.")
        return
    
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

options = ["Add income", "Add expense", "View balance", "See current month breakdown", "See current year breakdown"]

# def view_transactions(period="month"):
#     now = datetime.now()
#     year = str(now.year)

#     # Load the data for the current year
#     transactions_data = load_data(year)
#     period_transactions = []

#     # Filter transactions based on the period
#     if period == "month":
#         period_transactions = [t for t in transactions_data["transactions"]
#                                if datetime.strptime(t["date"], "%Y-%m-%d").month == now.month]
#     elif period == "year":
#         period_transactions = transactions_data["transactions"]

#     # Calculate totals and display
#     total_income = 0
#     total_expense = 0

#     for t in period_transactions:
#         amount = t['amount']
#         if t['type'] == 'income':
#             total_income += amount
#         else:
#             total_expense += amount
#         print(f"{t['date']} - {t['type'].capitalize()}: ${amount:.2f} ({t['description']})")

#     # Display summary
#     net_balance = total_income - total_expense
#     print("\nSummary:")
#     print(f"Total Income: ${total_income:.2f}")
#     print(f"Total Expense: ${total_expense:.2f}")
#     print(f"Net Balance: ${net_balance:.2f}")

def ensure_data_dir_exists():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def main():
    ensure_data_dir_exists()
    load_data('2024')
    while True:
        print("\nBudgeting App")
        print("1) Add income")
        print("2) Add expense")
        print("3) View balance")
        print("4) See current month breakdown")
        print("5) See current year breakdown")
        print("6) See breakdown by category")
        print("7) See breakdown by location")
        print("8) Settings")
        print("9) Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            name = input("Enter name of income source: ")
            amount = float(input("Enter income amount: "))
            description = input("Enter description (optional): ")
            date = input("Enter date (if left empty, it will add the current day) ")
            add_transaction(name, "income", amount, 'income', description, date)
            print("Income added.")
        elif choice == '2':
            name = input("Enter name of expense: ")

            amount = float(input("Enter expense amount: "))
            category = choose_category()
            description = input("Enter description (optional): ")
            date = input("Enter date (if left empty, it will add the current day) ")
            add_transaction(name, "expense", amount, category, description, date)
            print("Expense added.")
        elif choice == '4':
            print("Current month transactions:")
            view_transactions("month")
        elif choice == '5':
            print("Current year transactions:")
            view_transactions("year")
        elif choice == '6':
            print("Breakdown by category:")
            category = choose_category()
        elif choice =='7':
            print('breakdown by location')
        elif choice == '8':
            print('settings')
            choose_settings()
        elif choice == '9':
            print("Exiting the app.")
            break
            
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
     main()
