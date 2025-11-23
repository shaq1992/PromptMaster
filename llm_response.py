from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

def get_response(prompt):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    config = {
        "temperature": 0.1,
        "top_p": 0.9,
        # We keep safety settings loose to avoid false positives
        "safety_settings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    }
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=config
    )

    return response.text

# print(get_response("Can you hear me?"))