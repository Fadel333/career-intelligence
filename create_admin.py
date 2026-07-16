# create_admin.py
from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if admin already exists
    existing_admin = User.query.filter_by(email='fadiliddrisu24@gmail.com').first()
    
    if existing_admin:
        print('⚠️  Admin user already exists!')
        print(f'   Email: {existing_admin.email}')
        print(f'   User Type: {existing_admin.user_type}')
    else:
        admin = User(
            fullname='Fadel Iddrisu',
            email='fadiliddrisu24@gmail.com',
            password=generate_password_hash('admin123'),
            user_type='admin',
            is_verified=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created successfully!')
        print('   Email: fadiliddrisu24@gmail.com')
        print('   Password: admin123')