from datetime import datetime
import os
import json

def parse_date(date_str):
  try:
    parts = date_str.split('/')
    if(len(parts) == 1):
      day = parts[0]
      month = str(datetime.now().month)
      year = str(datetime.now().year)
    elif(len(parts) == 2):
      month, day = parts
      year = str(datetime.now().year)
    elif len(parts) == 3:
      month, day, year = parts
    else:
      raise ValueError('Date must be in DD, MM/DD or MM/DD/YYYY format. Unfilled data will be marked as current.')
    
    month = int(month)
    if not(1 <= month <= 12):
      raise ValueError("Month must be between 1 and 12")			
    
    formatted_date = f"{month}/{day}/{year}"
    return formatted_date
  except ValueError as e:
    print(f"Error: {e}")
    return None

def get_category_type(category_name, data):
  for category in data["categories"]:
    if category["name"] == category_name:
      return category["type"]
  return ""

def get_category_icon(category_name, data):
  for category in data["categories"]:
    if category["name"] == category_name:
      return category["icon"]
  return ""
  
def ignore_field(category_name, data):
  for category in data["categories"]:
    if category["name"] == category_name:
      return category["ignore"]
  return False
  
def load_file(datadir, filename):
  file_name = os.path.join(datadir, f'{filename}.json')
  if os.path.exists(file_name):
      with open(file_name, 'r') as file:
          return json.load(file)
  return {}

def save_to_file(datadir, data, filename):
  file_name = os.path.join(datadir, f'{filename}.json')
  with open(file_name, 'w') as file:
      json.dump(data, file, indent=4)

def choose_from_array(array, prompt="Please enter your selection", returnindex=False):
  for idx, item in enumerate(array, start=1):
        print(f"{idx}) {item}")
  while True:
    try:
        choice = int(input(f"{prompt}: "))  # Use f-string to format the prompt with ":"
        if 1 <= choice <= len(array):
            if returnindex:
              return choice - 1
            else:
              return array[choice - 1]
        else:
            print("Invalid choice, please enter a valid number.")
    except ValueError:
        print("Invalid input, please enter a number.")