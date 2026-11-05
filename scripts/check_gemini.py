
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("API key missing from .env")

model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

client = genai.Client(
    api_key=api_key,
    http_options=types.HttpOptions(
        timeout=60000,
        retry_options=types.HttpRetryOptions(attempts=1),
    ),
)

print(f"Testing {model} using a 60-second timeout...", flush=True)

try:
    response = client.models.generate_content(
        model=model,
        contents="Reply with exactly: CodeSift connected",
    )
    print("SUCCESS")
    print(response.text)

except Exception as exc:
    print("FAILED:", type(exc).__name__)
    print(str(exc)[:1500])
