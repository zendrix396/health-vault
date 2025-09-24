from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import PyPDF2
import io
import logging
from mangum import Mangum
import sys
import re
import json
import os
import pandas as pd
import traceback

# --- 1. SETUP LOGGING AND APP FIRST ---
logging.basicConfig(
    level=logging.INFO, # Use INFO for production, DEBUG for development
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- 2. CREATE THE FastAPI APP INSTANCE ---
app = FastAPI(title="Health Vault API", version="1.0.0")

# --- 3. CREATE THE LAMBDA HANDLER ---
# This must come AFTER 'app' is defined. This is what Lambda will run.
handler = Mangum(app)

# --- 4. CONFIGURE MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://health-vault-3lre.onrender.com", "https://health-vault-1.onrender.com", "https://healthvaultai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. LOAD MODELS AND SETUP GLOBAL VARIABLES ---
# Import model classes
try:
    from model_generator import MedicalPredictor, AdvancedMedicalPredictor, load_training_data
    logger.info("Successfully imported model classes")
except ImportError as e:
    logger.error(f"Failed to import from model_generator: {e}")
    # In a real app, you might want to exit or handle this gracefully
    MedicalPredictor, AdvancedMedicalPredictor, load_training_data = None, None, None

# Define model paths using absolute paths for robustness in Lambda
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDICAL_PREDICTOR_MODEL_PATH = os.path.join(BASE_DIR, "medical_basic_predictor.joblib")
ADVANCED_PREDICTOR_MODEL_PATH = os.path.join(BASE_DIR, "medical_advanced_predictor.joblib")

logger.info(f"Expecting basic model at: {MEDICAL_PREDICTOR_MODEL_PATH}")
logger.info(f"Expecting advanced model at: {ADVANCED_PREDICTOR_MODEL_PATH}")

basic_predictor = None
advanced_predictor = None

# Using a startup event is the correct way to load models in FastAPI
@app.on_event("startup")
async def load_models_on_startup():
    global basic_predictor, advanced_predictor
    
    if os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH):
        try:
            logger.info(f"Loading basic predictor from {MEDICAL_PREDICTOR_MODEL_PATH}...")
            basic_predictor = MedicalPredictor()
            basic_predictor.load_model(MEDICAL_PREDICTOR_MODEL_PATH)
            logger.info("Basic predictor loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading basic predictor: {e}\n{traceback.format_exc()}")
    else:
        logger.warning(f"Basic model file not found: {MEDICAL_PREDICTOR_MODEL_PATH}")

    if os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH):
        try:
            logger.info(f"Loading advanced predictor from {ADVANCED_PREDICTOR_MODEL_PATH}...")
            advanced_predictor = AdvancedMedicalPredictor()
            advanced_predictor.load_model(ADVANCED_PREDICTOR_MODEL_PATH)
            logger.info("Advanced predictor loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading advanced predictor: {e}\n{traceback.format_exc()}")
    else:
        logger.warning(f"Advanced model file not found: {ADVANCED_PREDICTOR_MODEL_PATH}")

# --- THIS IS THE CRITICAL FIX FOR THE FILE SYSTEM ---
# In AWS Lambda, the only writable directory is /tmp.
UPLOAD_DIR = Path('/tmp') / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True) # Create the directory when the app starts

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')


# --- 6. DEFINE ALL YOUR API ENDPOINTS ---

@app.get('/')
async def root():
    return {"message": "Hello World"}

# --- (The rest of your endpoint functions: analyze_medical_text, predict_medical, upload_excel, etc., remain here) ---
# NOTE: I am including the full code for all endpoints as requested.

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
    
    fallback_response = {
        "summary": "Unable to analyze the medical report due to processing error. This may be due to missing API configuration or network issues.",
        "findings": [{"emoji": "⚠️", "text": "Analysis failed - please try again"}],
        "terms": [{"term": "Error", "explanation": "Unable to process the document"}],
        "recommendations": [{"emoji": "🔄", "title": "Retry", "description": "Please try uploading the document again"}]
    }
    
    try:
        from llm import query_gemini # Import locally to avoid circular dependencies if any
        logger.info("Calling LLM for medical text analysis")
        raw_analysis = query_gemini(query, system_prompt)
        
        # Extract JSON from the raw response
        json_match = re.search(r'```json\s*({[\s\S]*?})\s*```|({[\s\S]*})', raw_analysis, re.DOTALL)
        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            try:
                parsed_json = json.loads(json_str)
                return json.dumps(parsed_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from LLM: {json_str}")
                return json.dumps(fallback_response)
        else:
            logger.error(f"No JSON found in LLM response: {raw_analysis}")
            return json.dumps(fallback_response)
            
    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}\n{traceback.format_exc()}")
        return json.dumps(fallback_response)

