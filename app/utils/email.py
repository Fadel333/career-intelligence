# app/utils/email.py
from flask import current_app, render_template
from flask_mail import Message
from threading import Thread
import os

# We'll use the mail instance from the app
def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        # Get mail instance from app
        mail = app.extensions.get('mail')
        if mail:
            mail.send(msg)
        else:
            # Fallback: try to send directly
            from flask_mail import Mail
            mail = Mail(app)
            mail.send(msg)

def send_email(subject, recipients, html_body, text_body=None, sender=None):
    """Send an email"""
    app = current_app._get_current_object()
    
    msg = Message(
        subject=subject,
        recipients=recipients if isinstance(recipients, list) else [recipients],
        html=html_body,
        body=text_body,
        sender=sender or app.config.get('MAIL_DEFAULT_SENDER', 'noreply@fadtechlabs.com')
    )
    
    # Send in background
    Thread(target=send_async_email, args=(app, msg)).start()
    return True


# ============================================
# EMAIL TEMPLATES
# ============================================

def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = "Welcome to FADTECH Labs! 🚀"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #ffd700; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
            </div>
            <div class="content">
                <h2 style="color: #2c3e50;">Welcome, {user.fullname}! 👋</h2>
                <p style="color: #555; line-height: 1.6;">Thank you for joining FADTECH Labs! We're excited to help you on your career journey.</p>
                
                <div style="background: #f8f6f0; padding: 20px; border-radius: 12px; margin: 20px 0;">
                    <p style="margin: 0; font-weight: 600;">Your Account Details:</p>
                    <p style="margin: 4px 0; color: #555;">Email: {user.email}</p>
                    <p style="margin: 4px 0; color: #555;">Account Type: {user.user_type.title()}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000/dashboard" class="btn">Go to Dashboard</a>
                </div>
                
                <p style="color: #555; font-size: 14px;">Need help? Reply to this email or visit our <a href="http://localhost:5000" style="color: #ffd700;">support page</a>.</p>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
                <p>Building Africa's employability intelligence infrastructure.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_verification_approved_email(recruiter):
    """Send verification approved email to recruiter"""
    from models import User
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
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .success {{ background: #e8f5e9; padding: 16px; border-radius: 12px; border-left: 4px solid #4CAF50; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
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
                    <a href="http://localhost:5000/recruiter/dashboard" class="btn">Go to Recruiter Dashboard</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_verification_rejected_email(recruiter):
    """Send verification rejected email to recruiter"""
    from models import User
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
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .rejected {{ background: #ffebee; padding: 16px; border-radius: 12px; border-left: 4px solid #f44336; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
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
                    <a href="http://localhost:5000/recruiter/verification" class="btn">Submit New Request</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_new_application_email(application, job):
    """Send new application notification to recruiter"""
    from models import RecruiterProfile, User
    recruiter = RecruiterProfile.query.get(job.recruiter_id)
    user = User.query.get(recruiter.user_id)
    
    subject = f"📝 New Application for {job.title}"
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #4CAF50; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
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
                    <a href="http://localhost:5000/jobs/recruiter/applications" class="btn">View All Applications</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_application_status_update_email(application):
    """Send application status update to candidate"""
    from models import RecruiterProfile, User
    
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
        # Try to get company name from recruiter relationship
        if hasattr(application.job, 'recruiter') and application.job.recruiter:
            company_name = application.job.recruiter.company_name or 'N/A'
        # Or try to get it from the user who posted the job
        elif hasattr(application.job, 'poster') and application.job.poster:
            if hasattr(application.job.poster, 'company_name'):
                company_name = application.job.poster.company_name or 'N/A'
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #ffd700; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
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
                    <a href="http://localhost:5000/jobs/{application.job_id}" class="btn">View Job Details</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, application.applicant_email, html)

def send_job_published_email(job):
    """Send job published confirmation to recruiter"""
    from models import RecruiterProfile, User
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
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
            </div>
            <div class="content">
                <h2 style="color: #2c3e50;">✅ Job Published Successfully!</h2>
                
                <p style="color: #555; line-height: 1.6;">Dear {recruiter.company_name},</p>
                <p style="color: #555; line-height: 1.6;">Your job posting has been published and is now live on the FADTECH Labs job board!</p>
                
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
                    <a href="http://localhost:5000/jobs/{job.id}" class="btn">View Your Job</a>
                    <br><br>
                    <a href="http://localhost:5000/recruiter/jobs/{job.id}/edit" style="color: #666; font-size: 14px;">Edit Job Posting</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)


def send_candidate_match_email(recruiter, candidate, job=None):
    """Send candidate match alert to recruiter"""
    from models import User
    user = User.query.get(recruiter.user_id)
    
    subject = "🎯 New Candidate Match Found!"
    
    job_text = f" for {job.title}" if job else ""
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background: #f8f6f0; color: #2c3e50; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); }}
            .header {{ text-align: center; padding-bottom: 20px; border-bottom: 2px solid #ffd700; }}
            .logo {{ font-size: 28px; font-weight: 800; color: #2c3e50; }}
            .logo span {{ color: #ffd700; }}
            .content {{ padding: 30px 0; }}
            .btn {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #ffd700, #f0a500); color: #0a0a0a; text-decoration: none; border-radius: 50px; font-weight: 600; }}
            .footer {{ text-align: center; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">FADTECH <span>Labs</span></div>
                <p style="color: #666; margin-top: 4px;">Career Intelligence System</p>
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
                    <a href="http://localhost:5000/recruiter/candidates/{candidate.id}" class="btn">View Candidate Profile</a>
                </div>
            </div>
            <div class="footer">
                <p>© 2026 FADTECH Labs. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    send_email(subject, user.email, html)