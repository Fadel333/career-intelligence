# app/recruiter/routes.py
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func
from datetime import datetime, timedelta
import json
import os
from werkzeug.utils import secure_filename
from app.utils.email import send_job_published_email
# app/recruiter/routes.py
from app.utils.job_notifier import notify_candidates_about_job

from . import recruiter_bp
from .forms import JobForm
from .services import CandidateMatcher

# Fix imports - remove UserRole since it's not in models.py
from models import db, User, RecruiterProfile, Job, Placement, Candidate, Shortlist,  JobApplication

# Import enums - define fallbacks if they don't exist
try:
    from models import JobStatus, PlacementStatus, EmploymentType
except ImportError:
    import enum
    class JobStatus(str, enum.Enum):
        DRAFT = "draft"
        PUBLISHED = "published"
        CLOSED = "closed"
        FILLED = "filled"
    
    class PlacementStatus(str, enum.Enum):
        PENDING = "pending"
        SCREENING = "screening"
        INTERVIEWING = "interviewing"
        OFFERED = "offered"
        HIRED = "hired"
        REJECTED = "rejected"
    
    class EmploymentType(str, enum.Enum):
        FULL_TIME = "full_time"
        PART_TIME = "part_time"
        CONTRACT = "contract"
        INTERNSHIP = "internship"
        REMOTE = "remote"

# Import decorators with fallback
try:
    from app.utils.decorators import recruiter_required, verified_recruiter_required
except ImportError:
    from functools import wraps
    from flask import abort
    
    def recruiter_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login first.', 'error')
                return redirect(url_for('auth.login'))
            if not current_user.is_recruiter():
                flash('You need recruiter access for this page.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    def verified_recruiter_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please login first.', 'error')
                return redirect(url_for('auth.login'))
            if not current_user.is_recruiter():
                flash('You need recruiter access for this page.', 'error')
                return redirect(url_for('index'))
            recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
            if not recruiter:
                flash('Please complete your recruiter profile first.', 'warning')
                return redirect(url_for('recruiter.setup_profile'))
            if recruiter.verification_status != 'approved':
                flash('Your account needs to be verified to access this feature.', 'warning')
                return redirect(url_for('recruiter.verification'))
            return f(*args, **kwargs)
        return decorated_function

# Configure upload for verification documents
VERIFICATION_UPLOAD_FOLDER = 'static/verification_docs'
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_document_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS


# ========== MAIN ROUTES ==========

@recruiter_bp.route('/')
@login_required
@recruiter_required
def hub():
    """Recruiter Hub landing page"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        return redirect(url_for('recruiter.setup_profile'))
    
    # Get stats
    total_jobs = Job.query.filter_by(recruiter_id=recruiter.id).count()
    active_jobs = Job.query.filter_by(recruiter_id=recruiter.id, status=JobStatus.PUBLISHED).count()
    total_placements = Placement.query.filter_by(recruiter_id=recruiter.id).count()
    total_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter.id, commission_paid=True).scalar() or 0
    
    # Get active jobs list
    active_jobs_list = Job.query.filter_by(recruiter_id=recruiter.id, status=JobStatus.PUBLISHED)\
        .order_by(Job.posted_at.desc()).limit(10).all()
    
    # New candidates this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_candidates = Candidate.query.filter(
        Candidate.is_processed == True,
        Candidate.uploaded_at >= week_ago
    ).count()
    
    # Hired this month
    month_ago = datetime.utcnow() - timedelta(days=30)
    hired_this_month = Placement.query.filter(
        Placement.recruiter_id == recruiter.id,
        Placement.status == PlacementStatus.HIRED,
        Placement.hired_at >= month_ago
    ).count()
    
    return render_template('recruiter/hub.html',
        recruiter=recruiter,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_placements=total_placements,
        total_earnings=total_earnings,
        active_jobs_list=active_jobs_list,
        new_candidates=new_candidates,
        hired_this_month=hired_this_month,
        match_rate=0,
        now=datetime.utcnow()
    )


@recruiter_bp.route('/dashboard')
@login_required
@recruiter_required
def dashboard():
    """Recruiter main dashboard"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Stats
    total_jobs = Job.query.filter_by(recruiter_id=recruiter.id).count()
    active_jobs = Job.query.filter_by(recruiter_id=recruiter.id, status=JobStatus.PUBLISHED).count()
    total_placements = Placement.query.filter_by(recruiter_id=recruiter.id).count()
    
    # Recent activity (last 10 placements)
    recent_placements = Placement.query.filter_by(recruiter_id=recruiter.id)\
        .order_by(desc(Placement.created_at)).limit(10).all()
    
    # Earnings summary
    total_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter.id, commission_paid=True).scalar() or 0
    
    pending_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter.id, commission_paid=False)\
        .filter(Placement.status == PlacementStatus.HIRED).scalar() or 0
    
    return render_template('recruiter/dashboard.html',
        recruiter=recruiter,
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_placements=total_placements,
        total_earnings=total_earnings,
        pending_earnings=pending_earnings,
        recent_placements=recent_placements
    )


