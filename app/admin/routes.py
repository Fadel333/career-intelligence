# app/admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime, timedelta

from models import db, User, RecruiterProfile, Job, Placement
from app.utils.decorators import admin_required

from app.utils.email import send_verification_approved_email, send_verification_rejected_email
from models import db, User, RecruiterProfile, Job, Placement, NewsletterSubscriber


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard — command center"""
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # ========== EXISTING METRICS ==========
    total_recruiters = RecruiterProfile.query.count()
    pending_verifications = RecruiterProfile.query.filter_by(verification_status='pending').count()
    total_jobs = Job.query.count()
    total_placements = Placement.query.count()

    # ========== NEW: USER METRICS ==========
    total_users = User.query.count()
    users_today = User.query.filter(User.created_at >= today).count()
    users_this_week = User.query.filter(User.created_at >= week_ago).count()

    total_students = User.query.filter_by(user_type='student').count()
    total_recruiter_users = User.query.filter_by(user_type='recruiter').count()

    # ========== NEW: CV METRICS ==========
    cvs_uploaded = User.query.filter(User.cv_filename.isnot(None)).count()
    cvs_this_week = User.query.filter(
        User.cv_uploaded_at >= week_ago,
        User.cv_filename.isnot(None)
    ).count()

    # ========== NEW: EMPLOYABILITY SCORE ==========
    avg_score = db.session.query(func.avg(User.employability_score)).filter(
        User.employability_score.isnot(None)
    ).scalar() or 0

    # ========== NEW: SIGNUPS OVER 30 DAYS (for chart) ==========
    signups_by_day = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at >= month_ago
    ).group_by(
        func.date(User.created_at)
    ).order_by(
        func.date(User.created_at)
    ).all()

    chart_data = [
        {'date': row.date.strftime('%b %d'), 'count': row.count}
        for row in signups_by_day
    ]

    # ========== NEW: TOP SECTORS ==========
    top_sectors = db.session.query(
        User.detected_sector,
        func.count(User.id).label('count')
    ).filter(
        User.detected_sector.isnot(None),
        User.detected_sector != ''
    ).group_by(
        User.detected_sector
    ).order_by(
        func.count(User.id).desc()
    ).limit(5).all()

    # ========== NEW: RECENT SIGNUPS ==========
    recent_users = User.query.order_by(
        desc(User.created_at)
    ).limit(10).all()

    # ========== EXISTING: Pending recruiters ==========
    pending_recruiters = RecruiterProfile.query.filter_by(verification_status='pending')\
        .order_by(desc(RecruiterProfile.created_at)).all()

    return render_template('admin/index.html',
        # Existing
        total_recruiters=total_recruiters,
        pending_verifications=pending_verifications,
        total_jobs=total_jobs,
        total_placements=total_placements,
        pending_recruiters=pending_recruiters,
        # New - user metrics
        total_users=total_users,
        users_today=users_today,
        users_this_week=users_this_week,
        total_students=total_students,
        total_recruiter_users=total_recruiter_users,
        # New - CV metrics
        cvs_uploaded=cvs_uploaded,
        cvs_this_week=cvs_this_week,
        cv_completion_rate=round((cvs_uploaded / total_users * 100), 1) if total_users else 0,
        # New - score
        avg_score=round(float(avg_score), 1),
        # New - chart
        chart_data=chart_data,
        # New - sectors
        top_sectors=top_sectors,
        # New - recent
        recent_users=recent_users,
        # For "updated at"
        now=now
    )


@admin_bp.route('/verifications')
@login_required
@admin_required
def verifications():
    """View all verification requests"""
    status_filter = request.args.get('status', 'pending')

    query = RecruiterProfile.query

    if status_filter:
        query = query.filter_by(verification_status=status_filter)

    recruiters = query.order_by(desc(RecruiterProfile.created_at)).all()

    return render_template('admin/verifications.html',
        recruiters=recruiters,
        status_filter=status_filter
    )


@admin_bp.route('/verification/<int:recruiter_id>')
@login_required
@admin_required
def verification_detail(recruiter_id):
    """View a specific verification request"""
    recruiter = RecruiterProfile.query.get_or_404(recruiter_id)
    user = User.query.get(recruiter.user_id)

    return render_template('admin/verification_detail.html',
        recruiter=recruiter,
        user=user
    )


@admin_bp.route('/verification/<int:recruiter_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_verification(recruiter_id):
    """Approve a recruiter's verification request"""
    recruiter = RecruiterProfile.query.get_or_404(recruiter_id)

    # Update verification status
    recruiter.verification_status = 'approved'
    recruiter.verified_at = datetime.utcnow()
    recruiter.verified_by = current_user.id
    recruiter.rejection_reason = None

    # Update all documents status
    if recruiter.verification_documents:
        for doc in recruiter.verification_documents:
            doc['status'] = 'approved'

    db.session.commit()

    send_verification_approved_email(recruiter)

    flash(f'✅ {recruiter.company_name} has been verified successfully!', 'success')
    return redirect(url_for('admin.verifications'))


