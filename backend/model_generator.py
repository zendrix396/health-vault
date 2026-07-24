import json
import numpy as np
import joblib
import os
import time
from collections import Counter
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    AdaBoostClassifier, ExtraTreesClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer, StandardScaler
from sklearn.model_selection import (
    train_test_split, cross_val_score, StratifiedKFold
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2
import warnings
warnings.filterwarnings('ignore')

MEDICAL_PREDICTOR_MODEL_PATH = "medical_predictor_model.joblib"
ADVANCED_PREDICTOR_MODEL_PATH = "advanced_predictor_model.joblib"


def _to_python(obj):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _to_python(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_python(v) for v in obj]
    return obj


def _safe_split(value):
    if not value:
        return []
    return [item.strip() for item in str(value).split(',') if item.strip()]


def _clean_data(data):
    cleaned = []
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
                cleaned.append(cleaned_record)
        except Exception:
            continue
    return cleaned


def _prepare_features(data, symptom_encoder=None, cause_encoder=None, fit=True):
    symptoms = [_safe_split(record['Symptoms']) for record in data]
    causes = [record['Causes'] for record in data]
    ages = np.array([record['Age'] for record in data]).reshape(-1, 1)
    genders = np.array([1 if record['Gender'].startswith('M') else 0
                       for record in data]).reshape(-1, 1)

    if fit:
        X_symptoms = symptom_encoder.fit_transform(symptoms)
        X_causes = cause_encoder.fit_transform(causes).reshape(-1, 1)
    else:
        X_symptoms = symptom_encoder.transform(symptoms)
        safe_causes = []
        for c in causes:
            if c in cause_encoder.classes_:
                safe_causes.append(c)
            else:
                safe_causes.append(cause_encoder.classes_[0])
        X_causes = cause_encoder.transform(safe_causes).reshape(-1, 1)

    return np.hstack([ages, genders, X_symptoms, X_causes])


def benchmark_models(X_train, y_train, X_test, y_test, task_name="disease"):
    """Train multiple classifiers and return the best one with full metrics."""
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=200, max_depth=None, min_samples_split=5,
            random_state=42, n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=150, learning_rate=0.1, max_depth=5,
            random_state=42
        ),
        'ExtraTrees': ExtraTreesClassifier(
            n_estimators=200, random_state=42, n_jobs=-1
        ),
        'AdaBoost': AdaBoostClassifier(
            n_estimators=150, random_state=42, algorithm='SAMME'
        ),
        'LogisticRegression': LogisticRegression(
            max_iter=1000, random_state=42, multi_class='multinomial'
        ),
    }

    results = {}
    best_f1 = -1
    best_name = None
    best_model = None

    for name, model in models.items():
        print(f"  Training {name}...")
        start = time.time()
        try:
            model.fit(X_train, y_train)
            train_time = time.time() - start

            y_pred = model.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)

            results[name] = {
                'accuracy': round(acc * 100, 2),
                'precision': round(prec * 100, 2),
                'recall': round(rec * 100, 2),
                'f1_score': round(f1 * 100, 2),
                'train_time_seconds': round(train_time, 2)
            }

            print(f"    {name}: acc={acc*100:.1f}% f1={f1*100:.1f}% ({train_time:.1f}s)")

            if f1 > best_f1:
                best_f1 = f1
                best_name = name
                best_model = model
        except Exception as e:
            print(f"    {name} failed: {e}")
            results[name] = {'error': str(e)}

    return best_name, best_model, results


def cross_validate_model(model, X, y, cv=5):
    """Run stratified k-fold cross validation."""
    n_classes = len(np.unique(y))
    min_class_count = min(np.bincount(y))
    k = min(cv, n_classes, min_class_count) if min_class_count > 1 else 2
    k = max(k, 2)
    skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
    return {
        'mean_accuracy': round(float(scores.mean()) * 100, 2),
        'std_accuracy': round(float(scores.std()) * 100, 2),
        'fold_scores': [round(float(s) * 100, 2) for s in scores],
        'n_folds': k
    }


