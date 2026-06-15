import os

class Config:
    SECRET_KEY = 'your-secret-key-change-this-in-production'
    
    # Use SQLite instead of PostgreSQL
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "career.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False