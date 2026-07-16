# create_tables.py
from app import create_app
from extensions import db
from models import User, Profile, PartnerProfile, Candidate, Vacancy, Placement

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully!")