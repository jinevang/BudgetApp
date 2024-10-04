from datetime import datetime

def parse_date(date_str):
  try:
    parts = date_str.split('/')
    
    if(len(parts) is 2):
      month, day = parts
      year = str(datetime.now().year)
    elif len(parts) is 3:
      month, day, year = parts
    else:
      raise ValueError('Date must be in MM/DD or MM/DD/YYYY format.')
    
    month = int(month)
    if not(1 <= month <= 12):
      raise ValueError("Month must be between 1 and 12")			
    
    formatted_date = f"{month}/{day}/{year}"
    return formatted_date
  except ValueError as e:
    print(f"Error: {e}")
    return None