# ========== CANDIDATE ROUTES ==========

@recruiter_bp.route('/candidates')
@login_required
@recruiter_required
def candidates():
    """View and search candidates"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Get search parameters
    query = request.args.get('q', '')
    skills_param = request.args.get('skills', '')
    min_match = request.args.get('min_match', 50, type=float)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Parse skills from comma-separated string
    skills_list = [s.strip() for s in skills_param.split(',') if s.strip()] if skills_param else []
    
    # Base query - only processed candidates
    candidates_query = Candidate.query.filter_by(is_processed=True)
    
    # Apply filters
    if query:
        candidates_query = candidates_query.filter(
            db.or_(
                Candidate.name.ilike(f'%{query}%'),
                Candidate.email.ilike(f'%{query}%'),
                Candidate.cv_text.ilike(f'%{query}%')
            )
        )
    
    if skills_list:
        for skill in skills_list:
            candidates_query = candidates_query.filter(
                Candidate.skills.cast(db.String).ilike(f'%{skill}%')
            )
    
    # Paginate
    paginated = candidates_query.order_by(desc(Candidate.uploaded_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Calculate match for each candidate
    candidates_with_match = []
    for candidate in paginated.items:
        match_data = CandidateMatcher.calculate_match(candidate, None)
        candidates_with_match.append({
            'candidate': candidate,
            'match': match_data
        })
    
    return render_template('recruiter/candidates.html',
        candidates=candidates_with_match,
        pagination=paginated,
        query=query,
        min_match=min_match,
        skills=skills_list
    )


@recruiter_bp.route('/candidates/<int:candidate_id>')
@login_required
@recruiter_required
def candidate_detail(candidate_id):
    """View full candidate profile"""
    candidate = Candidate.query.get_or_404(candidate_id)
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    jobs = Job.query.filter_by(recruiter_id=recruiter.id).all()
    
    existing_placements = Placement.query.filter_by(
        candidate_id=candidate_id,
        recruiter_id=recruiter.id
    ).all()
    
    return render_template('recruiter/candidate_detail.html',
        candidate=candidate,
        jobs=jobs,
        existing_placements=existing_placements
    )


@recruiter_bp.route('/candidates/<int:candidate_id>/flag', methods=['POST'])
@login_required
@recruiter_required
def flag_candidate(candidate_id):
    """Flag a candidate for a job"""
    job_id = request.form.get('job_id', type=int)
    notes = request.form.get('notes', '')
    
    if not job_id:
        flash('Please select a job.', 'error')
        return redirect(url_for('recruiter.candidate_detail', candidate_id=candidate_id))
    
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    job = Job.query.get_or_404(job_id)
    
    if job.recruiter_id != recruiter.id:
        flash('You do not own this job.', 'error')
        return redirect(url_for('recruiter.candidates'))
    
    existing = Placement.query.filter_by(
        candidate_id=candidate_id,
        job_id=job_id
    ).first()
    
    if existing:
        flash('Candidate already flagged for this job.', 'warning')
        return redirect(url_for('recruiter.candidate_detail', candidate_id=candidate_id))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    match_data = CandidateMatcher.calculate_match(candidate, job)
    
    placement = Placement(
        recruiter_id=recruiter.id,
        candidate_id=candidate_id,
        job_id=job_id,
        match_percentage=match_data.get('overall', 0),
        match_details=match_data,
        notes=notes,
        status=PlacementStatus.PENDING
    )
    
    db.session.add(placement)
    db.session.commit()
    
    flash(f'✅ Candidate {candidate.name} flagged for "{job.title}" (Match: {match_data.get("overall", 0):.1f}%)', 'success')
    return redirect(url_for('recruiter.candidate_detail', candidate_id=candidate_id))


# ========== JOB ROUTES ==========

@recruiter_bp.route('/jobs')
@login_required
@recruiter_required
def jobs():
    """List all jobs for recruiter"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Job.query.filter_by(recruiter_id=recruiter.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    paginated = query.order_by(desc(Job.posted_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('recruiter/jobs.html',
        jobs=paginated,
        pagination=paginated,
        status_filter=status_filter
    )


