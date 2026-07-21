from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

from models import db, Job, JobApplication, Candidate, User, JobStatus, RecruiterProfile
from app.utils.decorators import recruiter_required
from app.utils.email import send_new_application_email, send_application_status_update_email

# Create blueprint
jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

# Configure upload for CVs
APPLICATION_UPLOAD_FOLDER = 'static/applications'
ALLOWED_CV_EXTENSIONS = {'pdf', 'docx'}


def allowed_cv_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CV_EXTENSIONS


# ========== HELPER FUNCTIONS ==========
def get_cv_file_path(application):
    """Get the correct CV file path"""
    if not application.cv_filepath:
        return None
    
    # Get just the filename
    filename = os.path.basename(application.cv_filepath)
    
    # Get project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Check possible locations in order
    possible_paths = [
        os.path.join(project_root, 'static', 'applications', filename),  # Project root static
        os.path.join(project_root, 'app', 'static', 'applications', filename),  # App static
        os.path.join('static', 'applications', filename),  # Relative path
        application.cv_filepath,  # Original path
    ]
    
    for path in possible_paths:
        normalized_path = path.replace('\\', '/')
        if os.path.exists(normalized_path):
            return normalized_path
    
    # If still not found, search the static/applications directory
    static_dir = os.path.join(project_root, 'static', 'applications')
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            if filename in files:
                return os.path.join(root, filename).replace('\\', '/')
    
    return None


# ========== PUBLIC JOB BOARD ==========
@jobs_bp.route('/')
def job_board():
    """Public job board - list all published jobs"""
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    employment_type = request.args.get('employment_type', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # FIX: Use string comparison instead of enum for status
    query = Job.query.filter_by(status='published')
    
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f'%{search}%'),
                Job.description.ilike(f'%{search}%'),
                Job.required_skills.cast(db.String).ilike(f'%{search}%')
            )
        )
    
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    
    if employment_type:
        try:
            from models import EmploymentType
            if employment_type in [e.value for e in EmploymentType]:
                query = query.filter_by(employment_type=EmploymentType(employment_type))
        except (ValueError, TypeError):
            pass
    
    query = query.order_by(desc(Job.posted_at))
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # FIX: Use string comparison for filters too
    locations = db.session.query(Job.location).filter_by(status='published').distinct().all()
    locations = [loc[0] for loc in locations if loc[0]]
    
    employment_types = db.session.query(Job.employment_type).filter_by(status='published').distinct().all()
    employment_types = [et[0] for et in employment_types if et[0]]
    
    return render_template('jobs/board.html',
        jobs=jobs,
        search=search,
        location=location,
        employment_type=employment_type,
        locations=locations,
        employment_types=employment_types
    )


@jobs_bp.route('/<int:job_id>')
def job_detail(job_id):
    """View job details - redirects if job is closed or filled"""
    job = Job.query.filter_by(id=job_id).first_or_404()
    
    # If job is not published, redirect to job board with message
    if job.status != 'published':
        if job.status == 'closed':
            flash('This job posting has been closed by the employer.', 'info')
        elif job.status == 'filled':
            flash('🎉 This position has been filled! Check out other opportunities below.', 'success')
        elif job.status == 'draft':
            flash('This job is not yet published.', 'warning')
        return redirect(url_for('jobs.job_board'))
    
    # Increment view count
    job.views_count = (job.views_count or 0) + 1
    db.session.commit()
    
    has_applied = False
    if current_user.is_authenticated:
        application = JobApplication.query.filter_by(
            job_id=job.id,
            user_id=current_user.id
        ).first()
        if application:
            has_applied = True
    
    return render_template('jobs/detail.html',
        job=job,
        has_applied=has_applied
    )


