
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from .base import ModelProvider

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


class GeminiProvider(ModelProvider):
    def __init__(self, model: str | None = None):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing. "
                "Add it to the project's .env file."
            )

        self.model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=60000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        output = response.text

        if not output or not output.strip():
            raise RuntimeError("Gemini returned an empty response.")

        return output.strip()
