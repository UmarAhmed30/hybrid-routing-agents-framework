import os
from google import genai
from dotenv import load_dotenv

class GeminiClient:
    def __init__(self):
        self.model = "gemini-2.0-flash-lite"
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

    def generate_content(self, prompt):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text
