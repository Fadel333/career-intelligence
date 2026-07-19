import os
from dotenv import load_dotenv

# Load .env file - make sure the path is correct
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # ========== DATABASE CONFIGURATION ==========
    # Get DATABASE_URL from environment (for production) or use local
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        # Fix: postgres:// → postgresql:// (for Supabase compatibility)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        # Add SSL mode for Supabase (required for production)
        if 'sslmode' not in DATABASE_URL:
            if '?' in DATABASE_URL:
                DATABASE_URL = DATABASE_URL + '&sslmode=require'
            else:
                DATABASE_URL = DATABASE_URL + '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local development database
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ghana%40123@localhost:5432/career_intelligence'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== SUPABASE CONFIGURATION ==========
    SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', 'https://twpqpeeqebsobgaawgug.supabase.co')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_3FZF-s7rliIgVCGXV_yq0Q_ZnS43BYp')
    
    # ========== OPENAI CONFIGURATION ==========
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # ========== UPLOAD CONFIGURATION ==========
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # ========== SESSION CONFIGURATION ==========
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

    # ========== EMAIL CONFIGURATION ==========
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@fadtechlabs.com')
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False') == 'True'


print(f"🔍 Database URL: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"🔍 Supabase URL: {Config.SUPABASE_URL}")
print(f"🔍 OpenAI Key: {'✅ Set' if Config.OPENAI_API_KEY else '❌ Not Set'}")