from google import genai
from google.genai import types
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# Allow overriding models via env; defaults align with working sample
MODEL_IMAGE = os.getenv("GEMINI_MODEL_IMAGE", "gemini-2.5-flash")
MODEL_TEXT = os.getenv("GEMINI_MODEL_TEXT", "gemini-2.5-flash")

def _get_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if key:
        logger.info("Using GEMINI_API_KEY")
        return key

    alt_key = os.getenv("GOOGLE_API_KEY")
    if alt_key:
        logger.info("Using GOOGLE_API_KEY")
        return alt_key

    logger.error("GEMINI_API_KEY/GOOGLE_API_KEY environment variable not set")
    return None

def query_gemini(query, system_prompt="You are Gemini, an AI assistant."):
    api_key = _get_api_key()
    if not api_key:
        return "Error: Missing GEMINI_API_KEY environment variable"
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"{system_prompt}\n\n{query}"
    
    try:
        logger.info("Calling Gemini API for text analysis")
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt
        )
        logger.info("Gemini API call successful")
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        return f"Error: {str(e)}"

def extract_text_from_image(image_path, prompt="Extract all text from this image"):
    api_key = _get_api_key()
    if not api_key:
        return "Error: Missing GEMINI_API_KEY environment variable"
    
    client = genai.Client(api_key=api_key)
    
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        logger.info(f"Successfully read image file: {image_path}")
    except Exception as e:
        logger.error(f"Error reading image file {image_path}: {str(e)}")
        return f"Error reading image file: {str(e)}"
    
    file_ext = image_path.split('.')[-1].lower()
    mime_type_map = {
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'webp': 'image/webp'
    }
    mime_type = mime_type_map.get(file_ext, 'image/jpeg')
    logger.info(f"Processing image with MIME type: {mime_type}")
    
    try:
        logger.info("Calling Gemini API for image text extraction")
        response = client.models.generate_content(
            model=MODEL_IMAGE,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
                prompt
            ]
        )
        logger.info("Gemini API image processing successful")
        return response.text
    except Exception as e:
        logger.error(f"Error processing image with Gemini API: {str(e)}")
        return f"Error processing image: {str(e)}"
