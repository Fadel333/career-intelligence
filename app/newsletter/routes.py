# app/newsletter/routes.py
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime

from models import db, NewsletterSubscriber
from app.utils.email import send_welcome_newsletter_email

newsletter_bp = Blueprint('newsletter', __name__, url_prefix='/newsletter')


@newsletter_bp.route('/subscribe', methods=['POST'])
def subscribe():
    """Handle newsletter subscription from footer form"""
    data = request.get_json() or request.form
    email = (data.get('email') or '').strip().lower()
    name = (data.get('name') or '').strip() or None
    
    # Validation
    if not email or '@' not in email or '.' not in email.split('@')[-1]:
        return jsonify({'message': 'Please enter a valid email address'}), 400
    
    # Check if already subscribed
    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    
    if existing:
        if existing.is_active:
            return jsonify({'message': 'You are already subscribed!'}), 200
        else:
            # Reactivate
            existing.is_active = True
            existing.unsubscribed_at = None
            db.session.commit()
            return jsonify({'message': 'Welcome back!'}), 200
    
    # New subscriber
    subscriber = NewsletterSubscriber(
        email=email,
        name=name,
        source='footer',
        is_active=True
    )
    db.session.add(subscriber)
    db.session.commit()
    
    # Send welcome email (non-blocking)
    try:
        send_welcome_newsletter_email(email, name)
        print(f"✅ Welcome email queued for {email}")
    except Exception as e:
        print(f"⚠️ Welcome email failed for {email}: {e}")
    
    return jsonify({'message': 'Subscribed successfully!'}), 201


@newsletter_bp.route('/unsubscribe')
def unsubscribe():
    """Handle unsubscribe requests"""
    email = (request.args.get('email') or '').strip().lower()
    
    if not email:
        return render_template('newsletter/unsubscribe.html', 
                             success=False, 
                             message='Invalid unsubscribe link')
    
    subscriber = NewsletterSubscriber.query.filter_by(email=email).first()
    
    if not subscriber:
        return render_template('newsletter/unsubscribe.html',
                             success=False,
                             message='Email not found in our list')
    
    if not subscriber.is_active:
        return render_template('newsletter/unsubscribe.html',
                             success=True,
                             message='You are already unsubscribed')
    
    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.utcnow()
    db.session.commit()
    
    return render_template('newsletter/unsubscribe.html',
                         success=True,
                         message='You have been unsubscribed')