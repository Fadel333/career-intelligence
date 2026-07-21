# app/utils/notification_service.py
import os
import logging
from flask import current_app, render_template
from flask_mail import Message
from extensions import mail

logger = logging.getLogger(__name__)

class NotificationService:
    """Handle email and SMS notifications"""
    
    @staticmethod
    def send_job_alert_email(user, alert, matching_jobs):
        """Send job alert email to user"""
        try:
            if not user.email:
                logger.warning(f"User {user.id} has no email address")
                return False
            
            subject = f"🔔 New Job Alert: {len(matching_jobs)} jobs matching your preferences"
            
            html_body = render_template('email/job_alert.html', 
                                       user=user, 
                                       alert=alert, 
                                       jobs=matching_jobs)
            
            msg = Message(
                subject=subject,
                recipients=[user.email],
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            mail.send(msg)
            logger.info(f"✅ Email sent to {user.email} with {len(matching_jobs)} jobs")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {user.email}: {e}")
            return False
    
    @staticmethod
    def send_job_alert_sms(user, alert, matching_jobs):
        """Send job alert SMS to user"""
        try:
            if not user.phone:
                logger.warning(f"User {user.id} has no phone number")
                return False
            
            # Format phone number (remove spaces, ensure +233 format)
            phone = user.phone.strip()
            if not phone.startswith('+'):
                # Assume Ghana number if no country code
                if phone.startswith('0'):
                    phone = '+233' + phone[1:]
                else:
                    phone = '+233' + phone
            
            # Get first 3 jobs for SMS (character limit)
            jobs_preview = matching_jobs[:3]
            job_titles = '\n'.join([f"• {j.title} at {j.company}" for j in jobs_preview])
            
            message = f"""🔔 New Job Alert!

Found {len(matching_jobs)} new job(s) matching "{alert.keywords or 'your skills'}"

{job_titles}

View all at: https://fadtechlabs.com/job-matches

Reply STOP to unsubscribe."""
            
            # Try Twilio first
            if current_app.config.get('TWILIO_ACCOUNT_SID'):
                return NotificationService._send_twilio_sms(phone, message)
            
            # Try Africa's Talking as fallback
            elif current_app.config.get('AFRICA_TALKING_API_KEY'):
                return NotificationService._send_africastalking_sms(phone, message)
            
            else:
                logger.warning("No SMS provider configured")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to send SMS to {user.phone}: {e}")
            return False
    
    @staticmethod
    def _send_twilio_sms(phone, message):
        """Send SMS using Twilio"""
        try:
            from twilio.rest import Client
            
            account_sid = current_app.config.get('TWILIO_ACCOUNT_SID')
            auth_token = current_app.config.get('TWILIO_AUTH_TOKEN')
            from_number = current_app.config.get('TWILIO_PHONE_NUMBER')
            
            if not all([account_sid, auth_token, from_number]):
                logger.warning("Twilio credentials not configured")
                return False
            
            client = Client(account_sid, auth_token)
            
            # Truncate message if too long (160 char limit per SMS)
            if len(message) > 160:
                message = message[:157] + '...'
            
            client.messages.create(
                body=message,
                from_=from_number,
                to=phone
            )
            
            logger.info(f"✅ SMS sent to {phone}")
            return True
            
        except ImportError:
            logger.warning("Twilio package not installed. Run: pip install twilio")
            return False
        except Exception as e:
            logger.error(f"Twilio error: {e}")
            return False
    
    @staticmethod
    def _send_africastalking_sms(phone, message):
        """Send SMS using Africa's Talking"""
        try:
            import africastalking
            
            username = current_app.config.get('AFRICA_TALKING_USERNAME')
            api_key = current_app.config.get('AFRICA_TALKING_API_KEY')
            sender_id = current_app.config.get('AFRICA_TALKING_SENDER_ID')
            
            if not all([username, api_key]):
                logger.warning("Africa's Talking credentials not configured")
                return False
            
            africastalking.initialize(username, api_key)
            sms = africastalking.SMS
            
            # Truncate message if too long
            if len(message) > 160:
                message = message[:157] + '...'
            
            response = sms.send(message, [phone], sender_id=sender_id)
            
            logger.info(f"✅ SMS sent to {phone} via Africa's Talking")
            return True
            
        except ImportError:
            logger.warning("Africa's Talking package not installed. Run: pip install africastalking")
            return False
        except Exception as e:
            logger.error(f"Africa's Talking error: {e}")
            return False
    
    @staticmethod
    def send_job_alert(user, alert, matching_jobs, methods=None):
        """Send job alert via configured methods"""
        if methods is None:
            methods = ['email', 'sms']
        
        results = {}
        
        # Send email
        if 'email' in methods:
            results['email'] = NotificationService.send_job_alert_email(user, alert, matching_jobs)
        
        # Send SMS
        if 'sms' in methods:
            results['sms'] = NotificationService.send_job_alert_sms(user, alert, matching_jobs)
        
        return results