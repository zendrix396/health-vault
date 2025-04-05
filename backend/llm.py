from google import generativeai as genai
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
