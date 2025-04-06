from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import PyPDF2
import io
import logging
import sys
from llm import query_gemini
import re, json
import joblib
import os
from data_cleaner import clean_excel_data, update_json_data
import pandas as pd
import traceback

# Setup more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import and load models
try:
    logger.debug("Attempting to import model classes from model_generator")
    from model_generator import MedicalPredictor, AdvancedMedicalPredictor, load_training_data
    logger.debug("Successfully imported model classes")
except ImportError as e:
    logger.error(f"Failed to import from model_generator: {e}")
    # Define fallback import if needed
    # from your_backup_module import MedicalPredictor, AdvancedMedicalPredictor, load_training_data

# Define model paths with more specific names
MEDICAL_PREDICTOR_MODEL_PATH = "medical_basic_predictor.joblib"
ADVANCED_PREDICTOR_MODEL_PATH = "medical_advanced_predictor.joblib"

logger.info(f"Basic model path: {MEDICAL_PREDICTOR_MODEL_PATH}")
logger.info(f"Advanced model path: {ADVANCED_PREDICTOR_MODEL_PATH}")

basic_predictor = None
advanced_predictor = None

# Check if model files exist and load them
if os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH):
    try:
        logger.debug(f"Basic model file found: {MEDICAL_PREDICTOR_MODEL_PATH}")
        logger.debug("Initializing basic predictor")
        basic_predictor = MedicalPredictor()
        logger.debug("Loading basic model")
        basic_predictor.load_model(MEDICAL_PREDICTOR_MODEL_PATH)
        logger.info(f"Basic predictor loaded from {MEDICAL_PREDICTOR_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading basic predictor: {e}")
        logger.error(traceback.format_exc())
else:
    logger.warning(f"Basic model file not found: {MEDICAL_PREDICTOR_MODEL_PATH}")

if os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH):
    try:
        logger.debug(f"Advanced model file found: {ADVANCED_PREDICTOR_MODEL_PATH}")
        logger.debug("Initializing advanced predictor")
        advanced_predictor = AdvancedMedicalPredictor()
        logger.debug("Loading advanced model")
        advanced_predictor.load_model(ADVANCED_PREDICTOR_MODEL_PATH)
        logger.info(f"Advanced predictor loaded from {ADVANCED_PREDICTOR_MODEL_PATH}")
    except Exception as e:
        logger.error(f"Error loading advanced predictor: {e}")
        logger.error(traceback.format_exc())
else:
    logger.warning(f"Advanced model file not found: {ADVANCED_PREDICTOR_MODEL_PATH}")

UPLOAD_DIR = Path() / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://health-vault-3lre.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def analyze_medical_text(text):
    system_prompt = """You are a medical report analyzer. Analyze the given medical report text and provide a JSON response in this format:
    {
        "summary": "Very detailed information in layman terms bullet points, about 3 paragraphs 250 words",
        "findings": [
            {"emoji": "emoji", "text": "detailed finding"}
        ],
        "terms": [
            {"term": "medical term", "explanation": "detailed explanation"}
        ],
        "recommendations": [
            {"emoji": "emoji", "title": "title", "description": "detailed description"}
        ]
    }"""

    query = f"Analyze this medical report and return only the JSON response:\n\n{text}"
    
    try:
        raw_analysis = query_gemini(query, system_prompt)
        logger.info(f"Raw LLM response: {raw_analysis}")  # Log the raw response
        
        # Try different regex patterns
        json_match = re.search(r'({[\s\S]*})', raw_analysis)
        if json_match:
            json_str = json_match.group(1)
            # Validate JSON
            try:
                json.loads(json_str)  # Test if it's valid JSON
                logger.debug("Valid JSON found in response")
                return json_str
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                return raw_analysis  # Return raw response if JSON is invalid
        else:
            logger.error("No JSON found in response")
            return raw_analysis  # Return raw response if no JSON found
            
    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}")
        return str(e)

