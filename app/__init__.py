from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, make_response
from flask_login import login_required, current_user
from extensions import db, login_manager
from flask_migrate import Migrate
from flask_mail import Mail
from werkzeug.utils import secure_filename
import os
import sys
import pickle
import base64
import json
import ast
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy import func


# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blueprints and utils
from app.auth.routes import auth_bp
from app.utils.cv_parser import CVParser
from app.utils.skill_analyzer import SkillAnalyzer
from app.utils.course_api import CourseAPI
from app.utils.hybrid_parser import HybridParser
from app.utils.openai_assistant import OpenAIAssistant
from app.utils.cv_detector import CVDetector
from models import User, Profile, RecruiterProfile, Candidate, Job, Placement, JobAlert, JobAlertLog, InterviewPractice, InterviewQuestion, InterviewResponse
from app.recruiter import recruiter_bp 
from app.admin.routes import admin_bp 
from app.jobs.routes import jobs_bp 
from app.cli import register_commands

# Initialize Flask-Mail ONCE
mail = Mail()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# ========== CV FILE VALIDATION ==========
ALLOWED_CV_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/msword'
}
MAX_CV_FILE_SIZE = 10 * 1024 * 1024  # 10MB


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


# Initialize hybrid parser
hybrid_parser = HybridParser()


def compress_parsed_data(data):
    """Compress large data to fit in session cookie"""
    if not data:
        return None
    try:
        pickled = pickle.dumps(data)
        compressed = base64.b64encode(pickled).decode('utf-8')
        return compressed
    except Exception as e:
        print(f"Compression error: {e}")
        return None


def decompress_parsed_data(compressed):
    """Decompress data from session"""
    if not compressed:
        return None
    
    if isinstance(compressed, dict):
        return compressed
    
    if isinstance(compressed, str):
        try:
            data = json.loads(compressed)
            if isinstance(data, dict):
                return data
        except:
            pass
        
        try:
            decoded = base64.b64decode(compressed.encode('utf-8'))
            data = pickle.loads(decoded)
            if isinstance(data, dict):
                return data
        except:
            pass
        
        try:
            if compressed.startswith('{') and compressed.endswith('}'):
                data = ast.literal_eval(compressed)
                if isinstance(data, dict):
                    return data
        except:
            pass
        
        return None
    
    return None


def allowed_file(filename):
    """Check if file has allowed extension (legacy function)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_extensions(app):
    """Initialize Flask extensions with app"""
    db.init_app(app)
    login_manager.init_app(app)


def configure_login_manager():
    """Configure Flask-Login settings"""
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'


def register_blueprints(app):
    """Register all blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/auth')


def get_parsed_data_from_session():
    """Helper to get parsed data from session with decompression"""
    data = session.get('parsed_cv', None)
    if not data:
        return None
    
    if isinstance(data, dict):
        return data
    
    if isinstance(data, str):
        try:
            result = json.loads(data)
            if isinstance(result, dict):
                return result
        except:
            pass
        
        try:
            decoded = base64.b64decode(data.encode('utf-8'))
            result = pickle.loads(decoded)
            if isinstance(result, dict):
                return result
        except:
            pass
        
        try:
            if data.startswith('{') and data.endswith('}'):
                result = ast.literal_eval(data)
                if isinstance(result, dict):
                    return result
        except:
            pass
        
        return None
    
    return None


def clear_parsed_data_from_session():
    """Clear parsed data from session"""
    if 'parsed_cv' in session:
        session.pop('parsed_cv', None)
    if 'cv_filename' in session:
        session.pop('cv_filename', None)
    if 'parsing_status' in session:
        session.pop('parsing_status', None)
    if 'detected_sector' in session:
        session.pop('detected_sector', None)
    print("🧹 Cleared all CV data from session")


def clear_user_cv_data(user_id):
    """Clear all CV data for a user from the database"""
    try:
        user = User.query.get(user_id)
        if user:
            user.cv_analysis = None
            user.detected_sector = None
            user.employability_score = None
            user.cv_filename = None
            user.cv_uploaded_at = None
            
            candidate = Candidate.query.filter_by(user_id=user_id).first()
            if candidate:
                candidate.skills = []
                candidate.employability_score = None
                candidate.cv_text = None
                candidate.cv_filename = None
                candidate.is_processed = False
            
            db.session.commit()
            print(f"🧹 Cleared CV data from database for user {user_id}")
            return True
    except Exception as e:
        print(f"❌ Error clearing user CV data: {e}")
        db.session.rollback()
        return False


