import json
import os
from datetime import datetime
import sqlite3

DATA_FILE = 'budget_data.json'
DATA_DIR = 'data'

expense_categories = ["Food/Dining", "Drink/Dessert", "Personal Care", "Transportation", "Utilities", "Shopping", "Income", "Health", "Groceries", "Entertainment", "Donation"]

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
                return expense_categories[choice - 1]  # Return the selected category
            else:
                print("Invalid choice, please enter a valid number.")
        except ValueError:
            print("Invalid input, please enter a number.")

def load_data(year):
    file_path = os.path.join(DATA_DIR, f'{year}_budget_data.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return {"transactions": []}  # Return an empty structure if no data for that year

def save_data(year, transactions):
    file_path = os.path.join(DATA_DIR, f'{year}_budget_data.json')
    with open(file_path, 'w') as file:
        json.dump({"transactions": transactions}, file, indent=4)
        

def view_recent_transactions():
    print('Viewing recent transactions')

def add_transaction(type, amount, category, description='', date=''):
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    year = date.split('-')[0]  # Extract the year from the date

    # Load existing data for the year
    transactions_data = load_data(year)

    # Create the transaction
    transaction = {
        "type": type,
        "amount": amount,
        "description": description,
        "date": date,
        "category": category
    }

    # Add the transaction to the data
    transactions_data['transactions'].append(transaction)
    
    # Save the data back to the file
    save_data(year, transactions_data['transactions'])


options = ["Add income", "Add expense", "View balance", "See current month breakdown", "See current year breakdown"]

def view_transactions(period="month"):
    now = datetime.now()
    year = str(now.year)

    # Load the data for the current year
    transactions_data = load_data(year)
    period_transactions = []

    # Filter transactions based on the period
    if period == "month":
        period_transactions = [t for t in transactions_data["transactions"]
                               if datetime.strptime(t["date"], "%Y-%m-%d").month == now.month]
    elif period == "year":
        period_transactions = transactions_data["transactions"]

    # Calculate totals and display
    total_income = 0
    total_expense = 0

    for t in period_transactions:
        amount = t['amount']
        if t['type'] == 'income':
            total_income += amount
        else:
            total_expense += amount
        print(f"{t['date']} - {t['type'].capitalize()}: ${amount:.2f} ({t['description']})")

    # Display summary
    net_balance = total_income - total_expense
    print("\nSummary:")
    print(f"Total Income: ${total_income:.2f}")
    print(f"Total Expense: ${total_expense:.2f}")
    print(f"Net Balance: ${net_balance:.2f}")

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
        print("7) Exit")
        print("8) clear transactions")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            amount = float(input("Enter income amount: "))
            description = input("Enter description (optional): ")
            date = input("Enter date (if left empty, it will add the current day) ")
            add_transaction("income", amount, 'income', description, date)
            print("Income added.")
        elif choice == '2':
            amount = float(input("Enter expense amount: "))
            category = choose_category()
            description = input("Enter description (optional): ")
            date = input("Enter date (if left empty, it will add the current day) ")
            add_transaction("expense", amount, category, description, date)
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
        elif choice == '7':
            print("Exiting the app.")
            break
        elif choice == '8':
            print('deleting everything')
            os.remove('budget_data.json')
        else:
            print("Invalid option. Please try again.")

if __name__ == '__main__':
     main()