@admin_bp.route('/verification/<int:recruiter_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_verification(recruiter_id):
    """Reject a recruiter's verification request"""
    recruiter = RecruiterProfile.query.get_or_404(recruiter_id)

    rejection_reason = request.form.get('rejection_reason', '')

    if not rejection_reason:
        flash('Please provide a reason for rejection.', 'error')
        return redirect(url_for('admin.verification_detail', recruiter_id=recruiter_id))

    # Update verification status
    recruiter.verification_status = 'rejected'
    recruiter.rejection_reason = rejection_reason
    recruiter.verified_by = current_user.id

    # Update all documents status
    if recruiter.verification_documents:
        for doc in recruiter.verification_documents:
            doc['status'] = 'rejected'

    db.session.commit()

    send_verification_rejected_email(recruiter)

    flash(f'❌ {recruiter.company_name} has been rejected.', 'warning')
    return redirect(url_for('admin.verifications'))


@admin_bp.route('/verification/<int:recruiter_id>/reset', methods=['POST'])
@login_required
@admin_required
def reset_verification(recruiter_id):
    """Reset verification status to pending"""
    recruiter = RecruiterProfile.query.get_or_404(recruiter_id)

    recruiter.verification_status = 'pending'
    recruiter.verified_at = None
    recruiter.verified_by = None
    recruiter.rejection_reason = None

    # Reset all documents status
    if recruiter.verification_documents:
        for doc in recruiter.verification_documents:
            doc['status'] = 'pending'

    db.session.commit()

    flash(f'🔄 {recruiter.company_name} verification has been reset to pending.', 'info')
    return redirect(url_for('admin.verifications'))

@admin_bp.route('/newsletter')
@login_required
@admin_required
def newsletter_composer():
    """Newsletter composer page"""
    subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
    total_subs = len(subscribers)
    
    return render_template('admin/newsletter.html',
        subscriber_count=total_subs,
        subscribers=subscribers[:20]  # Show first 20
    )


@admin_bp.route('/newsletter/send', methods=['POST'])
@login_required
@admin_required
def newsletter_send():
    """Send newsletter to all active subscribers"""
    from app.utils.email import send_newsletter_broadcast
    
    subject = request.form.get('subject', '').strip()
    html_content = request.form.get('html_content', '').strip()
    
    if not subject or not html_content:
        flash('Subject and content are required', 'error')
        return redirect(url_for('admin.newsletter_composer'))
    
    subscribers = NewsletterSubscriber.query.filter_by(is_active=True).all()
    
    if not subscribers:
        flash('No active subscribers to send to', 'warning')
        return redirect(url_for('admin.newsletter_composer'))
    
    sent = 0
    failed = 0
    
    for sub in subscribers:
        try:
            send_newsletter_broadcast(sub.email, subject, html_content)
            sent += 1
        except Exception as e:
            failed += 1
            print(f"❌ Failed to send to {sub.email}: {e}")
    
    flash(f'✅ Newsletter sent to {sent} subscribers ({failed} failed)', 'success')
    return redirect(url_for('admin.newsletter_composer'))