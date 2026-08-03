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
        if DATABASE_URL.startswith('postgres+psycopg2://'):
            DATABASE_URL = DATABASE_URL.replace('postgres+psycopg2://', 'postgresql://', 1)
        if DATABASE_URL.startswith('postgres://'):
            DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
        if 'sslmode' not in DATABASE_URL:
            if '?' in DATABASE_URL:
                DATABASE_URL = DATABASE_URL + '&sslmode=require'
            else:
                DATABASE_URL = DATABASE_URL + '?sslmode=require'
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:fadiliddrisu@db.twpqpeeqebsobgaawgug.supabase.co:5432/postgres?sslmode=require'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ========== BASE URL & SERVER NAME ==========
    BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
    # Extract SERVER_NAME from BASE_URL for url_for()
    SERVER_NAME = BASE_URL.replace('https://', '').replace('http://', '').split('/')[0]
    PREFERRED_URL_SCHEME = 'https' if 'https://' in BASE_URL else 'http'
    APPLICATION_ROOT = '/'
    
    # ========== SUPABASE CONFIGURATION ==========
    SUPABASE_URL = os.environ.get('NEXT_PUBLIC_SUPABASE_URL', 'https://twpqpeeqebsobgaawgug.supabase.co')
    SUPABASE_PUBLISHABLE_KEY = os.environ.get('NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_3FZF-s7rliIgVCGXV_yq0Q_ZnS43BYp')
    
    # ========== OPENAI CONFIGURATION ==========
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # ========== YOUTUBE API CONFIGURATION ==========
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    
    # ========== COURSERA API CONFIGURATION ==========
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
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}
    
    # ========== SESSION CONFIGURATION ==========
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600

    # ========== EMAIL CONFIGURATION - SENDGRID ==========
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL', 'fadtechlabs.com@gmail.com')
    SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME', 'TalentForge AI')
    
    # ========== EMAIL CONFIGURATION - SMTP FALLBACK ==========
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'fadtechlabs.com@gmail.com')
    MAIL_DEBUG = os.environ.get('MAIL_DEBUG', 'False') == 'True'
    
    # ========== OAUTH CONFIGURATION ==========
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    LINKEDIN_CLIENT_ID = os.environ.get('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET = os.environ.get('LINKEDIN_CLIENT_SECRET')
    
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET')
    
    # ========== ENGINE OPTIONS ==========
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
        'pool_size': 5,
        'max_overflow': 10,
    }

    @staticmethod
    def is_sendgrid_configured():
        return bool(os.environ.get('SENDGRID_API_KEY'))


# Print configuration status
print(f"🔍 Database URL: {Config.SQLALCHEMY_DATABASE_URI}")
print(f"🔍 Supabase URL: {Config.SUPABASE_URL}")
print(f"🔍 OpenAI Key: {'✅ Set' if Config.OPENAI_API_KEY else '❌ Not Set'}")
print(f"🔍 YouTube Key: {'✅ Set' if Config.YOUTUBE_API_KEY else '❌ Not Set'}")
print(f"🔍 Coursera: {'✅ Business API' if Config.COURSERA_CLIENT_ID else '⚠️ Using Public API (free)'}")
print(f"🔍 Udemy: {'✅ Set' if Config.UDEMY_CLIENT_ID else '❌ Not Set'}")
print(f"🔍 SendGrid: {'✅ Set' if Config.SENDGRID_API_KEY else '❌ Not Set'}")
print(f"🔍 Google OAuth: {'✅ Set' if Config.GOOGLE_CLIENT_ID else '❌ Not Set'}")
print(f"🔍 LinkedIn OAuth: {'✅ Set' if Config.LINKEDIN_CLIENT_ID else '❌ Not Set'}")
print(f"🔍 GitHub OAuth: {'✅ Set' if Config.GITHUB_CLIENT_ID else '❌ Not Set'}")
print(f"🔍 Base URL: {Config.BASE_URL}")
print(f"🔍 Server Name: {Config.SERVER_NAME}")