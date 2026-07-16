# app/jobs/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc, func, or_
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from models import db, Job, JobApplication, Candidate, User, JobStatus, RecruiterProfile
from app.utils.decorators import recruiter_required

# Create blueprint
jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

# Configure upload for CVs
APPLICATION_UPLOAD_FOLDER = 'static/applications'
ALLOWED_CV_EXTENSIONS = {'pdf', 'docx'}

def allowed_cv_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CV_EXTENSIONS


@jobs_bp.route('/')
def job_board():
    """Public job board - list all published jobs"""
    # Get query parameters
    search = request.args.get('search', '')
    location = request.args.get('location', '')
    employment_type = request.args.get('employment_type', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Base query - only published jobs
    query = Job.query.filter_by(status=JobStatus.PUBLISHED)
    
    # Apply filters
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
    
    # Fix: Handle employment_type filter properly
    if employment_type:
        # Convert string to EmploymentType enum
        try:
            from models import EmploymentType
            # If it's a string like "FULL_TIME", convert to enum
            if employment_type in [e.value for e in EmploymentType]:
                employment_type_enum = EmploymentType(employment_type)
                query = query.filter_by(employment_type=employment_type_enum)
        except (ValueError, TypeError):
            # If it's already an enum or invalid, skip filter
            pass
    
    # Order by newest first
    query = query.order_by(desc(Job.posted_at))
    
    # Paginate
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique locations and employment types for filters
    locations = db.session.query(Job.location).filter_by(status=JobStatus.PUBLISHED).distinct().all()
    locations = [loc[0] for loc in locations if loc[0]]
    
    # Get employment types - get the actual enum values
    employment_types = db.session.query(Job.employment_type).filter_by(status=JobStatus.PUBLISHED).distinct().all()
    # Filter out None values and convert to list of enum values
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
    """View job details"""
    job = Job.query.filter_by(id=job_id, status=JobStatus.PUBLISHED).first_or_404()
    
    # Increment view count
    job.views_count = (job.views_count or 0) + 1
    db.session.commit()
    
    # Check if user has already applied
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
    """Apply to a job"""
    job = Job.query.filter_by(id=job_id, status=JobStatus.PUBLISHED).first_or_404()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        cover_letter = request.form.get('cover_letter')
        cv_file = request.files.get('cv')
        
        # Validate
        if not name or not email:
            flash('Name and email are required.', 'error')
            return redirect(url_for('jobs.apply', job_id=job_id))
        
        # Check if already applied
        existing = JobApplication.query.filter_by(
            job_id=job_id,
            applicant_email=email
        ).first()
        
        if existing:
            flash('You have already applied to this job.', 'warning')
            return redirect(url_for('jobs.job_detail', job_id=job_id))
        
        # Save CV if uploaded
        cv_filename = None
        cv_filepath = None
        
        if cv_file and allowed_cv_file(cv_file.filename):
            # Create upload folder if it doesn't exist
            os.makedirs(APPLICATION_UPLOAD_FOLDER, exist_ok=True)
            
            filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{cv_file.filename}")
            filepath = os.path.join(APPLICATION_UPLOAD_FOLDER, filename)
            cv_file.save(filepath)
            
            cv_filename = filename
            cv_filepath = filepath
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            user_id=current_user.id if current_user.is_authenticated else None,
            applicant_name=name,
            applicant_email=email,
            applicant_phone=phone,
            cover_letter=cover_letter,
            cv_filename=cv_filename,
            cv_filepath=cv_filepath,
            status='pending'
        )
        
        db.session.add(application)
        
        # Increment applications count on job
        job.applications_count = (job.applications_count or 0) + 1
        
        db.session.commit()
        
        flash('✅ Your application has been submitted successfully!', 'success')
        return redirect(url_for('jobs.job_detail', job_id=job_id))
    
    return render_template('jobs/apply.html', job=job)


# ========== RECRUITER VIEW APPLICATIONS ==========
@jobs_bp.route('/recruiter/applications')
@login_required
@recruiter_required
def recruiter_applications():
    """Recruiter view - see applications for their jobs"""
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    
    if not recruiter:
        flash('Please complete your recruiter profile first.', 'warning')
        return redirect(url_for('recruiter.setup_profile'))
    
    # Get all jobs for this recruiter
    job_ids = [job.id for job in Job.query.filter_by(recruiter_id=recruiter.id).all()]
    
    # Get applications for these jobs
    applications = JobApplication.query.filter(JobApplication.job_id.in_(job_ids))\
        .order_by(desc(JobApplication.applied_at)).all()
    
    return render_template('recruiter/applications.html',
        applications=applications,
        recruiter=recruiter
    )


@jobs_bp.route('/recruiter/applications/<int:application_id>/status', methods=['POST'])
@login_required
@recruiter_required
def update_application_status(application_id):
    """Update application status"""
    application = JobApplication.query.get_or_404(application_id)
    
    # Check if the recruiter owns the job
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
        flash(f'✅ Application status updated to {new_status}', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('jobs.recruiter_applications'))