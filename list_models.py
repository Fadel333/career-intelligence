# list_models.py
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # reads .env in the current directory

api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    raise SystemExit("❌ GEMINI_API_KEY not found. Check your .env file or environment variables.")

client = genai.Client(api_key=api_key)

print("Models supporting generateContent:\n")
for m in client.models.list():
    for action in getattr(m, "supported_actions", []):
        if action == "generateContent":
            print(m.name)