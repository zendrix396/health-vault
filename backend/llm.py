from google import genai
from google.genai import types
import os
import logging
logger = logging.getLogger(__name__)

def query_gemini(query, system_prompt="You are Gemini, an AI assistant."):
    # Get API key from environment
    #
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return "Error: Missing GEMINI_API_KEY environment variable"
    
    # Initialize the Gemini API client
    client = genai.Client(api_key=api_key)
    
    # Format the messages
    prompt = f"{system_prompt}\n\n{query}"
    
    try:
        logger.info("Calling Gemini API for text analysis")
        # Generate content using the updated API
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        logger.info("Gemini API call successful")
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}")
        return f"Error: {str(e)}"

def extract_text_from_image(image_path, prompt="Extract all text from this image"):
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return "Error: Missing GEMINI_API_KEY environment variable"
    
    # Initialize the Gemini API client
    client = genai.Client(api_key=api_key)
    
    # Read the image file
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        logger.info(f"Successfully read image file: {image_path}")
    except Exception as e:
        logger.error(f"Error reading image file {image_path}: {str(e)}")
        return f"Error reading image file: {str(e)}"
    
    # Determine MIME type based on file extension
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
        # Generate content using the updated API with image
        response = client.models.generate_content(
            model='gemini-2.5-flash',
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
