from curses.ascii import isdigit
import json
import os
from datetime import datetime
import calendar
from collections import defaultdict
import math

from helpers import parse_date, load_file, save_to_file, choose_from_array, ignore_field, get_category_icon, get_category_type

DATA_DIR = 'data'

expense_categories = []

settings = ["Add category", "Delete category", "Update category", "Change ratio targets", "Add recurring transaction", "Remove recurring transaction", "Exit"]

options = ["Add income", "Add expense", "View balance", "See current month breakdown", "See current year breakdown"]

data = {
     "transactions": []
}

def add_recurring(name, type, amount, category, date, increment):
    recurring = load_file(DATA_DIR, 'recurring')
    type = type.lower()
        
    new_recurring = {
        "category": category,
        "name": name,
        "amount": amount,
        "type": get_category_type(category),
        "increment": increment,
        "date": date.replace(' ', '').split(',')
    }
    
    recurring["recurring"].append(new_recurring)
    
    save_to_file(DATA_DIR, recurring, 'recurring')

def delete_recurring(name):
    recurring = load_file(DATA_DIR, 'recurring')
    
    recurring['recurring'] = [r for r in recurring['recurring'] if r['name'] != name]
    
    save_to_file(DATA_DIR, recurring, 'recurring')
    
def delete_transaction(date):
    print()
    if not date:
        date = datetime.now().strftime('%m/%d/%Y')
        
    if date:
        date = parse_date(date)

    month, _, year = date.split('/')

    data = load_data(year)

def setup_month(date):
    currentyear = datetime.now().year
    currentmonth = datetime.now().month

    recurring = load_file(DATA_DIR, 'recurring')    
    recurring_setting = [s for s in recurring['recurring']]
    for item in recurring_setting:
        normalizedDates = []
        if(item["increment"] == "month"):
            for date in item["date"]:
                if type(date) == int or isdigit(date):
                    normalizedDates.append(str(currentmonth) + "/" + str(date) + "/" + str(currentyear))
                elif type(date) == str:
                    days = calendar.monthrange(currentyear, currentmonth)[1]
                    match date:
                        case "last":
                            normalizedDates.append(str(currentmonth) + "/" + str(days) + "/" + str(currentyear))
                        case "middle":
                            normalizedDates.append(str(currentmonth) + "/" + str(math.ceil(days/2)) + "/" + str(currentyear))
                        case "start":
                            normalizedDates.append(str(currentmonth) + "/1/" + str(currentyear))

        elif(item["increment"] == "year"):
            m, day = str(item['date']).split('/')
            newdate = m + '/' + day + '/' + str(currentyear)
            if int(m) == currentmonth:
                add_transaction(item["name"], get_category_type(item["category"]), item["amount"], item["category"], "Added automatically via reoccuring", newdate, monthsetup=True)
        
        for date in normalizedDates:
            add_transaction(item["name"], item["type"], item["amount"], item["category"], "Added automatically via reoccuring", date, monthsetup=True)

    
def update_category(categoryname, replace):
    print('Update category hasn\'t been implemented yet')

def delete_category(replacementcategory):
    print('Delete category hasn\'t been implemented yet')
    
def update_transaction(date):
    print('Updating transactions hasn\'t been implemented yet')

def load_data(year):
    return load_file(DATA_DIR, f'{year}_budget_data')

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

def add_transaction(name, type, amount, category, description='', date='', monthsetup=False):
    newentry = False
    
    if not date:
        date = datetime.now().strftime('%m/%d/%Y')
        
    if date:
        date = parse_date(date)

    month, _, year = date.split('/')

    data = load_data(year)
    
    if month not in data:
        newentry = True
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
    
    not monthsetup and print(f'{type.capitalize()} added! ({name} - ${amount} [{category}])')

    if newentry:
        setup_month(int(month))

# view monthly summary
def view_monthly_summary(month=''):
    now = datetime.now()
    try:
        month, year = month.split('/')
    except:
        # print('nothing')
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
        if get_category_type(obj['category']) == 'want':
            cumulative_want += obj['amount']
        elif obj['type'] != 'income':
            cumulative_need += obj['amount']
        if ignore_field(obj["category"], categories): continue
        cumulative_by_name[obj["name"]] += obj["amount"]
        # Group by category
        cumulative_by_category[obj["category"]] += obj["amount"]
        
    # highest name cumulative
    highest_name = max(cumulative_by_name, key=cumulative_by_name.get)
    highest_name_amount = cumulative_by_name[highest_name]

    # highest category
    highest_category = max(cumulative_by_category, key=cumulative_by_category.get)
    highest_category_amount = cumulative_by_category[highest_category]

    total_expense = 0
    total_income = 0
    print("\nTransactions:")
    for t in period_transactions:
        amount = t['amount']
        total_expense += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']} {get_category_icon(t['category'])})")
    print("\nIncome:")
    for t in period_income:
        amount = t['amount']
        total_income += amount
        print(f"{t['date']} - {t['name']}: ${amount:.2f} ({t['category']} {get_category_icon(t['category'],)})")

    print(f"\nTotal Expenses this month: ${total_expense:.2f}")
    print(f"Total Income this month: ${total_income:.2f}")
    
    print(f"\nLocation with highest amount: {highest_name} - ${highest_name_amount:.2f}")
    
    print(f"Category with highest amount: {highest_category} - ${highest_category_amount:.2f}")
    
    print(f"\nNeeds: ${cumulative_need:.2f}")
    print(f"Wants: ${cumulative_want:.2f}")
    print(f"Savings: ${(total_income - total_expense):.2f}")
    
    if total_income > 0:
        needs = (cumulative_need / total_income) * 100
        wants = (cumulative_want / total_income) * 100
        print(f"\nNeeds % (target: 50): {needs:.2f}%")
        print(f"Wants % (target: 30): {wants:.2f}%")
        print(f"Savings % (target: 20): {(100 - needs - wants):.2f}%")