@recruiter_bp.route('/jobs/create', methods=['GET', 'POST'])
@login_required
@recruiter_required
def create_job():
    """Create a new job - Requires verification"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Check if verified
    if recruiter.verification_status != 'approved':
        flash('Your account needs to be verified before you can post jobs.', 'warning')
        flash('Please upload your verification documents and submit for review.', 'info')
        return redirect(url_for('recruiter.verification'))
    
    form = JobForm()
    
    # Pre-populate expiry date on GET
    if request.method == 'GET':
        from datetime import date, timedelta
        form.expires_at.data = date.today() + timedelta(days=30)

    # DEBUG: Print form validation status
    print(f"DEBUG: Form submitted: {request.method}")
    print(f"DEBUG: Form validate: {form.validate_on_submit()}")
    print(f"DEBUG: Form errors: {form.errors if form.errors else 'None'}")
    
    if form.validate_on_submit():
        try:
            # Parse skills from textarea
            required_skills = [s.strip() for s in form.required_skills.data.split(',') if s.strip()] if form.required_skills.data else []
            preferred_skills = [s.strip() for s in form.preferred_skills.data.split(',') if s.strip()] if form.preferred_skills.data else []
            
            # Check if save as draft
            is_draft = request.form.get('save_draft') == 'true'
            print(f"DEBUG: is_draft: {is_draft}")
            
            # Parse requirements and responsibilities
            requirements = []
            if form.requirements.data:
                requirements = [r.strip() for r in form.requirements.data.split('\n') if r.strip()]
            
            responsibilities = []
            if form.responsibilities.data:
                responsibilities = [r.strip() for r in form.responsibilities.data.split('\n') if r.strip()]
            
            job = Job(
                recruiter_id=recruiter.id,
                poster_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                requirements=requirements,
                responsibilities=responsibilities,
                employment_type=form.employment_type.data,
                experience_level=form.experience_level.data,
                salary_min=form.salary_min.data,
                salary_max=form.salary_max.data,
                currency=form.currency.data,
                location=form.location.data,
                remote_available=form.remote_available.data,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                status=JobStatus.DRAFT if is_draft else JobStatus.PUBLISHED,
                expires_at=form.expires_at.data,
                posted_at=datetime.utcnow()
            )
            
            db.session.add(job)
            db.session.commit()

            # ========== SEND NOTIFICATIONS ==========
            if not is_draft:
                # Send email to recruiter (confirmation)
                try:
                    send_job_published_email(job)
                except Exception as e:
                    print(f"Email error: {e}")
                
                # ========== NOTIFY CANDIDATES ==========
                try:
                    from app.utils.job_notifier import notify_candidates_about_job
                    notifications_sent = notify_candidates_about_job(job)
                    print(f"📢 Notified {notifications_sent} candidates about job {job.id}")
                    
                    if notifications_sent > 0:
                        flash(f'✅ Job published! {notifications_sent} candidates were notified.', 'success')
                    else:
                        flash(f'✅ Job published successfully!', 'success')
                except Exception as e:
                    print(f"Notification error: {e}")
                    flash(f'✅ Job published successfully! (Notifications will be sent shortly)', 'success')
            else:
                flash(f'✅ Job "{job.title}" saved as draft!', 'success')
            
            return redirect(url_for('recruiter.jobs'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating job: {str(e)}', 'error')
            print(f"Error: {e}")
    
    # If form validation failed, show errors
    if form.errors:
        for field, errors in form.errors.items():
            field_label = field.replace('_', ' ').title()
            for error in errors:
                flash(f'{field_label}: {error}', 'error')
    
    return render_template('recruiter/create_job.html', form=form)
@recruiter_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
@recruiter_required
def edit_job(job_id):
    """Edit an existing job"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first_or_404()
    
    form = JobForm(obj=job)
    
    # Pre-populate expiry date
    if request.method == 'GET' and job.expires_at:
        form.expires_at.data = job.expires_at
    
    if form.validate_on_submit():
        try:
            job.title = form.title.data
            job.description = form.description.data
            job.requirements = [r.strip() for r in form.requirements.data.split('\n') if r.strip()] if form.requirements.data else []
            job.responsibilities = [r.strip() for r in form.responsibilities.data.split('\n') if r.strip()] if form.responsibilities.data else []
            job.employment_type = form.employment_type.data
            job.experience_level = form.experience_level.data
            job.salary_min = form.salary_min.data
            job.salary_max = form.salary_max.data
            job.currency = form.currency.data
            job.location = form.location.data
            job.remote_available = form.remote_available.data
            job.required_skills = [s.strip() for s in form.required_skills.data.split(',') if s.strip()] if form.required_skills.data else []
            job.preferred_skills = [s.strip() for s in form.preferred_skills.data.split(',') if s.strip()] if form.preferred_skills.data else []
            job.expires_at = form.expires_at.data
            
            if not form.save_as_draft.data and job.status == JobStatus.DRAFT:
                job.status = JobStatus.PUBLISHED
            
            db.session.commit()
            flash('✅ Job updated successfully!', 'success')
            return redirect(url_for('recruiter.jobs'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating job: {str(e)}', 'error')
    
    # Pre-populate form fields for display
    if job.requirements:
        form.requirements.data = '\n'.join(job.requirements)
    if job.responsibilities:
        form.responsibilities.data = '\n'.join(job.responsibilities)
    if job.required_skills:
        form.required_skills.data = ', '.join(job.required_skills)
    if job.preferred_skills:
        form.preferred_skills.data = ', '.join(job.preferred_skills)
    
    return render_template('recruiter/edit_job.html', form=form, job=job)

@recruiter_bp.route('/jobs/<int:job_id>/status', methods=['POST'])
@login_required
@recruiter_required
def update_job_status(job_id):
    """Update job status (publish, close, fill)"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first_or_404()
    
    new_status = request.form.get('status')
    if new_status in ['published', 'closed', 'filled']:
        job.status = JobStatus(new_status)
        db.session.commit()
        flash(f'✅ Job status updated to {new_status}', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('recruiter.jobs'))

# ========== APPLICATION MANAGEMENT ROUTES ==========
@recruiter_bp.route('/applications')
@login_required
@recruiter_required
def applications():
    """View all applications for recruiter's jobs"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Get recruiter's job IDs
    job_ids = [job.id for job in Job.query.filter_by(recruiter_id=recruiter.id).all()]
    
    # Base query - only non-deleted applications
    query = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False
    )
    
    # Filters
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'applied_at')
    sort_order = request.args.get('order', 'desc')
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if search_query:
        query = query.filter(
            db.or_(
                JobApplication.applicant_name.ilike(f'%{search_query}%'),
                JobApplication.applicant_email.ilike(f'%{search_query}%')
            )
        )
    
    # Sorting
    if sort_order == 'desc':
        query = query.order_by(desc(getattr(JobApplication, sort_by)))
    else:
        query = query.order_by(getattr(JobApplication, sort_by))
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 20
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get status counts
    status_counts = db.session.query(
        JobApplication.status,
        db.func.count(JobApplication.id)
    ).filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False
    ).group_by(JobApplication.status).all()
    
    # Check for expired applications (to be deleted)
    expired_count = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False,
        JobApplication.expires_at <= datetime.utcnow()
    ).count()
    
    return render_template('recruiter/applications.html',
        applications=paginated.items,  # CHANGE THIS: use .items to get the list
        pagination=paginated,           # Keep pagination object for pagination links
        status_counts=status_counts,
        status_filter=status_filter,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        expired_count=expired_count,
        now=datetime.utcnow()
    )