@app.post("/predict-medical")
async def predict_medical(data: dict):
    try:
        logger.debug(f"Received prediction request with data: {data}")
        
        # Convert age to int before passing to predictor
        age = int(data.get('age')) if data.get('age') else 0
        gender = data.get('gender')
        symptoms = data.get('symptoms')
        cause = data.get('cause')
        
        logger.debug(f"Processing request: Age={age}, Gender={gender}, Symptoms={symptoms}, Cause={cause}")
        
        # Initialize response structure
        response = {
            "advanced_prediction": {
                "disease": {"name": "Unknown", "confidence": 0},
                "medicine": {"name": "Unknown", "confidence": 0}
            },
            "basic_prediction": {
                "diseases": [],
                "medicines": []
            },
            "model_metrics": {
                "disease_accuracy": 0,
                "medicine_accuracy": 0
            }
        }
        
        # Global variables for the predictors
        global basic_predictor, advanced_predictor
        
        # Use advanced predictor if loaded
        if advanced_predictor and hasattr(advanced_predictor, 'is_trained') and advanced_predictor.is_trained:
            logger.debug("Using pre-loaded advanced predictor")
            advanced_result = advanced_predictor.predict_single(age, gender, symptoms, cause)
            logger.debug(f"Advanced prediction result: {advanced_result}")
            
            if 'error' not in advanced_result:
                response["advanced_prediction"] = advanced_result
                
            # Get model metrics if available
            try:
                metrics = advanced_predictor.get_model_accuracies()
                logger.debug(f"Advanced metrics: {metrics}")
                response["model_metrics"]["disease_accuracy"] = metrics["disease_accuracy"]
                response["model_metrics"]["medicine_accuracy"] = metrics["medicine_accuracy"]
            except Exception as metrics_error:
                logger.error(f"Error getting advanced metrics: {metrics_error}")
        else:
            # Train on the fly if model not available
            logger.info("Advanced model not loaded. Creating a new instance.")
            try:
                temp_advanced = AdvancedMedicalPredictor('output.json')
                logger.debug("Successfully created temporary advanced predictor")
                
                advanced_result = temp_advanced.predict_single(age, gender, symptoms, cause)
                logger.debug(f"Advanced prediction result: {advanced_result}")
                
                if 'error' not in advanced_result:
                    response["advanced_prediction"] = advanced_result
                
                # Get model metrics
                try:
                    metrics = temp_advanced.get_model_accuracies()
                    logger.debug(f"Advanced metrics: {metrics}")
                    response["model_metrics"]["disease_accuracy"] = metrics["disease_accuracy"]
                    response["model_metrics"]["medicine_accuracy"] = metrics["medicine_accuracy"]
                    
                    # Save this instance for future use
                    logger.debug("Saving advanced predictor for future use")
                    temp_advanced.save_model(ADVANCED_PREDICTOR_MODEL_PATH)
                    advanced_predictor = temp_advanced
                except Exception as metrics_error:
                    logger.error(f"Error getting temporary advanced metrics: {metrics_error}")
            except Exception as adv_error:
                logger.error(f"Error creating temporary advanced predictor: {adv_error}")
                logger.error(traceback.format_exc())
        
        # Use basic predictor if loaded
        if basic_predictor and hasattr(basic_predictor, 'is_trained') and basic_predictor.is_trained:
            logger.debug("Using pre-loaded basic predictor")
            diseases, medicines = basic_predictor.predict(age, gender, symptoms, cause)
            logger.debug(f"Basic prediction result - diseases: {diseases}")
            logger.debug(f"Basic prediction result - medicines: {medicines}")
            
            response["basic_prediction"]["diseases"] = [
                {"name": name, "confidence": round(float(conf), 2)} 
                for name, conf in diseases
            ]
            response["basic_prediction"]["medicines"] = [
                {"name": name, "confidence": round(float(conf), 2)} 
                for name, conf in medicines
            ]
        else:
            # Train on the fly if model not available
            logger.info("Basic model not loaded. Creating a new instance.")
            try:
                training_data = load_training_data('output.json')
                logger.debug(f"Loaded {len(training_data)} training records")
                
                temp_basic = MedicalPredictor()
                logger.debug("Training temporary basic predictor")
                temp_basic.train(training_data)
                
                diseases, medicines = temp_basic.predict(age, gender, symptoms, cause)
                logger.debug(f"Basic prediction result - diseases: {diseases}")
                logger.debug(f"Basic prediction result - medicines: {medicines}")
                
                response["basic_prediction"]["diseases"] = [
                    {"name": name, "confidence": round(float(conf), 2)} 
                    for name, conf in diseases
                ]
                response["basic_prediction"]["medicines"] = [
                    {"name": name, "confidence": round(float(conf), 2)} 
                    for name, conf in medicines
                ]
                
                # Save this instance for future use
                logger.debug("Saving basic predictor for future use")
                temp_basic.save_model(MEDICAL_PREDICTOR_MODEL_PATH)
                basic_predictor = temp_basic
            except Exception as basic_error:
                logger.error(f"Error creating temporary basic predictor: {basic_error}")
                logger.error(traceback.format_exc())
        
        logger.debug(f"Returning response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error in medical prediction: {str(e)}")
        logger.error(traceback.format_exc())
        # Return a structured error response instead of raising an exception
        return {
            "advanced_prediction": {
                "disease": {"name": "Error", "confidence": 0},
                "medicine": {"name": "Error", "confidence": 0}
            },
            "basic_prediction": {
                "diseases": [],
                "medicines": []
            },
            "model_metrics": {
                "disease_accuracy": 0,
                "medicine_accuracy": 0
            },
            "error": str(e)
        }

