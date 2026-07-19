# test_connection.py
from dotenv import load_dotenv
import os
from pathlib import Path

# Force reload .env
env_path = Path('.env')
load_dotenv(dotenv_path=env_path, override=True)

print(f"🔍 DATABASE_URL: {os.environ.get('DATABASE_URL')}")