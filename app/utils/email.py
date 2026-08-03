# app/utils/email.py
from flask import current_app, render_template, url_for
from flask_mail import Message
from threading import Thread
import os
import logging
import requests

# Set up logging
logger = logging.getLogger(__name__)

# We'll use the mail instance from the app
def send_async_email(app, subject, recipients, html_body, sender):
    """Send email asynchronously via SendGrid API"""
    with app.app_context():
        try:
            print(f"📧 Sending email to: {recipients}")

            api_key = app.config.get('SENDGRID_API_KEY')
            if not api_key:
                print("❌ SENDGRID_API_KEY not set")
                logger.error("SENDGRID_API_KEY not configured")
                return

            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "personalizations": [
                        {"to": [{"email": r} for r in recipients]}
                    ],
                    "from": {"email": sender},
                    "subject": subject,
                    "content": [{"type": "text/html", "value": html_body}],
                },
                timeout=10,
            )

            if response.status_code in (200, 201, 202):
                print(f"✅ Email sent successfully to {recipients}")
            else:
                print(f"❌ SendGrid error {response.status_code}: {response.text}")
                logger.error(f"SendGrid error {response.status_code}: {response.text}")

        except Exception as e:
            print(f"❌ Error sending email: {e}")
            logger.error(f"Email error: {e}")


def send_email(subject, recipients, html_body, text_body=None, sender=None):
    """Send an email via SendGrid (async, non-blocking)"""
    try:
        app = current_app._get_current_object()
        recipients_list = recipients if isinstance(recipients, list) else [recipients]
        sender_email = sender or app.config.get('MAIL_DEFAULT_SENDER', 'fadtechlabs.com@gmail.com')

        print(f"📧 Preparing email: {subject}")
        print(f"📧 Recipients: {recipients_list}")
        print(f"📧 From: {sender_email}")

        Thread(
            target=send_async_email,
            args=(app, subject, recipients_list, html_body, sender_email)
        ).start()

        print(f"📧 Email thread started for {recipients_list}")
        return True
    except Exception as e:
        print(f"❌ Failed to prepare email: {e}")
        logger.error(f"Send email error: {e}")
        return False


# ============================================
# EMAIL TEMPLATES
# ============================================

# ========== EMAIL VERIFICATION ==========