@app.post("/upload-excel")
async def upload_excel(file: UploadFile):
    try:
        logger.debug(f"Received Excel file: {file.filename}")
        
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f"Invalid file format: {file.filename}")
            raise HTTPException(status_code=400, detail="Only Excel files are accepted")
        
        # Read the Excel file
        contents = await file.read()
        logger.debug(f"Excel file size: {len(contents)} bytes")
        
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.debug(f"Excel file saved to {file_path}")
        
        df = pd.read_excel(file_path)
        logger.debug(f"Excel data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Clean the data
        cleaned_data = clean_excel_data(df)
        logger.debug(f"Cleaned data: {len(cleaned_data)} records")
        
        # Update the JSON file
        records_added = update_json_data(cleaned_data)
        logger.info(f"Added {records_added} records to training data")
        
        # Try to retrain models with new data
        global basic_predictor, advanced_predictor
        
        try:
            logger.debug("Attempting to retrain models with updated data")
            training_data = load_training_data('output.json')
            
            # Retrain basic predictor
            if basic_predictor:
                logger.debug("Retraining basic predictor")
                basic_predictor.train(training_data)
                basic_predictor.save_model(MEDICAL_PREDICTOR_MODEL_PATH)
                logger.info("Basic predictor retrained and saved")
            else:
                logger.debug("Creating new basic predictor")
                basic_predictor = MedicalPredictor()
                basic_predictor.train(training_data)
                basic_predictor.save_model(MEDICAL_PREDICTOR_MODEL_PATH)
                logger.info("Basic predictor created and saved")
                
            # Retrain advanced predictor
            if advanced_predictor:
                logger.debug("Retraining advanced predictor")
                advanced_predictor._train(training_data)
                logger.info("Advanced predictor retrained")
            else:
                logger.debug("Creating new advanced predictor")
                advanced_predictor = AdvancedMedicalPredictor()
                advanced_predictor._train(training_data)
                logger.info("Advanced predictor created")
                
            logger.info("Both models successfully retrained with new data")
            
            # Explicitly check that both files exist
            basic_exists = os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH)
            advanced_exists = os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH)
            logger.debug(f"Model files exist? Basic: {basic_exists}, Advanced: {advanced_exists}")
            
        except Exception as train_error:
            logger.error(f"Error retraining models: {train_error}")
            logger.error(traceback.format_exc())
        
        return {
            "message": "Excel file processed successfully",
            "records_added": records_added,
            "filename": file.filename,
            "models_retrained": True,
            "model_files": {
                "basic_model": os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH),
                "advanced_model": os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH)
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_report(file_upload: UploadFile):
    try:
        logger.info(f"Received file: {file_upload.filename}")
        
        if not file_upload.filename.endswith('.pdf'):
            logger.warning(f"Invalid file format: {file_upload.filename}")
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        data = await file_upload.read()
        logger.info(f"File size: {len(data)} bytes")

        save_to = UPLOAD_DIR / file_upload.filename
        with open(save_to, 'wb') as f:
            f.write(data)
        logger.info(f"File saved to {save_to}")

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
        
        if pdf_reader.is_encrypted:
            logger.warning("Encrypted PDF detected")
            raise HTTPException(status_code=400, detail="Cannot process encrypted PDF")

        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        
        logger.info(f"Successfully extracted text from PDF. Text length: {len(text_content)} characters")
        
        analysis = await analyze_medical_text(text_content)
        
        return {
            "filename": file_upload.filename,
            "text_content": text_content,
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Debug route to check model existence
@app.get("/model-status")
async def model_status():
    try:
        basic_exists = os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH)
        advanced_exists = os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH)
        
        basic_loaded = basic_predictor is not None and hasattr(basic_predictor, 'is_trained') and basic_predictor.is_trained
        advanced_loaded = advanced_predictor is not None and hasattr(advanced_predictor, 'is_trained') and advanced_predictor.is_trained
        
        file_sizes = {}
        if basic_exists:
            file_sizes["basic_model"] = os.path.getsize(MEDICAL_PREDICTOR_MODEL_PATH)
        if advanced_exists:
            file_sizes["advanced_model"] = os.path.getsize(ADVANCED_PREDICTOR_MODEL_PATH)
        
        # Add working directory contents
        dir_contents = os.listdir('.')
        joblib_files = [f for f in dir_contents if f.endswith('.joblib')]
        
        return {
            "model_files": {
                "basic_model": {
                    "path": MEDICAL_PREDICTOR_MODEL_PATH,
                    "exists": basic_exists,
                    "loaded": basic_loaded
                },
                "advanced_model": {
                    "path": ADVANCED_PREDICTOR_MODEL_PATH,
                    "exists": advanced_exists,
                    "loaded": advanced_loaded
                }
            },
            "file_sizes": file_sizes,
            "joblib_files_in_directory": joblib_files,
            "working_directory": os.getcwd()
        }
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}