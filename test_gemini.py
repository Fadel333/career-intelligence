# test_gemini.py
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
API_KEY = os.environ.get('GEMINI_API_KEY')

if not API_KEY:
    print("❌ No GEMINI_API_KEY found in .env file")
    print("💡 Get your API key from: https://makersuite.google.com/app/apikey")
    exit(1)

print(f"✅ API Key found: {API_KEY[:20]}...")

try:
    # Initialize Gemini client
    client = genai.Client(api_key=API_KEY)
    
    # ✅ UPDATED: Use gemini-3.6-flash
    MODEL = "gemini-3.6-flash"
    
    print(f"📊 Using model: {MODEL}")
    print("⏳ Sending request...")
    
    response = client.models.generate_content(
        model=MODEL,
        contents="Say 'Hello, Gemini is working!' in 5 words"
    )
    
    print("✅ SUCCESS! Gemini is working!")
    print(f"💬 Response: {response.text}")
    
except Exception as e:
    print(f"❌ ERROR: {e}")