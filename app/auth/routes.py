# app/auth/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Profile, RecruiterProfile
from extensions import db
from app.utils.oauth import oauth
from app.utils.email import send_welcome_email, send_verification_email
import secrets
from datetime import datetime, timedelta
import jwt

auth_bp = Blueprint("auth", __name__)


# ========== TOKEN FUNCTIONS ==========

def generate_verification_token(user_id):
    """Generate email verification token (expires in 7 days)"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token):
    """Verify and decode token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ========== REGISTRATION ==========

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user_type = request.form.get("user_type", "student")
        company_name = request.form.get("company_name", "").strip()
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
        
        # For recruiters, company name is required
        if user_type == 'recruiter' and not company_name:
            flash("Company name is required for recruiters.", "error")
            return redirect(url_for("auth.register"))
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists. Please login instead.", "error")
            return redirect(url_for("auth.login"))
        
        # ✅ Create user as INACTIVE (requires email verification)
        hashed_password = generate_password_hash(password)
        user = User(
            fullname=name,
            email=email,
            password=hashed_password,
            user_type=user_type,
            is_active=False,      # ✅ User cannot login until verified
            is_verified=False     # ✅ Not verified yet
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
                    company_name=company_name or f"{name}'s Company",
                    min_match_percentage=70.0,
                    verification_status='pending'
                )
                db.session.add(recruiter_profile)
                
                # Also set company_name in User model
                user.company_name = company_name or f"{name}'s Company"
            
            db.session.commit()

            # ✅ GENERATE AND SEND VERIFICATION EMAIL
            try:
                token = generate_verification_token(user.id)
                send_verification_email(email, token, name)
                flash("✅ Please check your email to verify your account.", "success")
            except Exception as e:
                print(f"Verification email error: {e}")
                # Still create account, but warn user
                flash("⚠️ Account created but we couldn't send verification email. Please contact support.", "warning")
            
            # ✅ DO NOT LOGIN USER - they need to verify first
            return redirect(url_for("auth.login"))
                
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash("An error occurred. Please try again.", "error")
            return redirect(url_for("auth.register"))
    
    # GET request - show registration form
    return render_template("register.html")


# ========== EMAIL VERIFICATION ==========

