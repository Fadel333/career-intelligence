# app/utils/email_notifier.py
import os
from flask import current_app, render_template
from flask_mail import Message
from extensions import mail

def send_job_alert_email(user, alert, matching_jobs):
    """Send job alert email to user"""
    try:
        # Create email message
        subject = f"🔔 New Job Alert: {len(matching_jobs)} jobs matching '{alert.keywords or 'your skills'}'"
        
        # Build email body with HTML
        html_body = render_template('email/job_alert.html', 
                                   user=user, 
                                   alert=alert, 
                                   jobs=matching_jobs)
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Failed to send job alert email: {e}")
        return False


def send_test_email(email):
    """Send a test email"""
    try:
        msg = Message(
            subject="🔔 FADTECH Labs - Job Alert System Test",
            recipients=[email],
            html="<h1>✅ Job Alert System is working!</h1><p>You will receive notifications when jobs match your preferences.</p>",
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False