# model_generator.py
import json
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import defaultdict
import os
import time
from typing import List, Dict

MEDICAL_PREDICTOR_MODEL_PATH = "medical_predictor_model.joblib"
ADVANCED_PREDICTOR_MODEL_PATH = "advanced_predictor_model.joblib"

class MedicalPredictor:
    def __init__(self):
        self.disease_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.medicine_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()
        self.is_trained = False

    def clean_data(self, data):
        """Clean and validate the training data"""
        cleaned_data = []
        for record in data:
            try:
                cleaned_record = {
                    'Age': int(record.get('Age', 0)),
                    'Gender': str(record.get('Gender', '')).strip().upper(),
                    'Symptoms': str(record.get('Symptoms', '')),
                    'Causes': str(record.get('Causes', '')),
                    'Disease': str(record.get('Disease', '')),
                    'Medicine': str(record.get('Medicine', ''))
                }
                if cleaned_record['Disease'] and cleaned_record['Symptoms']:
                    cleaned_data.append(cleaned_record)
            except Exception as e:
                print(f"Skipping invalid record: {str(e)}")
        return cleaned_data

    def prepare_features(self, data):
        """Prepare features from raw data"""
        symptoms = [self.safe_split(record['Symptoms']) for record in data]
        causes = [record['Causes'] for record in data]
        ages = np.array([record['Age'] for record in data]).reshape(-1, 1)
        genders = np.array([1 if record['Gender'].startswith('M') else 0 
                           for record in data]).reshape(-1, 1)

        X_symptoms = self.symptom_encoder.fit_transform(symptoms)
        X_causes = self.cause_encoder.fit_transform(causes).reshape(-1, 1)

        X = np.hstack([ages, genders, X_symptoms, X_causes])
        return X

    def prepare_targets(self, data):
        """Prepare target variables"""
        diseases = [record['Disease'] for record in data]
        medicines = [self.safe_split(record['Medicine']) for record in data]

        y_diseases = self.disease_encoder.fit_transform(diseases)
        y_medicines = self.medicine_encoder.fit_transform(medicines)

        return y_diseases, y_medicines

    def train(self, training_data):
        """Train the models"""
        print("Cleaning and validating data...")
        cleaned_data = self.clean_data(training_data)
        if not cleaned_data:
            raise ValueError("No valid training data after cleaning")
        
        print(f"Using {len(cleaned_data)} valid records for training")
        
        print("Preparing features...")
        X = self.prepare_features(cleaned_data)
        y_diseases, y_medicines = self.prepare_targets(cleaned_data)

        X_train, X_test, y_disease_train, y_disease_test, y_medicine_train, y_medicine_test = \
            train_test_split(X, y_diseases, y_medicines, test_size=0.2, random_state=42)

        print("Training disease classifier...")
        self.disease_classifier.fit(X_train, y_disease_train)
        disease_accuracy = self.disease_classifier.score(X_test, y_disease_test)

        print("Training medicine classifier...")
        self.medicine_classifier.fit(X_train, y_medicine_train)
        medicine_accuracy = accuracy_score(y_medicine_test, 
                                        self.medicine_classifier.predict(X_test))

        print(f"Disease Classifier Accuracy: {disease_accuracy*100:.2f}%")
        print(f"Medicine Classifier Accuracy: {medicine_accuracy*100:.2f}%")
        
        self.is_trained = True
        
        return {
            "disease_accuracy": disease_accuracy * 100,
            "medicine_accuracy": medicine_accuracy * 100
        }

    def predict(self, age, gender, symptoms, cause):
        """Make predictions with confidence scores"""
        if not self.is_trained:
            raise ValueError("Model not trained yet. Call train() first or load a trained model.")
            
        try:
            symptoms_list = self.safe_split(symptoms)
            if not symptoms_list:
                raise ValueError("No valid symptoms provided")

            X_symptoms = self.symptom_encoder.transform([symptoms_list])
            safe_cause = cause
            if hasattr(self.cause_encoder, "classes_") and cause not in self.cause_encoder.classes_:
                # fall back to most frequent/first known cause to avoid transform errors on unseen text
                safe_cause = self.cause_encoder.classes_[0]
            X_cause = self.cause_encoder.transform([safe_cause]).reshape(1, -1)
            X = np.hstack([
                np.array([[age]]), 
                np.array([[1 if gender == 'M' else 0]]), 
                X_symptoms, 
                X_cause
            ])

            disease_probs = self.disease_classifier.predict_proba(X)[0]
            top_diseases_idx = np.argsort(disease_probs)[-5:][::-1]
            diseases = [(self.disease_encoder.inverse_transform([idx])[0], 
                        float(disease_probs[idx] * 100)) 
                       for idx in top_diseases_idx if disease_probs[idx] > 0.2]

            medicine_pred = self.medicine_classifier.predict(X)
            medicine_probs = self.medicine_classifier.predict_proba(X)
            
            medicines = []
            for i, (is_recommended, prob_array) in enumerate(zip(medicine_pred[0], medicine_probs)):
                # lower threshold to surface more medicines; avoid zero-confidence filtering
                if np.any(is_recommended) or np.max(prob_array) > 0.05:
                    medicine_name = self.medicine_encoder.classes_[i]
                    confidence = float(np.max(prob_array) * 100)
                    medicines.append((str(medicine_name), confidence))
            
            medicines.sort(key=lambda x: x[1], reverse=True)
            return diseases[:5], medicines[:5]

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return [], []

    def save_model(self, filepath=MEDICAL_PREDICTOR_MODEL_PATH):
        """Save the trained model to a file using joblib"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model. Call train() first.")
            
        model_data = {
            'disease_classifier': self.disease_classifier,
            'medicine_classifier': self.medicine_classifier,
            'symptom_encoder': self.symptom_encoder,
            'disease_encoder': self.disease_encoder,
            'medicine_encoder': self.medicine_encoder,
            'cause_encoder': self.cause_encoder,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"MedicalPredictor model saved to {filepath}")
        
    def load_model(self, filepath=MEDICAL_PREDICTOR_MODEL_PATH):
        """Load a trained model from a file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
            
        model_data = joblib.load(filepath)
        
        self.disease_classifier = model_data['disease_classifier']
        self.medicine_classifier = model_data['medicine_classifier']
        self.symptom_encoder = model_data['symptom_encoder']
        self.disease_encoder = model_data['disease_encoder']
        self.medicine_encoder = model_data['medicine_encoder']
        self.cause_encoder = model_data['cause_encoder']
        self.is_trained = model_data['is_trained']
        
        print(f"MedicalPredictor model loaded from {filepath}")

    @staticmethod
    def safe_split(value):
        """Safely split a string, handling None and empty values"""
        if not value:
            return []
        return [item.strip() for item in str(value).split(',') if item.strip()]


