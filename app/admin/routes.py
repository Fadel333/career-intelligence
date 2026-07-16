# app/admin/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import desc
from datetime import datetime

from models import db, User, RecruiterProfile, Job, Placement
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard"""
    # Get stats
    total_recruiters = RecruiterProfile.query.count()
    pending_verifications = RecruiterProfile.query.filter_by(verification_status='pending').count()
    total_jobs = Job.query.count()
    total_placements = Placement.query.count()
    
    # Recent verification requests
    pending_recruiters = RecruiterProfile.query.filter_by(verification_status='pending')\
        .order_by(desc(RecruiterProfile.created_at)).all()
    
    return render_template('admin/index.html',
        total_recruiters=total_recruiters,
        pending_verifications=pending_verifications,
        total_jobs=total_jobs,
        total_placements=total_placements,
        pending_recruiters=pending_recruiters
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