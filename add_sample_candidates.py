# add_sample_candidates.py
from app import create_app
from extensions import db
from models import Candidate
from datetime import datetime

app = create_app()

sample_candidates = [
    {
        'name': 'Sarah Kwakye',
        'email': 'sarah.k@email.com',
        'phone': '+233 24 123 4567',
        'location': 'Accra, Ghana',
        'skills': ['Python', 'Django', 'React', 'AWS', 'Docker', 'PostgreSQL'],
        'experience_years': 8.0,
        'education': [{'degree': 'BSc', 'field': 'Computer Science', 'school': 'University of Ghana', 'year': '2016'}],
        'certifications': ['AWS Certified Solutions Architect', 'Django Certification'],
        'employability_score': 92,
        'cv_text': 'Experienced Senior Developer with 8+ years of experience...',
        'is_processed': True
    },
    {
        'name': 'Michael Osei',
        'email': 'michael.o@email.com',
        'phone': '+233 54 987 6543',
        'location': 'Kumasi, Ghana',
        'skills': ['Python', 'Flask', 'PostgreSQL', 'Docker', 'JavaScript', 'Node.js'],
        'experience_years': 6.0,
        'education': [{'degree': 'MSc', 'field': 'Software Engineering', 'school': 'KNUST', 'year': '2018'}],
        'certifications': ['Docker Certified', 'MongoDB Certified'],
        'employability_score': 88,
        'cv_text': 'Backend Engineer with 6 years of experience...',
        'is_processed': True
    },
    {
        'name': 'Ama Asante',
        'email': 'ama.a@email.com',
        'phone': '+233 20 456 7890',
        'location': 'Tema, Ghana',
        'skills': ['JavaScript', 'React', 'Node.js', 'MongoDB', 'GraphQL', 'TypeScript'],
        'experience_years': 5.0,
        'education': [{'degree': 'BSc', 'field': 'Information Technology', 'school': 'UG', 'year': '2019'}],
        'certifications': ['React Certified', 'Node.js Developer'],
        'employability_score': 85,
        'cv_text': 'Full Stack Developer with 5 years of experience...',
        'is_processed': True
    },
    {
        'name': 'Kofi Mensah',
        'email': 'kofi.m@email.com',
        'phone': '+233 50 123 4567',
        'location': 'Accra, Ghana',
        'skills': ['Java', 'Spring Boot', 'Hibernate', 'MySQL', 'AWS', 'Microservices'],
        'experience_years': 10.0,
        'education': [{'degree': 'MSc', 'field': 'Computer Science', 'school': 'UG', 'year': '2014'}],
        'certifications': ['Oracle Certified Professional', 'AWS Certified'],
        'employability_score': 90,
        'cv_text': 'Senior Java Developer with 10+ years of experience...',
        'is_processed': True
    },
    {
        'name': 'Esi Tetteh',
        'email': 'esi.t@email.com',
        'phone': '+233 54 789 0123',
        'location': 'Takoradi, Ghana',
        'skills': ['Python', 'Data Science', 'Machine Learning', 'TensorFlow', 'SQL', 'Pandas'],
        'experience_years': 4.0,
        'education': [{'degree': 'MSc', 'field': 'Data Science', 'school': 'Ashesi', 'year': '2020'}],
        'certifications': ['Google Data Analytics', 'TensorFlow Developer'],
        'employability_score': 82,
        'cv_text': 'Data Scientist with 4 years of experience...',
        'is_processed': True
    }
]

with app.app_context():
    # Clear existing candidates (optional)
    # Candidate.query.delete()
    # db.session.commit()
    
    for data in sample_candidates:
        candidate = Candidate(**data)
        db.session.add(candidate)
    
    db.session.commit()
    print(f"✅ Added {len(sample_candidates)} sample candidates!")
    print("\n📋 Candidates added:")
    for c in sample_candidates:
        print(f"  - {c['name']} ({c['skills'][:3]})")