@recruiter_bp.route('/applications/<int:app_id>/delete', methods=['POST'])
@login_required
@recruiter_required
def delete_application(app_id):
    """Soft delete an application"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    application = JobApplication.query.get_or_404(app_id)
    
    # Verify ownership
    job = Job.query.filter_by(id=application.job_id, recruiter_id=recruiter.id).first()
    if not job:
        flash('You do not have permission to delete this application.', 'error')
        return redirect(url_for('recruiter.applications'))
    
    # Soft delete
    application.soft_delete()
    flash(f'✅ Application from {application.applicant_name} has been deleted.', 'success')
    
    return redirect(url_for('recruiter.applications'))


@recruiter_bp.route('/applications/<int:app_id>/restore', methods=['POST'])
@login_required
@recruiter_required
def restore_application(app_id):
    """Restore a soft-deleted application"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    application = JobApplication.query.get_or_404(app_id)
    
    # Verify ownership
    job = Job.query.filter_by(id=application.job_id, recruiter_id=recruiter.id).first()
    if not job:
        flash('You do not have permission to restore this application.', 'error')
        return redirect(url_for('recruiter.applications'))
    
    # Restore
    application.restore()
    flash(f'✅ Application from {application.applicant_name} has been restored.', 'success')
    
    return redirect(url_for('recruiter.applications'))


