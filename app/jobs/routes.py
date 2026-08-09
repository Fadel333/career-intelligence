# app/jobs/routes.py

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

# ========== CV FILE VALIDATION ==========
ALLOWED_CV_EXTENSIONS = {'pdf', 'docx'}
ALLOWED_CV_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
}
MAX_CV_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_cv_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_CV_EXTENSIONS


def is_valid_cv_file(file):
    """Check if file is a valid CV (PDF or DOCX)"""
    if not file:
        return False, "No file selected."
    
    if not file.filename:
        return False, "No file selected."
    
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
    if file_ext not in ['pdf', 'docx']:
        return False, "Please upload a PDF or DOCX file."
    
    if file.mimetype not in ALLOWED_CV_MIME_TYPES:
        return False, "Invalid file type. Please upload a PDF or DOCX."
    
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_CV_FILE_SIZE:
        return False, f"File too large. Maximum size is {MAX_CV_FILE_SIZE // (1024 * 1024)}MB."
    
    if size == 0:
        return False, "File is empty. Please upload a valid PDF or DOCX."
    
    return True, "Valid CV file"


# ========== HELPER FUNCTIONS ==========
def get_cv_file_path(application):
    """Get the correct CV file path - returns absolute path"""
    if not application.cv_filename and not application.cv_filepath:
        return None
    
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    if application.cv_filename:
        filename = application.cv_filename
    else:
        filename = os.path.basename(application.cv_filepath)
    
    print(f"🔍 Looking for CV file: {filename}")
    print(f"📁 Project root: {project_root}")
    
    possible_paths = [
        os.path.join(project_root, 'static', 'applications', filename),
        os.path.join(project_root, 'app', 'static', 'applications', filename),
        os.path.join(project_root, 'uploads', filename),
        os.path.join(os.getcwd(), 'static', 'applications', filename),
        os.path.join(project_root, application.cv_filepath) if application.cv_filepath else None,
        os.path.join('static', 'applications', filename),
    ]
    
    if '_' in filename:
        parts = filename.split('_', 2)
        if len(parts) >= 3:
            clean_filename = parts[2]
            possible_paths.extend([
                os.path.join(project_root, 'static', 'applications', clean_filename),
                os.path.join(project_root, 'app', 'static', 'applications', clean_filename),
                os.path.join(project_root, 'uploads', clean_filename),
                os.path.join('static', 'applications', clean_filename),
            ])
    
    for path in possible_paths:
        if path:
            abs_path = os.path.abspath(path)
            print(f"🔍 Checking: {abs_path}")
            if os.path.exists(abs_path):
                print(f"✅ Found CV at: {abs_path}")
                return abs_path
    
    static_dir = os.path.join(project_root, 'static', 'applications')
    if os.path.exists(static_dir):
        for root, dirs, files in os.walk(static_dir):
            for file in files:
                if file == filename or (len(filename.split('_')) >= 3 and file.endswith(filename.split('_')[-1])):
                    full_path = os.path.join(root, file)
                    print(f"✅ Found CV in search: {full_path}")
                    return full_path
    
    print(f"❌ CV not found. Tried: {possible_paths}")
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
    
    if job.status != 'published':
        if job.status == 'closed':
            flash('This job posting has been closed by the employer.', 'info')
        elif job.status == 'filled':
            flash('🎉 This position has been filled! Check out other opportunities below.', 'success')
        elif job.status == 'draft':
            flash('This job is not yet published.', 'warning')
        return redirect(url_for('jobs.job_board'))
    
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
        
        if cv_file and cv_file.filename:
            is_valid, error_message = is_valid_cv_file(cv_file)
            if not is_valid:
                flash(error_message, 'error')
                return redirect(url_for('jobs.apply', job_id=job_id))
            
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            upload_folder = os.path.join(project_root, 'static', 'applications')
            
            os.makedirs(upload_folder, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{timestamp}_{current_user.id if current_user.is_authenticated else 'guest'}_{cv_file.filename}")
            filepath = os.path.join(upload_folder, filename)
            cv_file.save(filepath)
            
            cv_filename = filename
            cv_filepath = os.path.join('static', 'applications', filename).replace('\\', '/')
            
            print(f"📄 CV saved to: {filepath}")
        
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
            expires_at=datetime.utcnow() + timedelta(days=30)
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
    
    job_ids = [job.id for job in Job.query.filter_by(recruiter_id=recruiter.id).all()]
    
    query = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False
    )
    
    applications = query.order_by(desc(JobApplication.applied_at)).all()
    
    expired_count = JobApplication.query.filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False,
        JobApplication.expires_at <= datetime.utcnow()
    ).count()
    
    status_counts = db.session.query(
        JobApplication.status,
        db.func.count(JobApplication.id)
    ).filter(
        JobApplication.job_id.in_(job_ids),
        JobApplication.is_deleted == False
    ).group_by(JobApplication.status).all()
    
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'applied_at')
    sort_order = request.args.get('order', 'desc')
    
    if status_filter:
        applications = [app for app in applications if app.status == status_filter]
    
    if search_query:
        applications = [app for app in applications 
                       if search_query.lower() in app.applicant_name.lower() 
                       or search_query.lower() in app.applicant_email.lower()]
    
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
    
    cv_file_path = get_cv_file_path(application)
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
    
    recruiter = RecruiterProfile.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get(application.job_id)
    
    if not recruiter or job.recruiter_id != recruiter.id:
        flash('You do not have permission to download this CV.', 'error')
        return redirect(url_for('recruiter.dashboard'))
    
    if not application.cv_filename and not application.cv_filepath:
        flash('No CV uploaded for this application.', 'warning')
        return redirect(url_for('jobs.application_detail', application_id=application.id))
    
    file_path = get_cv_file_path(application)
    
    if not file_path or not os.path.exists(file_path):
        if application.cv_filepath:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            abs_path = os.path.join(project_root, application.cv_filepath)
            if os.path.exists(abs_path):
                file_path = abs_path
        
        if not file_path or not os.path.exists(file_path):
            flash('CV file not found. Please contact support.', 'error')
            return redirect(url_for('jobs.application_detail', application_id=application.id))
    
    if not os.path.exists(file_path):
        flash('CV file not found. Please contact support.', 'error')
        return redirect(url_for('jobs.application_detail', application_id=application.id))
    
    download_name = application.cv_filename or os.path.basename(file_path)
    
    print(f"📄 Sending file: {file_path}")
    
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
        
        flash(f'✅ Application status updated to {new_status}', 'success')
    else:
        flash('Invalid status.', 'error')
    
    return redirect(url_for('jobs.recruiter_applications'))


