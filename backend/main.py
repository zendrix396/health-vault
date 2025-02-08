from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import PyPDF2
import io
import logging
from llm import query_claude
import re, json
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