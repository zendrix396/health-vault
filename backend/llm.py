import base64
import json
import re

# First try to import the new Google Generative AI Python client
try:
    from google import genai
    from google.genai import types
    
    # Flag to indicate which API version we're using
    USING_NEW_API = True
    
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

# If the new client isn't available, fall back to the older library
except ImportError:
    import google.generativeai as genai
    
    # Flag to indicate which API version we're using
    USING_NEW_API = False
    
    # Initialize the Gemini API client
    API_KEY = "AIzaSyDLt094GXKv16EY5M3gpPcsbkGzWP-sN-0"
    genai.configure(api_key=API_KEY)
    
    def query_gemini(query, system_prompt="You are Gemini, an AI assistant."):
        # Format the messages with explicit JSON instruction
        json_instruction = "You MUST respond with valid JSON only. No markdown, no explanations, just pure JSON."
        prompt = f"{system_prompt}\n\n{json_instruction}\n\n{query}"
        
        try:
            # Create a GenerativeModel object
            model = genai.GenerativeModel(model_name="gemini-2.0-flash")
            
            # Generate content
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response if it's not already pure JSON
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
        try:
            # Read the image file and convert to base64
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()
                encoded_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create a GenerativeModel object for Gemini's multimodal capabilities
            model = genai.GenerativeModel(model_name="gemini-2.0-flash")
            
            # Prepare content with the image
            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": f"image/{image_path.split('.')[-1]}",
                                "data": encoded_image
                            }
                        }
                    ]
                }
            ]
            
            # Generate content from the image
            response = model.generate_content(contents)
            return response.text
        except Exception as e:
            return f"Error processing image: {str(e)}"
