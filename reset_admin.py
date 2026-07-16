from app import create_app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if user exists
    user = User.query.filter_by(email='fadiliddrisu24@gmail.com').first()
    
    if user:
        # Update existing user
        user.password = generate_password_hash('admin123')
        user.user_type = 'admin'
        user.is_active = True
        user.is_verified = True
        db.session.commit()
        print('✅ Admin user updated!')
        print(f'   Email: {user.email}')
        print(f'   Type: {user.user_type}')
    else:
        # Create new admin
        admin = User(
            fullname='Fadel Iddrisu',
            email='fadiliddrisu24@gmail.com',
            password=generate_password_hash('admin123'),
            user_type='admin',
            is_active=True,
            is_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created!')
        print('   Email: fadiliddrisu24@gmail.com')
        print('   Password: admin123')