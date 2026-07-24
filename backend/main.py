from fastapi import FastAPI, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
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
import tempfile
from data_cleaner import clean_excel_data, update_json_data, convert_csv_to_model_format, convert_jsonl_to_model_format
import llm
import rag
import groq_llm

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Health Vault API", version="1.0.0")

handler = Mangum(app)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173","http://localhost:5174", "http://127.0.0.1:5173", "https://health-vault-3lre.onrender.com", "https://health-vault-1.onrender.com", "https://healthvaultai.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    from model_generator import MedicalPredictor, AdvancedMedicalPredictor, load_training_data
    logger.info("Successfully imported model classes")
except ImportError as e:
    logger.error(f"Failed to import from model_generator: {e}")
    MedicalPredictor, AdvancedMedicalPredictor, load_training_data = None, None, None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDICAL_PREDICTOR_MODEL_PATH = os.path.join(BASE_DIR, "medical_basic_predictor.joblib")
ADVANCED_PREDICTOR_MODEL_PATH = os.path.join(BASE_DIR, "medical_advanced_predictor.joblib")

# Also consider alternate packaged filenames produced by model_generator defaults
ALT_BASIC_MODEL_PATH = os.path.join(BASE_DIR, "medical_predictor_model.joblib")
ALT_ADVANCED_MODEL_PATH = os.path.join(BASE_DIR, "advanced_predictor_model.joblib")

# Writable runtime locations (AWS Lambda uses /tmp, local dev uses system temp)
TMP_DIR = "/tmp" if os.name == 'posix' else tempfile.gettempdir()
TMP_BASIC_MODEL_PATH = os.path.join(TMP_DIR, "medical_basic_predictor.joblib")
TMP_ADVANCED_MODEL_PATH = os.path.join(TMP_DIR, "medical_advanced_predictor.joblib")
JSON_DATA_PATH = os.path.join(TMP_DIR, "output.json")
DEFAULT_CACHE_FLAG = os.path.join(TMP_DIR, "default_data_cached.flag")

logger.info(f"Expecting basic model at: {MEDICAL_PREDICTOR_MODEL_PATH}")
logger.info(f"Expecting advanced model at: {ADVANCED_PREDICTOR_MODEL_PATH}")

basic_predictor = None
advanced_predictor = None

@app.on_event("startup")
async def load_models_on_startup():
    global basic_predictor, advanced_predictor
    
    # Try loading from /tmp then packaged paths (including alternate names)
    basic_candidates = [TMP_BASIC_MODEL_PATH, MEDICAL_PREDICTOR_MODEL_PATH, ALT_BASIC_MODEL_PATH]
    advanced_candidates = [TMP_ADVANCED_MODEL_PATH, ADVANCED_PREDICTOR_MODEL_PATH, ALT_ADVANCED_MODEL_PATH]

    basic_loaded = False
    for path in basic_candidates:
        if os.path.exists(path):
            try:
                logger.info(f"Loading basic predictor from {path}...")
                basic_predictor = MedicalPredictor()
                basic_predictor.load_model(path)
                logger.info("Basic predictor loaded successfully.")
                basic_loaded = True
                break
            except Exception as e:
                logger.error(f"Error loading basic predictor from {path}: {e}\n{traceback.format_exc()}")
    if not basic_loaded:
        logger.warning("No basic model file found in candidates")

    adv_loaded = False
    for path in advanced_candidates:
        if os.path.exists(path):
            try:
                logger.info(f"Loading advanced predictor from {path}...")
                advanced_predictor = AdvancedMedicalPredictor()
                advanced_predictor.load_model(path)
                logger.info("Advanced predictor loaded successfully.")
                adv_loaded = True
                break
            except Exception as e:
                logger.error(f"Error loading advanced predictor from {path}: {e}\n{traceback.format_exc()}")
    if not adv_loaded:
        logger.warning("No advanced model file found in candidates")

    try:
        if os.path.exists(JSON_DATA_PATH):
            logger.info("Ingesting training data into vector store...")
            rag.ingest_training_data(JSON_DATA_PATH)
    except Exception as e:
        logger.warning(f"RAG ingestion skipped: {e}")