def get_feature_importance(model, feature_names, top_n=15):
    """Extract feature importance from tree-based models."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_)
    else:
        return []

    if len(importances) != len(feature_names):
        return []

    indices = np.argsort(importances)[::-1][:top_n]
    return [
        {'feature': feature_names[i], 'importance': round(float(importances[i]) * 100, 2)}
        for i in indices
    ]


class MedicalPredictor:
    def __init__(self):
        self.disease_classifier = None
        self.medicine_classifier = None
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()
        self.is_trained = False
        self.evaluation = {}
        self.feature_names = []

    def train(self, training_data, sample_size=None):
        cleaned_data = _clean_data(training_data)
        if not cleaned_data:
            raise ValueError("No valid training data after cleaning")

        if sample_size and len(cleaned_data) > sample_size:
            np.random.seed(42)
            indices = np.random.choice(len(cleaned_data), sample_size, replace=False)
            cleaned_data = [cleaned_data[i] for i in indices]
            print(f"Sampled {sample_size} records for training")

        print(f"Training with {len(cleaned_data)} records...")

        X = _prepare_features(cleaned_data, self.symptom_encoder, self.cause_encoder, fit=True)
        diseases = [r['Disease'] for r in cleaned_data]
        y_diseases = self.disease_encoder.fit_transform(diseases)

        symptom_names = [f"sym_{s}" for s in self.symptom_encoder.classes_]
        self.feature_names = ['Age', 'Gender'] + symptom_names + ['Cause']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_diseases, test_size=0.2, random_state=42,
            stratify=y_diseases if min(np.bincount(y_diseases)) >= 2 else None
        )

        print("\n--- Benchmarking Disease Classifiers ---")
        best_name, best_model, bench_results = benchmark_models(
            X_train, y_train, X_test, y_test, "disease"
        )
        print(f"\nBest model: {best_name}")

        self.disease_classifier = best_model
        y_pred = best_model.predict(X_test)

        report_dict = classification_report(
            y_test, y_pred,
            labels=sorted(set(y_test)),
            target_names=[self.disease_encoder.classes_[i] for i in sorted(set(y_test))],
            zero_division=0, output_dict=True
        )
        cm = confusion_matrix(y_test, y_pred)

        print(f"\n--- Cross-Validation ({best_name}) ---")
        cv_results = cross_validate_model(best_model, X, y_diseases, cv=5)
        print(f"CV Accuracy: {cv_results['mean_accuracy']}% ± {cv_results['std_accuracy']}%")

        feature_importance = get_feature_importance(
            best_model, self.feature_names, top_n=15
        )

        unique_meds = set(r.get('Medicine', '') for r in cleaned_data)
        has_real_medicine_data = unique_meds - {None, '', 'TBD', 'Consult physician'}
        medicine_trained = False

        if has_real_medicine_data and len(has_real_medicine_data) > 1:
            medicines = [_safe_split(r['Medicine']) for r in cleaned_data]
            y_medicines = self.medicine_encoder.fit_transform(medicines)
            self.medicine_classifier = RandomForestClassifier(
                n_estimators=200, random_state=42, n_jobs=-1
            )
            Xm_train, Xm_test, ym_train, ym_test = train_test_split(
                X, y_medicines, test_size=0.2, random_state=42
            )
            self.medicine_classifier.fit(Xm_train, ym_train)
            medicine_trained = True
        else:
            self.medicine_encoder = None
            self.medicine_classifier = None

        self.is_trained = True

        top_k = min(10, len(self.disease_encoder.classes_))
        cm_top = cm[:top_k, :top_k].tolist() if cm.shape[0] >= top_k else cm.tolist()

        self.evaluation = _to_python({
            'n_training_samples': len(cleaned_data),
            'n_features': X.shape[1],
            'n_classes': len(self.disease_encoder.classes_),
            'benchmark_results': bench_results,
            'best_model': best_name,
            'test_metrics': {
                'accuracy': bench_results.get(best_name, {}).get('accuracy', 0),
                'precision': bench_results.get(best_name, {}).get('precision', 0),
                'recall': bench_results.get(best_name, {}).get('recall', 0),
                'f1_score': bench_results.get(best_name, {}).get('f1_score', 0),
            },
            'cross_validation': cv_results,
            'feature_importance': feature_importance,
            'classification_report': {
                k: v for k, v in report_dict.items()
                if k in ('accuracy', 'macro avg', 'weighted avg') or
                   k in self.disease_encoder.classes_
            },
            'confusion_matrix_top_classes': cm_top,
            'medicine_model_trained': medicine_trained,
        })

        return {
            'disease_accuracy': self.evaluation['test_metrics']['accuracy'],
            'medicine_accuracy': 0.0,
            'evaluation': self.evaluation
        }

    def predict(self, age, gender, symptoms, cause):
        if not self.is_trained:
            raise ValueError("Model not trained yet")

        try:
            symptoms_list = _safe_split(symptoms)
            if not symptoms_list:
                raise ValueError("No valid symptoms provided")

            X_symptoms = self.symptom_encoder.transform([symptoms_list])
            safe_cause = cause
            if hasattr(self.cause_encoder, "classes_") and cause not in self.cause_encoder.classes_:
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
            diseases = [
                (self.disease_encoder.inverse_transform([idx])[0],
                 float(disease_probs[idx] * 100))
                for idx in top_diseases_idx if disease_probs[idx] > 0.1
            ]

            if self.medicine_encoder is None or self.medicine_classifier is None:
                return diseases, []

            medicine_probs = self.medicine_classifier.predict_proba(X)
            medicines = []
            for i, prob_array in enumerate(medicine_probs):
                if np.max(prob_array) > 0.05:
                    medicine_name = self.medicine_encoder.classes_[i]
                    confidence = float(np.max(prob_array) * 100)
                    medicines.append((str(medicine_name), confidence))
            medicines.sort(key=lambda x: x[1], reverse=True)
            return diseases, medicines[:5]

        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return [], []

    def save_model(self, filepath=MEDICAL_PREDICTOR_MODEL_PATH):
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        model_data = {
            'disease_classifier': self.disease_classifier,
            'medicine_classifier': self.medicine_classifier,
            'symptom_encoder': self.symptom_encoder,
            'disease_encoder': self.disease_encoder,
            'medicine_encoder': self.medicine_encoder,
            'cause_encoder': self.cause_encoder,
            'is_trained': self.is_trained,
            'evaluation': self.evaluation,
            'feature_names': self.feature_names,
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath=MEDICAL_PREDICTOR_MODEL_PATH):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        model_data = joblib.load(filepath)
        self.disease_classifier = model_data['disease_classifier']
        self.medicine_classifier = model_data.get('medicine_classifier')
        self.symptom_encoder = model_data['symptom_encoder']
        self.disease_encoder = model_data['disease_encoder']
        self.medicine_encoder = model_data.get('medicine_encoder')
        self.cause_encoder = model_data['cause_encoder']
        self.is_trained = model_data['is_trained']
        self.evaluation = model_data.get('evaluation', {})
        self.feature_names = model_data.get('feature_names', [])
        print(f"Model loaded from {filepath}")


class AdvancedMedicalPredictor:
    def __init__(self, json_file=None):
        self.disease_classifier = None
        self.medicine_classifier = None
        self.symptom_encoder = MultiLabelBinarizer()
        self.disease_encoder = LabelEncoder()
        self.medicine_encoder = MultiLabelBinarizer()
        self.cause_encoder = LabelEncoder()
        self.disease_accuracy = 0.0
        self.medicine_accuracy = 0.0
        self.is_trained = False
        self.evaluation = {}

        if json_file:
            self._load_and_train(json_file)

    def _load_and_train(self, json_file):
        if os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH):
            print(f"Loading pre-trained model from {ADVANCED_PREDICTOR_MODEL_PATH}")
            self.load_model()
            return
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            training_data = data if isinstance(data, list) else data.get('records', [])
            if not training_data:
                raise ValueError("No training data found in JSON file")
            self._train(training_data)
        except Exception as e:
            raise Exception(f"Failed to load and train: {str(e)}")

    def _train(self, training_data, sample_size=None):
        cleaned_data = _clean_data(training_data)
        if not cleaned_data:
            raise ValueError("No valid training data after cleaning")

        if sample_size and len(cleaned_data) > sample_size:
            np.random.seed(42)
            indices = np.random.choice(len(cleaned_data), sample_size, replace=False)
            cleaned_data = [cleaned_data[i] for i in indices]

        print(f"Training with {len(cleaned_data)} records...")
        X = _prepare_features(cleaned_data, self.symptom_encoder, self.cause_encoder, fit=True)
        diseases = [r['Disease'] for r in cleaned_data]
        y_diseases = self.disease_encoder.fit_transform(diseases)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y_diseases, test_size=0.2, random_state=42,
            stratify=y_diseases if min(np.bincount(y_diseases)) >= 2 else None
        )

        print("--- Benchmarking ---")
        best_name, best_model, bench_results = benchmark_models(
            X_train, y_train, X_test, y_test
        )

        self.disease_classifier = best_model
        self.disease_accuracy = bench_results.get(best_name, {}).get('accuracy', 0) / 100

        cv_results = cross_validate_model(best_model, X, y_diseases, cv=5)

        feature_names = ['Age', 'Gender'] + \
            [f"sym_{s}" for s in self.symptom_encoder.classes_] + ['Cause']
        feature_importance = get_feature_importance(best_model, feature_names)

        unique_meds = set(r.get('Medicine', '') for r in cleaned_data)
        has_real_medicine_data = unique_meds - {None, '', 'TBD', 'Consult physician'}

        if has_real_medicine_data and len(has_real_medicine_data) > 1:
            medicines = [_safe_split(r['Medicine']) for r in cleaned_data]
            y_medicines = self.medicine_encoder.fit_transform(medicines)
            self.medicine_classifier = RandomForestClassifier(
                n_estimators=200, random_state=42, n_jobs=-1
            )
            Xm_train, Xm_test, ym_train, ym_test = train_test_split(
                X, y_medicines, test_size=0.2, random_state=42
            )
            self.medicine_classifier.fit(Xm_train, ym_train)
            self.medicine_accuracy = accuracy_score(
                ym_test, self.medicine_classifier.predict(Xm_test)
            )
        else:
            self.medicine_encoder = None
            self.medicine_classifier = None
            self.medicine_accuracy = 0.0

        self.is_trained = True
        self.evaluation = _to_python({
            'best_model': best_name,
            'benchmark_results': bench_results,
            'cross_validation': cv_results,
            'feature_importance': feature_importance,
            'n_samples': len(cleaned_data),
            'n_classes': len(self.disease_encoder.classes_),
        })

        print(f"Best: {best_name} | CV: {cv_results['mean_accuracy']}% ± {cv_results['std_accuracy']}%")

    def get_model_accuracies(self):
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return {
            'disease_accuracy': round(self.disease_accuracy * 100, 2),
            'medicine_accuracy': round(self.medicine_accuracy * 100, 2)
        }

    def predict_single(self, age, gender, symptoms, cause):
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
            if not diseases:
                return {'error': 'Could not make predictions with sufficient confidence'}

            top_disease = max(diseases, key=lambda x: x[1])
            result = {
                'disease': {
                    'name': top_disease[0],
                    'confidence': round(top_disease[1], 2)
                }
            }
            if medicines:
                top_medicine = max(medicines, key=lambda x: x[1])
                result['medicine'] = {
                    'name': top_medicine[0],
                    'confidence': round(top_medicine[1], 2)
                }
            return result
        except Exception as e:
            return {'error': str(e)}

    def _predict(self, age, gender, symptoms, cause):
        symptoms_list = _safe_split(symptoms)
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
        top_idx = np.argsort(disease_probs)[-5:][::-1]
        diseases = [
            (self.disease_encoder.inverse_transform([i])[0],
             float(disease_probs[i] * 100))
            for i in top_idx if disease_probs[i] > 0.1
        ]

        if self.medicine_encoder is None or self.medicine_classifier is None:
            return diseases, []

        medicine_probs = self.medicine_classifier.predict_proba(X)
        medicines = []
        for i, prob_array in enumerate(medicine_probs):
            if np.max(prob_array) > 0.05:
                medicines.append((str(self.medicine_encoder.classes_[i]), float(np.max(prob_array) * 100)))
        return diseases, medicines

    def save_model(self, filepath=ADVANCED_PREDICTOR_MODEL_PATH):
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
            'is_trained': self.is_trained,
            'evaluation': self.evaluation,
        }
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath=ADVANCED_PREDICTOR_MODEL_PATH):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        model_data = joblib.load(filepath)
        self.disease_classifier = model_data['disease_classifier']
        self.medicine_classifier = model_data.get('medicine_classifier')
        self.symptom_encoder = model_data['symptom_encoder']
        self.disease_encoder = model_data['disease_encoder']
        self.medicine_encoder = model_data.get('medicine_encoder')
        self.cause_encoder = model_data['cause_encoder']
        self.disease_accuracy = model_data['disease_accuracy']
        self.medicine_accuracy = model_data['medicine_accuracy']
        self.is_trained = model_data['is_trained']
        self.evaluation = model_data.get('evaluation', {})


def load_training_data(json_path='output.json'):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        training_data = data if isinstance(data, list) else data.get('records', [])
        if not training_data:
            raise ValueError("No training data found")
        return training_data
    except FileNotFoundError:
        print(f"File not found: {json_path}")
        return []
    except json.JSONDecodeError:
        print(f"Invalid JSON: {json_path}")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []


if __name__ == "__main__":
    import sys
    json_path = sys.argv[1] if len(sys.argv) > 1 else "output.json"
    print(f"\n=== TRAINING ON {json_path} ===\n")
    data = load_training_data(json_path)
    if not data:
        print("No data. Exiting.")
        sys.exit(1)
    print(f"Loaded {len(data)} records.\n")

    predictor = MedicalPredictor()
    result = predictor.train(data)
    predictor.save_model()

    print(json.dumps(result['evaluation'], indent=2, default=str))
