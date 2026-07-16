# update_admin.py
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Find the user
    user = User.query.filter_by(email='fadiliddrisu24@gmail.com').first()
    
    if user:
        # Update to admin
        user.user_type = 'admin'
        user.is_verified = True
        user.is_active = True
        db.session.commit()
        print('✅ User updated to admin successfully!')
        print(f'   Email: {user.email}')
        print(f'   User Type: {user.user_type}')
        print(f'   Is Verified: {user.is_verified}')
    else:
        print('❌ User not found!')