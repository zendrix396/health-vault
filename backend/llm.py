import base64
import json
import re
from google import genai
from google.genai import types

# Initialize the Gemini API client
API_KEY = "AIzaSyDLt094GXKv16EY5M3gpPcsbkGzWP-sN-0"

def query_gemini(query, system_prompt="You are Gemini, an AI assistant."):
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash"
    
    # Format the messages with explicit JSON instruction
    json_instruction = "You MUST respond with valid JSON only. No markdown, no explanations, just pure JSON."
    prompt = f"{system_prompt}\n\n{json_instruction}\n\n{query}"
    
    try:
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            ),
        ]
        
        response = client.models.generate_content(
            model=model,
            contents=contents,
            response_mime_type="application/json",
        )
        
        response_text = response.text
        
        # Extract JSON if needed (sometimes response might include extra text)
        json_match = re.search(r'({[\s\S]*})', response_text)
        if json_match:
            json_str = json_match.group(1)
            # Validate JSON
            try:
                parsed_json = json.loads(json_str)
                return json.dumps(parsed_json)  # Return cleaned, validated JSON
            except json.JSONDecodeError:
                return f"Error: Invalid JSON format in response"
        else:
            return f"Error: No JSON found in response"
            
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_image(image_path, prompt="Extract all text from this image"):
    client = genai.Client(api_key=API_KEY)
    model = "gemini-2.0-flash"
    
    try:
        # Read the image file and convert to base64
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
        
        # Determine mime type based on file extension
        file_extension = image_path.split('.')[-1].lower()
        mime_type = f"image/{file_extension}"
        
        # Create contents with text prompt and image
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                    types.Part.from_data(mime_type=mime_type, data=image_data)
                ],
            ),
        ]
        
        # Generate content
        response = client.models.generate_content(
            model=model,
            contents=contents,
        )
        
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"
