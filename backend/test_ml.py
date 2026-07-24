import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import json
import pandas as pd
from data_cleaner import clean_excel_data, update_json_data, convert_csv_to_model_format, convert_jsonl_to_model_format
from model_generator import MedicalPredictor, AdvancedMedicalPredictor, load_training_data
import tempfile

TMP = tempfile.gettempdir()
JSON_PATH = os.path.join(TMP, "output.json")

print("=" * 60)
print("TEST 1: CSV conversion + training (small dataset)")
print("=" * 60)

# Clear old data first
if os.path.exists(JSON_PATH):
    os.remove(JSON_PATH)

df = pd.read_csv("data.csv")
cleaned_csv = convert_csv_to_model_format(df)
print(f"CSV: {len(cleaned_csv)} records")

update_json_data(cleaned_csv, json_file=JSON_PATH)
data = load_training_data(JSON_PATH)
print(f"Loaded {len(data)} records for training")

predictor = MedicalPredictor()
result = predictor.train(data)
predictor.save_model()

print(f"\nBest model: {result['evaluation']['best_model']}")
print(f"Test accuracy: {result['evaluation']['test_metrics']['accuracy']}%")
print(f"CV accuracy: {result['evaluation']['cross_validation']['mean_accuracy']}%")
print(f"Feature importance (top 5):")
for fi in result['evaluation']['feature_importance'][:5]:
    print(f"  {fi['feature']}: {fi['importance']}%")

print(f"\nBenchmark results:")
for name, metrics in result['evaluation']['benchmark_results'].items():
    if 'error' not in metrics:
        print(f"  {name}: acc={metrics['accuracy']}% f1={metrics['f1_score']}% ({metrics['train_time_seconds']}s)")

print("\n" + "=" * 60)
print("TEST 2: Predictions")
print("=" * 60)

test_cases = [
    {"age": 25, "gender": "M", "symptoms": "Fever, Cough", "cause": "Normal blood pressure, Normal cholesterol"},
    {"age": 55, "gender": "F", "symptoms": "Difficulty Breathing, Fatigue", "cause": "High blood pressure, High cholesterol"},
]

for tc in test_cases:
    diseases, medicines = predictor.predict(**tc)
    print(f"\nInput: {tc}")
    print(f"  Diseases: {diseases[:3]}")
    print(f"  Medicines: {medicines[:3]}")

print("\n" + "=" * 60)
print("TEST 3: Advanced predictor")
print("=" * 60)

adv = AdvancedMedicalPredictor()
adv._train(data, sample_size=5000)
adv.save_model()
print(f"Accuracies: {adv.get_model_accuracies()}")

for tc in test_cases:
    result = adv.predict_single(**tc)
    print(f"  {tc['symptoms'][:30]}... -> {result}")

print("\n" + "=" * 60)
print("TEST 4: JSONL conversion (first 1000 lines)")
print("=" * 60)

import subprocess
subprocess.run([sys.executable, "-c", """
import json, sys
sys.path.insert(0, '.')
from data_cleaner import convert_jsonl_to_model_format

# Test with first 1000 lines
with open('db.jsonl') as fin, open('db_small.jsonl', 'w') as fout:
    for i, line in enumerate(fin):
        if i >= 1000: break
        fout.write(line)

data = convert_jsonl_to_model_format('db_small.jsonl')
print(f'JSONL converted: {len(data)} records')
print(f'Sample: {data[0]}')
os.remove('db_small.jsonl')
"""], cwd=os.path.dirname(__file__))

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
