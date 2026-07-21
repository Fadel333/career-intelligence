# app/utils/job_alert_checker.py
from datetime import datetime, timedelta
from flask import current_app
from extensions import db
from models import JobAlert, Job, User, JobAlertLog
from app.utils.notification_service import NotificationService

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
                continue
            
            # Check if user wants notifications
            if not user.receive_notifications:
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
                # Determine notification methods based on user preferences
                methods = ['email']
                if user.phone and user.sms_notifications:
                    methods.append('sms')
                
                # Send notifications
                results = NotificationService.send_job_alert(
                    user, alert, matching_jobs, methods
                )
                
                # Log results
                log = JobAlertLog(
                    alert_id=alert.id,
                    user_id=user.id,
                    jobs_found=len(matching_jobs),
                    sent_at=datetime.utcnow(),
                    status='sent' if any(results.values()) else 'failed',
                    email_sent=results.get('email', False),
                    sms_sent=results.get('sms', False),
                    error_message=None
                )
                db.session.add(log)
                
                # Update last sent time
                alert.last_sent_at = datetime.utcnow()
                db.session.commit()
                
                notifications_sent += 1
                print(f"✅ Sent alert to {user.email} ({len(matching_jobs)} jobs)")
            
        except Exception as e:
            errors += 1
            print(f"⚠️ Error processing alert {alert.id}: {e}")
    
    print(f"📊 Summary: {notifications_sent} notifications sent, {errors} errors")
    return notifications_sent, errors


def calculate_match_score(alert, job):
    """Calculate how well a job matches an alert"""
    score = 0
    max_score = 0
    
    # Keywords match (weight: 50%)
    if alert.keywords:
        max_score += 50
        keywords = alert.keywords.lower().split()
        job_text = f"{job.title} {job.description or ''} {job.company}".lower()
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
        if alert.job_type.lower() in job.employment_type.lower():
            score += 20
    
    # Category match (weight: 10%)
    if alert.category and job.category:
        max_score += 10
        if alert.category.lower() in job.category.lower():
            score += 10
    
    # Calculate percentage
    return round((score / max_score) * 100) if max_score > 0 else 0