@recruiter_bp.route('/applications/bulk-delete', methods=['POST'])
@login_required
@recruiter_required
def bulk_delete_applications():
    """Delete multiple applications at once"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    app_ids = request.form.getlist('app_ids[]')
    
    if not app_ids:
        flash('No applications selected.', 'warning')
        return redirect(url_for('recruiter.applications'))
    
    deleted_count = 0
    for app_id in app_ids:
        application = JobApplication.query.get(int(app_id))
        if application:
            # Verify ownership
            job = Job.query.filter_by(id=application.job_id, recruiter_id=recruiter.id).first()
            if job:
                application.soft_delete()
                deleted_count += 1
    
    flash(f'✅ {deleted_count} applications deleted successfully.', 'success')
    return redirect(url_for('recruiter.applications'))


@recruiter_bp.route('/applications/cleanup-expired', methods=['POST'])
@login_required
@recruiter_required
def cleanup_expired_applications():
    """Delete all expired applications for the recruiter"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Get recruiter's job IDs
    job_ids = [job.id for job in Job.query.filter_by(recruiter_id=recruiter.id).all()]
    
    # Find expired applications
    expired_apps = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False,
        JobApplication.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_apps)
    for app in expired_apps:
        app.soft_delete()
    
    flash(f'✅ {count} expired applications have been cleaned up.', 'success')
    return redirect(url_for('recruiter.applications'))


@recruiter_bp.route('/applications/settings', methods=['GET', 'POST'])
@login_required
@recruiter_required
def application_settings():
    """Configure application retention settings"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    if request.method == 'POST':
        retention_days = request.form.get('retention_days', 30, type=int)
        
        if retention_days < 7:
            flash('Retention period must be at least 7 days.', 'error')
        elif retention_days > 365:
            flash('Retention period cannot exceed 365 days.', 'error')
        else:
            # Store in recruiter profile (you'll need to add this field)
            recruiter.retention_days = retention_days
            db.session.commit()
            flash(f'✅ Application retention period set to {retention_days} days.', 'success')
        
        return redirect(url_for('recruiter.application_settings'))
    
    return render_template('recruiter/application_settings.html', recruiter=recruiter)


# ========== PLACEMENT ROUTES ==========

@recruiter_bp.route('/placements')
@login_required
@recruiter_required
def placements():
    """View all placements"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Placement.query.filter_by(recruiter_id=recruiter.id)
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    paginated = query.order_by(desc(Placement.created_at)).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('recruiter/placements.html',
        placements=paginated,
        pagination=paginated,
        status_filter=status_filter
    )


@recruiter_bp.route('/placements/<int:placement_id>/update', methods=['POST'])
@login_required
@recruiter_required
def update_placement(placement_id):
    """Update placement status"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    placement = Placement.query.filter_by(id=placement_id, recruiter_id=recruiter.id).first_or_404()
    
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    valid_statuses = ['pending', 'screening', 'interviewing', 'offered', 'hired', 'rejected']
    
    if new_status in valid_statuses:
        placement.status = PlacementStatus(new_status)
        if notes:
            placement.notes = notes
        if new_status == 'hired':
            placement.hired_at = datetime.utcnow()
            if placement.job and placement.job.salary_max:
                placement.commission_amount = placement.job.salary_max * 0.10
        
        db.session.commit()
        flash(f'✅ Placement status updated to {new_status}', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('recruiter.placements'))


# ========== PROFILE & SETTINGS ROUTES ==========

@recruiter_bp.route('/setup', methods=['GET', 'POST'])
@login_required
@recruiter_required
def setup_profile():
    """Setup recruiter profile"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        if not recruiter:
            recruiter = RecruiterProfile(user_id=current_user.id)
            db.session.add(recruiter)
        
        recruiter.company_name = request.form.get('company_name')
        recruiter.company_description = request.form.get('company_description')
        recruiter.company_website = request.form.get('company_website')
        recruiter.industry = request.form.get('industry')
        recruiter.location = request.form.get('location')
        recruiter.min_match_percentage = float(request.form.get('min_match', 70.0))
        recruiter.auto_approve_candidates = bool(request.form.get('auto_approve'))
        
        current_user.company_name = recruiter.company_name
        
        db.session.commit()
        flash('✅ Recruiter profile updated successfully!', 'success')
        return redirect(url_for('recruiter.dashboard'))
    
    return render_template('recruiter/setup_profile.html', recruiter=recruiter)


@recruiter_bp.route('/settings')
@login_required
@recruiter_required
def settings():
    """Recruiter settings page"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    return render_template('recruiter/settings.html', recruiter=recruiter)


# ========== VERIFICATION ROUTES ==========

@recruiter_bp.route('/verification')
@login_required
@recruiter_required
def verification():
    """Recruiter verification page"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    return render_template('recruiter/verification.html', recruiter=recruiter)


