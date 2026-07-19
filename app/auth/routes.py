# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Profile, RecruiterProfile
from extensions import db
from app.utils.oauth import oauth
from app.utils.email import send_welcome_email
import secrets

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type", "student")
        terms = request.form.get("terms")
        
        # Validation
        if not name or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))
        
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("auth.register"))
        
        if not terms:
            flash("You must agree to the Terms of Service.", "error")
            return redirect(url_for("auth.register"))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please login instead.", "error")
            return redirect(url_for("auth.login"))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        user = User(
            fullname=name,
            email=email,
            password=hashed_password,
            user_type=user_type,
            is_active=True,
            is_verified=True
        )
        
        try:
            db.session.add(user)
            db.session.flush()
            
            # Create profile for user
            profile = Profile(user_id=user.id)
            db.session.add(profile)
            
            # If user is a recruiter, create recruiter profile
            if user_type == 'recruiter':
                recruiter_profile = RecruiterProfile(
                    user_id=user.id,
                    company_name=name + "'s Company",
                    min_match_percentage=70.0,
                    verification_status='pending'
                )
                db.session.add(recruiter_profile)
            
            db.session.commit()

            send_welcome_email(user)
            
            flash("Account created successfully! Welcome!", "success")
            
            # Log the user in
            login_user(user)
            
            # Redirect based on user type
            if user_type == 'recruiter':
                return redirect(url_for('recruiter.setup_profile'))
            elif user_type == 'university':
                return redirect(url_for('university_dashboard'))
            elif user_type == 'admin':
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("auth.register"))
    
    # GET request - show registration form
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = request.form.get("remember")
        
        if not email or not password:
            flash("Please enter both email and password.", "error")
            return redirect(url_for("auth.login"))
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=bool(remember))
            flash(f"Welcome back, {user.fullname}!", "success")
            
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on user type
            if user.user_type == 'admin':
                return redirect(url_for('admin.index'))
            elif user.user_type == 'recruiter':
                return redirect(url_for('recruiter.dashboard'))
            elif user.user_type == 'university':
                return redirect(url_for('university_dashboard'))
            else:
                # Students and professionals
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))
    
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for("auth.login"))


# ========== OAUTH ROUTES ==========

def is_oauth_configured(provider):
    """Check if OAuth provider is configured"""
    return hasattr(oauth, provider) and oauth._clients.get(provider) is not None


@auth_bp.route('/login/google')
def google_login():
    """Google OAuth login"""
    if not is_oauth_configured('google'):
        flash('Google OAuth is not configured. Please contact support.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize/google')
def google_authorize():
    """Google OAuth callback"""
    if not is_oauth_configured('google'):
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token)
        
        profile = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'given_name': user_info.get('given_name'),
            'family_name': user_info.get('family_name'),
            'picture': user_info.get('picture')
        }
        
        return handle_oauth_callback('Google', profile)
        
    except Exception as e:
        flash(f'Google authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/linkedin')
def linkedin_login():
    """LinkedIn OAuth login"""
    if not is_oauth_configured('linkedin'):
        flash('LinkedIn OAuth is not configured. Please contact support.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.linkedin_authorize', _external=True)
    return oauth.linkedin.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize/linkedin')
def linkedin_authorize():
    """LinkedIn OAuth callback"""
    if not is_oauth_configured('linkedin'):
        flash('LinkedIn OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        token = oauth.linkedin.authorize_access_token()
        
        # Get user profile from LinkedIn
        resp = oauth.linkedin.get('userinfo', token=token)
        user_info = resp.json()
        
        profile = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'given_name': user_info.get('given_name'),
            'family_name': user_info.get('family_name'),
            'picture': user_info.get('picture')
        }
        
        return handle_oauth_callback('LinkedIn', profile)
        
    except Exception as e:
        flash(f'LinkedIn authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/github')
def github_login():
    """GitHub OAuth login"""
    if not is_oauth_configured('github'):
        flash('GitHub OAuth is not configured. Please contact support.', 'error')
        return redirect(url_for('auth.login'))
    
    redirect_uri = url_for('auth.github_authorize', _external=True)
    return oauth.github.authorize_redirect(redirect_uri)


@auth_bp.route('/authorize/github')
def github_authorize():
    """GitHub OAuth callback"""
    if not is_oauth_configured('github'):
        flash('GitHub OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        token = oauth.github.authorize_access_token()
        
        # Get user profile from GitHub
        resp = oauth.github.get('user', token=token)
        user_info = resp.json()
        
        # Get email from GitHub (may be private)
        email = user_info.get('email')
        if not email:
            # If email is private, get it from the emails endpoint
            email_resp = oauth.github.get('user/emails', token=token)
            emails = email_resp.json()
            for e in emails:
                if e.get('primary') and e.get('verified'):
                    email = e.get('email')
                    break
        
        profile = {
            'email': email,
            'name': user_info.get('name') or user_info.get('login'),
            'given_name': user_info.get('login'),
            'picture': user_info.get('avatar_url')
        }
        
        return handle_oauth_callback('GitHub', profile)
        
    except Exception as e:
        flash(f'GitHub authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


def handle_oauth_callback(provider, profile):
    """Handle OAuth callback for all providers"""
    from app.utils.oauth import handle_oauth_login
    return handle_oauth_login(provider, profile)