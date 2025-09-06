from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import PyPDF2
import io
import logging

import sys
from llm import query_gemini, extract_text_from_image 

import re, json
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

# Supported image file extensions
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "https://health-vault-3lre.onrender.com", "https://health-vault-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/')
async def root():
    return {"message": "Hello World"}

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
    
    # Default fallback response
    fallback_response = {
        "summary": "Unable to analyze the medical report due to processing error. This may be due to missing API configuration or network issues.",
        "findings": [{"emoji": "⚠️", "text": "Analysis failed - please try again"}],
        "terms": [{"term": "Error", "explanation": "Unable to process the document"}],
        "recommendations": [{"emoji": "🔄", "title": "Retry", "description": "Please try uploading the document again"}]
    }
    
    # Mock analysis for testing when API key is not available
    mock_response = {
        "summary": f"This appears to be a medical document containing {len(text.split())} words. The document has been successfully processed and uploaded to the system. Please note that detailed analysis requires proper API configuration.",
        "findings": [
            {"emoji": "📄", "text": "Document successfully processed"},
            {"emoji": "📊", "text": f"Document contains approximately {len(text.split())} words"},
            {"emoji": "✅", "text": "File upload completed successfully"}
        ],
        "terms": [
            {"term": "Document Processing", "explanation": "The file has been successfully uploaded and processed by the system"},
            {"term": "Text Extraction", "explanation": "Text content has been extracted from the uploaded document"}
        ],
        "recommendations": [
            {"emoji": "🔧", "title": "API Configuration", "description": "For detailed medical analysis, please configure the GEMINI_API_KEY environment variable"},
            {"emoji": "📋", "title": "Document Review", "description": "Review the extracted text content for any important medical information"},
            {"emoji": "🔄", "title": "Retry Analysis", "description": "Try uploading again after configuring the API key for full analysis"}
        ]
    }
    
    try:
        logger.info("Calling LLM for medical text analysis")
        raw_analysis = query_gemini(query, system_prompt)
        logger.info(f"Raw LLM response length: {len(raw_analysis)} characters")
        logger.info(f"Raw LLM response preview: {raw_analysis[:200]}...")
        
        # Check if the response indicates missing API key
        if "Missing GEMINI_API_KEY" in raw_analysis or "Error:" in raw_analysis:
            logger.warning("API key not configured, using mock response")
            return json.dumps(mock_response)
        
        # Try different regex patterns to extract JSON
        import re
        json_patterns = [
            r'({[\s\S]*})',  # Standard JSON object
            r'```json\s*({[\s\S]*?})\s*```',  # JSON in code blocks
            r'```\s*({[\s\S]*?})\s*```',  # JSON in generic code blocks
        ]
        
        json_str = None
        for pattern in json_patterns:
            json_match = re.search(pattern, raw_analysis, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                logger.info(f"Found JSON with pattern: {pattern}")
                break
        
        if json_str:
            # Clean up the JSON string
            json_str = json_str.strip()
            logger.info(f"Extracted JSON string length: {len(json_str)}")
            logger.info(f"JSON preview: {json_str[:200]}...")
            
            # Clean up control characters and escape sequences
            # Simple and effective JSON cleaning
            def clean_json_string(json_str):
                # Remove only problematic control characters, keep valid JSON whitespace
                json_str = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', json_str)
                
                # Fix common issues without breaking the structure
                # Replace actual newlines in string values with escaped newlines
                json_str = re.sub(r'(?<!\\)\n(?!\s*[}\]])', '\\n', json_str)
                
                return json_str
            
            cleaned_json = clean_json_string(json_str)
            
            # Validate JSON
            try:
                parsed_json = json.loads(cleaned_json)
                logger.info("Successfully parsed JSON from LLM response")
                return json.dumps(parsed_json)  # Return as JSON string
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from LLM: {e}")
                logger.error(f"Error at position: {e.pos}")
                logger.error(f"Problematic JSON around error: {cleaned_json[max(0, e.pos-50):e.pos+50]}")
                
                # Try a different approach - use a more lenient JSON parser
                try:
                    # Try to fix the specific issue at the error position
                    if e.pos < len(cleaned_json):
                        char_at_error = cleaned_json[e.pos]
                        logger.error(f"Character at error position: '{char_at_error}' (ord: {ord(char_at_error)})")
                        
                        # Replace the problematic character
                        fixed_json = cleaned_json[:e.pos] + ' ' + cleaned_json[e.pos+1:]
                        parsed_json = json.loads(fixed_json)
                        logger.info("Successfully parsed JSON after fixing character at error position")
                        return json.dumps(parsed_json)
                except:
                    logger.error("Failed to fix JSON, using fallback response")
                    return json.dumps(fallback_response)
        else:
            logger.error("No JSON found in LLM response")
            logger.error(f"Full response: {raw_analysis}")
            return json.dumps(fallback_response)
            
    except Exception as e:
        logger.error(f"Error in LLM analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return json.dumps(fallback_response)

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
        logger.info("=" * 50)
        logger.info("UPLOAD ENDPOINT CALLED")
        logger.info("=" * 50)
        logger.info(f"Received file: {file_upload.filename}")
        logger.info(f"File content type: {file_upload.content_type}")
        logger.info(f"File size: {file_upload.size if hasattr(file_upload, 'size') else 'Unknown'}")
        

        # Get file extension (lowercase) for type checking
        file_ext = Path(file_upload.filename).suffix.lower()
        logger.info(f"File extension: {file_ext}")
        
        # Check if file type is supported
        if not (file_ext == '.pdf' or file_ext in SUPPORTED_IMAGE_EXTENSIONS):
            logger.error(f"Unsupported file type: {file_ext}")
            raise HTTPException(
                status_code=400, 
                detail=f"Only PDF and image files ({', '.join(SUPPORTED_IMAGE_EXTENSIONS)}) are accepted"
            )

        logger.info("File type validation passed")
        
        data = await file_upload.read()
        logger.info(f"File data read successfully. Size: {len(data)} bytes")

        save_to = UPLOAD_DIR / file_upload.filename
        logger.info(f"Saving file to: {save_to}")
        
        with open(save_to, 'wb') as f:
            f.write(data)
        logger.info(f"File saved successfully to {save_to}")

        # Verify file was saved
        if os.path.exists(save_to):
            logger.info(f"File verification: File exists at {save_to}")
            logger.info(f"Saved file size: {os.path.getsize(save_to)} bytes")
        else:
            logger.error(f"File verification failed: File not found at {save_to}")

        # Extract text based on file type
        text_content = ""
        logger.info(f"Starting text extraction for file type: {file_ext}")
        
        if file_ext == '.pdf':
            # Process PDF file
            logger.info("Processing PDF file")
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
            logger.info(f"PDF has {len(pdf_reader.pages)} pages")
            
            if pdf_reader.is_encrypted:
                logger.error("PDF is encrypted, cannot process")
                raise HTTPException(status_code=400, detail="Cannot process encrypted PDF")

            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text_content += page_text
                logger.info(f"Extracted text from page {i+1}: {len(page_text)} characters")
            
            logger.info(f"Successfully extracted text from PDF. Total length: {len(text_content)} characters")
        else:
            # Process image file
            logger.info(f"Processing image file: {file_ext}")
            logger.info(f"Calling extract_text_from_image with file: {str(save_to)}")
            
            try:
                text_content = extract_text_from_image(str(save_to), 
                                                      "Extract all text from this medical report image in detail")
                logger.info(f"Successfully extracted text from image. Length: {len(text_content)} characters")
            except Exception as img_error:
                logger.error(f"Error extracting text from image: {img_error}")
                raise HTTPException(status_code=500, detail=f"Failed to extract text from image: {str(img_error)}")

        logger.info(f"Text extraction completed. Content preview: {text_content[:200]}...")

        # Analyze the extracted text
        logger.info("Starting medical text analysis")
        if not text_content.strip():
            logger.warning("No text content extracted from file")
            analysis = json.dumps({
                "summary": "No text content was extracted from the uploaded file. Please ensure the file contains readable text.",
                "findings": [{"emoji": "⚠️", "text": "No text content found"}],
                "terms": [{"term": "Empty Document", "explanation": "The uploaded file appears to be empty or unreadable"}],
                "recommendations": [{"emoji": "📄", "title": "Check File", "description": "Please verify the file contains readable text and try again"}]
            })
        else:
            analysis = await analyze_medical_text(text_content)
        logger.info(f"Analysis completed. Analysis type: {type(analysis)}")
        logger.info(f"Analysis preview: {str(analysis)[:200]}...")
        
        response_data = {
            "filename": file_upload.filename,
            "text_content": text_content,
            "analysis": analysis
        }
        
        logger.info("Returning successful response")
        logger.info("=" * 50)
        logger.info("UPLOAD ENDPOINT COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
        return response_data

    except Exception as e:
        logger.error("=" * 50)
        logger.error("UPLOAD ENDPOINT ERROR")
        logger.error("=" * 50)
        logger.error(f"Error processing file: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(traceback.format_exc())
        logger.error("=" * 50)
        raise HTTPException(status_code=500, detail=str(e))

# Simple test endpoint to verify backend connectivity
@app.get("/test")
async def test_endpoint():
    logger.info("Test endpoint called")
    return {
        "status": "success",
        "message": "Backend is running and accessible",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/available-terms")
async def get_available_terms():
    """Get available terms from uploaded documents for auto-complete suggestions"""
    try:
        logger.info("Fetching available terms for auto-complete")
        
        # Read the training data to extract unique terms
        try:
            training_data = load_training_data('output.json')
            logger.info(f"Loaded {len(training_data)} training records")
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            training_data = []
        
        # Extract unique symptoms, causes, diseases, and medicines
        symptoms = set()
        causes = set()
        diseases = set()
        medicines = set()
        
        def clean_and_split_text(text_field):
            """Enhanced text cleaning and splitting function"""
            if not text_field:
                return []
            
            text = str(text_field).strip()
            if not text or len(text) < 2:
                return []
            
            # Split by common separators: comma, semicolon, pipe, newline
            items = []
            for separator in [',', ';', '|', '\n', '\r\n']:
                if separator in text:
                    items.extend([item.strip() for item in text.split(separator) if item.strip()])
                    break
            else:
                # If no separator found, treat as single item
                items = [text]
            
            # Clean each item
            cleaned_items = []
            for item in items:
                # Remove common prefixes and suffixes
                item = item.strip()
                if item.startswith('e '):
                    item = item[2:]
                if item.startswith('+ '):
                    item = item[2:]
                if item.endswith('...'):
                    item = item[:-3]
                
                # Filter out very short or invalid entries
                if len(item) > 2 and not item.startswith('e ') and item not in ['...', 'etc', 'etc.']:
                    cleaned_items.append(item)
            
            return cleaned_items

        for record in training_data:
            if isinstance(record, dict):
                # Extract symptoms (check both capitalized and lowercase field names)
                symptoms_field = record.get('Symptoms') or record.get('symptoms')
                if symptoms_field:
                    symptom_list = clean_and_split_text(symptoms_field)
                    symptoms.update(symptom_list)
                
                # Extract causes (check both capitalized and lowercase field names)
                causes_field = record.get('Causes') or record.get('cause')
                if causes_field:
                    cause_list = clean_and_split_text(causes_field)
                    causes.update(cause_list)
                
                # Extract diseases (check both capitalized and lowercase field names)
                disease_field = record.get('Disease') or record.get('disease')
                if disease_field:
                    disease_list = clean_and_split_text(disease_field)
                    diseases.update(disease_list)
                
                # Extract medicines (check both capitalized and lowercase field names)
                medicine_field = record.get('Medicine') or record.get('medicine')
                if medicine_field:
                    medicine_list = clean_and_split_text(medicine_field)
                    medicines.update(medicine_list)
        
        # Convert sets to sorted lists
        symptoms_list = sorted(list(symptoms))
        causes_list = sorted(list(causes))
        diseases_list = sorted(list(diseases))
        medicines_list = sorted(list(medicines))
        
        logger.info(f"Extracted terms - Symptoms: {len(symptoms_list)}, Causes: {len(causes_list)}, Diseases: {len(diseases_list)}, Medicines: {len(medicines_list)}")
        
        return {
            "symptoms": symptoms_list,
            "causes": causes_list,
            "diseases": diseases_list,
            "medicines": medicines_list,
            "total_terms": len(symptoms_list) + len(causes_list) + len(diseases_list) + len(medicines_list)
        }
        
    except Exception as e:
        logger.error(f"Error fetching available terms: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "symptoms": [],
            "causes": [],
            "diseases": [],
            "medicines": [],
            "total_terms": 0,
            "error": str(e)
        }

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

