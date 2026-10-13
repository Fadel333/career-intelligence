"""
Weekly digest generator — run every Monday at 9 AM
"""
from datetime import datetime, timedelta
from app import create_app, db
from app.utils.email import send_weekly_digest

def generate_and_send_digests():
    """Generate and send weekly digest to all active users"""
    app = create_app()
    
    with app.app_context():
        from models import User, UserProgress, UserStreak, Job, WeeklyDigest
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Only users with CVs, active in last 30 days
        users = User.query.filter(
            User.cv_filename.isnot(None),
            User.user_type == 'student',
            User.last_login >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        sent = 0
        for user in users:
            try:
                # Gather data
                courses_completed = UserProgress.query.filter(
                    UserProgress.user_id == user.id,
                    UserProgress.status == 'completed',
                    UserProgress.completed_at >= week_ago
                ).count()
                
                streak = UserStreak.query.filter_by(user_id=user.id).first()
                
                # New jobs matching
                jobs = Job.query.filter(
                    Job.status == 'published',
                    Job.posted_at >= week_ago
                ).limit(3).all()
                
                jobs_html = ''
                if jobs:
                    for job in jobs:
                        jobs_html += f'''
                        <div class="job-item">
                            <strong>{job.title}</strong><br>
                            <span style="color: #718096; font-size: 13px;">{job.location or 'Remote'}</span>
                        </div>
                        '''
                
                digest_data = {
                    'week_of': datetime.utcnow().strftime('%b %d'),
                    'courses_completed': courses_completed,
                    'current_streak': streak.current_streak if streak else 0,
                    'employability_score': user.employability_score or 0,
                    'new_jobs_count': len(jobs),
                    'top_skill': 'Python',
                    'top_skill_demand': 60,
                    'new_jobs_html': jobs_html,
                }
                
                # Send
                send_weekly_digest(user, digest_data)
                
                # Log
                digest = WeeklyDigest(
                    user_id=user.id,
                    week_of=datetime.utcnow().date(),
                    content=digest_data
                )
                db.session.add(digest)
                sent += 1
                
            except Exception as e:
                print(f"❌ Digest failed for {user.email}: {e}")
        
        db.session.commit()
        print(f"✅ Sent weekly digest to {sent} users")
        return sent


if __name__ == '__main__':
    generate_and_send_digests()