# ========== APPLICANT APPLICATION TRACKER ==========

@jobs_bp.route('/my-applications')
@login_required
def my_applications():
    """View all applications submitted by the current user"""
    applications = JobApplication.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(desc(JobApplication.applied_at)).all()
    
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
    
    if application.status not in ['pending', 'reviewed']:
        flash('You cannot withdraw this application at this stage.', 'error')
        return redirect(url_for('jobs.my_applications'))
    
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


# ========== JOB ALERT ENDPOINTS ==========

@jobs_bp.route('/alerts/test', methods=['POST'])
@login_required
def test_alert_check():
    """Manually trigger job alert check (admin only)"""
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        from app.utils.job_alert_checker import check_job_alerts
        sent, errors = check_job_alerts()
        
        return jsonify({
            'success': True,
            'sent': sent,
            'errors': errors,
            'message': f'Checked alerts: {sent} sent, {errors} errors'
        })
    except Exception as e:
        print(f"❌ Error in test_alert_check: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@jobs_bp.route('/alert/<int:alert_id>/test', methods=['POST'])
@login_required
def test_single_alert(alert_id):
    """
    Test a single job alert - sends email via SendGrid
    
    This endpoint allows users to test their job alerts by sending
    a test email with matching jobs from the last 7 days.
    """
    print(f"🔍 TEST ALERT CALLED: alert_id={alert_id}, user={current_user.email}")
    
    from models import JobAlert
    from app.utils.job_alert_checker import find_matching_jobs, send_job_alert_notification
    
    # Get the alert
    alert = JobAlert.query.get_or_404(alert_id)
    print(f"📋 Alert found: {alert.keywords}, user_id={alert.user_id}")
    
    # Check permissions
    if alert.user_id != current_user.id and not current_user.is_admin():
        print(f"❌ Access denied for user {current_user.id} on alert {alert.user_id}")
        return jsonify({'error': 'Access denied'}), 403
    
    # Find matching jobs from the last 7 days
    print(f"🔍 Finding matching jobs for alert {alert_id}...")
    matching_jobs = find_matching_jobs(alert, datetime.utcnow() - timedelta(days=7))
    print(f"📊 Found {len(matching_jobs)} matching jobs")
    
    if matching_jobs:
        try:
            print(f"📧 Attempting to send email to {current_user.email}")
            result = send_job_alert_notification(alert, matching_jobs)
            print(f"📧 Send result: {result}")
            
            if result:
                return jsonify({
                    'success': True,
                    'message': f'✅ Test email sent to {current_user.email} with {len(matching_jobs)} matching jobs!',
                    'jobs_found': len(matching_jobs),
                    'email': current_user.email
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send email. Check server logs.'
                }), 500
        except Exception as e:
            print(f"❌ Exception in test_single_alert: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    else:
        return jsonify({
            'success': True,
            'message': 'No matching jobs found in the last 7 days.',
            'jobs_found': 0
        })


@jobs_bp.route('/alert/<int:alert_id>/jobs', methods=['GET'])
@login_required
def get_alert_matching_jobs(alert_id):
    """Get jobs matching a specific alert (API endpoint)"""
    from models import JobAlert
    from app.utils.job_alert_checker import find_matching_jobs
    
    alert = JobAlert.query.get_or_404(alert_id)
    
    if alert.user_id != current_user.id and not current_user.is_admin():
        return jsonify({'error': 'Access denied'}), 403
    
    matching_jobs = find_matching_jobs(alert, datetime.utcnow() - timedelta(days=7))
    
    jobs_data = []
    for job in matching_jobs:
        company_name = job.recruiter.company_name if job.recruiter else None
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'company': company_name,
            'location': job.location,
            'posted_at': job.posted_at.isoformat(),
            'url': url_for('jobs.job_detail', job_id=job.id, _external=True),
            'match_score': getattr(job, 'match_score', 0)
        })
    
    return jsonify({
        'success': True,
        'jobs': jobs_data,
        'count': len(jobs_data)
    })


