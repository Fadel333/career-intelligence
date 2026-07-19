# app/tasks.py
from datetime import datetime, timedelta
from models import db, JobApplication

def cleanup_expired_applications():
    """Background task to clean up expired applications"""
    print("🔄 Running expired application cleanup...")
    
    # Find expired applications
    expired_apps = JobApplication.query.filter(
        JobApplication.is_deleted == False,
        JobApplication.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_apps)
    for app in expired_apps:
        app.is_deleted = True
        app.updated_at = datetime.utcnow()
    
    db.session.commit()
    print(f"✅ Cleaned up {count} expired applications")
    return count