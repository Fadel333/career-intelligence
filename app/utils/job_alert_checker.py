# app/utils/job_alert_checker.py
from datetime import datetime, timedelta
from flask import current_app, url_for
from extensions import db
from models import JobAlert, Job, User, JobAlertLog
from app.utils.email import send_email
import logging

logger = logging.getLogger(__name__)

def check_job_alerts():
    """Check all active job alerts and send notifications"""
    print("🔍 Checking for new jobs matching alerts...")
    
    alerts = JobAlert.query.filter_by(is_active=True).all()
    print(f"📊 Found {len(alerts)} active alerts")
    
    notifications_sent = 0
    errors = 0
    
    for alert in alerts:
        try:
            user = User.query.get(alert.user_id)
            if not user:
                print(f"⚠️ User {alert.user_id} not found for alert {alert.id}")
                continue
            
            # Check if user wants notifications
            if not user.receive_notifications:
                print(f"ℹ️ User {user.id} has notifications disabled")
                continue
            
            last_check = alert.last_sent_at or datetime.utcnow() - timedelta(days=7)
            
            # Get new jobs
            new_jobs = Job.query.filter(
                Job.status == 'published',
                Job.posted_at > last_check
            ).all()
            
            # Find matching jobs
            matching_jobs = []
            for job in new_jobs:
                if alert.matches_job(job):
                    score = calculate_match_score(alert, job)
                    job.match_score = score
                    matching_jobs.append(job)
            
            if matching_jobs:
                # Send email notification
                success = send_job_alert_notification(alert, matching_jobs)
                
                if success:
                    notifications_sent += 1
                    print(f"✅ Sent alert to {user.email} ({len(matching_jobs)} jobs)")
                else:
                    errors += 1
                    print(f"❌ Failed to send alert to {user.email}")
            else:
                print(f"ℹ️ No new matches for alert {alert.id}")
            
        except Exception as e:
            errors += 1
            print(f"⚠️ Error processing alert {alert.id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"📊 Summary: {notifications_sent} notifications sent, {errors} errors")
    return notifications_sent, errors


def calculate_match_score(alert, job):
    """Calculate how well a job matches an alert"""
    score = 0
    max_score = 0
    
    # Keywords match (weight: 50%)
    if alert.keywords:
        max_score += 50
        keywords = [k.strip() for k in alert.keywords.lower().split(',') if k.strip()]
        job_text = f"{job.title} {job.description or ''}".lower()
        matched = sum(1 for kw in keywords if kw in job_text)
        if keywords:
            score += (matched / len(keywords)) * 50
    
    # Location match (weight: 20%)
    if alert.location and job.location:
        max_score += 20
        if alert.location.lower() in job.location.lower():
            score += 20
    
    # Job type match (weight: 20%)
    if alert.job_type and job.employment_type:
        max_score += 20
        if alert.job_type.lower() in job.employment_type.value.lower():
            score += 20
    
    # Category match (weight: 10%)
    if alert.category and job.category:
        max_score += 10
        if alert.category.lower() in job.category.lower():
            score += 10
    
    # Calculate percentage
    return round((score / max_score) * 100) if max_score > 0 else 0


def find_matching_jobs(alert, since=None):
    """
    Find jobs that match a specific alert
    
    Args:
        alert: JobAlert object
        since: datetime to search from (default: 7 days ago)
    
    Returns:
        List of matching Job objects with match_score attribute
    """
    if since is None:
        since = datetime.utcnow() - timedelta(days=7)
    
    print(f"🔍 find_matching_jobs: Looking for jobs since {since}")
    
    # Get jobs published after the given date
    new_jobs = Job.query.filter(
        Job.status == 'published',
        Job.posted_at > since
    ).all()
    
    print(f"📊 Found {len(new_jobs)} published jobs since {since}")
    
    # Filter matching jobs
    matching_jobs = []
    for job in new_jobs:
        if alert.matches_job(job):
            score = calculate_match_score(alert, job)
            job.match_score = score
            matching_jobs.append(job)
            print(f"✅ Job '{job.title}' matches with score {score}%")
    
    # Sort by match score (highest first)
    matching_jobs.sort(key=lambda x: getattr(x, 'match_score', 0), reverse=True)
    
    print(f"📊 Found {len(matching_jobs)} matching jobs")
    return matching_jobs


def send_job_alert_notification(alert, jobs):
    """
    Send notification for matching jobs using SendGrid
    
    Args:
        alert: JobAlert object
        jobs: List of matching Job objects
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"📧 send_job_alert_notification called with {len(jobs)} jobs")
    
    if not jobs:
        print("❌ No jobs to send")
        return False
    
    user = User.query.get(alert.user_id)
    if not user:
        print(f"❌ User {alert.user_id} not found")
        return False
    
    print(f"📧 User found: {user.email}, receive_notifications={user.receive_notifications}")
    
    if not user.email:
        print(f"❌ User {user.id} has no email address")
        return False
    
    try:
        # Build email content
        job_listings = []
        for job in jobs[:10]:  # Limit to 10 jobs per email
            company_name = job.recruiter.company_name if job.recruiter else 'Unknown Company'
            salary_range = f"${job.salary_min:,.0f} - ${job.salary_max:,.0f}" if job.salary_min and job.salary_max else 'Salary not specified'
            
            job_listings.append({
                'title': job.title,
                'company': company_name,
                'location': job.location or 'Remote',
                'salary': salary_range,
                'url': f"https://career-intelligence-3.onrender.com/jobs/{job.id}",
                'posted_at': job.posted_at.strftime('%B %d, %Y'),
                'match_score': getattr(job, 'match_score', 0)
            })
        
        # Create HTML email content
        html_content = build_job_alert_html(alert, job_listings, len(jobs))
        plain_text = build_job_alert_text(alert, job_listings, len(jobs))
        
        # Send email using SendGrid via your email.py
        subject = f"🎯 {len(jobs)} New Job{'s' if len(jobs) > 1 else ''} Matching '{alert.keywords}'"
        
        print(f"📧 Calling send_email with subject: {subject}, to: {user.email}")
        
        result = send_email(
            subject=subject,
            recipients=user.email,
            html_body=html_content,
            text_body=plain_text
        )
        
        print(f"📧 send_email returned: {result}")
        
        if not result:
            print(f"❌ send_email returned False")
            return False
        
        # Log the notification
        log = JobAlertLog(
            alert_id=alert.id,
            user_id=user.id,
            jobs_found=len(jobs),
            sent_at=datetime.utcnow(),
            status='sent',
            email_sent=True,
            sms_sent=False,
            error_message=None
        )
        db.session.add(log)
        db.session.commit()
        
        print(f"✅ Email sent to {user.email} with {len(jobs)} jobs")
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def build_job_alert_html(alert, job_listings, total_jobs):
    """Build HTML email content for job alert"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }}
            .container {{ background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px 12px 0 0; text-align: center; margin: -30px -30px 30px -30px; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
            .header p {{ margin: 10px 0 0; opacity: 0.9; }}
            .job-card {{ border: 1px solid #e5e7eb; border-radius: 8px; padding: 20px; margin: 15px 0; background: white; }}
            .job-title {{ font-size: 18px; font-weight: 600; color: #1f2937; margin-bottom: 5px; }}
            .job-company {{ color: #6b7280; font-weight: 500; }}
            .match-score {{ display: inline-block; background: #10b981; color: white; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
            .job-details {{ margin: 10px 0; color: #6b7280; font-size: 14px; }}
            .job-details span {{ margin-right: 15px; }}
            .view-link {{ display: inline-block; background: #667eea; color: white; padding: 10px 24px; text-decoration: none; border-radius: 6px; font-weight: 500; margin-top: 10px; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 13px; text-align: center; }}
            .alert-info {{ background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎯 New Job Matches Found!</h1>
                <p>We found {total_jobs} new jobs matching your alert: <strong>"{alert.keywords}"</strong></p>
            </div>
            
            <div class="alert-info">
                <strong>📋 Alert Summary</strong><br>
                Keywords: {alert.keywords}<br>
                Location: {alert.location or 'Any'}<br>
                Frequency: {alert.frequency.title()}
            </div>
            
            <h3 style="margin: 25px 0 15px; color: #1f2937;">📋 Matching Jobs</h3>
            
            {''.join(f'''
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: start; flex-wrap: wrap;">
                    <div>
                        <div class="job-title">{job['title']}</div>
                        <div class="job-company">🏢 {job['company']}</div>
                    </div>
                    <span class="match-score">{job['match_score']}% Match</span>
                </div>
                <div class="job-details">
                    <span>📍 {job['location']}</span>
                    <span>💰 {job['salary']}</span>
                    <span>📅 {job['posted_at']}</span>
                </div>
                <a href="{job['url']}" class="view-link" target="_blank">View Job Details →</a>
            </div>
            ''' for job in job_listings)}
            
            {f'<p style="color: #6b7280; text-align: center; margin: 10px 0;">... and {total_jobs - 10} more jobs</p>' if total_jobs > 10 else ''}
            
            <div class="footer">
                <p style="margin: 5px 0;">
                    <strong>Manage your alerts:</strong>
                    <a href="https://career-intelligence-3.onrender.com/job-alerts">https://career-intelligence-3.onrender.com/job-alerts</a>
                </p>
                <p style="margin: 5px 0;">
                    You're receiving this because you have an active job alert on Career Intelligence.
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def build_job_alert_text(alert, job_listings, total_jobs):
    """Build plain text email content for job alert"""
    return f"""
    🎯 New Job Matches Found!
    
    We found {total_jobs} new jobs matching your alert: "{alert.keywords}"
    
    📋 Alert Summary:
    Keywords: {alert.keywords}
    Location: {alert.location or 'Any'}
    Frequency: {alert.frequency.title()}
    
    📋 Matching Jobs:
    {''.join(f'''
    {job['title']}
    Company: {job['company']}
    Location: {job['location']}
    Salary: {job['salary']}
    Match: {job['match_score']}%
    Posted: {job['posted_at']}
    View: {job['url']}
    {'-' * 50}
    ''' for job in job_listings)}
    
    {'... and ' + str(total_jobs - 10) + ' more jobs' if total_jobs > 10 else ''}
    
    Manage your alerts:
    https://career-intelligence-3.onrender.com/job-alerts
    """