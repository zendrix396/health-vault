from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import PyPDF2
import io
import logging
from llm import query_claude
import re, json
from medical_recommender import AdvancedMedicalPredictor
from medical_predictor import MedicalPredictor, load_training_data

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path() / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def analyze_medical_text(text):
    system_prompt = """You are a medical report analyzer. Analyze the given medical report text and provide a JSON response in this format:
    {
        "summary": "Very detailed summary in layman terms",
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
        raw_analysis = query_claude(query, system_prompt)
        logger.info(f"Raw LLM response: {raw_analysis}")  # Log the raw response
        
        # Try different regex patterns
        json_match = re.search(r'({[\s\S]*})', raw_analysis)
        if json_match:
            json_str = json_match.group(1)
            # Validate JSON
            try:
                json.loads(json_str)  # Test if it's valid JSON
                print("\n\n\nGOING TO SEND THE JSON\n\n\n")
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
        # Advanced predictor
        predictor2 = AdvancedMedicalPredictor('output.json')
        
        # Convert age to int before passing to predictor
        age = int(data.get('age')) if data.get('age') else 0
        
        advanced_prediction = predictor2.predict_single(
            age=age,
            gender=data.get('gender'),
            symptoms=data.get('symptoms'),
            cause=data.get('cause')
        )
        
        # Basic predictor
        training_data = load_training_data('output.json')
        predictor = MedicalPredictor()
        predictor.train(training_data)
        
        diseases, medicines = predictor.predict(
            age,
            data.get('gender'),
            data.get('symptoms'),
            data.get('cause')
        )

        # Format the response
        response = {
            "advanced_prediction": {
                "disease": {
                    "name": advanced_prediction.get('disease', {}).get('name', 'Unknown'),
                    "confidence": round(float(advanced_prediction.get('disease', {}).get('confidence', 0)), 2)
                },
                "medicine": {
                    "name": advanced_prediction.get('medicine', {}).get('name', 'Unknown'),
                    "confidence": round(float(advanced_prediction.get('medicine', {}).get('confidence', 0)), 2)
                }
            },
            "basic_prediction": {
                "diseases": [{"name": name, "confidence": round(float(conf), 2)} for name, conf in diseases],
                "medicines": [{"name": name, "confidence": round(float(conf), 2)} for name, conf in medicines]
            },
            "model_metrics": {
                "disease_accuracy": 64.71,
                "medicine_accuracy": 74.51
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error in medical prediction: {str(e)}")
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
@app.post("/upload")
async def upload_report(file_upload: UploadFile):
    try:
        logger.info(f"Received file: {file_upload.filename}")
        
        if not file_upload.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")
        
        data = await file_upload.read()
        logger.info(f"File size: {len(data)} bytes")

        save_to = UPLOAD_DIR / file_upload.filename
        with open(save_to, 'wb') as f:
            f.write(data)
        logger.info(f"File saved to {save_to}")

        pdf_reader = PyPDF2.PdfReader(io.BytesIO(data))
        
        if pdf_reader.is_encrypted:
            raise HTTPException(status_code=400, detail="Cannot process encrypted PDF")

        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
        
        logger.info("Successfully extracted text from PDF")
        
        analysis = await analyze_medical_text(text_content)
        
        return {
            "filename": file_upload.filename,
            "text_content": text_content,
            "analysis": analysis
        }

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))