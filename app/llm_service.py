import os
from dotenv import load_dotenv
from google import genai

load_dotenv()


class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing from .env"
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.models = [
            "gemini-3.8-flash",
            "gemini-3.7-flash",
        ]

    def generate(self, prompt):

        last_error = None

        for model_name in self.models:

            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except Exception as e:
                last_error = e
                print(
                    f"Model {model_name} failed: {e}"
                )

        raise RuntimeError(
            f"All Gemini models failed. Last error: {last_error}"
        )