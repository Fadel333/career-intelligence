import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Secret Key - from environment
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # Database - from environment with fallback
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:Ghana%40123@localhost:5432/career_intelligence'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    
    # Session
    SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))

# Print for debugging (remove in production)
print(f"🔍 Database URL: {Config.SQLALCHEMY_DATABASE_URI}")