@jobs_bp.route('/test-email', methods=['GET'])
@login_required
def test_email():
    """
    Simple endpoint to test if SendGrid email sending is working.
    Visit /jobs/test-email to test.
    """
    from app.utils.email import send_email
    
    print(f"📧 Testing email to: {current_user.email}")
    
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
                .success { background: #10b981; color: white; padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📧 Test Email</h1>
                <p>Career Intelligence - Email Test</p>
            </div>
            <div class="success">
                ✅ Email sent successfully!
            </div>
            <p>If you're seeing this email, your SendGrid configuration is working correctly.</p>
            <p><strong>Sent to:</strong> {email}</p>
            <p><strong>Sent at:</strong> {timestamp}</p>
        </body>
        </html>
        """.format(
            email=current_user.email,
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        )
        
        text_body = f"""
        Test Email from Career Intelligence
        
        If you're seeing this email, your SendGrid configuration is working correctly.
        
        Sent to: {current_user.email}
        Sent at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        
        result = send_email(
            subject="📧 Test Email from Career Intelligence",
            recipients=current_user.email,
            html_body=html_content,
            text_body=text_body
        )
        
        print(f"📧 Test email result: {result}")
        
        if result:
            return jsonify({
                'success': True,
                'email': current_user.email,
                'message': '✅ Test email sent successfully! Check your inbox (and spam folder).'
            })
        else:
            return jsonify({
                'success': False,
                'email': current_user.email,
                'error': 'Email sending failed. Check server logs for details.'
            }), 500
            
    except Exception as e:
        print(f"❌ Test email error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== JOB ALERT TRIGGER ==========
def create_job():
    """Helper function for job creation with alert triggers"""
    # ... save job to database ...
    
    # After saving, check for matching alerts
    if job.status == 'published':
        from app.utils.job_alert_checker import check_job_alerts
        import threading
        threading.Thread(target=check_job_alerts).start()