def send_verification_email(email, token, fullname):
    """Send email verification link to new user"""
    # Get base URL from config
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    verification_url = f"{base_url}/auth/verify/{token}"
    
    subject = "✅ Verify Your Email - TalentForge AI"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 14px 35px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .btn:hover {{ opacity: 0.9; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
            .token-box {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; word-break: break-all; font-size: 12px; }}
            .warning {{ background: #fef3c7; padding: 16px; border-radius: 12px; border-left: 4px solid #f59e0b; }}
        </style>
    </head>
    <body>
        <div class="container">
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
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" class="btn">Verify Email Address</a>
                </div>
                
                <p style="color: #718096; font-size: 14px; text-align: center;">
                    Or copy and paste this link into your browser:
                </p>
                
                <div class="token-box">
                    {verification_url}
                </div>
                
                <div class="warning">
                    <p style="margin: 0; color: #92400e; font-size: 14px;">
                        ⚠️ This link expires in <strong>7 days</strong>.
                    </p>
                </div>
                
                <p style="color: #999; font-size: 12px; margin-top: 20px;">
                    If you didn't create an account, you can safely ignore this email.
                </p>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
                <p>Ghana · West Africa</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(subject, email, html)


# ========== WELCOME EMAIL ==========

def send_welcome_email(user):
    """Send welcome email to new user"""
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    
    subject = "Welcome to TalentForge AI! 🚀"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <h2 style="color: #2c3e50;">Welcome, {user.fullname}! 👋</h2>
                <p style="color: #555; line-height: 1.6;">Thank you for joining TalentForge AI! We're excited to help you on your career journey.</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">Your Account Details:</p>
                    <p style="margin: 4px 0; color: #555;">Email: {user.email}</p>
                    <p style="margin: 4px 0; color: #555;">Account Type: {user.user_type.title()}</p>
                </div>
                
                <div style="background: #e8f5e9; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; color: #2e7d32;">🎯 Get started by uploading your CV to receive your personalized skill analysis!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/dashboard" class="btn">Go to Dashboard</a>
                </div>
                
                <p style="color: #555; font-size: 14px;">Need help? Reply to this email or visit our <a href="{base_url}" style="color: #6366f1;">support page</a>.</p>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
                <p>Building Africa's talent intelligence infrastructure.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_verification_approved_email(recruiter):
    """Send verification approved email to recruiter"""
    from models import User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    user = User.query.get(recruiter.user_id)
    
    subject = "✅ Your Recruiter Account Has Been Verified!"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #4CAF50; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .success {{ background: #e8f5e9; padding: 16px; border-radius: 12px; border-left: 4px solid #4CAF50; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <div class="success">
                    <h2 style="color: #2e7d32; margin: 0;">✅ Your Account is Verified!</h2>
                </div>
                
                <p style="color: #555; line-height: 1.6; margin-top: 20px;">Dear {recruiter.company_name},</p>
                <p style="color: #555; line-height: 1.6;">Your recruiter account has been verified and approved by our team. You now have full access to all recruiter features!</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">🎉 What you can do now:</p>
                    <ul style="color: #555; padding-left: 20px;">
                        <li>Post unlimited job vacancies</li>
                        <li>Search and view candidate profiles</li>
                        <li>Flag candidates for your jobs</li>
                        <li>Track placements and applications</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/recruiter/dashboard" class="btn">Go to Recruiter Dashboard</a>
                </div>
            </div>
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
    user = User.query.get(recruiter.user_id)
    
    subject = "❌ Recruiter Verification Update"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #f44336; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .rejected {{ background: #ffebee; padding: 16px; border-radius: 12px; border-left: 4px solid #f44336; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <div class="rejected">
                    <h2 style="color: #c62828; margin: 0;">❌ Verification Not Approved</h2>
                </div>
                
                <p style="color: #555; line-height: 1.6; margin-top: 20px;">Dear {recruiter.company_name},</p>
                <p style="color: #555; line-height: 1.6;">We regret to inform you that your recruiter verification request could not be approved at this time.</p>
                
                <div style="background: #ffebee; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600; color: #c62828;">Reason:</p>
                    <p style="margin: 4px 0; color: #555;">{recruiter.rejection_reason or 'Please contact support for more details.'}</p>
                </div>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">What you can do:</p>
                    <ul style="color: #555; padding-left: 20px;">
                        <li>Review the reason above</li>
                        <li>Upload updated verification documents</li>
                        <li>Contact our support team for assistance</li>
                        <li>Submit a new verification request</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/recruiter/verification" class="btn">Submit New Request</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_new_application_email(application, job):
    """Send new application notification to recruiter"""
    from models import RecruiterProfile, User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    recruiter = RecruiterProfile.query.get(job.recruiter_id)
    user = User.query.get(recruiter.user_id)
    
    subject = f"📝 New Application for {job.title}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <h2 style="color: #2c3e50;">📝 New Job Application</h2>
                
                <p style="color: #555; line-height: 1.6;">A new candidate has applied for the position:</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">{job.title}</p>
                    <p style="margin: 4px 0; color: #555;">Posted by: {recruiter.company_name}</p>
                </div>
                
                <div style="background: #e3f2fd; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">👤 Applicant Details:</p>
                    <p style="margin: 4px 0; color: #555;">Name: {application.applicant_name}</p>
                    <p style="margin: 4px 0; color: #555;">Email: {application.applicant_email}</p>
                    <p style="margin: 4px 0; color: #555;">Applied: {application.applied_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/jobs/recruiter/applications" class="btn">View All Applications</a>
                </div>
            </div>
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
    from models import RecruiterProfile, User
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
    
    # Get company name safely
    company_name = 'N/A'
    if application.job:
        if hasattr(application.job, 'recruiter') and application.job.recruiter:
            company_name = application.job.recruiter.company_name or 'N/A'
        elif hasattr(application.job, 'poster') and application.job.poster:
            if hasattr(application.job.poster, 'company_name'):
                company_name = application.job.poster.company_name or 'N/A'
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <h2 style="color: #2c3e50;">📋 Application Status Updated</h2>
                
                <p style="color: #555; line-height: 1.6;">Dear {application.applicant_name},</p>
                <p style="color: #555; line-height: 1.6;">Your application for <strong>{application.job.title}</strong> has been updated:</p>
                
                <div style="background: {color}10; padding: 20px; border-radius: 12px; text-align: center; margin: 20px 0; border: 2px solid {color};">
                    <p style="margin: 0; font-size: 24px; font-weight: 700; color: {color};">
                        {application.status.upper()}
                    </p>
                    <p style="margin: 4px 0; color: #555;">Status updated on {application.updated_at.strftime('%B %d, %Y')}</p>
                </div>
                
                <div style="background: #f8f6f0; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">📌 Application Details:</p>
                    <p style="margin: 4px 0; color: #555;">Job: {application.job.title}</p>
                    <p style="margin: 4px 0; color: #555;">Company: {company_name}</p>
                    <p style="margin: 4px 0; color: #555;">Applied: {application.applied_at.strftime('%B %d, %Y')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/jobs/{application.job_id}" class="btn">View Job Details</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, application.applicant_email, html)


def send_job_published_email(job):
    """Send job published confirmation to recruiter"""
    from models import RecruiterProfile, User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    recruiter = RecruiterProfile.query.get(job.recruiter_id)
    user = User.query.get(recruiter.user_id)
    
    subject = f"✅ Job Published: {job.title}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #4CAF50; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <h2 style="color: #2c3e50;">✅ Job Published Successfully!</h2>
                
                <p style="color: #555; line-height: 1.6;">Dear {recruiter.company_name},</p>
                <p style="color: #555; line-height: 1.6;">Your job posting has been published and is now live on the TalentForge AI job board!</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">📌 Job Details:</p>
                    <p style="margin: 4px 0; color: #555;">Title: {job.title}</p>
                    <p style="margin: 4px 0; color: #555;">Location: {job.location or 'Remote'}</p>
                    <p style="margin: 4px 0; color: #555;">Type: {job.employment_type.value.replace('_', ' ').title() if job.employment_type else 'Full Time'}</p>
                    <p style="margin: 4px 0; color: #555;">Posted: {job.posted_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="background: #e8f5e9; padding: 16px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; color: #2e7d32;">🎯 Your job is now visible to thousands of job seekers!</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/jobs/{job.id}" class="btn">View Your Job</a>
                    <br><br>
                    <a href="{base_url}/recruiter/jobs/{job.id}/edit" style="color: #666; font-size: 14px;">Edit Job Posting</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_candidate_match_email(recruiter, candidate, job=None):
    """Send candidate match alert to recruiter"""
    from models import User
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    user = User.query.get(recruiter.user_id)
    
    subject = "🎯 New Candidate Match Found!"
    
    job_text = f" for {job.title}" if job else ""
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
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
                <h2 style="color: #2c3e50;">🎯 New Candidate Match Found!</h2>
                
                <p style="color: #555; line-height: 1.6;">Dear {recruiter.company_name},</p>
                <p style="color: #555; line-height: 1.6;">Our AI has found a promising candidate that matches your requirements{job_text}!</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">👤 Candidate Profile:</p>
                    <p style="margin: 4px 0; color: #555;">Name: {candidate.name}</p>
                    <p style="margin: 4px 0; color: #555;">Email: {candidate.email}</p>
                    <p style="margin: 4px 0; color: #555;">Skills: {', '.join(candidate.skills[:5]) if candidate.skills else 'N/A'}</p>
                    <p style="margin: 4px 0; color: #555;">Experience: {candidate.experience_years or 0} years</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{base_url}/recruiter/candidates/{candidate.id}" class="btn">View Candidate Profile</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


# ============================================
# PASSWORD RESET EMAIL
# ============================================

def send_password_reset_email(user, token):
    """Send password reset email to user"""
    print(f"📧 ===== SENDING PASSWORD RESET EMAIL =====")
    print(f"📧 User: {user.email}")
    print(f"📧 Token: {token[:20]}...")
    
    subject = "🔐 Reset Your Password - TalentForge AI"
    
    # Get base URL from config
    base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
    reset_url = f"{base_url}/auth/reset-password/{token}"
    
    print(f"📧 Reset URL: {reset_url}")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #6366f1; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #6366f1; }}
            .tagline {{ color: #10b981; font-size: 14px; font-weight: 500; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #6366f1, #10b981); color: white; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .btn:hover {{ opacity: 0.9; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
            .token-box {{ background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0; word-break: break-all; font-size: 12px; }}
            .warning {{ background: #fef3c7; padding: 16px; border-radius: 12px; border-left: 4px solid #f59e0b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">TalentForge <span>AI</span></div>
                <p class="tagline">Africa's Talent Intelligence Platform</p>
            </div>
            <div class="content">
                <h2 style="color: #2c3e50;">🔐 Reset Your Password</h2>
                
                <p style="color: #555; line-height: 1.6;">Hi {user.fullname},</p>
                
                <p style="color: #555; line-height: 1.6;">
                    We received a request to reset your password for your TalentForge AI account.
                    Click the button below to set a new password:
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" class="btn">Reset Password</a>
                </div>
                
                <p style="color: #718096; font-size: 14px; text-align: center;">
                    Or copy and paste this link into your browser:
                </p>
                
                <div class="token-box">
                    {reset_url}
                </div>
                
                <div class="warning">
                    <p style="margin: 0; color: #92400e; font-size: 14px;">
                        ⚠️ This link will expire in <strong>24 hours</strong>.
                    </p>
                </div>
                
                <p style="color: #718096; font-size: 14px; margin-top: 20px;">
                    If you didn't request this, please ignore this email and your password will remain unchanged.
                </p>
                
                <div style="margin: 20px 0; padding: 15px; background: #ebf8ff; border-radius: 5px;">
                    <p style="color: #2b6cb0; font-size: 12px; margin: 0;">
                        <strong>🔒 Security Tip:</strong> Never share this link with anyone.
                    </p>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 TalentForge AI. All rights reserved.</p>
                <p>Ghana · West Africa</p>
                <p style="margin-top: 4px;">
                    <a href="{base_url}" style="color: #6366f1; text-decoration: none;">Visit our website</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    print(f"📧 HTML email built, sending...")
    result = send_email(subject, user.email, html)
    print(f"📧 Send result: {result}")
    return result