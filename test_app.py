# test_app.py
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    print('✅ App initialized with DB')
    db.engine.connect()
    print('✅ Connected to Supabase!')