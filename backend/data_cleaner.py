import pandas as pd
import json
from datetime import datetime
from collections import Counter

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
    df = df.dropna(how='all')
    
    cleaned_data = []
    
    for _, row in df.iterrows():
        cleaned_row = {}
        for col, value in row.items():
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
        with open(json_file, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    
    existing_data.extend(new_data)
    
    with open(json_file, 'w') as f:
        json.dump(existing_data, f, indent=4)
    
    return len(new_data)

def convert_csv_to_model_format(df):
    """Convert CSV with Yes/No symptom columns to model's expected format.
    
    Expected CSV columns: Disease, Fever, Cough, Fatigue, Difficulty Breathing,
                         Age, Gender, Blood Pressure, Cholesterol Level, Outcome Variable
    
    Output format: Age, Gender, Symptoms (comma-separated), Causes, Disease, Medicine
    """
    symptom_columns = ['Fever', 'Cough', 'Fatigue', 'Difficulty Breathing']
    
    cleaned_data = []
    for _, row in df.iterrows():
        try:
            age = int(row.get('Age', 0))
            
            gender_raw = str(row.get('Gender', '')).strip().upper()
            gender = 'M' if gender_raw.startswith('M') else 'F'
            
            symptoms = []
            for col in symptom_columns:
                if col in df.columns and str(row.get(col, '')).strip().upper() == 'YES':
                    symptoms.append(col)
            symptoms_str = ', '.join(symptoms) if symptoms else 'None'
            
            bp = str(row.get('Blood Pressure', '')).strip()
            chol = str(row.get('Cholesterol Level', '')).strip()
            causes = f"{bp} blood pressure, {chol} cholesterol" if bp and chol else bp or chol or "Unknown"
            
            disease = str(row.get('Disease', '')).strip()
            
            medicine = row.get('Medicine', None)
            if pd.isna(medicine) or not str(medicine).strip():
                medicine = "TBD"
            else:
                medicine = str(medicine).strip()
            
            if disease and symptoms_str != 'None':
                cleaned_data.append({
                    'Age': age,
                    'Gender': gender,
                    'Symptoms': symptoms_str,
                    'Causes': causes,
                    'Disease': disease,
                    'Medicine': medicine
                })
        except Exception as e:
            print(f"Skipping row: {e}")
            continue
    
    return cleaned_data

SPECIALTY_TO_CONDITIONS = {
    "Cardiology": {"disease": "Heart Disease", "symptoms": "Chest Pain, Shortness of Breath, Fatigue, Palpitations"},
    "Dermatology": {"disease": "Skin Disorder", "symptoms": "Skin Rash, Itching, Redness, Swelling"},
    "Endocrinology": {"disease": "Diabetes", "symptoms": "Fatigue, Weight Loss, Frequent Urination, Blurred Vision"},
    "Gastroenterology": {"disease": "Gastrointestinal Disorder", "symptoms": "Abdominal Pain, Nausea, Bloating, Diarrhea"},
    "Hematology": {"disease": "Blood Disorder", "symptoms": "Fatigue, Weakness, Bruising, Shortness of Breath"},
    "Hematology & Oncology": {"disease": "Blood Cancer", "symptoms": "Fatigue, Weight Loss, Night Sweats, Swelling"},
    "Nephrology": {"disease": "Chronic Kidney Disease", "symptoms": "Fatigue, Swelling, Difficulty Breathing, Nausea"},
    "Neurology": {"disease": "Neurological Disorder", "symptoms": "Headache, Dizziness, Numbness, Difficulty Breathing"},
    "Oncology": {"disease": "Cancer", "symptoms": "Weight Loss, Fatigue, Pain, Swelling"},
    "Ophthalmology": {"disease": "Eye Disease", "symptoms": "Blurred Vision, Eye Pain, Redness, Sensitivity"},
    "Orthopedic Surgery": {"disease": "Musculoskeletal Injury", "symptoms": "Joint Pain, Muscle Pain, Back Pain, Swelling"},
    "Psychiatry": {"disease": "Mental Health Disorder", "symptoms": "Anxiety, Sadness, Fatigue, Sleep Disturbance"},
    "Pulmonology": {"disease": "Respiratory Disease", "symptoms": "Cough, Difficulty Breathing, Chest Pain, Fatigue"},
    "Rheumatology": {"disease": "Autoimmune Disorder", "symptoms": "Joint Pain, Muscle Pain, Fatigue, Swelling"},
    "Urology": {"disease": "Urinary Tract Disorder", "symptoms": "Abdominal Pain, Frequent Urination, Fatigue"},
    "Allergy": {"disease": "Allergic Rhinitis", "symptoms": "Sneezing, Itching, Cough, Difficulty Breathing"},
    "Allergy & Immunology": {"disease": "Immune Disorder", "symptoms": "Fatigue, Swelling, Skin Rash, Fever"},
    "Anesthesiology": {"disease": "Chronic Pain", "symptoms": "Pain, Fatigue, Muscle Pain, Difficulty Breathing"},
    "Critical Care Medicine": {"disease": "Critical Illness", "symptoms": "Difficulty Breathing, Chest Pain, Fatigue, Confusion"},
    "Emergency Medicine": {"disease": "Acute Condition", "symptoms": "Pain, Difficulty Breathing, Chest Pain, Dizziness"},
    "Family Practice": {"disease": "General Condition", "symptoms": "Fever, Cough, Fatigue, Headache"},
    "General Practice": {"disease": "General Condition", "symptoms": "Fever, Cough, Fatigue, Headache"},
    "Geriatric Medicine": {"disease": "Age-Related Condition", "symptoms": "Fatigue, Joint Pain, Memory Loss, Difficulty Breathing"},
    "Gynecology": {"disease": "Gynecological Condition", "symptoms": "Abdominal Pain, Fatigue, Cramps, Nausea"},
    "Infectious Disease": {"disease": "Infection", "symptoms": "Fever, Fatigue, Chills, Muscle Pain"},
    "Internal Medicine": {"disease": "Internal Condition", "symptoms": "Fatigue, Fever, Cough, Pain"},
    "Interventional Cardiology": {"disease": "Coronary Artery Disease", "symptoms": "Chest Pain, Shortness of Breath, Palpitations, Fatigue"},
    "Neonatal-Perinatal Medicine": {"disease": "Neonatal Condition", "symptoms": "Difficulty Breathing, Fever, Fatigue"},
    "Obstetrics & Gynecology": {"disease": "Pregnancy Complication", "symptoms": "Abdominal Pain, Nausea, Fatigue, Swelling"},
    "Pain Medicine": {"disease": "Chronic Pain Syndrome", "symptoms": "Pain, Muscle Pain, Joint Pain, Fatigue"},
    "Pathology": {"disease": "Diagnostic Condition", "symptoms": "Fatigue, Weight Loss, Swelling"},
    "Physical Medicine & Rehabilitation": {"disease": "Rehabilitation Condition", "symptoms": "Joint Pain, Muscle Pain, Back Pain, Fatigue"},
    "Plastic and Reconstructive Surgery": {"disease": "Surgical Condition", "symptoms": "Pain, Swelling, Redness"},
    "Preventive Medicine": {"disease": "Preventive Care", "symptoms": "Fatigue, Headache, Stress"},
    "Psychiatry & Neurology": {"disease": "Neuropsychiatric Disorder", "symptoms": "Anxiety, Headache, Fatigue, Sleep Disturbance"},
    "Radiology": {"disease": "Diagnostic Finding", "symptoms": "Pain, Fatigue"},
    "Sports Medicine": {"disease": "Sports Injury", "symptoms": "Joint Pain, Muscle Pain, Swelling, Back Pain"},
    "Surgery": {"disease": "Surgical Condition", "symptoms": "Pain, Swelling, Fatigue"},
    "Thoracic Surgery": {"disease": "Thoracic Condition", "symptoms": "Chest Pain, Difficulty Breathing, Cough, Fatigue"},
    "Vascular Surgery": {"disease": "Vascular Disease", "symptoms": "Chest Pain, Swelling, Difficulty Breathing, Fatigue"},
}

DEFAULT_CONDITION = {"disease": "General Condition", "symptoms": "Fever, Fatigue, Headache"}

def convert_jsonl_to_model_format(filepath):
    """Convert CMS prescription JSONL to model's expected format.
    
    Maps specialty → disease/conditions, top prescriptions → medicine,
    region → causes, provider demographics → age/gender.
    """
    cleaned_data = []
    
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                record = json.loads(line.strip())
                if not record.get('cms_prescription_counts'):
                    continue
                
                pvars = record.get('provider_variables', {})
                prescriptions = record['cms_prescription_counts']
                
                specialty = pvars.get('specialty', '')
                condition = SPECIALTY_TO_CONDITIONS.get(specialty, DEFAULT_CONDITION)
                disease = condition['disease']
                symptoms = condition['symptoms']
                
                top_drugs = sorted(prescriptions.items(), key=lambda x: x[1], reverse=True)
                medicine = top_drugs[0][0] if top_drugs else "TBD"
                
                gender_raw = pvars.get('gender', '').strip().upper()
                gender = 'M' if gender_raw == 'M' else 'F'
                
                years = pvars.get('years_practicing', 5)
                age = 25 + years
                
                region = pvars.get('region', 'Unknown')
                settlement = pvars.get('settlement_type', 'Unknown')
                causes = f"{region} region, {settlement} area"
                
                cleaned_data.append({
                    'Age': age,
                    'Gender': gender,
                    'Symptoms': symptoms,
                    'Causes': causes,
                    'Disease': disease,
                    'Medicine': medicine
                })
                
            except Exception as e:
                print(f"Skipping line {line_num}: {e}")
                continue
    
    return cleaned_data