class AdvancedMedicalPredictor:
    def __init__(self, json_file=None):
        """Initialize the medical predictor"""
        self.disease_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.medicine_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()
        self.disease_accuracy = 0.0
        self.medicine_accuracy = 0.0
        self.is_trained = False
        
        if json_file:
            self._load_and_train(json_file)

    def _safe_split(self, value):
        """Safely split a string, handling None and empty values"""
        if not value:
            return []
        return [item.strip() for item in str(value).split(',') if item.strip()]

    def _clean_data(self, data):
        """Clean and validate the training data"""
        cleaned_data = []
        for record in data:
            try:
                cleaned_record = {
                    'Age': int(record.get('Age', 0)),
                    'Gender': str(record.get('Gender', '')).strip().upper(),
                    'Symptoms': str(record.get('Symptoms', '')),
                    'Causes': str(record.get('Causes', '')),
                    'Disease': str(record.get('Disease', '')),
                    'Medicine': str(record.get('Medicine', ''))
                }
                if cleaned_record['Disease'] and cleaned_record['Symptoms']:
                    cleaned_data.append(cleaned_record)
            except Exception:
                continue
        return cleaned_data

    def _prepare_features(self, data):
        """Prepare features from raw data"""
        symptoms = [self._safe_split(record['Symptoms']) for record in data]
        causes = [record['Causes'] for record in data]
        ages = np.array([record['Age'] for record in data]).reshape(-1, 1)
        genders = np.array([1 if record['Gender'].startswith('M') else 0 
                           for record in data]).reshape(-1, 1)

        X_symptoms = self.symptom_encoder.fit_transform(symptoms)
        X_causes = self.cause_encoder.fit_transform(causes).reshape(-1, 1)

        return np.hstack([ages, genders, X_symptoms, X_causes])

    def _prepare_targets(self, data):
        """Prepare target variables"""
        diseases = [record['Disease'] for record in data]
        medicines = [self._safe_split(record['Medicine']) for record in data]

        y_diseases = self.disease_encoder.fit_transform(diseases)
        y_medicines = self.medicine_encoder.fit_transform(medicines)

        return y_diseases, y_medicines

    def _load_and_train(self, json_file):
        """Load data from JSON file and train the models"""
        if os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH):
            print(f"Pre-trained model found. Loading from {ADVANCED_PREDICTOR_MODEL_PATH}")
            self.load_model()
            return
            
        try:
            print(f"No pre-trained model found. Training from {json_file}")
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            training_data = data if isinstance(data, list) else data.get('records', [])
            if not training_data:
                raise ValueError("No training data found in JSON file")
            
            self._train(training_data)
            
        except Exception as e:
            raise Exception(f"Failed to load and train with data: {str(e)}")

    def _train(self, training_data):
        """Train the models with the provided data"""
        print("Cleaning and preparing data...")
        cleaned_data = self._clean_data(training_data)
        if not cleaned_data:
            raise ValueError("No valid training data after cleaning")

        print(f"Training with {len(cleaned_data)} records...")
        X = self._prepare_features(cleaned_data)
        y_diseases, y_medicines = self._prepare_targets(cleaned_data)

        print("Splitting data into training and test sets...")
        X_train, X_test, y_disease_train, y_disease_test, y_medicine_train, y_medicine_test = \
            train_test_split(X, y_diseases, y_medicines, test_size=0.2, random_state=42)

        print("Training disease classifier...")
        start_time = time.time()
        self.disease_classifier.fit(X_train, y_disease_train)
        print(f"Disease classifier training completed in {time.time() - start_time:.2f} seconds")
        
        print("Training medicine classifier...")
        start_time = time.time()
        self.medicine_classifier.fit(X_train, y_medicine_train)
        print(f"Medicine classifier training completed in {time.time() - start_time:.2f} seconds")

        print("Evaluating classifiers...")
        self.disease_accuracy = self.disease_classifier.score(X_test, y_disease_test)
        self.medicine_accuracy = accuracy_score(y_medicine_test, 
                                             self.medicine_classifier.predict(X_test))
        
        print(f"Disease accuracy: {self.disease_accuracy * 100:.2f}%")
        print(f"Medicine accuracy: {self.medicine_accuracy * 100:.2f}%")
        
        self.is_trained = True

    def get_model_accuracies(self):
        """Return the accuracy scores of the models"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
            
        return {
            'disease_accuracy': round(self.disease_accuracy * 100, 2),
            'medicine_accuracy': round(self.medicine_accuracy * 100, 2)
        }

    def predict_single(self, age, gender, symptoms, cause):
        """Make a single prediction with the highest confidence"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
            
        try:
            if not (0 <= age <= 120):
                raise ValueError("Invalid age")
            if gender.upper() not in ['M', 'F']:
                raise ValueError("Invalid gender")
            if not symptoms.strip():
                raise ValueError("Symptoms cannot be empty")
            if not cause.strip():
                raise ValueError("Cause cannot be empty")

            diseases, medicines = self._predict(age, gender, symptoms, cause)
            
            if not diseases or not medicines:
                return {'error': 'Could not make predictions with sufficient confidence'}

            top_disease = max(diseases, key=lambda x: x[1])
            top_medicine = max(medicines, key=lambda x: x[1])

            return {
                'disease': {
                    'name': top_disease[0],
                    'confidence': round(top_disease[1], 2)
                },
                'medicine': {
                    'name': top_medicine[0],
                    'confidence': round(top_medicine[1], 2)
                }
            }

        except Exception as e:
            return {'error': str(e)}

    def _predict(self, age, gender, symptoms, cause):
        """Internal prediction method"""
        symptoms_list = self._safe_split(symptoms)
        
        X_symptoms = self.symptom_encoder.transform([symptoms_list])
        safe_cause = cause
        if hasattr(self.cause_encoder, "classes_") and cause not in self.cause_encoder.classes_:
            safe_cause = self.cause_encoder.classes_[0]
        X_cause = self.cause_encoder.transform([safe_cause]).reshape(1, -1)
        X = np.hstack([
            np.array([[age]]),
            np.array([[1 if gender.upper() == 'M' else 0]]),
            X_symptoms,
            X_cause
        ])

        disease_probs = self.disease_classifier.predict_proba(X)[0]
        medicine_probs = self.medicine_classifier.predict_proba(X)

        top_diseases_idx = np.argsort(disease_probs)[-5:][::-1]
        diseases = [(self.disease_encoder.inverse_transform([idx])[0],
                    float(disease_probs[idx] * 100))
                   for idx in top_diseases_idx if disease_probs[idx] > 0.2]

        medicines = []
        for i, prob_array in enumerate(medicine_probs):
            # lower threshold to surface candidates
            if np.max(prob_array) > 0.05:
                medicine_name = self.medicine_encoder.classes_[i]
                confidence = float(np.max(prob_array) * 100)
                medicines.append((str(medicine_name), confidence))

        return diseases, medicines
    
    def save_model(self, filepath=ADVANCED_PREDICTOR_MODEL_PATH):
        """Save the trained model to a file using joblib"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
            
        model_data = {
            'disease_classifier': self.disease_classifier,
            'medicine_classifier': self.medicine_classifier,
            'symptom_encoder': self.symptom_encoder,
            'disease_encoder': self.disease_encoder,
            'medicine_encoder': self.medicine_encoder,
            'cause_encoder': self.cause_encoder,
            'disease_accuracy': self.disease_accuracy,
            'medicine_accuracy': self.medicine_accuracy,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, filepath)
        print(f"AdvancedMedicalPredictor model saved to {filepath}")
        
    def load_model(self, filepath=ADVANCED_PREDICTOR_MODEL_PATH):
        """Load a trained model from a file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
            
        model_data = joblib.load(filepath)
        
        self.disease_classifier = model_data['disease_classifier']
        self.medicine_classifier = model_data['medicine_classifier']
        self.symptom_encoder = model_data['symptom_encoder']
        self.disease_encoder = model_data['disease_encoder']
        self.medicine_encoder = model_data['medicine_encoder']
        self.cause_encoder = model_data['cause_encoder']
        self.disease_accuracy = model_data['disease_accuracy']
        self.medicine_accuracy = model_data['medicine_accuracy']
        self.is_trained = model_data['is_trained']
        
        print(f"AdvancedMedicalPredictor model loaded from {filepath}")