def safe_delete_file(filepath):
    """Safely delete a file with error handling"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except OSError as e:
        print(f"Warning: Could not delete file {filepath}: {e}")
    return False


# ========== REAL ANALYTICS FUNCTIONS ==========

def get_real_student_count():
    """Get real number of students"""
    return User.query.filter_by(user_type='student').count()


def get_real_recruiter_count():
    """Get real number of recruiters/employers"""
    return User.query.filter_by(user_type='recruiter').count()


def get_real_university_count():
    """Get real number of university users"""
    return User.query.filter_by(user_type='university').count()


def get_real_employability_rate():
    """Calculate real average employability score from actual CVs"""
    candidates = Candidate.query.filter(Candidate.employability_score > 0).all()
    if not candidates:
        return 0
    total = sum(c.employability_score or 0 for c in candidates)
    return round(total / len(candidates), 1)


def get_real_skill_gaps_count():
    """Count unique skill gaps from real job data"""
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    jobs = Job.query.filter_by(status='published').all()
    if not jobs:
        return 0
    
    all_skills = set()
    for job in jobs[:100]:
        if job.description:
            result = parser._quick_parse(job.description)
            if result and isinstance(result, dict):
                skills_data = result.get('skills', {})
                if isinstance(skills_data, dict):
                    for category, skills in skills_data.items():
                        if isinstance(skills, list):
                            all_skills.update(skills)
                        elif isinstance(skills, str):
                            all_skills.add(skills)
                elif isinstance(skills_data, list):
                    all_skills.update(skills_data)
    
    return len(all_skills)


def get_real_job_count():
    """Get real number of published jobs"""
    return Job.query.filter_by(status='published').count()


def get_real_placement_count():
    """Get real number of placements"""
    return Placement.query.count()


def get_real_candidate_count():
    """Get real number of candidates with CVs"""
    return Candidate.query.count()


def get_department_performance():
    """Get real department performance from actual CV analysis data"""
    candidates = Candidate.query.filter(Candidate.employability_score > 0).all()
    
    if not candidates:
        return get_mock_department_performance()
    
    dept_stats = {}
    for candidate in candidates:
        user = User.query.get(candidate.user_id)
        if user and user.university_department:
            dept = user.university_department
            if dept not in dept_stats:
                dept_stats[dept] = {'total': 0, 'sum_scores': 0}
            dept_stats[dept]['total'] += 1
            dept_stats[dept]['sum_scores'] += candidate.employability_score or 0
    
    result = []
    for dept, stats in dept_stats.items():
        avg_score = stats['sum_scores'] / stats['total'] if stats['total'] > 0 else 0
        result.append({
            'name': dept,
            'employability': round(avg_score, 1),
            'students': stats['total']
        })
    
    result.sort(key=lambda x: x['employability'], reverse=True)
    return result if result else get_mock_department_performance()


def get_mock_department_performance():
    """Fallback mock data when no real data exists"""
    return [
        {'name': 'Computer Science', 'employability': 92, 'students': 340},
        {'name': 'Business Administration', 'employability': 78, 'students': 280},
        {'name': 'Engineering', 'employability': 85, 'students': 210},
        {'name': 'Information Technology', 'employability': 81, 'students': 190},
        {'name': 'Data Science', 'employability': 88, 'students': 140},
        {'name': 'Cybersecurity', 'employability': 76, 'students': 87}
    ]


def get_top_skill_gaps(parsed_data=None, limit=5):
    """Get real skill gaps from actual job market data"""
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    jobs = Job.query.filter_by(status='published').all()
    
    if not jobs:
        return get_mock_skill_gaps()
    
    all_job_skills = []
    for job in jobs[:50]:
        if job.description:
            result = parser._quick_parse(job.description)
            if result and isinstance(result, dict):
                skills_data = result.get('skills', {})
                if isinstance(skills_data, dict):
                    for category, skills in skills_data.items():
                        if isinstance(skills, list):
                            all_job_skills.extend(skills)
                        elif isinstance(skills, str):
                            all_job_skills.append(skills)
                elif isinstance(skills_data, list):
                    all_job_skills.extend(skills_data)
    
    skill_counts = Counter(all_job_skills)
    top_demands = skill_counts.most_common(20)
    
    candidate_skills = []
    if parsed_data and parsed_data.get('skills'):
        for category, skills in parsed_data['skills'].items():
            if isinstance(skills, list):
                candidate_skills.extend(skills)
            elif isinstance(skills, str):
                candidate_skills.append(skills)
    
    gaps = []
    total_jobs = len(jobs)
    for skill, count in top_demands[:10]:
        demand_pct = (count / total_jobs) * 100
        if skill not in candidate_skills:
            priority = 'Critical' if demand_pct > 60 else 'High' if demand_pct > 35 else 'Medium'
            gaps.append({
                'skill': skill,
                'demand': round(demand_pct),
                'priority': priority,
                'growth': f'+{round(demand_pct * 0.4)}%'
            })
    
    return gaps[:limit] if gaps else get_mock_skill_gaps()


def get_mock_skill_gaps():
    """Fallback mock data"""
    return [
        {'skill': 'Machine Learning', 'demand': 88, 'priority': 'Critical', 'growth': '+45%'},
        {'skill': 'Cloud Computing', 'demand': 85, 'priority': 'High', 'growth': '+35%'},
        {'skill': 'Python Programming', 'demand': 92, 'priority': 'Critical', 'growth': '+25%'},
        {'skill': 'Data Analysis', 'demand': 82, 'priority': 'High', 'growth': '+20%'},
        {'skill': 'Cybersecurity', 'demand': 78, 'priority': 'Medium', 'growth': '+30%'}
    ]


def get_industry_trends():
    """Get real industry trends from actual job data"""
    jobs = Job.query.filter_by(status='published').all()
    
    if not jobs:
        return get_mock_industry_trends()
    
    sector_counts = Counter()
    for job in jobs:
        if job.category:
            sector_counts[job.category] += 1
    
    top_sectors = sector_counts.most_common(5)
    total = sum(sector_counts.values())
    
    trends = []
    for sector, count in top_sectors:
        pct = (count / total) * 100
        growth = max(5, min(50, pct * 0.5))
        trends.append({
            'sector': sector,
            'growth': round(growth),
            'demand': round(pct)
        })
    
    return trends if trends else get_mock_industry_trends()


def get_mock_industry_trends():
    """Fallback mock data"""
    return [
        {'sector': 'Fintech', 'growth': 45, 'demand': 92},
        {'sector': 'HealthTech', 'growth': 38, 'demand': 85},
        {'sector': 'EdTech', 'growth': 32, 'demand': 78},
        {'sector': 'AgriTech', 'growth': 28, 'demand': 72},
        {'sector': 'E-commerce', 'growth': 25, 'demand': 68}
    ]


def get_curriculum_recommendations(parsed_data=None):
    """Get real curriculum recommendations from actual skill gaps"""
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    if parsed_data and parsed_data.get('skills'):
        all_skills = []
        for category, skills in parsed_data['skills'].items():
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.append(skills)
        
        detected_sector = SkillAnalyzer.detect_sector(all_skills)
        
        jobs = Job.query.filter_by(status='published').all()
        if jobs:
            job_skills = []
            for job in jobs[:30]:
                if job.description:
                    result = parser._quick_parse(job.description)
                    if result and isinstance(result, dict):
                        skills_data = result.get('skills', {})
                        if isinstance(skills_data, dict):
                            for category, skills in skills_data.items():
                                if isinstance(skills, list):
                                    job_skills.extend(skills)
                                elif isinstance(skills, str):
                                    job_skills.append(skills)
                        elif isinstance(skills_data, list):
                            job_skills.extend(skills_data)
            
            job_skill_counts = Counter(job_skills)
            
            skill_departments = {
                'Python': 'Computer Science',
                'Machine Learning': 'Computer Science',
                'Cloud Computing': 'Information Technology',
                'Data Analysis': 'Data Science',
                'SQL': 'Information Technology',
                'JavaScript': 'Computer Science',
                'React': 'Computer Science',
                'AWS': 'Information Technology',
                'Docker': 'Information Technology',
                'TensorFlow': 'Data Science',
                'Django': 'Computer Science',
                'Flask': 'Computer Science',
                'PostgreSQL': 'Information Technology',
                'Git': 'Computer Science',
                'Agile': 'Business Administration',
                'Project Management': 'Business Administration',
                'Cybersecurity': 'Cybersecurity',
                'DevOps': 'Information Technology',
                'Patient Care': 'Medicine and Surgery',
                'Medical Diagnosis': 'Medicine and Surgery',
                'Nursing Care': 'Nursing and Midwifery',
                'Pharmacy': 'Pharmacy',
                'Public Health': 'Nursing and Midwifery',
                'Teaching': 'Education',
                'Curriculum Development': 'Education',
                'Financial Analysis': 'Business Administration',
                'Accounting': 'Business Administration',
                'Crop Production': 'Agriculture',
                'Agribusiness': 'Agriculture',
                'Social Work': 'Social Science',
                'Counseling': 'Social Science',
                'Civil Engineering': 'Engineering',
                'Construction': 'Engineering'
            }
            
            dept_gaps = {}
            for skill, count in job_skill_counts.most_common(10):
                if skill not in all_skills:
                    dept = skill_departments.get(skill, 'General')
                    if dept not in dept_gaps:
                        dept_gaps[dept] = []
                    dept_gaps[dept].append(skill)
            
            recommendations = []
            for dept, skills in dept_gaps.items():
                priority = 'High' if len(skills) >= 3 else 'Medium'
                recommendations.append({
                    'department': dept,
                    'add_skills': skills[:3],
                    'remove_skills': [],
                    'priority': priority
                })
            
            return recommendations if recommendations else get_curriculum_recommendations_default()
    
    return get_curriculum_recommendations_default()


def get_curriculum_recommendations_default():
    """Fallback curriculum recommendations"""
    return [
        {
            'department': 'Computer Science',
            'add_skills': ['Python', 'Machine Learning', 'Cloud Computing'],
            'remove_skills': ['COBOL', 'Pascal'],
            'priority': 'High'
        },
        {
            'department': 'Business Administration',
            'add_skills': ['Data Analysis', 'Digital Marketing', 'Project Management'],
            'remove_skills': [],
            'priority': 'Medium'
        },
        {
            'department': 'Engineering',
            'add_skills': ['CAD Software', 'Renewable Energy', 'IoT'],
            'remove_skills': ['Manual Drafting'],
            'priority': 'High'
        },
        {
            'department': 'Information Technology',
            'add_skills': ['Cybersecurity', 'Cloud Computing', 'DevOps'],
            'remove_skills': ['Legacy Systems'],
            'priority': 'High'
        },
        {
            'department': 'Data Science',
            'add_skills': ['TensorFlow', 'PyTorch', 'Big Data'],
            'remove_skills': ['Excel Basics'],
            'priority': 'Medium'
        }
    ]


def get_real_job_matches(user_skills, limit=10):
    """Get real job matches based on user skills"""
    if not user_skills:
        return []
    
    jobs = Job.query.filter_by(status='published').all()
    if not jobs:
        return []
    
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    scored_jobs = []
    for job in jobs:
        result = parser._quick_parse(job.description or '')
        
        job_skills = []
        if result and isinstance(result, dict):
            skills_data = result.get('skills', {})
            if isinstance(skills_data, dict):
                for category, skills in skills_data.items():
                    if isinstance(skills, list):
                        job_skills.extend(skills)
                    elif isinstance(skills, str):
                        job_skills.append(skills)
            elif isinstance(skills_data, list):
                job_skills = skills_data
        
        if job_skills:
            match_count = len(set(user_skills) & set(job_skills))
            match_score = (match_count / len(job_skills)) * 100
            
            scored_jobs.append({
                'job': job,
                'score': round(match_score, 1),
                'matched_skills': list(set(user_skills) & set(job_skills))[:5],
                'total_skills': len(job_skills)
            })
    
    scored_jobs.sort(key=lambda x: x['score'], reverse=True)
    return scored_jobs[:limit]


# ========== TRENDING SKILLS FUNCTIONS ==========
def get_trending_skills(limit=10):
    """Get trending skills from job market data"""
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    jobs = Job.query.filter_by(status='published').all()
    if not jobs:
        return [
            {'skill': 'Python', 'growth': '+45%', 'demand': 92},
            {'skill': 'Machine Learning', 'growth': '+38%', 'demand': 88},
            {'skill': 'Cloud Computing', 'growth': '+35%', 'demand': 85},
            {'skill': 'Data Analysis', 'growth': '+30%', 'demand': 82},
            {'skill': 'Cybersecurity', 'growth': '+28%', 'demand': 78}
        ]
    
    all_job_skills = []
    for job in jobs[:50]:
        if job.description:
            result = parser._quick_parse(job.description)
            if result and isinstance(result, dict):
                skills_data = result.get('skills', {})
                if isinstance(skills_data, dict):
                    for category, skills in skills_data.items():
                        if isinstance(skills, list):
                            all_job_skills.extend(skills)
                        elif isinstance(skills, str):
                            all_job_skills.append(skills)
                elif isinstance(skills_data, list):
                    all_job_skills.extend(skills_data)
    
    skill_counts = Counter(all_job_skills)
    top_skills = skill_counts.most_common(limit)
    
    trending = []
    total_jobs = len(jobs)
    for skill, count in top_skills:
        demand_pct = (count / total_jobs) * 100 if total_jobs > 0 else 0
        growth = min(50, max(5, demand_pct * 0.4))
        trending.append({
            'skill': skill,
            'growth': f'+{round(growth)}%',
            'demand': round(demand_pct)
        })
    
    return trending if trending else get_mock_trending_skills()


def get_mock_trending_skills():
    """Fallback trending skills"""
    return [
        {'skill': 'Python', 'growth': '+45%', 'demand': 92},
        {'skill': 'Machine Learning', 'growth': '+38%', 'demand': 88},
        {'skill': 'Cloud Computing', 'growth': '+35%', 'demand': 85},
        {'skill': 'Data Analysis', 'growth': '+30%', 'demand': 82},
        {'skill': 'Cybersecurity', 'growth': '+28%', 'demand': 78}
    ]


# ========== RECRUITER HUB HELPER FUNCTIONS ==========
def get_recruiter_stats(recruiter_id):
    """Get real recruiter statistics"""
    total_jobs = Job.query.filter_by(recruiter_id=recruiter_id).count()
    active_jobs = Job.query.filter_by(recruiter_id=recruiter_id, status='published').count()
    total_placements = Placement.query.filter_by(recruiter_id=recruiter_id).count()
    
    total_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter_id, commission_paid=True).scalar() or 0
    
    pending_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter_id, commission_paid=False)\
        .filter(Placement.status == 'hired').scalar() or 0
    
    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_placements': total_placements,
        'total_earnings': float(total_earnings),
        'pending_earnings': float(pending_earnings)
    }


def register_routes(app):
    """Register all application routes"""
    
    # ========== PUBLIC ROUTES ==========
    @app.route('/')
    def index():
        stats = {
            'students': get_real_student_count(),
            'employers': get_real_recruiter_count(),
            'jobs': get_real_job_count(),
            'placements': get_real_placement_count()
        }
        return render_template('base.html', stats=stats)
    
    @app.route('/privacy-policy')
    def privacy_policy():
        return render_template('privacy_policy.html')
    
    @app.route('/terms-of-use')
    def terms_of_use():
        return render_template('terms_of_use.html')

    @app.route('/methodology')
    def methodology():
        """Methodology page explaining how TalentForge AI works"""
        return render_template('methodology.html')

    # ========== STUDENT-ONLY ROUTES ==========
    @app.route('/upload-cv', methods=['GET', 'POST'])
    @login_required
    def upload_cv():
        if current_user.is_recruiter():
            flash('Recruiters cannot upload CVs. This feature is for job seekers.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('Admins cannot upload CVs.', 'warning')
            return redirect(url_for('admin.index'))
        
        if request.method == 'POST':
            if 'cv_file' not in request.files:
                flash('No file selected', 'error')
                return redirect(url_for('upload_cv'))
            
            file = request.files['cv_file']
            
            if file.filename == '':
                flash('No file selected', 'error')
                return redirect(url_for('upload_cv'))
            
            # ---- validate file type / size ----
            is_valid, error_message = is_valid_cv_file(file)
            if not is_valid:
                flash(error_message, 'error')
                return redirect(url_for('upload_cv'))
            
            # ---- save file to disk ----
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # ---- CV content detection ----
            try:
                text = hybrid_parser._extract_text_fast(filepath)
                
                if not text:
                    flash("⚠️ Could not read file content. Please ensure it's a valid PDF or DOCX.", "error")
                    safe_delete_file(filepath)
                    clear_parsed_data_from_session()
                    clear_user_cv_data(current_user.id)
                    return redirect(url_for('upload_cv'))
                
                is_cv, confidence, reason = CVDetector.detect(text)
                
                print(f"📊 CV Detection Report:")
                print(f"   - Is CV: {is_cv}")
                print(f"   - Confidence: {confidence*100:.1f}%")
                print(f"   - Reason: {reason}")
                
                if not is_cv:
                    flash(f"❌ CV detection failed: {reason} (Confidence: {confidence*100:.1f}%)", 'error')
                    safe_delete_file(filepath)
                    clear_parsed_data_from_session()
                    clear_user_cv_data(current_user.id)
                    return redirect(url_for('upload_cv'))
                
                # Reject if confidence is too low
                if confidence < 0.3:
                    print(f"⚠️ LOW CONFIDENCE: {confidence*100:.1f}% - rejecting file")
                    flash(f"⚠️ File doesn't appear to be a valid CV (Confidence: {confidence*100:.1f}%). Please upload a proper CV/resume.", 'error')
                    safe_delete_file(filepath)
                    clear_parsed_data_from_session()
                    clear_user_cv_data(current_user.id)
                    return redirect(url_for('upload_cv'))
                
                print(f"✅ CV Detection: {reason} (Confidence: {confidence*100:.1f}%)")
                
            except Exception as e:
                print(f"CV detection error: {e}")
                flash('Error validating CV content. Please try again.', 'error')
                safe_delete_file(filepath)
                clear_parsed_data_from_session()
                clear_user_cv_data(current_user.id)
                return redirect(url_for('upload_cv'))
            
            flash('Processing CV... Please wait.', 'info')
            
            # ---- full parse + persist ----
            try:
                parsed_data = hybrid_parser.parse_hybrid(filepath, current_user.id)
                
                if parsed_data:
                    # Extra safety check
                    if parsed_data.get('is_cv') is False:
                        print(f"🚫 Parser rejected: Not a CV")
                        flash(f"❌ File is not a valid CV: {parsed_data.get('reason', 'Unknown reason')}", 'error')
                        safe_delete_file(filepath)
                        clear_parsed_data_from_session()
                        clear_user_cv_data(current_user.id)
                        return redirect(url_for('upload_cv'))
                    
                    user = User.query.get(current_user.id)
                    if user:
                        all_skills = []
                        for category, skills in parsed_data.get('skills', {}).items():
                            if isinstance(skills, list):
                                all_skills.extend(skills)
                            elif isinstance(skills, str):
                                all_skills.append(skills)
                        
                        detected_sector = SkillAnalyzer.detect_sector(all_skills)
                        parsed_data['detected_sector'] = detected_sector
                        
                        market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
                            detected_sector, 
                            SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
                        )
                        
                        employability = SkillAnalyzer.calculate_employability_score(
                            all_skills, 
                            parsed_data.get('experience_years', 0),
                            market_demands
                        )
                        
                        parsed_data['employability_score'] = employability['score']
                        
                        user.save_cv_analysis(parsed_data)
                        user.detected_sector = detected_sector
                        user.employability_score = employability['score']
                        user.cv_filename = file.filename
                        user.cv_uploaded_at = datetime.utcnow()
                        
                        existing_candidate = Candidate.query.filter_by(user_id=current_user.id).first()
                        if existing_candidate:
                            existing_candidate.name = user.fullname
                            existing_candidate.email = user.email
                            existing_candidate.skills = all_skills
                            existing_candidate.experience_years = parsed_data.get('experience_years', 0)
                            existing_candidate.education = parsed_data.get('education', [])
                            existing_candidate.certifications = parsed_data.get('certifications', [])
                            existing_candidate.employability_score = employability['score']
                            existing_candidate.cv_text = parsed_data.get('raw_text', '')
                            existing_candidate.is_processed = True
                            existing_candidate.last_updated = datetime.utcnow()
                            existing_candidate.cv_filename = file.filename
                        else:
                            candidate = Candidate(
                                user_id=current_user.id,
                                name=user.fullname,
                                email=user.email,
                                phone=user.phone,
                                skills=all_skills,
                                experience_years=parsed_data.get('experience_years', 0),
                                education=parsed_data.get('education', []),
                                certifications=parsed_data.get('certifications', []),
                                employability_score=employability['score'],
                                cv_text=parsed_data.get('raw_text', ''),
                                cv_filename=file.filename,
                                is_processed=True
                            )
                            db.session.add(candidate)
                        
                        db.session.commit()
                        print(f"✅ CV data saved to database for user {user.email}")
                    
                    try:
                        json_data = json.dumps(parsed_data)
                        if len(json_data) > 4000:
                            session['parsed_cv'] = compress_parsed_data(parsed_data)
                        else:
                            session['parsed_cv'] = json_data
                        session['cv_filename'] = file.filename
                        session['parsing_status'] = parsed_data.get('status', 'processing')
                        print(f"✅ Stored CV data in session with {parsed_data.get('total_skills', 0)} skills")
                    except Exception as e:
                        print(f"❌ Error storing session data: {e}")
                        flash('Error storing CV data. Please try again.', 'error')
                        safe_delete_file(filepath)
                        clear_parsed_data_from_session()
                        return redirect(url_for('upload_cv'))
                    
                    flash(f'✅ CV uploaded! Quick analysis complete. Found {parsed_data["total_skills"]} skills.', 'success')
                    return redirect(url_for('skill_analysis'))
                else:
                    flash('Could not parse CV. Please ensure it\'s readable.', 'error')
                    safe_delete_file(filepath)
                    clear_parsed_data_from_session()
                    clear_user_cv_data(current_user.id)
                    return redirect(url_for('upload_cv'))
            except Exception as e:
                print(f"Error: {e}")
                flash(f'Error parsing CV: {str(e)}', 'error')
                safe_delete_file(filepath)
                clear_parsed_data_from_session()
                clear_user_cv_data(current_user.id)
                return redirect(url_for('upload_cv'))
        
        return render_template('upload_cv.html', user=current_user)
    
    @app.route('/skill-analysis')
    @login_required
    def skill_analysis():
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        # FIRST: Try to get data from database (most reliable)
        user = User.query.get(current_user.id)
        parsed_data = None
        showing_previous_cv = False
        
        if user and user.cv_analysis:
            parsed_data = user.get_cv_analysis()
            showing_previous_cv = True
            print(f"📊 Skill Analysis: Retrieved {parsed_data.get('total_skills', 0)} skills from database")
            
            if parsed_data and isinstance(parsed_data, dict):
                try:
                    session['parsed_cv'] = json.dumps(parsed_data)
                    session['cv_filename'] = user.cv_filename
                    session['parsing_status'] = 'complete'
                except Exception as e:
                    print(f"Error updating session: {e}")
        else:
            # SECOND: Try session as fallback
            parsed_data = get_parsed_data_from_session()
            if parsed_data and isinstance(parsed_data, dict):
                print(f"📊 Skill Analysis: Retrieved {parsed_data.get('total_skills', 0)} skills from session")
        
        if not parsed_data or not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if not parsed_data.get('skills'):
            parsed_data['skills'] = {}
        
        # Check if we have any actual data
        has_data = False
        if parsed_data and parsed_data.get('skills'):
            for category, skills in parsed_data['skills'].items():
                if skills:
                    has_data = True
                    break
        
        if not has_data:
            print(f"⚠️ No CV data found for user {current_user.id}")
            return render_template('skill_analysis.html', 
                                 user=current_user, 
                                 parsed_data={'skills': {}},
                                 is_processing=False,
                                 detected_sector=None,
                                 employability={'score': 0, 'level': 'Beginner', 'color': 'red',
                                              'total_skills_matched': 0, 'base_score': 0, 'experience_bonus': 0},
                                 gaps=[],
                                 roadmap={'immediate': [], 'short_term': [], 'medium_term': [], 'long_term': []},
                                 job_matches=[],
                                 all_skills=[],
                                 no_cv=True,
                                 showing_previous_cv=showing_previous_cv)
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.append(skills)
            
            print(f"📊 Total skills extracted: {len(all_skills)}")
            print(f"📂 Skill categories: {list(parsed_data['skills'].keys())}")
            
            detected_sector = SkillAnalyzer.detect_sector(all_skills)
            session['detected_sector'] = detected_sector
            
            market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
                detected_sector, 
                SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
            )
            
            employability = SkillAnalyzer.calculate_employability_score(
                all_skills, 
                parsed_data.get('experience_years', 0),
                market_demands
            )
            
            gaps = SkillAnalyzer.analyze_gaps(all_skills, market_demands)
            roadmap = SkillAnalyzer.generate_learning_roadmap(gaps)
            job_matches = get_real_job_matches(all_skills)
            
            return render_template('skill_analysis.html', 
                                 user=current_user, 
                                 parsed_data=parsed_data,
                                 employability=employability,
                                 gaps=gaps,
                                 roadmap=roadmap,
                                 job_matches=job_matches,
                                 all_skills=all_skills,
                                 is_processing=False,
                                 detected_sector=detected_sector.capitalize(),
                                 no_cv=False,
                                 showing_previous_cv=showing_previous_cv)
        
        return render_template('skill_analysis.html', 
                             user=current_user, 
                             parsed_data={'skills': {}},
                             is_processing=False, 
                             no_cv=True,
                             showing_previous_cv=showing_previous_cv)
    
    @app.route('/learning-roadmap')
    @login_required
    def learning_roadmap():
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data or not isinstance(parsed_data, dict):
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data and isinstance(parsed_data, dict):
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                    except:
                        pass
                else:
                    parsed_data = {}
        
        if not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if not parsed_data.get('skills'):
            parsed_data['skills'] = {}
        
        course_api = CourseAPI()
        
        return render_template('learning_roadmap.html', 
                             user=current_user, 
                             parsed_data=parsed_data,
                             skill_analyzer=SkillAnalyzer,
                             course_api=course_api,
                             no_cv=not parsed_data or not parsed_data.get('skills'))

    @app.route('/job-matches')
    @login_required
    def job_matches():
        if not current_user or not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        session_data = get_parsed_data_from_session()
        
        parsed_data = {}
        if session_data and isinstance(session_data, dict):
            parsed_data = session_data
        else:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                db_data = user.get_cv_analysis()
                if db_data and isinstance(db_data, dict):
                    parsed_data = db_data
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                    except Exception as e:
                        print(f"Error storing session data: {e}")
        
        if not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if 'skills' not in parsed_data:
            parsed_data['skills'] = {}
        
        if parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.append(skills)
            
            job_matches = get_real_job_matches(all_skills)
            return render_template('job_matches.html', 
                                 user=current_user, 
                                 job_matches=job_matches,
                                 parsed_data=parsed_data,
                                 skill_analyzer=SkillAnalyzer,
                                 no_cv=False)
        
        return render_template('job_matches.html', 
                             user=current_user, 
                             job_matches=None, 
                             parsed_data={'skills': {}},
                             skill_analyzer=SkillAnalyzer, 
                             no_cv=True)

    @app.route('/career-assistant')
    @login_required
    def career_assistant():
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data or not isinstance(parsed_data, dict):
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data and isinstance(parsed_data, dict):
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                    except:
                        pass
                else:
                    parsed_data = {}
        
        if not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if not parsed_data.get('skills'):
            parsed_data['skills'] = {}
        
        return render_template('career_assistant.html', user=current_user, parsed_data=parsed_data)
    
    @app.route('/api/ask', methods=['POST'])
    @login_required
    def api_ask():
        if current_user.is_recruiter() or current_user.is_admin():
            return jsonify({'error': 'This feature is for job seekers only.'}), 403
        
        data = request.get_json()
        question = data.get('question', '')
        
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data or not isinstance(parsed_data, dict):
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if not isinstance(parsed_data, dict):
                    parsed_data = {}
        
        user_skills = []
        experience = 0
        sector = 'general'
        
        if parsed_data:
            for category, skills in parsed_data.get('skills', {}).items():
                if isinstance(skills, list):
                    user_skills.extend(skills)
                elif isinstance(skills, str):
                    user_skills.append(skills)
            experience = parsed_data.get('experience_years', 0)
            sector = SkillAnalyzer.detect_sector(user_skills)
        
        assistant = OpenAIAssistant()
        response = assistant.get_response(question, user_skills, experience, sector)
        
        return jsonify(response)
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # FIRST: Check if current user has data in database
        user = User.query.get(current_user.id)
        parsed_data = None
        
        # Try to get data from database first
        if user and user.cv_analysis:
            parsed_data = user.get_cv_analysis()
            print(f"📊 Dashboard: Retrieved {parsed_data.get('total_skills', 0)} skills from database for user {current_user.id}")
            
            if parsed_data and isinstance(parsed_data, dict):
                try:
                    session['parsed_cv'] = json.dumps(parsed_data)
                    session['cv_filename'] = user.cv_filename
                except Exception as e:
                    print(f"Error updating session: {e}")
        else:
            # If no data in database, clear session to prevent showing old data
            clear_parsed_data_from_session()
            print(f"📊 Dashboard: No CV data found for user {current_user.id}, cleared session")
            parsed_data = {}
        
        # If still no data, try session as fallback (but only if it belongs to current user)
        if not parsed_data or not isinstance(parsed_data, dict) or not parsed_data.get('skills'):
            session_data = get_parsed_data_from_session()
            if session_data and isinstance(session_data, dict):
                # Only use session data if it has skills
                if session_data.get('skills'):
                    parsed_data = session_data
                    print(f"📊 Dashboard: Using session data for user {current_user.id}")
                else:
                    clear_parsed_data_from_session()
                    parsed_data = {}
                    print(f"📊 Dashboard: Cleared empty session data")

        if not parsed_data or not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if not parsed_data.get('skills'):
            parsed_data['skills'] = {}
        
        # ========== REAL STATS ==========
        all_skills = []
        for category, skills in parsed_data.get('skills', {}).items():
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.append(skills)
        
        # 1. Employability Score
        employability_score = current_user.employability_score or 0
        if employability_score == 0 and all_skills:
            detected_sector = SkillAnalyzer.detect_sector(all_skills)
            market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
                detected_sector,
                SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
            )
            employability_result = SkillAnalyzer.calculate_employability_score(
                all_skills,
                parsed_data.get('experience_years', 0),
                market_demands
            )
            employability_score = employability_result.get('score', 0)
        
        # 2. Skills Identified
        skills_identified = len(all_skills)
        
        # 3. Courses Recommended
        courses_recommended = 0
        gaps = []
        if all_skills:
            detected_sector = SkillAnalyzer.detect_sector(all_skills)
            market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
                detected_sector,
                SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
            )
            gaps = SkillAnalyzer.analyze_gaps(all_skills, market_demands)
            if gaps:
                courses_recommended = len(gaps) * 2
        
        # 4. Job Matches
        job_matches = get_real_job_matches(all_skills, limit=10)
        job_matches_count = len(job_matches)
        
        # 5. Learning Roadmap
        roadmap = SkillAnalyzer.generate_learning_roadmap(gaps) if gaps else {'immediate': [], 'short_term': [], 'medium_term': [], 'long_term': []}
        
        # 6. Recent Activity
        recent_activity = []
        
        if hasattr(current_user, 'cv_uploaded_at') and current_user.cv_uploaded_at:
            recent_activity.append({
                'action': 'CV Uploaded',
                'description': f'You uploaded your CV',
                'time': current_user.cv_uploaded_at,
                'icon': 'fas fa-file-upload',
                'color': 'text-teal-400'
            })
        
        if current_user.profile and current_user.profile.updated_at:
            recent_activity.append({
                'action': 'Profile Updated',
                'description': 'You updated your profile information',
                'time': current_user.profile.updated_at,
                'icon': 'fas fa-user-edit',
                'color': 'text-purple-400'
            })
        
        if job_matches_count > 0:
            recent_activity.append({
                'action': 'Job Matches Found',
                'description': f'Found {job_matches_count} jobs matching your skills',
                'time': datetime.utcnow(),
                'icon': 'fas fa-briefcase',
                'color': 'text-green-400'
            })
        
        if skills_identified > 0:
            recent_activity.append({
                'action': 'Skill Analysis Complete',
                'description': f'Identified {skills_identified} skills from your CV',
                'time': current_user.cv_uploaded_at or datetime.utcnow(),
                'icon': 'fas fa-chart-bar',
                'color': 'text-blue-400'
            })
        
        recent_activity.sort(key=lambda x: x['time'], reverse=True)
        
        # 7. Trending Skills
        trending_skills = get_trending_skills()
        
        # 8. Skill Categories Breakdown
        skill_categories = {}
        if isinstance(parsed_data, dict):
            skills_data = parsed_data.get('skills', {})
            if isinstance(skills_data, dict):
                for category, skills in skills_data.items():
                    if skills:
                        if isinstance(skills, list):
                            skill_categories[category] = len(skills)
                        elif isinstance(skills, (str, int, float)):
                            skill_categories[category] = 1
                        else:
                            skill_categories[category] = 0

        if not skill_categories or not isinstance(skill_categories, dict):
            skill_categories = {}

        stats = {
            'employability_score': employability_score,
            'skills_identified': skills_identified,
            'courses_recommended': courses_recommended,
            'job_matches_count': job_matches_count,
            'job_matches': job_matches[:5],
            'recent_activity': recent_activity[:5],
            'trending_skills': trending_skills[:5],
            'skill_categories': skill_categories,
            'all_skills': all_skills
        }
        
        if current_user.is_recruiter(): 
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        
        return render_template('dashboard.html', 
                             user=current_user, 
                             parsed_data=parsed_data,
                             stats=stats,
                             gaps=gaps[:4],
                             roadmap=roadmap)
    
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        if request.method == 'POST':
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            bio = request.form.get('bio')
            location = request.form.get('location')
            phone = request.form.get('phone')
            current_job = request.form.get('current_job')
            company = request.form.get('company')
            skills = request.form.get('skills')
            university_department = request.form.get('university_department')
            
            user = User.query.get(current_user.id)
            if user:
                user.fullname = fullname or user.fullname
                user.email = email or user.email
                user.bio = bio or user.bio
                user.location = location or user.location
                user.phone = phone or user.phone
                user.university_department = university_department or user.university_department
                
                if user.profile:
                    user.profile.current_job = current_job or user.profile.current_job
                    user.profile.company = company or user.profile.company
                    user.profile.skills = skills or user.profile.skills
                else:
                    profile = Profile(
                        user_id=user.id,
                        current_job=current_job,
                        company=company,
                        skills=skills
                    )
                    db.session.add(profile)
                
                db.session.commit()
                flash('Profile updated successfully!', 'success')
            
            return redirect(url_for('profile'))
        
        return render_template('profile.html', user=current_user)
    
    @app.route('/upload-profile-pic', methods=['POST'])
    @login_required
    def upload_profile_pic():
        if 'profile_pic' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return jsonify({'success': False, 'message': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP.'})
        
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        filepath = os.path.join('static/profile_pics', filename)
        
        os.makedirs('static/profile_pics', exist_ok=True)
        
        if current_user.profile_image:
            old_path = os.path.join('static/profile_pics', current_user.profile_image)
            safe_delete_file(old_path)
        
        file.save(filepath)
        
        current_user.profile_image = filename
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile picture updated successfully!'})
    
    # ========== NOTIFICATION SETTINGS ROUTE ==========
    @app.route('/update-notification-settings', methods=['POST'])
    @login_required
    def update_notification_settings():
        user = User.query.get(current_user.id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('profile'))
        
        user.receive_notifications = request.form.get('receive_notifications') == 'true'
        user.email_notifications = request.form.get('email_notifications') == 'true'
        user.sms_notifications = request.form.get('sms_notifications') == 'true'
        user.notification_frequency = request.form.get('notification_frequency', 'daily')
        
        db.session.commit()
        flash('✅ Notification settings updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    @app.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        from werkzeug.security import generate_password_hash, check_password_hash
        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('profile'))
        
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('profile'))
        
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('profile'))
        
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    @app.route('/university-dashboard')
    @login_required
    def university_dashboard():
        if not current_user.is_university():
            flash('This feature is for university administrators only.', 'warning')
            if current_user.is_recruiter():
                return redirect(url_for('recruiter.dashboard'))
            elif current_user.is_admin():
                return redirect(url_for('admin.index'))
            else:
                return redirect(url_for('dashboard'))
        
        parsed_data = get_parsed_data_from_session()
        
        if not isinstance(parsed_data, dict):
            parsed_data = {}
        
        analytics = {
            'total_students': get_real_student_count(),
            'employability_rate': get_real_employability_rate(),
            'skill_gaps_identified': get_real_skill_gaps_count(),
            'partners': get_real_recruiter_count(),
            'jobs': get_real_job_count(),
            'departments': get_department_performance(),
            'top_skill_gaps': get_top_skill_gaps(parsed_data),
            'industry_trends': get_industry_trends(),
            'curriculum_recommendations': get_curriculum_recommendations(parsed_data)
        }
        
        current_time = datetime.now().strftime('%H:%M')
        
        return render_template('university_dashboard.html',
                             user=current_user,
                             analytics=analytics,
                             parsed_data=parsed_data,
                             current_time=current_time)
    
    @app.route('/api/parsing-status')
    @login_required
    def parsing_status():
        parsed_data = get_parsed_data_from_session()
        parsing_status = session.get('parsing_status', 'complete')
        
        if parsed_data and isinstance(parsed_data, dict):
            status = parsed_data.get('status', parsing_status)
            return jsonify({
                'status': status,
                'total_skills': parsed_data.get('total_skills', 0)
            })
        
        return jsonify({'status': 'unknown'})

    # ========== JOB ALERTS ROUTES ==========
    @app.route('/job-alerts')
    @login_required
    def job_alerts():
        alerts = JobAlert.query.filter_by(user_id=current_user.id).all()
        return render_template('job_alerts.html', user=current_user, alerts=alerts)

    @app.route('/job-alerts/create', methods=['GET', 'POST'])
    @login_required
    def create_job_alert():
        if request.method == 'POST':
            keywords = request.form.get('keywords')
            job_type = request.form.get('job_type')
            location = request.form.get('location')
            salary_min = request.form.get('salary_min', type=float)
            salary_max = request.form.get('salary_max', type=float)
            category = request.form.get('category')
            experience_level = request.form.get('experience_level')
            frequency = request.form.get('frequency', 'daily')
            
            try:
                alert = JobAlert(
                    user_id=current_user.id,
                    keywords=keywords,
                    job_type=job_type,
                    location=location,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    category=category,
                    experience_level=experience_level,
                    frequency=frequency
                )
                db.session.add(alert)
                db.session.commit()
                
                flash('✅ Job alert created successfully!', 'success')
                return redirect(url_for('job_alerts'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating alert: {str(e)}', 'error')
        
        categories = [
            'Technology', 'Healthcare', 'Law', 'Finance', 'Education',
            'Agriculture', 'Business', 'Creative Arts', 'Trades',
            'Engineering', 'Social Services', 'Customer Service',
            'Administration', 'Sales', 'Marketing'
        ]
        
        return render_template('create_job_alert.html', 
                             user=current_user, 
                             categories=categories)

    @app.route('/job-alerts/<int:alert_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_job_alert(alert_id):
        alert = JobAlert.query.get_or_404(alert_id)
        
        if alert.user_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('job_alerts'))
        
        if request.method == 'POST':
            try:
                alert.keywords = request.form.get('keywords')
                alert.job_type = request.form.get('job_type')
                alert.location = request.form.get('location')
                alert.salary_min = request.form.get('salary_min', type=float)
                alert.salary_max = request.form.get('salary_max', type=float)
                alert.category = request.form.get('category')
                alert.experience_level = request.form.get('experience_level')
                alert.frequency = request.form.get('frequency', 'daily')
                alert.is_active = 'is_active' in request.form
                
                db.session.commit()
                flash('✅ Alert updated successfully!', 'success')
                return redirect(url_for('job_alerts'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating alert: {str(e)}', 'error')
        
        categories = [
            'Technology', 'Healthcare', 'Law', 'Finance', 'Education',
            'Agriculture', 'Business', 'Creative Arts', 'Trades',
            'Engineering', 'Social Services', 'Customer Service',
            'Administration', 'Sales', 'Marketing'
        ]
        
        return render_template('edit_job_alert.html', 
                             user=current_user, 
                             alert=alert,
                             categories=categories)

    @app.route('/job-alerts/<int:alert_id>/delete', methods=['POST'])
    @login_required
    def delete_job_alert(alert_id):
        alert = JobAlert.query.get_or_404(alert_id)
        
        if alert.user_id != current_user.id:
            flash('Access denied', 'error')
            return redirect(url_for('job_alerts'))
        
        try:
            db.session.delete(alert)
            db.session.commit()
            flash('Alert deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error deleting alert: {str(e)}', 'error')
        
        return redirect(url_for('job_alerts'))

    @app.route('/job-alerts/<int:alert_id>/toggle', methods=['POST'])
    @login_required
    def toggle_job_alert(alert_id):
        alert = JobAlert.query.get_or_404(alert_id)
        
        if alert.user_id != current_user.id:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        try:
            alert.is_active = not alert.is_active
            db.session.commit()
            return jsonify({
                'success': True,
                'is_active': alert.is_active,
                'message': 'Alert ' + ('activated' if alert.is_active else 'deactivated')
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500

    @app.route('/check-alerts')
    @login_required
    def check_alerts_manually():
        if not current_user or not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('Only admins can trigger alerts manually.', 'warning')
            return redirect(url_for('dashboard'))
        
        try:
            from app.utils.job_alert_checker import check_job_alerts
            sent, errors = check_job_alerts()
            flash(f'✅ Check complete: {sent} notifications sent, {errors} errors', 'success')
        except Exception as e:
            flash(f'❌ Error checking alerts: {str(e)}', 'error')
        
        return redirect(url_for('admin.index'))

    @app.route('/api/job-alerts/check-new')
    @login_required
    def check_new_jobs_for_alerts():
        alerts = JobAlert.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        results = []
        for alert in alerts:
            last_sent = alert.last_sent_at or datetime.utcnow() - timedelta(days=7)
            jobs = Job.query.filter(
                Job.status == 'published',
                Job.posted_at > last_sent
            ).all()
            
            matching_jobs = [job for job in jobs if alert.matches_job(job)]
            
            if matching_jobs:
                results.append({
                    'alert_id': alert.id,
                    'count': len(matching_jobs),
                    'jobs': [{'id': j.id, 'title': j.title} for j in matching_jobs[:5]]
                })
        
        return jsonify({
            'total_alerts': len(alerts),
            'alerts_with_new_jobs': len(results),
            'results': results
        })
    
    # ========== INTERVIEW PRACTICE ROUTES ==========
    @app.route('/interview-practice')
    @login_required
    def interview_practice_hub():
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        sessions = InterviewPractice.query.filter_by(
            user_id=current_user.id
        ).order_by(InterviewPractice.created_at.desc()).all()
        
        return render_template('interview/hub.html',
            user=current_user,
            sessions=sessions
        )

    @app.route('/interview-practice/setup', methods=['GET', 'POST'])
    @login_required
    def interview_practice_setup():
        if current_user.is_recruiter() or current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('dashboard'))
        
        skills = []
        parsed_data = get_parsed_data_from_session()
        if parsed_data and parsed_data.get('skills'):
            for category, skill_list in parsed_data['skills'].items():
                if isinstance(skill_list, list):
                    skills.extend(skill_list)
                elif isinstance(skill_list, str):
                    skills.append(skill_list)
        
        if request.method == 'POST':
            job_title = request.form.get('job_title')
            industry = request.form.get('industry')
            experience_level = request.form.get('experience_level', 'mid')
            question_type = request.form.get('question_type', 'technical')
            num_questions = int(request.form.get('num_questions', 5))
            
            if not job_title:
                flash('Please enter a job title.', 'error')
                return redirect(url_for('interview_practice_setup'))
            
            try:
                practice = InterviewPractice(
                    user_id=current_user.id,
                    job_title=job_title,
                    industry=industry,
                    experience_level=experience_level,
                    question_type=question_type,
                    status='in_progress'
                )
                db.session.add(practice)
                db.session.flush()
                
                questions = generate_interview_questions(
                    job_title=job_title,
                    industry=industry,
                    experience_level=experience_level,
                    question_type=question_type,
                    skills=skills,
                    num_questions=num_questions
                )
                
                for i, q in enumerate(questions):
                    question = InterviewQuestion(
                        practice_id=practice.id,
                        question_text=q['question'],
                        question_type=q.get('type', question_type),
                        category=q.get('category'),
                        difficulty=q.get('difficulty', 'medium'),
                        order=i,
                        expected_answer=q.get('expected_answer'),
                        tips=q.get('tips')
                    )
                    db.session.add(question)
                
                db.session.commit()
                
                flash('✅ Interview practice session created!', 'success')
                return redirect(url_for('interview_practice_session', practice_id=practice.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating interview session: {str(e)}', 'error')
                return redirect(url_for('interview_practice_setup'))
        
        return render_template('interview/setup.html',
            user=current_user,
            skills=skills[:10]
        )

    @app.route('/interview-practice/<int:practice_id>')
    @login_required
    def interview_practice_session(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        questions = InterviewQuestion.query.filter_by(
            practice_id=practice.id
        ).order_by(InterviewQuestion.order).all()
        
        responses = {}
        for q in questions:
            response = InterviewResponse.query.filter_by(
                practice_id=practice.id,
                question_id=q.id
            ).first()
            if response:
                responses[q.id] = response
        
        answered_count = sum(1 for r in responses.values() if r.answer is not None)
        
        return render_template('interview/session.html',
            user=current_user,
            practice=practice,
            questions=questions,
            responses=responses,
            answered_count=answered_count,
            now=datetime.utcnow()
        )

    @app.route('/interview-practice/<int:practice_id>/answer', methods=['POST'])
    @login_required
    def interview_practice_answer(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        question_id = request.form.get('question_id', type=int)
        answer = request.form.get('answer')
        time_taken = request.form.get('time_taken', 0, type=int)
        
        if not answer:
            return jsonify({'success': False, 'message': 'Please provide an answer.'}), 400
        
        response = InterviewResponse.query.filter_by(
            practice_id=practice.id,
            question_id=question_id
        ).first()
        
        if not response:
            response = InterviewResponse(
                practice_id=practice.id,
                question_id=question_id
            )
            db.session.add(response)
        
        response.answer = answer
        response.time_taken = time_taken
        response.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Answer saved!'})

    @app.route('/interview-practice/<int:practice_id>/feedback', methods=['POST'])
    @login_required
    def interview_practice_feedback(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        question_id = request.form.get('question_id', type=int)
        
        question = InterviewQuestion.query.filter_by(
            id=question_id,
            practice_id=practice.id
        ).first_or_404()
        
        response = InterviewResponse.query.filter_by(
            practice_id=practice.id,
            question_id=question_id
        ).first_or_404()
        
        if not response.answer:
            return jsonify({'success': False, 'message': 'No answer to evaluate.'}), 400
        
        feedback = get_interview_feedback(
            question=question.question_text,
            answer=response.answer,
            job_title=practice.job_title,
            question_type=question.question_type
        )
        
        response.feedback = feedback.get('feedback')
        response.score = feedback.get('score', 0)
        response.strengths = feedback.get('strengths', [])
        response.improvements = feedback.get('improvements', [])
        response.key_points = feedback.get('key_points', [])
        db.session.commit()
        
        return jsonify({
            'success': True,
            'feedback': feedback
        })

    @app.route('/interview-practice/<int:practice_id>/complete', methods=['POST'])
    @login_required
    def interview_practice_complete(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        responses = InterviewResponse.query.filter_by(practice_id=practice.id).all()
        if responses:
            scores = [r.score for r in responses if r.score > 0]
            if scores:
                practice.score = sum(scores) / len(scores)
        
        practice.status = 'completed'
        practice.completed_at = datetime.utcnow()
        db.session.commit()
        
        flash('✅ Interview practice completed!', 'success')
        return redirect(url_for('interview_practice_summary', practice_id=practice.id))

    @app.route('/interview-practice/<int:practice_id>/summary')
    @login_required
    def interview_practice_summary(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        responses = InterviewResponse.query.filter_by(
            practice_id=practice.id
        ).all()
        
        return render_template('interview/summary.html',
            user=current_user,
            practice=practice,
            responses=responses
        )

    @app.route('/interview-practice/<int:practice_id>/delete', methods=['POST'])
    @login_required
    def interview_practice_delete(practice_id):
        practice = InterviewPractice.query.filter_by(
            id=practice_id,
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(practice)
        db.session.commit()
        
        flash('Interview session deleted.', 'success')
        return redirect(url_for('interview_practice_hub'))
    
    @app.route('/clear-session')
    @login_required
    def clear_session():
        clear_parsed_data_from_session()
        session.pop('parsing_status', None)
        flash('Session cleared successfully!', 'success')
        return redirect(url_for('dashboard'))


# ========== INTERVIEW HELPER FUNCTIONS ==========

def generate_interview_questions(job_title, industry, experience_level, question_type, skills, num_questions=5):
    """Generate interview questions using AI"""
    questions = []
    
    prompt = f"""Generate {num_questions} interview questions for a {question_type} interview for a {job_title} position.

