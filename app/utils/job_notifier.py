# app/utils/job_notifier.py
from flask import current_app, render_template
from flask_mail import Message
from extensions import db  # Remove mail from here
from models import User, Candidate, JobAlert, JobAlertLog
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Import mail from the app context when needed
def get_mail():
    """Get mail instance from current app"""
    from flask import current_app
    return current_app.extensions.get('mail')


def notify_candidates_about_job(job):
    """Notify candidates who match a new job posting"""
    try:
        # Get all candidates with skills
        candidates = Candidate.query.filter(
            Candidate.is_processed == True,
            Candidate.skills.isnot(None)
        ).all()
        
        if not candidates:
            logger.info(f"No candidates found to notify for job {job.id}")
            return 0
        
        notifications_sent = 0
        
        for candidate in candidates:
            # Calculate match score
            match_score = calculate_match_score(candidate, job)
            
            # Only notify if match is above threshold (e.g., 50%)
            if match_score >= 50:
                user = User.query.get(candidate.user_id)
                if user and user.receive_notifications:
                    send_job_notification(user, job, candidate, match_score)
                    notifications_sent += 1
        
        # Also check Job Alerts
        alert_notifications = check_job_alerts_for_job(job)
        notifications_sent += alert_notifications
        
        logger.info(f"✅ Sent {notifications_sent} notifications for job {job.id}")
        return notifications_sent
        
    except Exception as e:
        logger.error(f"Error notifying candidates for job {job.id}: {e}")
        return 0


def calculate_match_score(candidate, job):
    """Calculate how well a candidate matches a job"""
    if not candidate.skills:
        return 0
    
    candidate_skills = set(candidate.skills or [])
    job_skills = set(job.required_skills or [])
    
    if not job_skills:
        return 70  # Default if no skills specified
    
    # Calculate match percentage
    matched_skills = candidate_skills & job_skills
    match_score = (len(matched_skills) / len(job_skills)) * 100
    
    # Add bonus for experience
    if candidate.experience_years and job.experience_level:
        experience_bonus = 0
        if job.experience_level == 'entry' and candidate.experience_years >= 1:
            experience_bonus = 10
        elif job.experience_level == 'mid' and candidate.experience_years >= 3:
            experience_bonus = 15
        elif job.experience_level == 'senior' and candidate.experience_years >= 5:
            experience_bonus = 20
        
        match_score = min(100, match_score + experience_bonus)
    
    return min(100, match_score)


def check_job_alerts_for_job(job):
    """Check if any job alerts match this job"""
    alerts = JobAlert.query.filter_by(is_active=True).all()
    notifications_sent = 0
    
    for alert in alerts:
        if alert.matches_job(job):
            user = User.query.get(alert.user_id)
            if user and user.receive_notifications:
                send_alert_notification(user, alert, job)
                notifications_sent += 1
                
                # Update alert last_sent_at
                alert.last_sent_at = datetime.utcnow()
                db.session.commit()
    
    return notifications_sent


def send_alert_notification(user, alert, job):
    """Send notification for a job alert match"""
    try:
        subject = f"🔔 Job Alert Match: {job.title}"
        
        html_body = render_template(
            'email/job_alert_match.html',
            user=user,
            alert=alert,
            job=job
        )
        
        # Get mail from current app
        mail = current_app.extensions.get('mail')
        if not mail:
            logger.error("Mail extension not initialized")
            return False
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        mail.send(msg)
        return True
        
    except Exception as e:
        logger.error(f"Alert email error for {user.email}: {e}")
        return False


def send_job_notification(user, job, candidate, match_score):
    """Send job notification to a user based on their preferences"""
    results = []
    
    # Email notification
    if user.email_notifications and user.email:
        email_result = send_job_notification_email(user, job, candidate, match_score)
        results.append(('email', email_result))
    
    # SMS notification
    if user.sms_notifications and user.phone:
        sms_result = send_job_notification_sms(user, job, candidate, match_score)
        results.append(('sms', sms_result))
    
    # Log the notification
    try:
        log = JobAlertLog(
            alert_id=None,
            job_id=job.id,
            sent_at=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error logging notification: {e}")
    
    return results


def send_job_notification_email(user, job, candidate, match_score):
    """Send email notification to a candidate about a new job"""
    try:
        subject = f"🎯 New Job Match: {job.title}"
        
        html_body = render_template(
            'email/job_match_notification.html',
            user=user,
            job=job,
            candidate=candidate,
            match_score=match_score
        )
        
        # Get mail from current app
        mail = current_app.extensions.get('mail')
        if not mail:
            logger.error("Mail extension not initialized")
            return False
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        
        mail.send(msg)
        logger.info(f"📧 Email sent to {user.email} for job {job.id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Email error for {user.email}: {e}")
        return False


def send_job_notification_sms(user, job, candidate, match_score):
    """Send SMS notification to a candidate about a new job"""
    try:
        if not user.phone:
            return False
        
        # Format phone number
        phone = user.phone.strip()
        if not phone.startswith('+'):
            if phone.startswith('0'):
                phone = '+233' + phone[1:]
            else:
                phone = '+233' + phone
        
        # Build SMS message (160 char limit)
        message = f"🎯 New job match! {job.title} ({int(match_score)}% match). View now: https://fadtechlabs.com/jobs/{job.id}"
        
        if len(message) > 160:
            message = message[:157] + '...'
        
        # Try Twilio
        if current_app.config.get('TWILIO_ACCOUNT_SID'):
            from app.utils.notification_service import NotificationService
            result = NotificationService._send_twilio_sms(phone, message)
            logger.info(f"📱 SMS sent to {phone} via Twilio")
            return result
        
        # Try Africa's Talking
        elif current_app.config.get('AFRICA_TALKING_API_KEY'):
            from app.utils.notification_service import NotificationService
            result = NotificationService._send_africastalking_sms(phone, message)
            logger.info(f"📱 SMS sent to {phone} via Africa's Talking")
            return result
        
        else:
            logger.warning("No SMS provider configured")
            return False
            
    except Exception as e:
        logger.error(f"❌ SMS error for {user.phone}: {e}")
        return False