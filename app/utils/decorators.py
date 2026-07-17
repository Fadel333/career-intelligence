# app/utils/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def login_required(f):
    """Standard login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def recruiter_required(f):
    """Require recruiter role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_recruiter():
            flash('You need recruiter access for this page.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def student_required(f):
    """Require student role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_student():
            flash('This page is for students only.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin():
            flash('You need admin access for this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def verified_recruiter_required(f):
    """Require verified recruiter status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_recruiter():
            flash('You need recruiter access for this page.', 'error')
            return redirect(url_for('dashboard'))
        from models import RecruiterProfile
        recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
        if not recruiter:
            flash('Please complete your recruiter profile first.', 'warning')
            return redirect(url_for('recruiter.setup_profile'))
        if recruiter.verification_status != 'approved':
            flash('Your account needs to be verified to access this feature.', 'warning')
            return redirect(url_for('recruiter.verification'))
        return f(*args, **kwargs)
    return decorated_function