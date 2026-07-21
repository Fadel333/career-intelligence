from authlib.integrations.flask_client import OAuth
from flask import session, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from flask_login import login_user
from models import User
from extensions import db
import secrets
import os

oauth = OAuth()

def configure_oauth(app):
    """Configure OAuth providers"""
    oauth.init_app(app)
    
    # Check if credentials exist, use placeholders if not
    google_client_id = os.environ.get('GOOGLE_CLIENT_ID', '')
    google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET', '')
    
    linkedin_client_id = os.environ.get('LINKEDIN_CLIENT_ID', '')
    linkedin_client_secret = os.environ.get('LINKEDIN_CLIENT_SECRET', '')
    
    github_client_id = os.environ.get('GITHUB_CLIENT_ID', '')
    github_client_secret = os.environ.get('GITHUB_CLIENT_SECRET', '')
    
    # ============================================================
    # GOOGLE OAUTH - FIXED
    # ============================================================
    if google_client_id and google_client_secret:
        oauth.register(
            name='google',
            client_id=google_client_id,
            client_secret=google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            },
            # ✅ FIX: Remove authorize_params - let the route handle nonce
            redirect_uri=os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/authorize/google')
        )
        print("✅ Google OAuth configured")
    
    # ============================================================
    # LINKEDIN OAUTH
    # ============================================================
    if linkedin_client_id and linkedin_client_secret:
        oauth.register(
            name='linkedin',
            client_id=linkedin_client_id,
            client_secret=linkedin_client_secret,
            access_token_url='https://www.linkedin.com/oauth/v2/accessToken',
            authorize_url='https://www.linkedin.com/oauth/v2/authorization',
            api_base_url='https://api.linkedin.com/v2/',
            client_kwargs={
                'scope': 'openid profile email'
            },
            redirect_uri=os.environ.get('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/auth/authorize/linkedin')
        )
        print("✅ LinkedIn OAuth configured")
    
    # ============================================================
    # GITHUB OAUTH
    # ============================================================
    if github_client_id and github_client_secret:
        oauth.register(
            name='github',
            client_id=github_client_id,
            client_secret=github_client_secret,
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={
                'scope': 'user:email'
            },
            redirect_uri=os.environ.get('GITHUB_REDIRECT_URI', 'http://localhost:5000/auth/authorize/github')
        )
        print("✅ GitHub OAuth configured")
    
    return oauth


def handle_oauth_login(provider, profile):
    """Handle OAuth login or registration"""
    email = profile.get('email')
    
    if not email:
        flash('Email not provided by the provider.', 'error')
        return redirect(url_for('auth.login'))
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Login existing user
        login_user(user, remember=True)
        flash(f'Welcome back, {user.fullname}!', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Create new user
        fullname = profile.get('name') or profile.get('fullname') or profile.get('given_name', 'User')
        
        # Generate random password for OAuth users
        random_password = secrets.token_urlsafe(16)
        hashed_password = generate_password_hash(random_password)
        
        new_user = User(
            fullname=fullname,
            email=email,
            password=hashed_password,
            user_type='student',
            is_verified=True
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user, remember=True)
            flash(f'Account created successfully with {provider}! Welcome {fullname}!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'error')
            return redirect(url_for('auth.register'))