Industry: {industry or 'General'}
Experience Level: {experience_level}
Skills: {', '.join(skills[:5]) if skills else 'General'}

For each question, provide:
1. The question text
2. Category (e.g., Python, Leadership, Problem Solving)
3. Difficulty (easy, medium, hard)
4. Expected answer (brief)
5. Tips for answering

Return as a JSON array with fields: question, type, category, difficulty, expected_answer, tips"""

    try:
        assistant = OpenAIAssistant()
        response = assistant.get_response(prompt, skills, 0, 'interview')
        answer = response.get('answer', '')
        
        try:
            import json
            json_start = answer.find('[')
            json_end = answer.rfind(']') + 1
            if json_start != -1 and json_end > json_start:
                json_str = answer[json_start:json_end]
                questions = json.loads(json_str)
            else:
                questions = generate_fallback_questions(job_title, question_type, num_questions)
        except:
            questions = generate_fallback_questions(job_title, question_type, num_questions)
            
    except Exception as e:
        print(f"AI question generation error: {e}")
        questions = generate_fallback_questions(job_title, question_type, num_questions)
    
    return questions


def generate_fallback_questions(job_title, question_type, num_questions):
    """Generate fallback questions if AI is unavailable"""
    questions = []
    
    technical_questions = {
        'data analyst': [
            "What is the difference between INNER JOIN and LEFT JOIN in SQL?",
            "How do you handle missing data in a dataset?",
            "Explain the difference between correlation and causation.",
            "What is a pivot table and when would you use it?",
            "How would you clean a dataset with inconsistent formats?",
            "What is the purpose of data normalization?"
        ],
        'software engineer': [
            "Explain the difference between a class and an object.",
            "What is the time complexity of a binary search?",
            "How does garbage collection work?",
            "What is the difference between GET and POST requests?",
            "Explain the SOLID principles.",
            "What is a design pattern? Give an example."
        ],
        'product manager': [
            "How would you prioritize features for a new product?",
            "What is a product roadmap?",
            "Explain the importance of user research.",
            "How do you measure product success?",
            "What is the difference between product and project management?",
            "How would you handle a feature request that doesn't align with the product vision?"
        ],
        'data scientist': [
            "Explain the bias-variance tradeoff.",
            "What is the difference between classification and regression?",
            "How do you evaluate a machine learning model?",
            "What is the difference between bagging and boosting?",
            "Explain the concept of feature engineering.",
            "What is cross-validation and why is it important?"
        ]
    }
    
    behavioral_questions = [
        "Tell me about a time you had to work under pressure.",
        "Describe a situation where you had to resolve a conflict with a coworker.",
        "How do you handle criticism?",
        "Give an example of a time you went above and beyond for a project.",
        "Describe a time when you had to learn something new quickly.",
        "Tell me about a failure and what you learned from it.",
        "How do you prioritize tasks when everything is urgent?",
        "Describe a situation where you demonstrated leadership."
    ]
    
    general_questions = [
        "Tell me about yourself.",
        "Why do you want to work in this industry?",
        "Where do you see yourself in 5 years?",
        "What are your strengths and weaknesses?",
        "Why should we hire you?",
        "Tell me about a project you're proud of."
    ]
    
    if question_type == 'technical':
        job_lower = job_title.lower()
        for title, qs in technical_questions.items():
            if title in job_lower:
                base_questions = qs
                break
        else:
            base_questions = technical_questions.get('software engineer', [])
        
        questions = base_questions[:num_questions]
        if len(questions) < num_questions:
            import random
            remaining = num_questions - len(questions)
            questions.extend(random.sample(behavioral_questions, min(remaining, len(behavioral_questions))))
    
    elif question_type == 'behavioral':
        import random
        questions = random.sample(behavioral_questions, min(num_questions, len(behavioral_questions)))
    else:
        import random
        questions = random.sample(general_questions, min(num_questions, len(general_questions)))
    
    formatted = []
    for i, q in enumerate(questions):
        formatted.append({
            'question': q,
            'type': question_type,
            'category': 'General' if question_type == 'general' else 'Technical',
            'difficulty': 'medium',
            'expected_answer': 'Provide a clear, concise, and structured response.',
            'tips': 'Be specific, use examples, and stay focused on the question.'
        })
    
    return formatted


def get_interview_feedback(question, answer, job_title, question_type):
    """Get AI feedback on an interview answer"""
    prompt = f"""You are an expert interview coach. Provide feedback on this interview answer.