def category_breakdown(month=''):
    
    if not month:
        month = datetime.now().month
    
    isyear = False
    categories = load_file(DATA_DIR, 'categories')

    if type(month) is str and month.lower() == 'y':
        print(f'\nViewing summary of categories for {datetime.now().year}')
        isyear = True
    elif type(month) is int:
        print(f'\nViewing summary of categories for {calendar.month_name[int(month)]}')
    else:
        try:
            int(month)
            print(f'\nViewing summary of categories for {calendar.month_name[int(month)]}')
        except ValueError:
            print('\nNot a valid selection, try again please')
            return
    
    transactions_data = load_data(datetime.now().year)
    
    if isyear:
        period_transactions = [t for month_data in transactions_data.values() for t in month_data if t['type'] != "income"]
    else:
        period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]

    cumulative_by_category = defaultdict(lambda: {"amount": 0, "count": 0})
    
    for obj in period_transactions:
        cumulative_by_category[obj["category"]]["amount"] += obj["amount"]
        cumulative_by_category[obj["category"]]["count"] += 1

    sorted_categories = sorted(cumulative_by_category.items(), key=lambda item: item[1]["amount"], reverse=True)

    for category, data in sorted_categories:
        icon = get_category_icon(category).strip()

        print(f"{icon} {category}: ${data['amount']:.2f} ({data['count']} transaction{'s' if data['count'] > 1 else ''})")

def location_breakdown(month='', limit=15):
    if not month:
        month = datetime.now().month
    
    isyear = False
    
    if type(month) is str and month.lower() == 'y':
        print(f'\nViewing summary of locations for {datetime.now().year}')
        isyear = True
    else:
        try:
            int(month)
            print(f'\nViewing summary of locations for {calendar.month_name[int(month)]}')
        except ValueError:
            print('\nNot a valid selection, try again please')
            return
    
    transactions_data = load_data(datetime.now().year)
    
    if isyear:
        period_transactions = [t for month_data in transactions_data.values() for t in month_data if t['type'] != "income"]
    else:
        period_transactions = [t for t in transactions_data[str(month)] if t['type'] != "income"]
    cumulative_by_name = defaultdict(lambda: {"amount": 0, "count": 0})

    for obj in period_transactions:
        cumulative_by_name[obj["name"]]["amount"] += obj["amount"]
        cumulative_by_name[obj["name"]]["count"] += 1
    
    sorted_locations = sorted(cumulative_by_name.items(), key=lambda item: item[1]["amount"], reverse=True)

    if not limit:
        limit = len(sorted_locations)
    elif int(limit) > len(sorted_locations) or int(limit) < 0:
        limit = len(sorted_locations)
    else:
        limit = int(limit)

    for name, data in sorted_locations[:limit]:
        print(f"{name}: ${data['amount']:.2f}")
    
    if len(sorted_locations) - limit > 0:
        print(f"[...And {len(sorted_locations) - limit} more...]")

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
        print('Deleting categories has not been set up yet')
    if chosensetting == 2:
        # update category
        print('Updating categories has not been set up yet')
    if chosensetting == 3:
        # change ratio targets
        print('Ratio targets have not been set up yet')
    if chosensetting == 4:
        # add recurring
        newline="\\"
        print('\n---ADD RECURRING TRANSACTION---')
        print('\nFor subscriptions, loan payments, pay, rent, and anything that happens on a fixed schedule')
        name = input("Enter name of the transaction: ")
        amount = input('Amount: ')
        category = choose_from_array(expense_categories, 'Choose category')
        increment = input('How often does it occur? (month/year): ')
        date = input(f"Which day(s) does it occur on? Separate different days using a space.{'Days can be 1, 15 => which means the recurring transaction will occur on the 1st and 15th of every month - Additonally, you can pass in conditional days as well: last, middle, and start' if increment.startswith('m') else ''}{'For increment year, type in the date like this: mm/dd, separate these out by spaces if it happens multiple times in a year but not on a month-to-month basis' if increment.startswith('y') else ''}")
        # TODO type is based off of the category
        add_recurring(name, '', amount, category, date, increment)
    if chosensetting == 5:
        recurring = load_file(DATA_DIR, "recurring")
        print('\n---REMOVE RECURRING TRANSACTION---')
        to_remove = choose_from_array([item['name'] for item in recurring['recurring']])
        delete_recurring(to_remove)

        
    if chosensetting == 5:
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
            month = input('Enter month [mm/yyyy]: ')
            view_monthly_summary(month)
        elif choice == '4':
            print('\n---BREAKDOWN OF THE CURRENT YEAR---')
            view_year_transactions()
        elif choice == '5':
            print("\n---BREAKDOWN BY CATEGORY---")
            month = input('Enter month (as number), for full year, type Y: ')
            category_breakdown(month)
        elif choice =='6':
            print('\n---BREAKDOWN BY LOCATION---')
            month = input('Enter month (as number), for full year, type Y: ')
            limit = input('Would you like to limit how many are shown? If not, skip: ')
            location_breakdown(month, limit)
        elif choice == '7':
            print('\n---SETTINGS---')
            choose_settings()

        elif choice == '8':
            print("---EXITING THE APP: bye bye!---")
            break
        elif choice == '9':
            print('This is a lightweight budgeting app built in Python!')
            print('© Evan Jin 2024')
            print('Notes')
            print('- Generally, months should be passed in as integers')
            print('- You can usually press enter to skip a step, and it will fill in with a default (usually the current day/month/year)')
        elif choice == 'sm':
            setup_month(12)
        else:
            print("Invalid option! Please try again.")

if __name__ == '__main__':
     main()
