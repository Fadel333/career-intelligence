# app/utils/email.py
from flask import current_app, render_template, url_for
from threading import Thread
import os
import logging
from extensions import db
import requests
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


# ============================================================
# CORE SEND FUNCTION — BREVO
# ============================================================

def _send_async_brevo(app, subject, recipients, html_body, sender_email, sender_name="TalentForge AI"):
    """Send email via Brevo API (async, non-blocking)"""
    with app.app_context():
        try:
            print(f"📧 Sending email via Brevo to: {recipients}")

            api_key = app.config.get('BREVO_API_KEY')
            if not api_key:
                print("❌ BREVO_API_KEY not set")
                logger.error("BREVO_API_KEY not configured")
                return

            to_list = [{"email": r} for r in recipients]

            payload = {
                "sender": {
                    "email": sender_email,
                    "name": sender_name,
                },
                "to": to_list,
                "subject": subject,
                "htmlContent": html_body,
            }

            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json=payload,
                timeout=15,
            )

            if response.status_code in (200, 201, 202):
                print(f"✅ Email sent successfully to {recipients}")
            else:
                print(f"❌ Brevo error {response.status_code}: {response.text}")
                logger.error(f"Brevo error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            logger.error(f"Email error: {e}")


def send_email(subject, recipients, html_body, text_body=None, sender=None):
    """Send an email via Brevo (async, non-blocking)"""
    try:
        app = current_app._get_current_object()
        recipients_list = recipients if isinstance(recipients, list) else [recipients]

        sender_email = sender or app.config.get(
            'BREVO_FROM_EMAIL',
            'fadtechlabs.com@gmail.com'
        )
        sender_name = app.config.get('BREVO_FROM_NAME', 'TalentForge AI')

        print(f"📧 Preparing email: {subject}")
        print(f"📧 Recipients: {recipients_list}")
        print(f"📧 From: {sender_email}")

        Thread(
            target=_send_async_brevo,
            args=(app, subject, recipients_list, html_body, sender_email, sender_name),
        ).start()

        print(f"📧 Email thread started for {recipients_list}")
        return True
    except Exception as e:
        print(f"❌ Failed to prepare email: {e}")
        logger.error(f"Send email error: {e}")
        return False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_clickable_button(text, url, color='#6366f1'):
    """Create a fully clickable email button with proper styling"""
    return f'''
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="text-align: center; margin: 20px 0;">
        <tr>
            <td align="center">
                <a href="{url}" 
                   style="display: inline-block; 
                          padding: 14px 40px; 
                          background: {color}; 
                          color: #ffffff !important; 
                          text-decoration: none !important; 
                          border-radius: 50px; 
                          font-weight: 600; 
                          font-size: 16px; 
                          border: none; 
                          cursor: pointer; 
                          text-align: center; 
                          line-height: 1.5; 
                          -webkit-text-size-adjust: none;
                          box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);">
                    {text}
                </a>
            </td>
        </tr>
    </table>
    '''


def create_clickable_text_link(text, url):
    """Create a clickable text link"""
    return f'<a href="{url}" style="color: #6366f1; text-decoration: underline; font-weight: 500;">{text}</a>'


# ============================================================
# WEEKLY DIGEST EMAIL
# ============================================================

def send_weekly_digest(user, digest_data):
    """Send weekly progress digest email"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    subject = f"📊 Your TalentForge Weekly — {digest_data.get('week_of', '')}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 20px 0; }}
            .stat {{ background: #f8f6f0; border-radius: 12px; padding: 16px; }}
            .stat-label {{ color: #718096; font-size: 12px; text-transform: uppercase; }}
            .stat-value {{ color: #2c3e50; font-size: 24px; font-weight: 700; margin-top: 4px; }}
            .section-title {{ color: #2c3e50; font-size: 16px; font-weight: 600; margin-top: 24px; }}
            .job-item {{ padding: 12px; background: #f8f6f0; border-radius: 8px; margin-bottom: 8px; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f6f0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="container" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width: 600px; width: 100%;">
                        <tr>
                            <td style="padding: 40px 30px;">
                                <div class="header">
                                    <div class="logo">TalentForge <span>AI</span></div>
                                    <p class="tagline">Africa's Talent Intelligence Platform</p>
                                </div>
                                <div class="content">
                                    <h2 style="color: #2c3e50;">Hi {user.fullname.split()[0] if user.fullname else 'there'}! 👋</h2>
                                    <p style="color: #555; line-height: 1.6;">Here's what happened this week:</p>

                                    <div class="stat-grid">
                                        <div class="stat">
                                            <div class="stat-label">Courses Completed</div>
                                            <div class="stat-value">{digest_data.get('courses_completed', 0)}</div>
                                        </div>
                                        <div class="stat">
                                            <div class="stat-label">Current Streak</div>
                                            <div class="stat-value">{digest_data.get('current_streak', 0)}🔥</div>
                                        </div>
                                        <div class="stat">
                                            <div class="stat-label">Employability</div>
                                            <div class="stat-value">{digest_data.get('employability_score', 0)}</div>
                                        </div>
                                        <div class="stat">
                                            <div class="stat-label">Job Matches</div>
                                            <div class="stat-value">{digest_data.get('new_jobs_count', 0)}</div>
                                        </div>
                                    </div>

                                    <h3 class="section-title">🔥 This week's top skill: {digest_data.get('top_skill', 'Python')}</h3>
                                    <p style="color: #555; font-size: 14px;">
                                        {digest_data.get('top_skill_demand', 60)}% of new jobs mention it.
                                    </p>

                                    <h3 class="section-title">💼 New jobs matching your skills</h3>
                                    {digest_data.get('new_jobs_html', '<p style="color: #999; font-size: 14px;">No new matches this week — keep building your skills!</p>')}

                                    <div style="text-align: center; margin: 32px 0;">
                                        <a href="{base_url}/progress"
                                           style="display: inline-block; padding: 14px 32px; background: #6366f1; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600;">
                                            View My Progress
                                        </a>
                                    </div>
                                </div>
                                <div class="footer">
                                    <p>© 2026 TalentForge AI. All rights reserved.</p>
                                    <p style="margin-top: 8px;">
                                        <a href="{base_url}/progress" style="color: #999;">Manage preferences</a>
                                    </p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return send_email(subject, user.email, html)


# ============================================================
# EMAIL VERIFICATION
# ============================================================

def send_verification_email(email, token, fullname):
    """Send email verification link to new user"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    verification_url = f"{base_url}/auth/verify/{token}"

    subject = "✅ Verify Your Email - TalentForge AI"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .token-box {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; word-break: break-all; font-size: 12px; }}
            .warning {{ background: #fef3c7; padding: 16px; border-radius: 12px; border-left: 4px solid #f59e0b; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f6f0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="container" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width: 600px; width: 100%;">
                        <tr>
                            <td style="padding: 40px 30px;">
                                <div class="header">
                                    <div class="logo">TalentForge <span>AI</span></div>
                                    <p class="tagline">Africa's Talent Intelligence Platform</p>
                                </div>
                                <div class="content">
                                    <h2 style="color: #2c3e50;">Welcome, {fullname}! 👋</h2>
                                    <p style="color: #555; line-height: 1.6;">
                                        Thanks for registering with <strong>TalentForge AI</strong>. 
                                        Please verify your email address to get started.
                                    </p>
                                    {create_clickable_button('✅ Verify Email Address', verification_url)}
                                    <p style="color: #718096; font-size: 14px; text-align: center;">
                                        Or copy and paste this link into your browser:
                                    </p>
                                    <div class="token-box">{verification_url}</div>
                                    <div class="warning">
                                        <p style="margin: 0; color: #92400e; font-size: 14px;">
                                            ⚠️ This link expires in <strong>7 days</strong>.
                                        </p>
                                    </div>
                                </div>
                                <div class="footer">
                                    <p>© 2026 TalentForge AI. All rights reserved.</p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return send_email(subject, email, html)


# ============================================================
# WELCOME EMAIL
# ============================================================

def send_welcome_email(user):
    """Send welcome email to new user"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    subject = "Welcome to TalentForge AI! 🚀"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f6f0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="container" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width: 600px; width: 100%;">
                        <tr>
                            <td style="padding: 40px 30px;">
                                <div class="header">
                                    <div class="logo">TalentForge <span>AI</span></div>
                                    <p class="tagline">Africa's Talent Intelligence Platform</p>
                                </div>
                                <div class="content">
                                    <h2 style="color: #2c3e50;">Welcome, {user.fullname}! 👋</h2>
                                    <p style="color: #555; line-height: 1.6;">Thank you for joining TalentForge AI!</p>
                                    <div style="background: #e8f5e9; padding: 16px; border-radius: 12px; margin: 20px 0;">
                                        <p style="margin: 0; color: #2e7d32;">🎯 Upload your CV to receive your personalized skill analysis!</p>
                                    </div>
                                    {create_clickable_button('🚀 Go to Dashboard', f'{base_url}/dashboard')}
                                </div>
                                <div class="footer">
                                    <p>© 2026 TalentForge AI. All rights reserved.</p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


# ============================================================
# PASSWORD RESET
# ============================================================

def send_password_reset_email(user, token):
    """Send password reset email to user"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    reset_url = f"{base_url}/auth/reset-password/{token}"

    subject = "🔐 Reset Your Password - TalentForge AI"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .token-box {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; word-break: break-all; font-size: 12px; }}
            .warning {{ background: #fef3c7; padding: 16px; border-radius: 12px; border-left: 4px solid #f59e0b; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f6f0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="container" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width: 600px; width: 100%;">
                        <tr>
                            <td style="padding: 40px 30px;">
                                <div class="header">
                                    <div class="logo">TalentForge <span>AI</span></div>
                                    <p class="tagline">Africa's Talent Intelligence Platform</p>
                                </div>
                                <div class="content">
                                    <h2 style="color: #2c3e50;">🔐 Reset Your Password</h2>
                                    <p style="color: #555; line-height: 1.6;">Hi {user.fullname},</p>
                                    <p style="color: #555; line-height: 1.6;">
                                        We received a request to reset your password. Click the button below:
                                    </p>
                                    {create_clickable_button('🔐 Reset Password', reset_url)}
                                    <div class="token-box">{reset_url}</div>
                                    <div class="warning">
                                        <p style="margin: 0; color: #92400e; font-size: 14px;">
                                            ⚠️ This link expires in <strong>24 hours</strong>.
                                        </p>
                                    </div>
                                </div>
                                <div class="footer">
                                    <p>© 2026 TalentForge AI. All rights reserved.</p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return send_email(subject, user.email, html)


# ============================================================
# TEST EMAIL
# ============================================================

def send_test_email(email):
    """Send a test email to verify configuration"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    subject = "✅ Test Email - TalentForge AI"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .success-box {{ background: #f0fdf4; padding: 20px; border-radius: 12px; border-left: 4px solid #10b981; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f8f6f0">
            <tr>
                <td align="center" style="padding: 20px 0;">
                    <table class="container" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="max-width: 600px; width: 100%;">
                        <tr>
                            <td style="padding: 40px 30px;">
                                <div class="header">
                                    <div class="logo">TalentForge <span>AI</span></div>
                                </div>
                                <div class="content">
                                    <h2 style="color: #1a1a2e;">✅ Test Email</h2>
                                    <p style="color: #4b5563;">Your Brevo configuration is working correctly.</p>
                                    <div class="success-box">
                                        <p style="margin: 0; color: #065f46; font-weight: 600;">✅ Brevo is live!</p>
                                        <p style="margin: 4px 0; color: #065f46; font-size: 14px;">📧 Sent from: {base_url}</p>
                                        <p style="margin: 4px 0; color: #065f46; font-size: 14px;">📅 Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                                    </div>
                                </div>
                                <div class="footer">
                                    <p>© 2026 TalentForge AI. All rights reserved.</p>
                                </div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return send_email(subject, email, html)


# ============================================================
# VERIFICATION EMAILS (Recruiter Approved/Rejected)
# ============================================================

def send_verification_approved_email(recruiter):
    """Send verification approved email to recruiter"""
    from models import User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    user = db.session.get(User, recruiter.user_id)

    subject = "✅ Your Recruiter Account Has Been Verified!"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #4CAF50; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .success {{ background: #e8f5e9; padding: 16px; border-radius: 12px; border-left: 4px solid #4CAF50; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <div class="success">
                <h2 style="color: #2e7d32; margin: 0;">✅ Your Account is Verified!</h2>
            </div>
            <p style="color: #555;">Dear {recruiter.company_name},</p>
            <p style="color: #555;">Your recruiter account has been verified. You now have full access!</p>
            {create_clickable_button('🎯 Go to Recruiter Dashboard', f'{base_url}/recruiter/dashboard')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


def send_verification_rejected_email(recruiter):
    """Send verification rejected email to recruiter"""
    from models import User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    user = db.session.get(User, recruiter.user_id)

    subject = "❌ Recruiter Verification Update"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #f44336; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .rejected {{ background: #ffebee; padding: 16px; border-radius: 12px; border-left: 4px solid #f44336; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <div class="rejected">
                <h2 style="color: #c62828; margin: 0;">❌ Verification Not Approved</h2>
            </div>
            <p style="color: #555;">Dear {recruiter.company_name},</p>
            <p style="color: #555;">Unfortunately your verification request could not be approved at this time.</p>
            <div style="background: #ffebee; padding: 16px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 0; font-weight: 600; color: #c62828;">Reason:</p>
                <p style="margin: 4px 0; color: #555;">{recruiter.rejection_reason or 'Please contact support for more details.'}</p>
            </div>
            {create_clickable_button('🔄 Submit New Request', f'{base_url}/recruiter/verification')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


# ============================================================
# JOB APPLICATION EMAILS
# ============================================================

def send_new_application_email(application, job):
    """Send new application notification to recruiter"""
    from models import RecruiterProfile, User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    recruiter = db.session.get(RecruiterProfile, job.recruiter_id)
    user = db.session.get(User, recruiter.user_id)

    subject = f"📝 New Application for {job.title}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <h2>📝 New Job Application</h2>
            <p>A new candidate has applied for: <strong>{job.title}</strong></p>
            <div style="background: #e3f2fd; padding: 16px; border-radius: 12px;">
                <p style="margin: 0;"><strong>👤 Applicant:</strong> {application.applicant_name}</p>
                <p style="margin: 4px 0;"><strong>📧 Email:</strong> {application.applicant_email}</p>
                <p style="margin: 4px 0;"><strong>📅 Applied:</strong> {application.applied_at.strftime('%B %d, %Y')}</p>
            </div>
            {create_clickable_button('📋 View Applications', f'{base_url}/jobs/recruiter/applications')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


def send_application_status_update_email(application):
    """Send application status update to candidate"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    subject = f"📋 Application Status Update - {application.job.title}"

    status_colors = {
        'pending': '#ff9800',
        'reviewed': '#2196f3',
        'shortlisted': '#9c27b0',
        'hired': '#4CAF50',
        'rejected': '#f44336'
    }

    color = status_colors.get(application.status, '#666')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <h2>📋 Status Update</h2>
            <p>Dear {application.applicant_name},</p>
            <p>Your application for <strong>{application.job.title}</strong> has been updated:</p>
            <div style="background: {color}10; padding: 20px; border-radius: 12px; text-align: center; border: 2px solid {color};">
                <p style="margin: 0; font-size: 24px; font-weight: 700; color: {color};">
                    {application.status.upper()}
                </p>
            </div>
            {create_clickable_button('🔍 View Job Details', f'{base_url}/jobs/{application.job_id}')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, application.applicant_email, html)


# ============================================================
# JOB PUBLISHED EMAIL
# ============================================================

def send_job_published_email(job):
    """Send job published confirmation to recruiter"""
    from models import RecruiterProfile, User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    recruiter = db.session.get(RecruiterProfile, job.recruiter_id)
    user = db.session.get(User, recruiter.user_id)

    subject = f"✅ Job Published: {job.title}"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #4CAF50; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <h2>✅ Job Published Successfully!</h2>
            <p>Dear {recruiter.company_name},</p>
            <p>Your job posting is now live on the TalentForge AI job board!</p>
            <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 0; font-weight: 600;">📌 Job Details:</p>
                <p style="margin: 4px 0; color: #555;">Title: {job.title}</p>
                <p style="margin: 4px 0; color: #555;">Location: {job.location or 'Remote'}</p>
                <p style="margin: 4px 0; color: #555;">Posted: {job.posted_at.strftime('%B %d, %Y at %I:%M %p') if job.posted_at else 'Today'}</p>
            </div>
            {create_clickable_button('🔍 View Your Job', f'{base_url}/jobs/{job.id}')}
            <br><br>
            <p style="text-align: center;">
                {create_clickable_text_link('✏️ Edit Job Posting', f'{base_url}/recruiter/jobs/{job.id}/edit')}
            </p>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


# ============================================================
# CANDIDATE MATCH EMAIL
# ============================================================

def send_candidate_match_email(recruiter, candidate, job=None):
    """Send candidate match alert to recruiter"""
    from models import User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    user = db.session.get(User, recruiter.user_id)

    subject = "🎯 New Candidate Match Found!"

    job_text = f" for {job.title}" if job else ""

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <h2>🎯 New Candidate Match Found!</h2>
            <p>Dear {recruiter.company_name},</p>
            <p>Our AI has found a promising candidate that matches your requirements{job_text}!</p>
            <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 0; font-weight: 600;">👤 Candidate Profile:</p>
                <p style="margin: 4px 0; color: #555;">Name: {candidate.name}</p>
                <p style="margin: 4px 0; color: #555;">Email: {candidate.email}</p>
                <p style="margin: 4px 0; color: #555;">Skills: {', '.join(candidate.skills[:5]) if candidate.skills else 'N/A'}</p>
                <p style="margin: 4px 0; color: #555;">Experience: {candidate.experience_years or 0} years</p>
            </div>
            {create_clickable_button('👤 View Candidate Profile', f'{base_url}/recruiter/candidates/{candidate.id}')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    send_email(subject, user.email, html)


# ============================================================
# ALERT TEST — no matches
# ============================================================

def send_alert_test_no_matches_email(user, alert):
    """Send a confirmation email when a job-alert test finds no matches."""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    subject = f"✅ Alert Test: '{alert.keywords}' — No Matches Yet"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .success-box {{ background: #f0fdf4; padding: 20px; border-radius: 12px; border-left: 4px solid #10b981; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
            </div>
            <h2>✅ Your Alert Test Worked!</h2>
            <div class="success-box">
                <p style="margin: 0; color: #065f46; font-weight: 600;">📬 Email delivery is working!</p>
                <p style="margin: 4px 0; color: #065f46; font-size: 14px;">No matching jobs in the last 7 days yet.</p>
            </div>
            <div style="background: #f8fafc; padding: 16px; border-radius: 12px; margin: 20px 0;">
                <p style="margin: 0; font-weight: 600;">📋 Alert Details</p>
                <p style="margin: 4px 0; color: #555;">Keywords: {alert.keywords}</p>
                <p style="margin: 4px 0; color: #555;">Location: {alert.location or 'Any'}</p>
                <p style="margin: 4px 0; color: #555;">Frequency: {alert.frequency.title() if alert.frequency else 'Daily'}</p>
            </div>
            {create_clickable_button('🔔 Manage Alerts', f'{base_url}/job-alerts')}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(subject, user.email, html)


# ============================================================
# NEWSLETTER EMAILS
# ============================================================

def send_welcome_newsletter_email(email, name=None):
    """Send welcome email to new newsletter subscriber."""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    display_name = name or "there"

    subject = "Welcome to TalentForge AI Newsletter 🎉"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
                <p class="tagline">Africa's Talent Intelligence Platform</p>
            </div>
            <h2>Welcome, {display_name}! 🎉</h2>
            <p style="color: #555; line-height: 1.6;">
                Thanks for subscribing to the TalentForge AI newsletter! You'll be the first to hear about:
            </p>
            <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                <ul style="color: #555; padding-left: 20px; margin: 0;">
                    <li style="margin-bottom: 8px;">📊 New job market insights for Africa</li>
                    <li style="margin-bottom: 8px;">🚀 Feature updates and improvements</li>
                    <li style="margin-bottom: 8px;">💡 Career tips and learning resources</li>
                    <li>🎯 Job opportunities matching your skills</li>
                </ul>
            </div>
            <p style="color: #555; line-height: 1.6;">
                We typically send one update per week — no spam, ever.
            </p>
            {create_clickable_button('🚀 Visit TalentForge', base_url)}
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
                <p>Ghana · West Africa</p>
                <p style="margin-top: 8px;">
                    <a href="{base_url}/newsletter/unsubscribe?email={email}"
                       style="color: #999; text-decoration: underline;">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(subject, email, html)


def send_newsletter_broadcast(subscriber_email, subject, html_content):
    """Send a newsletter to one subscriber.
    Called in a loop by the admin broadcast route.
    """
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')

    wrapped_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
                <p class="tagline">Africa's Talent Intelligence Platform</p>
            </div>
            <div class="content">
                {html_content}
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
                <p>Ghana · West Africa</p>
                <p style="margin-top: 8px;">
                    <a href="{base_url}/newsletter/unsubscribe?email={subscriber_email}"
                       style="color: #999; text-decoration: underline;">Unsubscribe</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(subject, subscriber_email, wrapped_html)