def load_training_data(json_path='output.json'):
    """Load training data from a JSON file"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        training_data = data if isinstance(data, list) else data.get('records', [])
        if not training_data:
            raise ValueError("No training data found in JSON file")
        return training_data
    except FileNotFoundError:
        print("Error: output.json file not found")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in output.json")
        return []
    except Exception as e:
        print(f"Error loading training data: {str(e)}")
        return []


def main():
    """Generate and save the models"""
    json_path = input("Enter the path to the JSON file (or press Enter to use 'output.json'): ")
    if not json_path:
        json_path = "output.json"
    
    print("\n=== GENERATING MEDICAL PREDICTION MODELS ===\n")
    
    basic_exists = os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH)
    advanced_exists = os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH)
    
    if basic_exists and advanced_exists:
        print(f"Both models already exist:")
        print(f"1. Basic model: {MEDICAL_PREDICTOR_MODEL_PATH}")
        print(f"2. Advanced model: {ADVANCED_PREDICTOR_MODEL_PATH}")
        
        choice = input("\nDo you want to rebuild the models? (y/n): ")
        if choice.lower() != 'y':
            print("Using existing models. Exiting.")
            return
    
    print(f"\nLoading training data from {json_path}...")
    training_data = load_training_data(json_path)
    if not training_data:
        print("No training data found. Exiting.")
        return
    
    print(f"Loaded {len(training_data)} training records.")
    
    print("\n=== TRAINING BASIC MEDICAL PREDICTOR ===\n")
    basic_predictor = MedicalPredictor()
    metrics = basic_predictor.train(training_data)
    basic_predictor.save_model()
    
    print("\n=== TRAINING ADVANCED MEDICAL PREDICTOR ===\n")
    advanced_predictor = AdvancedMedicalPredictor()
    advanced_predictor._train(training_data)
    
    print("\n=== TESTING LOADED MODELS ===\n")
    
    test_basic = MedicalPredictor()
    test_basic.load_model()
    
    test_advanced = AdvancedMedicalPredictor()
    test_advanced.load_model()
    
    # Test prediction
    test_symptoms = "fever, headache, cough"
    test_age = 35
    test_gender = "M"
    test_cause = "Viral Infection"
    
    print(f"Test prediction with: Age={test_age}, Gender={test_gender}, Symptoms='{test_symptoms}', Cause='{test_cause}'")
    
    diseases, medicines = test_basic.predict(test_age, test_gender, test_symptoms, test_cause)
    print("\nBasic predictor results:")
    if diseases:
        print("Top diseases:")
        for disease, conf in diseases:
            print(f"  - {disease}: {conf:.2f}%")
    else:
        print("No diseases predicted")
        
    result = test_advanced.predict_single(test_age, test_gender, test_symptoms, test_cause)
    print("\nAdvanced predictor results:")
    if 'error' not in result:
        print(f"Disease: {result['disease']['name']} ({result['disease']['confidence']}%)")
        print(f"Medicine: {result['medicine']['name']} ({result['medicine']['confidence']}%)")
    else:
        print(f"Error: {result['error']}")
    
    print("\n=== MODEL GENERATION COMPLETED ===\n")
    print(f"Models saved to:")
    print(f"1. Basic model: {MEDICAL_PREDICTOR_MODEL_PATH}")
    print(f"2. Advanced model: {ADVANCED_PREDICTOR_MODEL_PATH}")
    print("\nThese models can now be loaded directly in your application.")


if __name__ == "__main__":
    main()