@auth_bp.route('/verify/<token>')
def verify_email(token):
    """Verify user's email address"""
    user_id = verify_token(token)
    
    if not user_id:
        flash('❌ Invalid or expired verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(user_id)
    
    if not user:
        flash('❌ User not found.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('✅ Email already verified. Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    # ✅ ACTIVATE USER
    user.is_verified = True
    user.is_active = True
    db.session.commit()
    
    flash('✅ Email verified! You can now login.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('auth.resend_verification'))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('No account found with this email.', 'error')
            return redirect(url_for('auth.resend_verification'))
        
        if user.is_verified:
            flash('✅ Email already verified. Please login.', 'success')
            return redirect(url_for('auth.login'))
        
        try:
            token = generate_verification_token(user.id)
            send_verification_email(user.email, token, user.fullname)
            flash('✅ Verification email resent. Please check your inbox.', 'success')
        except Exception as e:
            print(f"Resend verification error: {e}")
            flash('Could not send verification email. Please try again later.', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('resend_verification.html')


# ========== LOGIN ==========

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
        
        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))
        
        # ✅ CHECK IF EMAIL IS VERIFIED
        if not user.is_verified:
            flash("⚠️ Please verify your email first. Check your inbox or request a new verification link.", "error")
            return redirect(url_for("auth.resend_verification"))
        
        # ✅ CHECK IF USER IS ACTIVE
        if not user.is_active:
            flash("⚠️ Your account is inactive. Please contact support.", "error")
            return redirect(url_for("auth.login"))
        
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
            return redirect(url_for('dashboard'))
    
    return render_template("login.html")


# ========== LOGOUT ==========

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
    
    nonce = secrets.token_urlsafe(16)
    session['oauth_nonce'] = nonce
    
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri, nonce=nonce)


@auth_bp.route('/authorize/google')
def google_authorize():
    """Google OAuth callback"""
    if not is_oauth_configured('google'):
        flash('Google OAuth is not configured.', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('https://www.googleapis.com/oauth2/v3/userinfo', token=token)
        user_info = resp.json()
        
        if not user_info or not user_info.get('email'):
            flash('Could not get user information from Google.', 'error')
            return redirect(url_for('auth.login'))
        
        profile = {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'given_name': user_info.get('given_name'),
            'family_name': user_info.get('family_name'),
            'picture': user_info.get('picture')
        }
        
        return handle_oauth_callback('Google', profile)
        
    except Exception as e:
        print(f"Google OAuth error: {e}")
        flash(f'Google authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


# ========== LINKEDIN OAUTH - FIXED ==========

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
        
        # ✅ FIX: Use the correct endpoint for LinkedIn
        resp = oauth.linkedin.get('userinfo', token=token)
        user_info = resp.json()
        
        print(f"🔍 LinkedIn user info: {user_info}")  # Debug
        
        # ✅ Extract email and name from the response
        email = user_info.get('email')
        
        # ✅ Get name from different possible fields
        name = user_info.get('name')
        given_name = user_info.get('given_name')
        family_name = user_info.get('family_name')
        
        # If name is not available, combine given_name and family_name
        if not name and given_name and family_name:
            name = f"{given_name} {family_name}"
        elif not name:
            name = given_name or 'LinkedIn User'
        
        if not email:
            flash('Could not get email from LinkedIn.', 'error')
            return redirect(url_for('auth.login'))
        
        profile = {
            'email': email,
            'name': name,
            'given_name': given_name,
            'family_name': family_name,
            'picture': user_info.get('picture')
        }
        
        return handle_oauth_callback('LinkedIn', profile)
        
    except Exception as e:
        print(f"❌ LinkedIn OAuth error: {e}")
        flash(f'LinkedIn authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


# ========== GITHUB OAUTH ==========

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
        
        # Get user profile
        resp = oauth.github.get('user', token=token)
        user_info = resp.json()
        
        print(f"🔍 GitHub user info: {user_info}")  # Debug
        
        # Get email (may be private)
        email = user_info.get('email')
        if not email:
            email_resp = oauth.github.get('user/emails', token=token)
            emails = email_resp.json()
            for e in emails:
                if e.get('primary') and e.get('verified'):
                    email = e.get('email')
                    break
        
        if not email:
            flash('Could not get email from GitHub.', 'error')
            return redirect(url_for('auth.login'))
        
        profile = {
            'email': email,
            'name': user_info.get('name') or user_info.get('login'),
            'given_name': user_info.get('login'),
            'picture': user_info.get('avatar_url')
        }
        
        return handle_oauth_callback('GitHub', profile)
        
    except Exception as e:
        print(f"❌ GitHub OAuth error: {e}")
        flash(f'GitHub authentication failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))


def handle_oauth_callback(provider, profile):
    """Handle OAuth callback for all providers"""
    from app.utils.oauth import handle_oauth_login
    return handle_oauth_login(provider, profile)


# ========== PASSWORD RESET ==========

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Please enter your email address.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('If an account exists with this email, you will receive a password reset link.', 'success')
            return redirect(url_for('auth.login'))
        
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expiry = datetime.utcnow() + timedelta(hours=24)
        db.session.commit()
        
        try:
            from app.utils.email import send_password_reset_email
            send_password_reset_email(user, token)
            flash('Password reset link sent to your email.', 'success')
        except Exception as e:
            print(f"Email error: {e}")
            flash('We could not send the reset email. Please try again later.', 'error')
        
        return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password using token"""
    user = User.query.filter_by(reset_token=token).first()
    
    if not user:
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if user.reset_token_expiry and user.reset_token_expiry < datetime.utcnow():
        flash('Password reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        
        user.password = generate_password_hash(password)
        user.reset_token = None
        user.reset_token_expiry = None
        db.session.commit()
        
        flash('Password reset successfully! Please login with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', token=token)