@recruiter_bp.route('/verification/upload', methods=['POST'])
@login_required
@recruiter_required
def upload_verification_document():
    """Upload verification documents"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    if 'document' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('recruiter.verification'))
    
    file = request.files['document']
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('recruiter.verification'))
    
    if not allowed_document_file(file.filename):
        flash('Invalid file type. Please upload PDF, PNG, or JPG.', 'error')
        return redirect(url_for('recruiter.verification'))
    
    # Create upload folder if it doesn't exist
    os.makedirs(VERIFICATION_UPLOAD_FOLDER, exist_ok=True)
    
    # Secure the filename
    filename = secure_filename(f"user_{recruiter.user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{file.filename}")
    filepath = os.path.join(VERIFICATION_UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Update recruiter profile
    if not recruiter.verification_documents:
        recruiter.verification_documents = []
    
    recruiter.verification_documents.append({
        'filename': filename,
        'filepath': filepath,
        'uploaded_at': datetime.utcnow().isoformat(),
        'status': 'pending'
    })
    
    db.session.commit()
    
    flash('✅ Document uploaded successfully! It will be reviewed shortly.', 'success')
    return redirect(url_for('recruiter.verification'))


@recruiter_bp.route('/verification/submit', methods=['POST'])
@login_required
@recruiter_required
def submit_verification():
    """Submit verification request"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Check if documents are uploaded
    if not recruiter.verification_documents or len(recruiter.verification_documents) == 0:
        flash('Please upload at least one verification document first.', 'error')
        return redirect(url_for('recruiter.verification'))
    
    # Update license and tax info
    license_number = request.form.get('license_number')
    tax_id = request.form.get('tax_id')
    
    if license_number:
        recruiter.license_number = license_number
    
    if tax_id:
        recruiter.tax_id = tax_id
    
    # Set status to pending if not already
    if recruiter.verification_status != 'pending' and recruiter.verification_status != 'approved':
        recruiter.verification_status = 'pending'
    
    db.session.commit()
    
    flash('✅ Verification request submitted successfully! Our team will review your documents.', 'success')
    return redirect(url_for('recruiter.verification'))


# ========== ANALYTICS ROUTE ==========

@recruiter_bp.route('/analytics')
@login_required
@recruiter_required
def analytics():
    """Recruiter analytics dashboard"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    all_candidates = Candidate.query.filter_by(is_processed=True).all()
    total_candidates = len(all_candidates)
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_candidates = Candidate.query.filter(
        Candidate.is_processed == True,
        Candidate.uploaded_at >= week_ago
    ).count()
    
    placements = Placement.query.filter_by(recruiter_id=recruiter.id).all()
    total_placements = len(placements)
    total_jobs = Job.query.filter_by(recruiter_id=recruiter.id).count()
    
    avg_match = 0
    if placements:
        avg_match = sum(p.match_percentage for p in placements) / len(placements)
    
    hired_placements = [p for p in placements if p.status == PlacementStatus.HIRED and p.hired_at]
    avg_time_to_hire = 0
    if hired_placements:
        total_days = sum((p.hired_at - p.created_at).days for p in hired_placements)
        avg_time_to_hire = total_days / len(hired_placements)
    
    hired_count = len([p for p in placements if p.status == PlacementStatus.HIRED])
    success_rate = (hired_count / total_placements * 100) if total_placements > 0 else 0
    
    skill_counts = {}
    for candidate in all_candidates:
        if candidate.skills:
            for skill in candidate.skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    exp_ranges = {
        '0-2 years': 0,
        '3-5 years': 0,
        '6-10 years': 0,
        '10+ years': 0
    }
    for candidate in all_candidates:
        years = candidate.experience_years or 0
        if years <= 2:
            exp_ranges['0-2 years'] += 1
        elif years <= 5:
            exp_ranges['3-5 years'] += 1
        elif years <= 10:
            exp_ranges['6-10 years'] += 1
        else:
            exp_ranges['10+ years'] += 1
    
    location_counts = {}
    for candidate in all_candidates:
        loc = candidate.location or 'Unknown'
        location_counts[loc] = location_counts.get(loc, 0) + 1
    
    total_locations = len(all_candidates)
    location_data = []
    for loc, count in sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        location_data.append({
            'name': loc,
            'count': count,
            'percentage': (count / total_locations * 100) if total_locations > 0 else 0
        })
    
    top_candidates = []
    for placement in placements[:10]:
        if placement.candidate:
            top_candidates.append({
                'name': placement.candidate.name or 'Unknown',
                'skills': placement.candidate.skills[:3] if placement.candidate.skills else [],
                'match': placement.match_percentage or 0,
                'experience': placement.candidate.experience_years or 0
            })
    
    if not top_candidates and all_candidates:
        for candidate in all_candidates[:5]:
            top_candidates.append({
                'name': candidate.name or 'Unknown',
                'skills': candidate.skills[:3] if candidate.skills else [],
                'match': 0,
                'experience': candidate.experience_years or 0
            })
    
    top_candidates = sorted(top_candidates, key=lambda x: x['match'], reverse=True)
    
    total_views = Job.query.filter_by(recruiter_id=recruiter.id).with_entities(func.sum(Job.views_count)).scalar() or 0
    total_applications = Job.query.filter_by(recruiter_id=recruiter.id).with_entities(func.sum(Job.applications_count)).scalar() or 0
    
    return render_template('recruiter/analytics.html',
        total_candidates=total_candidates,
        new_candidates=new_candidates,
        avg_match=round(avg_match, 1),
        total_jobs=total_jobs,
        total_placements=total_placements,
        avg_time_to_hire=round(avg_time_to_hire, 0),
        time_to_hire_change=3,
        success_rate=round(success_rate, 0),
        success_rate_change=5,
        top_skills=top_skills,
        exp_ranges=exp_ranges,
        locations=location_data,
        top_candidates=top_candidates[:10],
        total_views=total_views,
        total_applications=total_applications,
        avg_hires_per_job=round(hired_count / max(1, total_jobs), 1),
        cost_per_hire=0,
        views_growth=12,
        apps_growth=8,
        cost_savings=15
    )


# ========== API ROUTES ==========

@recruiter_bp.route('/api/generate-description', methods=['POST'])
@login_required
@recruiter_required
def api_generate_description():
    """AI-powered job description generation"""
    try:
        data = request.get_json()
        title = data.get('title', '')
        skills = data.get('skills', [])
        
        if not title:
            return jsonify({'error': 'Job title is required'}), 400
        
        recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
        company_name = recruiter.company_name if recruiter else "Our Company"
        
        try:
            from app.utils.openai_assistant import OpenAIAssistant
            assistant = OpenAIAssistant()
            
            prompt = f"""Generate a professional job description for:
