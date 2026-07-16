# app/utils/decorators.py
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

# app/utils/decorators.py

def recruiter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_recruiter():
            flash('You need recruiter access for this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Keep partner_required for backward compatibility, but redirect to recruiter
def partner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_recruiter():
            flash('Please use the Recruiter Hub.', 'error')
            return redirect(url_for('recruiter.hub'))
        return f(*args, **kwargs)
    return decorated_function


def verified_recruiter_required(f):
    """Decorator to require verified recruiter status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_recruiter():
            flash('You need recruiter access for this page.', 'error')
            return redirect(url_for('index'))
        
        # Check verification status
        recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
        
        if not recruiter:
            flash('Please complete your recruiter profile first.', 'warning')
            return redirect(url_for('recruiter.setup_profile'))
        
        if recruiter.verification_status != 'approved':
            flash('Your account needs to be verified to access this feature.', 'warning')
            return redirect(url_for('recruiter.verification'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access"""
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
    """Decorator to require verified recruiter status"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'error')
            return redirect(url_for('auth.login'))
        if not current_user.is_recruiter():
            flash('You need recruiter access for this page.', 'error')
            return redirect(url_for('index'))
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