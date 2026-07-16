# create_recruiter.py
from app import create_app
from extensions import db
from models import User, RecruiterProfile
from werkzeug.security import generate_password_hash

app = create_app()

def create_recruiter():
    with app.app_context():
        # Check if recruiter already exists
        existing_recruiter = RecruiterProfile.query.first()
        if existing_recruiter:
            print(f'✅ Recruiter already exists:')
            print(f'   Company: {existing_recruiter.company_name}')
            print(f'   ID: {existing_recruiter.id}')
            return
        
        # Create user
        email = 'recruiter@fadtech.com'
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                fullname='Test Recruiter',
                email=email,
                password=generate_password_hash('recruiter123'),
                user_type='recruiter',
                is_active=True,
                is_verified=True
            )
            db.session.add(user)
            db.session.flush()
            print(f'✅ Created user: {email}')
        else:
            print(f'✅ User already exists: {email}')
        
        # Create recruiter profile
        recruiter = RecruiterProfile(
            user_id=user.id,
            company_name='FADTECH Labs',
            company_description='Leading technology company in Africa',
            company_website='https://fadtechlabs.com',
            industry='Technology',
            location='Accra, Ghana',
            verification_status='approved'
        )
        db.session.add(recruiter)
        db.session.commit()
        
        print(f'\n✅ Recruiter created successfully!')
        print(f'   Company: {recruiter.company_name}')
        print(f'   Email: {email}')
        print(f'   Password: recruiter123')
        print(f'   Recruiter ID: {recruiter.id}')

if __name__ == '__main__':
    create_recruiter()