Job Title: {job_title}
Question Type: {question_type}
Question: {question}
Candidate's Answer: {answer}

Provide feedback in the following format (JSON):
{{
    "feedback": "Overall feedback on the answer",
    "score": 0-100,
    "strengths": ["Strength 1", "Strength 2"],
    "improvements": ["Improvement 1", "Improvement 2"],
    "key_points": ["Key point 1", "Key point 2"]
}}"""

    try:
        assistant = OpenAIAssistant()
        response = assistant.get_response(prompt, [], 0, 'interview_coach')
        answer_text = response.get('answer', '')
        
        try:
            import json
            json_start = answer_text.find('{')
            json_end = answer_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = answer_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {
            'feedback': 'Good effort! Consider providing more specific examples and structuring your answer clearly.',
            'score': 75,
            'strengths': ['You addressed the question', 'Good effort'],
            'improvements': ['Add more specific examples', 'Structure your answer more clearly'],
            'key_points': ['Answer the question directly', 'Use the STAR method']
        }
        
    except Exception as e:
        print(f"Feedback generation error: {e}")
        return {
            'feedback': 'Good effort! Review the tips and try again.',
            'score': 70,
            'strengths': ['You attempted the question'],
            'improvements': ['Provide more detail', 'Use examples'],
            'key_points': ['Answer directly', 'Be specific']
        }


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')
    app.config.from_object('config.Config')
    
    mail.init_app(app)
    app.mail = mail
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    initialize_extensions(app)
    
    migrate = Migrate(app, db)
    
    configure_login_manager()
    
    from app.utils.oauth import configure_oauth
    configure_oauth(app)
    
    register_blueprints(app)
    
    register_routes(app)
    
    # ✅ Register CLI commands
    register_commands(app)
    
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(jobs_bp) 
    
    return app