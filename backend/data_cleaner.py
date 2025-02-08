import pandas as pd
import json
from datetime import datetime

def standardize_date(date_str):
    if pd.isna(date_str):
        return None
        
    date_str = str(date_str).split(' ')[0]
    
    date_formats = [
        '%d-%m-%Y', '%d/%m/%Y',
        '%Y-%m-%d', '%Y/%m/%d',
        '%d-%m-%y', '%d/%m/%y',
        '%m/%d/%Y', '%m-%d-%Y'
    ]
    
    for fmt in date_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime('%d-%m-%Y')
        except ValueError:
            continue
    
    return None

def clean_excel_data(df):
    # Drop rows with all null values
    df = df.dropna(how='all')
    
    # Clean each column
    cleaned_data = []
    
    for _, row in df.iterrows():
        cleaned_row = {}
        for col, value in row.items():
            # Convert to string and strip whitespace
            if pd.notna(value):
                if col == 'DateOfBirth':
                    cleaned_row[col] = standardize_date(value)
                else:
                    cleaned_row[col] = str(value).strip()
            else:
                cleaned_row[col] = None
        cleaned_data.append(cleaned_row)
    
    return cleaned_data

def update_json_data(new_data, json_file='output.json'):
    try:
        # Read existing data
        with open(json_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    
    # Append new data
    existing_data.extend(new_data)
    
    # Write updated data back to file
    with open(json_file, 'w') as f:
        json.dump(existing_data, f, indent=4)
    
    return len(new_data)