@jobs_bp.route('/<int:job_id>/apply', methods=['GET', 'POST'])
def apply(job_id):
    """Apply to a job - redirects if job is closed or filled"""
    job = Job.query.filter_by(id=job_id).first_or_404()
    
    # If job is not published, redirect to job board with message
    if job.status != 'published':
        if job.status == 'closed':
            flash('This job posting has been closed by the employer and is no longer accepting applications.', 'info')
        elif job.status == 'filled':
            flash('🎉 This position has been filled and is no longer accepting applications.', 'info')
        elif job.status == 'draft':
            flash('This job is not yet published.', 'warning')
        return redirect(url_for('jobs.job_board'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cover_letter = request.form.get('cover_letter')
        cv_file = request.files.get('cv')
        
        if not name or not email:
            flash('Name and email are required.', 'error')
            return redirect(url_for('jobs.apply', job_id=job_id))
        
        existing = JobApplication.query.filter_by(
            job_id=job_id,
            applicant_email=email
        ).first()
        
        if existing:
            flash('You have already applied to this job.', 'warning')
            return redirect(url_for('jobs.job_detail', job_id=job_id))
        
        cv_filename = None
        cv_filepath = None
        
        if cv_file and allowed_cv_file(cv_file.filename):
            # Create upload folder if it doesn't exist
            os.makedirs(APPLICATION_UPLOAD_FOLDER, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{timestamp}_{cv_file.filename}")
            filepath = os.path.join(APPLICATION_UPLOAD_FOLDER, filename).replace('\\', '/')
            cv_file.save(filepath)
            
            cv_filename = filename
            cv_filepath = filepath
        
        application = JobApplication(
            job_id=job_id,
            user_id=current_user.id if current_user.is_authenticated else None,
            applicant_name=name,
            applicant_email=email,
            applicant_phone=phone,
            cover_letter=cover_letter,
            cv_filename=cv_filename,
            cv_filepath=cv_filepath,
            status='pending',
            expires_at=datetime.utcnow() + timedelta(days=30)  # Auto-expire after 30 days
        )
        
        db.session.add(application)
        job.applications_count = (job.applications_count or 0) + 1
        db.session.commit()

        send_new_application_email(application, job)
        
        flash('✅ Your application has been submitted successfully!', 'success')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    return render_template('jobs/apply.html', job=job)


# ========== RECRUITER APPLICATIONS ==========
@jobs_bp.route('/recruiter/applications')
@login_required
@recruiter_required
def recruiter_applications():
    """Recruiter view - see applications for their jobs"""
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
    
    # Get all applications
    applications = query.order_by(desc(JobApplication.applied_at)).all()
    
    # Calculate expired count
    expired_count = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False,
        JobApplication.expires_at <= datetime.utcnow()
    ).count()
    
    # Get status counts
    status_counts = db.session.query(
        JobApplication.status,
        db.func.count(JobApplication.id)
    ).filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False
    ).group_by(JobApplication.status).all()
    
    # Get filters from request
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'applied_at')
    sort_order = request.args.get('order', 'desc')
    
    # Apply filters if present
    if status_filter:
        applications = [app for app in applications if app.status == status_filter]
    
    if search_query:
        applications = [app for app in applications 
                       if search_query.lower() in app.applicant_name.lower() 
                       or search_query.lower() in app.applicant_email.lower()]
    
    # Apply sorting
    if sort_by == 'applied_at':
        applications.sort(key=lambda x: x.applied_at, reverse=(sort_order == 'desc'))
    elif sort_by == 'applicant_name':
        applications.sort(key=lambda x: x.applicant_name.lower(), reverse=(sort_order == 'desc'))
    elif sort_by == 'status':
        applications.sort(key=lambda x: x.status, reverse=(sort_order == 'desc'))
    
    return render_template('recruiter/applications.html',
        applications=applications,
        recruiter=recruiter,
        expired_count=expired_count,
        status_counts=status_counts,
        status_filter=status_filter,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        now=datetime.utcnow()
    )


@jobs_bp.route('/recruiter/applications/<int:application_id>')
@login_required
@recruiter_required
def application_detail(application_id):
    """View full application details"""
    application = JobApplication.query.get_or_404(application_id)
    
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get(application.job_id)
    
    if not recruiter or job.recruiter_id != recruiter.id:
        flash('You do not have permission to view this application.', 'error')
        return redirect(url_for('recruiter.dashboard'))
    
    # Get the CV file path for preview
    cv_file_path = get_cv_file_path(application)
    
    # Check if file exists
    cv_exists = cv_file_path and os.path.exists(cv_file_path)
    
    return render_template('recruiter/application_detail.html',
        application=application,
        job=job,
        recruiter=recruiter,
        cv_file_path=cv_file_path,
        cv_exists=cv_exists
    )