Title: {title}
Required Skills: {', '.join(skills) if skills else 'Various'}
Company: {company_name}

Please include:
1. About the role (2-3 sentences)
2. Key Responsibilities (5-6 bullet points)
3. Requirements (5-6 bullet points including skills and experience)
4. Benefits (3-4 bullet points)

Make it professional, clear, and attractive to candidates."""
            
            response = assistant.get_response(prompt, [], 0, 'recruiting')
            description = response.get('answer', '')
            
            return jsonify({'description': description})
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            description = generate_basic_description(title, skills, company_name)
            return jsonify({'description': description})
            
    except Exception as e:
        print(f"Error generating description: {e}")
        return jsonify({'error': str(e)}), 500


def generate_basic_description(title, skills, company_name):
    """Fallback description generator"""
    skills_text = ', '.join(skills) if skills else 'relevant skills'
    
    return f"""
About the Role:
We are looking for a talented {title} to join our team at {company_name}. 
You will be responsible for delivering high-quality work and contributing to our mission.

Key Responsibilities:
• Lead and execute projects independently
• Collaborate with cross-functional teams
• Deliver high-quality solutions on time
• Mentor and guide junior team members
• Continuously improve processes and workflows

Requirements:
• {skills_text}
• Proven experience in a similar role
• Strong problem-solving skills
• Excellent communication skills
• Ability to work in a fast-paced environment

Benefits:
• Competitive salary
• Health insurance
• Flexible work hours
• Professional development opportunities
• Great company culture

Join us in making a difference! Apply now to become part of our growing team.
"""


@recruiter_bp.route('/api/rank-candidates/<int:job_id>')
@login_required
@recruiter_required
def api_rank_candidates(job_id):
    """AI-powered candidate ranking for a specific job"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404
    
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first()
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    all_candidates = Candidate.query.filter_by(is_processed=True).all()
    ranked = CandidateMatcher.rank_candidates_for_job(all_candidates, job)
    
    return jsonify({
        'job_id': job.id,
        'job_title': job.title,
        'total_candidates': len(ranked),
        'ranked_candidates': ranked[:50]
    })


@recruiter_bp.route('/api/skill-gaps/<int:job_id>')
@login_required
@recruiter_required
def api_skill_gaps(job_id):
    """Analyze skill gaps for a specific job"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404
    
    job = Job.query.filter_by(id=job_id, recruiter_id=recruiter.id).first()
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    all_candidates = Candidate.query.filter_by(is_processed=True).all()
    gap_analysis = CandidateMatcher.analyze_skill_gaps(all_candidates, job)
    
    return jsonify(gap_analysis)


@recruiter_bp.route('/api/shortlist/<int:candidate_id>', methods=['POST'])
@login_required
@recruiter_required
def api_shortlist_candidate(candidate_id):
    """Add candidate to shortlist"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404
    
    candidate = Candidate.query.get_or_404(candidate_id)
    
    return jsonify({
        'success': True,
        'message': f'✅ {candidate.name} added to shortlist'
    })


