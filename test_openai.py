import os
from dotenv import load_dotenv
import openai

load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
print(f"API Key found: {api_key is not None}")
print(f"API Key starts with: {api_key[:20] if api_key else 'None'}...")

if api_key:
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Say hello in 5 words"}
            ],
            max_tokens=50
        )
        print("✅ OpenAI API is working!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
else:
    print("❌ No API key found in .env")