UPLOAD_DIR = Path(tempfile.gettempdir()) / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')



@app.get('/')
async def root():
    return {"message": "Hello World"}


@app.post("/rag-query")
async def rag_query(data: dict):
    try:
        query = data.get("query", "")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        rag_context = rag.build_rag_context(query, n_results=5)
        response = groq_llm.generate_response(query, rag_context)

        return {
            "query": query,
            "response": response,
            "context_used": rag_context != "",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag-ingest")
async def rag_ingest():
    try:
        if not os.path.exists(JSON_DATA_PATH):
            return {"error": "No training data found"}
        count = rag.ingest_training_data(JSON_DATA_PATH)
        return {"message": f"Ingested {count} records into vector store"}
    except Exception as e:
        logger.error(f"RAG ingest error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_medical_text(text, language: str = "english"):
    fallback_response = {
        "summary": "Unable to analyze the medical report due to processing error.",
        "findings": [{"emoji": "⚠️", "text": "Analysis failed - please try again"}],
        "terms": [{"term": "Error", "explanation": "Unable to process the document"}],
        "recommendations": [{"emoji": "🔄", "title": "Retry", "description": "Please try uploading the document again"}]
    }

    try:
        logger.info("Building RAG context for medical analysis")
        rag_context = rag.build_rag_context(text, n_results=5)

        logger.info("Calling Groq LLM for medical text analysis")
        raw_analysis = groq_llm.analyze_medical_report(text, language=language)

        json_match = re.search(r'```json\s*({[\s\S]*?})\s*```|({[\s\S]*})', raw_analysis, re.DOTALL)
        if json_match:
            json_str = json_match.group(1) or json_match.group(2)
            try:
                parsed_json = json.loads(json_str)
                return json.dumps(parsed_json)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from LLM, returning raw text")
                return json.dumps({**fallback_response, "summary": raw_analysis[:500]})
        else:
            return json.dumps({**fallback_response, "summary": raw_analysis[:500]})

    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}\n{traceback.format_exc()}")
        return json.dumps(fallback_response)


def train_and_save_models():
    """Train models from JSON_DATA_PATH and save to /tmp, then update loaded instances."""
    global basic_predictor, advanced_predictor
    try:
        training_data = load_training_data(JSON_DATA_PATH)
        if not training_data:
            raise ValueError("No training data available to train models")

        n = len(training_data)
        sample = min(n, 50000) if n > 50000 else None
        if sample:
            logger.info(f"Large dataset ({n} records), sampling {sample} for training")

        basic = MedicalPredictor()
        result = basic.train(training_data, sample_size=sample)
        os.makedirs(TMP_DIR, exist_ok=True)
        basic.save_model(TMP_BASIC_MODEL_PATH)
        basic_predictor = basic
        logger.info(f"Basic model trained and saved to {TMP_BASIC_MODEL_PATH}")

        adv = AdvancedMedicalPredictor()
        adv._train(training_data, sample_size=sample)
        adv.save_model(TMP_ADVANCED_MODEL_PATH)
        advanced_predictor = adv
        logger.info(f"Advanced model trained and saved to {TMP_ADVANCED_MODEL_PATH}")

    except Exception as e:
        logger.error(f"Error training models: {str(e)}\n{traceback.format_exc()}")
        raise

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
        is_csv = file.filename.lower().endswith('.csv')
        is_excel = file.filename.lower().endswith(('.xlsx', '.xls'))
        is_jsonl = file.filename.lower().endswith('.jsonl')
        
        if not is_csv and not is_excel and not is_jsonl:
            raise HTTPException(status_code=400, detail="Accepted formats: .xlsx, .xls, .csv, .jsonl")

        # If default data.xlsx has already been trained and models are loaded, reuse cached models.
        if (
            file.filename.lower() == "data.xlsx"
            and os.path.exists(DEFAULT_CACHE_FLAG)
            and basic_predictor
            and advanced_predictor
        ):
            return {
                "message": "Default data.xlsx already trained; using cached models.",
                "records_added": 0,
                "filename": file.filename,
                "cached": True,
            }
        
        contents = await file.read()
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as f:
            f.write(contents)
        
        if is_jsonl:
            cleaned_data = convert_jsonl_to_model_format(str(file_path))
        elif is_csv:
            df = pd.read_csv(file_path)
            cleaned_data = convert_csv_to_model_format(df)
        else:
            df = pd.read_excel(file_path)
            cleaned_data = clean_excel_data(df)
        
        records_added = update_json_data(cleaned_data, json_file=JSON_DATA_PATH)
        logger.info(f"Added {records_added} records to training data")
        
        train_and_save_models()

        if file.filename.lower() == "data.xlsx":
            try:
                with open(DEFAULT_CACHE_FLAG, "w") as flagf:
                    flagf.write("cached")
            except Exception as e:
                logger.warning(f"Could not write cache flag: {e}")
        
        fmt = "JSONL" if is_jsonl else ("CSV" if is_csv else "Excel")
        return {
            "message": f"{fmt} file processed and models retrained",
            "records_added": records_added,
            "filename": file.filename,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_report(file_upload: UploadFile, language: str = Form("english")):
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
            text_content = llm.extract_text_from_image(str(save_to), "Extract all text from this medical report image in detail")

        if not text_content.strip():
            analysis = json.dumps({"summary": "No text content was extracted from the file."})
        else:
            analysis = await analyze_medical_text(text_content, language=language)
        
        logger.info("UPLOAD ENDPOINT COMPLETED SUCCESSFULLY")
        
        return {
            "filename": file_upload.filename,
            "text_content": text_content,
            "analysis": json.loads(analysis)
        }

    except Exception as e:
        logger.error(f"UPLOAD ENDPOINT ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/available-terms")
async def get_available_terms():
    try:
        training_data = load_training_data(JSON_DATA_PATH)
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
        status = {
            "model_files": {
                "basic_model": {
                    "package_path": MEDICAL_PREDICTOR_MODEL_PATH,
                    "package_exists": os.path.exists(MEDICAL_PREDICTOR_MODEL_PATH),
                    "alt_package_path": ALT_BASIC_MODEL_PATH,
                    "alt_package_exists": os.path.exists(ALT_BASIC_MODEL_PATH),
                    "tmp_path": TMP_BASIC_MODEL_PATH,
                    "tmp_exists": os.path.exists(TMP_BASIC_MODEL_PATH),
                    "loaded": basic_predictor is not None
                },
                "advanced_model": {
                    "package_path": ADVANCED_PREDICTOR_MODEL_PATH,
                    "package_exists": os.path.exists(ADVANCED_PREDICTOR_MODEL_PATH),
                    "alt_package_path": ALT_ADVANCED_MODEL_PATH,
                    "alt_package_exists": os.path.exists(ALT_ADVANCED_MODEL_PATH),
                    "tmp_path": TMP_ADVANCED_MODEL_PATH,
                    "tmp_exists": os.path.exists(TMP_ADVANCED_MODEL_PATH),
                    "loaded": advanced_predictor is not None
                }
            },
            "json_data_path": JSON_DATA_PATH,
            "json_data_exists": os.path.exists(JSON_DATA_PATH),
            "working_directory": os.getcwd()
        }
        return status
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}


import numpy as np


def _to_python(obj):
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


@app.get("/model-evaluation")
async def model_evaluation():
    try:
        eval_data = {}
        if basic_predictor and hasattr(basic_predictor, 'evaluation'):
            eval_data['basic_model'] = basic_predictor.evaluation
        if advanced_predictor and hasattr(advanced_predictor, 'evaluation'):
            eval_data['advanced_model'] = advanced_predictor.evaluation
        if not eval_data:
            return {"error": "No trained models with evaluation data"}
        return _to_python(eval_data)
    except Exception as e:
        logger.error(f"Error fetching evaluation: {str(e)}\n{traceback.format_exc()}")
        return {"error": str(e)}


@app.get("/dummy-excel")
async def download_dummy_excel():
    """Serve a dummy Excel training dataset for download."""
    try:
        dummy_path = os.path.join(BASE_DIR, "uploads", "data.xlsx")
        if not os.path.exists(dummy_path):
            raise HTTPException(status_code=404, detail="Dummy Excel not found")
        return FileResponse(
            dummy_path,
            filename="data.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving dummy Excel: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