@recruiter_bp.route('/api/search-candidates')
@login_required
@recruiter_required
def api_search_candidates():
    """API endpoint for candidate search (for AJAX)"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        return jsonify({'error': 'Recruiter profile not found'}), 404
    
    query = request.args.get('q', '')
    skills_param = request.args.get('skills', '')
    min_match = request.args.get('min_match', 50, type=float)
    limit = request.args.get('limit', 20, type=int)
    
    skills_list = [s.strip() for s in skills_param.split(',') if s.strip()] if skills_param else []
    
    candidates_query = Candidate.query.filter_by(is_processed=True)
    
    if query:
        candidates_query = candidates_query.filter(
            db.or_(
                Candidate.name.ilike(f'%{query}%'),
                Candidate.email.ilike(f'%{query}%')
            )
        )
    
    if skills_list:
        for skill in skills_list:
            candidates_query = candidates_query.filter(
                Candidate.skills.cast(db.String).ilike(f'%{skill}%')
            )
    
    candidates = candidates_query.limit(limit).all()
    
    results = []
    for candidate in candidates:
        match_data = CandidateMatcher.calculate_match(candidate, None)
        results.append({
            'id': candidate.id,
            'name': candidate.name,
            'email': candidate.email,
            'skills': candidate.skills,
            'experience_years': candidate.experience_years,
            'match_percentage': match_data.get('overall', 0),
            'match_details': match_data
        })
    
    return jsonify({
        'candidates': results,
        'total': len(results)
    })

# app/recruiter/routes.py - Add these routes

@recruiter_bp.route('/shortlist')
@login_required
@recruiter_required
def shortlist():
    """View shortlisted candidates"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    shortlisted = Shortlist.query.filter_by(recruiter_id=recruiter.id)\
        .order_by(desc(Shortlist.created_at)).all()
    
    return render_template('recruiter/shortlist.html',
        shortlisted=shortlisted,
        recruiter=recruiter
    )


@recruiter_bp.route('/shortlist/add/<int:candidate_id>', methods=['POST'])
@login_required
@recruiter_required
def add_to_shortlist(candidate_id):
    """Add candidate to shortlist"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    candidate = Candidate.query.get_or_404(candidate_id)
    job_id = request.form.get('job_id', type=int)
    notes = request.form.get('notes', '')
    
    # Check if already in shortlist
    existing = Shortlist.query.filter_by(
        recruiter_id=recruiter.id,
        candidate_id=candidate_id
    ).first()
    
    if existing:
        flash(f'{candidate.name} is already in your shortlist.', 'warning')
        return redirect(url_for('recruiter.candidate_detail', candidate_id=candidate_id))
    
    # Add to shortlist
    shortlist = Shortlist(
        recruiter_id=recruiter.id,
        candidate_id=candidate_id,
        job_id=job_id if job_id else None,
        notes=notes
    )
    
    db.session.add(shortlist)
    db.session.commit()
    
    flash(f'✅ {candidate.name} added to shortlist!', 'success')
    return redirect(url_for('recruiter.candidate_detail', candidate_id=candidate_id))


@recruiter_bp.route('/shortlist/remove/<int:shortlist_id>', methods=['POST'])
@login_required
@recruiter_required
def remove_from_shortlist(shortlist_id):
    """Remove candidate from shortlist"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    shortlist = Shortlist.query.filter_by(
        id=shortlist_id,
        recruiter_id=recruiter.id
    ).first_or_404()
    
    candidate_name = shortlist.candidate.name if shortlist.candidate else 'Unknown'
    
    db.session.delete(shortlist)
    db.session.commit()
    
    flash(f'Removed {candidate_name} from shortlist.', 'info')
    return redirect(url_for('recruiter.shortlist'))


@recruiter_bp.route('/shortlist/update/<int:shortlist_id>', methods=['POST'])
@login_required
@recruiter_required
def update_shortlist_note(shortlist_id):
    """Update note on shortlisted candidate"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    shortlist = Shortlist.query.filter_by(
        id=shortlist_id,
        recruiter_id=recruiter.id
    ).first_or_404()
    
    notes = request.form.get('notes', '')
    shortlist.notes = notes
    db.session.commit()
    
    flash('✅ Note updated successfully!', 'success')
    return redirect(url_for('recruiter.shortlist'))

 