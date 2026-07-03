import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # Use the new database
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ghana%40123@localhost:5432/career_intelligence'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

print(f"🔍 Database URL: {Config.SQLALCHEMY_DATABASE_URI}")