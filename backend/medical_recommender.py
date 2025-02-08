# medical_predictor.py

import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from typing import List, Tuple, Dict, Any, Optional
class AdvancedMedicalPredictor:
    def __init__(self, json_file: str):
        """Initialize and train the medical predictor with data from json_file"""
        # Initialize classifiers and encoders
        self.disease_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.medicine_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()
        
        # Load and train with data
        self._load_and_train(json_file)

    def _safe_split(self, value: str) -> List[str]:
        """Safely split a string, handling None and empty values"""
        if not value:
            return []
        return [item.strip() for item in str(value).split(',') if item.strip()]

    def _clean_data(self, data: List[Dict]) -> List[Dict]:
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

    def _prepare_features(self, data: List[Dict]) -> np.ndarray:
        """Prepare features from raw data"""
        symptoms = [self._safe_split(record['Symptoms']) for record in data]
        causes = [record['Causes'] for record in data]
        ages = np.array([record['Age'] for record in data]).reshape(-1, 1)
        genders = np.array([1 if record['Gender'].startswith('M') else 0 
                           for record in data]).reshape(-1, 1)

        X_symptoms = self.symptom_encoder.fit_transform(symptoms)
        X_causes = self.cause_encoder.fit_transform(causes).reshape(-1, 1)

        return np.hstack([ages, genders, X_symptoms, X_causes])

    def _prepare_targets(self, data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare target variables"""
        diseases = [record['Disease'] for record in data]
        medicines = [self._safe_split(record['Medicine']) for record in data]

        y_diseases = self.disease_encoder.fit_transform(diseases)
        y_medicines = self.medicine_encoder.fit_transform(medicines)

        return y_diseases, y_medicines

    def _load_and_train(self, json_file: str) -> None:
        """Load data from JSON file and train the models"""
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            training_data = data if isinstance(data, list) else data.get('records', [])
            if not training_data:
                raise ValueError("No training data found in JSON file")
            
            self._train(training_data)
            
        except Exception as e:
            raise Exception(f"Failed to load and train with data: {str(e)}")

    def _train(self, training_data: List[Dict]) -> None:
        """Train the models with the provided data"""
        cleaned_data = self._clean_data(training_data)
        if not cleaned_data:
            raise ValueError("No valid training data after cleaning")

        X = self._prepare_features(cleaned_data)
        y_diseases, y_medicines = self._prepare_targets(cleaned_data)

        X_train, X_test, y_disease_train, y_disease_test, y_medicine_train, y_medicine_test = \
            train_test_split(X, y_diseases, y_medicines, test_size=0.2, random_state=42)

        self.disease_classifier.fit(X_train, y_disease_train)
        self.medicine_classifier.fit(X_train, y_medicine_train)

        self.disease_accuracy = self.disease_classifier.score(X_test, y_disease_test)
        self.medicine_accuracy = accuracy_score(y_medicine_test, 
                                             self.medicine_classifier.predict(X_test))

    def get_model_accuracies(self) -> Dict[str, float]:
        """Return the accuracy scores of the models"""
        return {
            'disease_accuracy': round(self.disease_accuracy * 100, 2),
            'medicine_accuracy': round(self.medicine_accuracy * 100, 2)
        }

    def predict_single(self, age: int, gender: str, symptoms: str, cause: str) -> Dict[str, Any]:
        """Make a single prediction with the highest confidence"""
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

    def _predict(self, age: int, gender: str, symptoms: str, cause: str) -> Tuple[List, List]:
        """Internal prediction method"""
        symptoms_list = self._safe_split(symptoms)
        
        X_symptoms = self.symptom_encoder.transform([symptoms_list])
        X_cause = self.cause_encoder.transform([cause]).reshape(1, -1)
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
            if np.max(prob_array) > 0.3:
                medicine_name = self.medicine_encoder.classes_[i]
                confidence = float(np.max(prob_array) * 100)
                medicines.append((str(medicine_name), confidence))

        return diseases, medicines