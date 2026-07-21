import os
from dotenv import load_dotenv
from pathlib import Path

# Force load .env from the correct location
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    
    # ========== DATABASE CONFIGURATION ==========
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if DATABASE_URL:
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        if 'sslmode' not in DATABASE_URL:
            if '?' in DATABASE_URL:
                DATABASE_URL = DATABASE_URL + '&sslmode=require'
            else:
                DATABASE_URL = DATABASE_URL + '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Ghana%40123@localhost:5432/career_intelligence'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== SUPABASE CONFIGURATION ==========
    SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', 'https://twpqpeeqebsobgaawgug.supabase.co')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_3FZF-s7rliIgVCGXV_yq0Q_ZnS43BYp')
    
    # ========== OPENAI CONFIGURATION ==========
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # ========== YOUTUBE API CONFIGURATION ==========
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    
    # ========== COURSERA API CONFIGURATION ==========
    # Public API doesn't need a key, but Business API does
    COURSERA_CLIENT_ID = os.environ.get('COURSERA_CLIENT_ID')
    COURSERA_CLIENT_SECRET = os.environ.get('COURSERA_CLIENT_SECRET')
    COURSERA_ORGANIZATION_ID = os.environ.get('COURSERA_ORGANIZATION_ID')
    
    # ========== UDEMY API CONFIGURATION ==========
    UDEMY_CLIENT_ID = os.environ.get('UDEMY_CLIENT_ID')
    UDEMY_CLIENT_SECRET = os.environ.get('UDEMY_CLIENT_SECRET')
    UDEMY_ORG_ID = os.environ.get('UDEMY_ORG_ID')
    UDEMY_SUBDOMAIN = os.environ.get('UDEMY_SUBDOMAIN')
    
    # ========== UPLOAD CONFIGURATION ==========
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
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
    
    # ========== GOOGLE OAUTH ==========
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # ========== LINKEDIN OAUTH ==========
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET')
    
    # ========== GITHUB OAUTH ==========
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')

     # ========== SMS CONFIGURATION (Twilio) ==========
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # ========== SMS CONFIGURATION (Africa's Talking) ==========
    AFRICA_TALKING_USERNAME = os.environ.get('AFRICA_TALKING_USERNAME')
    AFRICA_TALKING_API_KEY = os.environ.get('AFRICA_TALKING_API_KEY')
    AFRICA_TALKING_SENDER_ID = os.environ.get('AFRICA_TALKING_SENDER_ID')


# Print configuration status (for debugging)
print(f"🔍 Database URL: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"🔍 Supabase URL: {Config.SUPABASE_URL}")
print(f"🔍 OpenAI Key: {'✅ Set' if Config.OPENAI_API_KEY else '❌ Not Set'}")
print(f"🔍 YouTube Key: {'✅ Set' if Config.YOUTUBE_API_KEY else '❌ Not Set'}")
print(f"🔍 Coursera: {'✅ Business API' if Config.COURSERA_CLIENT_ID else '⚠️ Using Public API (free)'}")
print(f"🔍 Udemy: {'✅ Set' if Config.UDEMY_CLIENT_ID else '❌ Not Set'}")