@jobs_bp.route('/recruiter/applications/<int:application_id>/download-cv')
@login_required
@recruiter_required
def download_cv(application_id):
    """Download candidate's CV"""
    application = JobApplication.query.get_or_404(application_id)
    
    # Check permission
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get(application.job_id)
    
    if not recruiter or job.recruiter_id != recruiter.id:
        flash('You do not have permission to download this CV.', 'error')
        return redirect(url_for('recruiter.dashboard'))
    
    if not application.cv_filename and not application.cv_filepath:
        flash('No CV uploaded for this application.', 'warning')
        return redirect(url_for('jobs.application_detail', application_id=application.id))
    
    # Get the correct file path using our helper
    file_path = get_cv_file_path(application)
    
    if not file_path or not os.path.exists(file_path):
        # Try looking in the absolute path
        if application.cv_filepath and os.path.exists(application.cv_filepath):
            file_path = application.cv_filepath
        else:
            flash('CV file not found. Please contact support.', 'error')
            return redirect(url_for('jobs.application_detail', application_id=application.id))
    
    # Use the filename from the application or extract from path
    download_name = application.cv_filename or os.path.basename(file_path)
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=download_name
    )


@jobs_bp.route('/recruiter/applications/<int:application_id>/status', methods=['POST'])
@login_required
@recruiter_required
def update_application_status(application_id):
    """Update application status"""
    application = JobApplication.query.get_or_404(application_id)
    
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get(application.job_id)
    
    if not recruiter or job.recruiter_id != recruiter.id:
        flash('You do not have permission to update this application.', 'error')
        return redirect(url_for('recruiter.dashboard'))
    
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status in ['pending', 'reviewed', 'shortlisted', 'rejected', 'hired']:
        application.status = new_status
        if notes:
            application.notes = notes
        if new_status in ['reviewed', 'shortlisted', 'rejected', 'hired']:
            application.reviewed_at = datetime.utcnow()
        
        db.session.commit()

        # Uncomment when email is ready
        # send_application_status_update_email(application)
        
        flash(f'✅ Application status updated to {new_status}', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('jobs.recruiter_applications'))

# ========== APPLICANT APPLICATION TRACKER ==========

@jobs_bp.route('/my-applications')
@login_required
def my_applications():
    """View all applications submitted by the current user"""
    # Get all applications for the current user
    applications = JobApplication.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(desc(JobApplication.applied_at)).all()
    
    # Get status counts
    status_counts = db.session.query(
        JobApplication.status,
        db.func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.is_deleted == False
    ).group_by(JobApplication.status).all()
    
    return render_template('jobs/my_applications.html',
        applications=applications,
        status_counts=status_counts,
        now=datetime.utcnow()
    )


@jobs_bp.route('/my-applications/<int:application_id>')
@login_required
def my_application_detail(application_id):
    """View details of a specific application"""
    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id,
        is_deleted=False
    ).first_or_404()
    
    return render_template('jobs/my_application_detail.html',
        application=application,
        now=datetime.utcnow()
    )


@jobs_bp.route('/my-applications/<int:application_id>/withdraw', methods=['POST'])
@login_required
def withdraw_application(application_id):
    """Withdraw an application (soft delete)"""
    application = JobApplication.query.filter_by(
        id=application_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Only allow withdrawal if status is pending or reviewed
    if application.status not in ['pending', 'reviewed']:
        flash('You cannot withdraw this application at this stage.', 'error')
        return redirect(url_for('jobs.my_applications'))
    
    # Soft delete the application
    application.is_deleted = True
    application.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('✅ Your application has been withdrawn successfully.', 'success')
    return redirect(url_for('jobs.my_applications'))


@jobs_bp.route('/api/applications/status-counts')
@login_required
def api_application_status_counts():
    """API endpoint for application status counts (for dashboard)"""
    counts = db.session.query(
        JobApplication.status,
        db.func.count(JobApplication.id)
    ).filter(
        JobApplication.user_id == current_user.id,
        JobApplication.is_deleted == False
    ).group_by(JobApplication.status).all()
    
    result = {status: count for status, count in counts}
    
    return jsonify({
        'total': sum(result.values()),
        'pending': result.get('pending', 0),
        'reviewed': result.get('reviewed', 0),
        'shortlisted': result.get('shortlisted', 0),
        'hired': result.get('hired', 0),
        'rejected': result.get('rejected', 0)
    })

# In your job creation/update route
def create_job():
    # ... save job to database ...
    
    # After saving, check for matching alerts
    if job.status == 'published':
        from app.utils.job_alert_checker import check_job_alerts
        # Check alerts (this will send notifications to users)
        # You can run this in a background thread or Celery task
        import threading
        threading.Thread(target=check_job_alerts).start()