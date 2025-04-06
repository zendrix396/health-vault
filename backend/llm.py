from google import generativeai as genai
import base64
def query_gemini(query, system_prompt="You are Gemini, an AI assistant."):
    # Initialize the Gemini API client
    genai.configure(api_key="AIzaSyBQsI-tqZ1vsCMJwMKaM1TEQi5czD438Z4")
    
    # Format the messages
    prompt = f"{system_prompt}\n\n{query}"
    
    # Create a GenerativeModel object
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    
    try:
        # Generate content
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def extract_text_from_image(image_path, prompt="Extract all text from this image"):
    # Initialize the Gemini API client
    genai.configure(api_key="AIzaSyBQsI-tqZ1vsCMJwMKaM1TEQi5czD438Z4")
    
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
    
    try:
        # Generate content from the image
        response = model.generate_content(contents)
        return response.text
    except Exception as e:
        return f"Error processing image: {str(e)}"
