import sys
import os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from data_cleaner import clean_excel_data, update_json_data, convert_csv_to_model_format
from model_generator import MedicalPredictor, AdvancedMedicalPredictor, load_training_data
import tempfile

TMP_DIR = tempfile.gettempdir()
JSON_DATA_PATH = os.path.join(TMP_DIR, "output.json")

print("=" * 60)
print("TEST 1: Convert CSV to model format")
print("=" * 60)

df = pd.read_csv("data.csv")
print(f"CSV shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

cleaned = convert_csv_to_model_format(df)
print(f"Converted {len(cleaned)} records")
print(f"Sample record: {cleaned[0]}")

# Check medicine values
meds = set(r['Medicine'] for r in cleaned)
print(f"Unique medicines: {meds}")

print("\n" + "=" * 60)
print("TEST 2: Train Basic Predictor on CSV data")
print("=" * 60)

update_json_data(cleaned, json_file=JSON_DATA_PATH)
training_data = load_training_data(JSON_DATA_PATH)
print(f"Loaded {len(training_data)} records for training")

basic = MedicalPredictor()
metrics = basic.train(training_data)
print(f"Metrics: {metrics}")

print("\n" + "=" * 60)
print("TEST 3: Train Advanced Predictor on CSV data")
print("=" * 60)

adv = AdvancedMedicalPredictor()
adv._train(training_data)
print(f"Accuracies: {adv.get_model_accuracies()}")

print("\n" + "=" * 60)
print("TEST 4: Predictions (CSV-trained models)")
print("=" * 60)

test_cases = [
    {"age": 25, "gender": "M", "symptoms": "Fever, Cough", "cause": "Normal blood pressure, Normal cholesterol"},
    {"age": 60, "gender": "F", "symptoms": "Fatigue, Difficulty Breathing", "cause": "High blood pressure, High cholesterol"},
    {"age": 35, "gender": "M", "symptoms": "Fever, Fatigue", "cause": "Low blood pressure, Low cholesterol"},
]

for tc in test_cases:
    print(f"\nInput: {tc}")
    diseases, medicines = basic.predict(**tc)
    print(f"  Basic diseases: {diseases[:3]}")
    print(f"  Basic medicines: {medicines[:3]}")
    
    result = adv.predict_single(**tc)
    print(f"  Advanced: {result}")

print("\n" + "=" * 60)
print("TEST 5: Also test on original xlsx data (if available)")
print("=" * 60)

if os.path.exists("data.xlsx"):
    df_xlsx = pd.read_excel("data.xlsx")
    cleaned_xlsx = clean_excel_data(df_xlsx)
    print(f"XLSX converted {len(cleaned_xlsx)} records")
    if cleaned_xlsx:
        print(f"Sample: {cleaned_xlsx[0]}")
else:
    print("data.xlsx not found, skipping")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