@app.post("/predict-medical")
async def predict_medical(data: dict):
    try:
        logger.debug(f"Received prediction request with data: {data}")
        
        age = int(data.get('age', 0))
        gender = data.get('gender')
        symptoms = data.get('symptoms')
        cause = data.get('cause')
        
        response = {
            "advanced_prediction": {"disease": {"name": "N/A", "confidence": 0}, "medicine": {"name": "N/A", "confidence": 0}},
            "basic_prediction": {"diseases": [], "medicines": []},
            "model_metrics": {"disease_accuracy": 0, "medicine_accuracy": 0}
        }
        
        if advanced_predictor:
            logger.debug("Using pre-loaded advanced predictor")
            response["advanced_prediction"] = advanced_predictor.predict_single(age, gender, symptoms, cause)
            if hasattr(advanced_predictor, 'get_model_accuracies'):
                response["model_metrics"] = advanced_predictor.get_model_accuracies()
        else:
            logger.warning("Advanced predictor not loaded.")

        if basic_predictor:
            logger.debug("Using pre-loaded basic predictor")
            diseases, medicines = basic_predictor.predict(age, gender, symptoms, cause)
            response["basic_prediction"]["diseases"] = [{"name": name, "confidence": round(float(conf), 2)} for name, conf in diseases]
            response["basic_prediction"]["medicines"] = [{"name": name, "confidence": round(float(conf), 2)} for name, conf in medicines]
        else:
            logger.warning("Basic predictor not loaded.")
        
        logger.debug(f"Returning response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error in medical prediction: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-excel")
async def upload_excel(file: UploadFile):
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only Excel files are accepted")
        
        contents = await file.read()
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        df = pd.read_excel(file_path)
        cleaned_data = clean_excel_data(df)
        records_added = update_json_data(cleaned_data)
        logger.info(f"Added {records_added} records to training data")
        
        # Trigger model retraining (could be offloaded to a background task in a real app)
        await load_models_on_startup() 
        
        return {
            "message": "Excel file processed and models retrained",
            "records_added": records_added,
        }
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_report(file_upload: UploadFile):
    try:
        logger.info(f"UPLOAD ENDPOINT CALLED for file: {file_upload.filename}")
        
        file_ext = Path(file_upload.filename).suffix.lower()
        if not (file_ext == '.pdf' or file_ext in SUPPORTED_IMAGE_EXTENSIONS):
            raise HTTPException(status_code=400, detail="Unsupported file type")

        data = await file_upload.read()
        save_to = UPLOAD_DIR / file_upload.filename
        
        with open(save_to, 'wb') as f:
            f.write(data)
        
        text_content = ""
        if file_ext == '.pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
            for page in pdf_reader.pages:
                text_content += page.extract_text()
        else:
            text_content = extract_text_from_image(str(save_to), "Extract all text from this medical report image in detail")

        if not text_content.strip():
            analysis = json.dumps({"summary": "No text content was extracted from the file."})
        else:
            analysis = await analyze_medical_text(text_content)
        
        logger.info("UPLOAD ENDPOINT COMPLETED SUCCESSFULLY")
        
        return {
            "filename": file_upload.filename,
            "text_content": text_content,
            "analysis": json.loads(analysis) # Return as a JSON object
        }

    except Exception as e:
        logger.error(f"UPLOAD ENDPOINT ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available-terms")
async def get_available_terms():
    try:
        training_data = load_training_data('output.json')
        symptoms, causes, diseases, medicines = set(), set(), set(), set()
        
        def clean_and_split_text(text_field):
            if not text_field: return []
            items = re.split(r'[,;|]\s*|\s*\n\s*', str(text_field).strip())
            return [item.strip() for item in items if len(item.strip()) > 2]

        for record in training_data:
            if isinstance(record, dict):
                symptoms.update(clean_and_split_text(record.get('Symptoms') or record.get('symptoms')))
                causes.update(clean_and_split_text(record.get('Causes') or record.get('cause')))
                diseases.update(clean_and_split_text(record.get('Disease') or record.get('disease')))
                medicines.update(clean_and_split_text(record.get('Medicine') or record.get('medicine')))
        
        return {
            "symptoms": sorted(list(symptoms)),
            "causes": sorted(list(causes)),
            "diseases": sorted(list(diseases)),
            "medicines": sorted(list(medicines)),
        }
        
    except Exception as e:
        logger.error(f"Error fetching available terms: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}

@app.get("/model-status")
async def model_status():
    try:
        basic_exists = os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH)
        advanced_exists = os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH)
        
        return {
            "model_files": {
                "basic_model": {"path": MEDICAL_PREDICTOR_MODEL_PATH, "exists": basic_exists, "loaded": basic_predictor is not None},
                "advanced_model": {"path": ADVANCED_PREDICTOR_MODEL_PATH, "exists": advanced_exists, "loaded": advanced_predictor is not None}
            },
            "working_directory": os.getcwd()
        }
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}
