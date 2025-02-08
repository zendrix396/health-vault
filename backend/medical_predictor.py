import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from collections import defaultdict

class MedicalPredictor:
    def __init__(self):
        self.disease_classifier = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.medicine_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()

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
        # Extract and validate features
        symptoms = [self.safe_split(record['Symptoms']) for record in data]
        causes = [record['Causes'] for record in data]
        ages = np.array([record['Age'] for record in data]).reshape(-1, 1)
        genders = np.array([1 if record['Gender'].startswith('M') else 0 
                           for record in data]).reshape(-1, 1)

        # Transform features
        X_symptoms = self.symptom_encoder.fit_transform(symptoms)
        X_causes = self.cause_encoder.fit_transform(causes).reshape(-1, 1)

        # Combine features
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

        # Split data
        X_train, X_test, y_disease_train, y_disease_test, y_medicine_train, y_medicine_test = \
            train_test_split(X, y_diseases, y_medicines, test_size=0.2, random_state=42)

        # Train disease classifier
        print("Training disease classifier...")
        self.disease_classifier.fit(X_train, y_disease_train)
        disease_accuracy = self.disease_classifier.score(X_test, y_disease_test)

        # Train medicine classifier
        print("Training medicine classifier...")
        self.medicine_classifier.fit(X_train, y_medicine_train)
        medicine_accuracy = accuracy_score(y_medicine_test, 
                                        self.medicine_classifier.predict(X_test))

        print(f"Disease Classifier Accuracy: {disease_accuracy*100:.2f}%")
        print(f"Medicine Classifier Accuracy: {medicine_accuracy*100:.2f}%")

    def predict(self, age, gender, symptoms, cause):
        """Make predictions with confidence scores"""
        try:
            # Prepare input features
            symptoms_list = self.safe_split(symptoms)
            if not symptoms_list:
                raise ValueError("No valid symptoms provided")

            X_symptoms = self.symptom_encoder.transform([symptoms_list])
            X_cause = self.cause_encoder.transform([cause]).reshape(1, -1)
            X = np.hstack([
                np.array([[age]]), 
                np.array([[1 if gender == 'M' else 0]]), 
                X_symptoms, 
                X_cause
            ])

            # Get disease predictions
            disease_probs = self.disease_classifier.predict_proba(X)[0]
            top_diseases_idx = np.argsort(disease_probs)[-5:][::-1]
            diseases = [(self.disease_encoder.inverse_transform([idx])[0], 
                        float(disease_probs[idx] * 100)) 
                       for idx in top_diseases_idx if disease_probs[idx] > 0.2]

            # Get medicine predictions
            medicine_pred = self.medicine_classifier.predict(X)
            medicine_probs = self.medicine_classifier.predict_proba(X)
            
            medicines = []
            for i, (is_recommended, prob_array) in enumerate(zip(medicine_pred[0], medicine_probs)):
                if np.any(is_recommended):
                    medicine_name = self.medicine_encoder.classes_[i]
                    confidence = float(np.max(prob_array) * 100)
                    medicines.append((str(medicine_name), confidence))
            
            medicines.sort(key=lambda x: x[1], reverse=True)
            return diseases[:5], medicines[:5]

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return [], []

    @staticmethod
    def safe_split(value):
        """Safely split a string, handling None and empty values"""
        if not value:
            return []
        return [item.strip() for item in str(value).split(',') if item.strip()]

def load_training_data(json_path='output.json'):
    """Load training data from a JSON file"""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        # Extract training records
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
    """Main function for standalone usage"""
    training_data = load_training_data()
    if not training_data:
        return

    # Initialize and train predictor
    predictor = MedicalPredictor()
    predictor.train(training_data)

    while True:
        try:
            print("\nEnter patient information:")
            age = int(input("Age: "))
            if age < 0 or age > 120:
                raise ValueError("Invalid age")
            
            gender = input("Gender (M/F): ").upper()
            if gender not in ['M', 'F']:
                raise ValueError("Invalid gender")
            
            symptoms = input("Symptoms (comma-separated): ")
            if not symptoms.strip():
                raise ValueError("Symptoms cannot be empty")
            
            cause = input("Cause: ")
            if not cause.strip():
                raise ValueError("Cause cannot be empty")

            diseases, medicines = predictor.predict(age, gender, symptoms, cause)

            print(f"\nInput:")
            print(f"Age: {age}")
            print(f"Gender: {gender}")
            print(f"Symptoms: {symptoms}")
            print(f"Cause: {cause}")

            print(f"\nPredictions:")
            if diseases:
                print("\nPredicted Diseases:")
                print("-" * 50)
                for disease, confidence in diseases:
                    print(f"• {disease:<30} (Confidence: {confidence:.1f}%)")
            else:
                print("No diseases predicted with high confidence")

            if medicines:
                print("\nRecommended Medicines:")
                print("-" * 50)
                for medicine, confidence in medicines:
                    print(f"• {medicine:<30} (Confidence: {confidence:.1f}%)")
            else:
                print("No medicines recommended with high confidence")

            choice = input("\nMake another prediction? (y/n): ")
            if choice.lower() != 'y':
                break

        except ValueError as ve:
            print(f"Input error: {str(ve)}")
        except Exception as e:
            print(f"Error during prediction: {str(e)}")

if __name__ == "__main__":
    main()