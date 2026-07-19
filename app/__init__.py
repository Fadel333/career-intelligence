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

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blueprints and utils
from app.auth.routes import auth_bp
from app.utils.cv_parser import CVParser
from app.utils.skill_analyzer import SkillAnalyzer
from app.utils.course_api import CourseAPI
from app.utils.hybrid_parser import HybridParser
from app.utils.openai_assistant import OpenAIAssistant
from models import User, Profile, RecruiterProfile, Candidate, Job, Placement, JobAlert, JobAlertLog
from app.recruiter import recruiter_bp 
from app.admin.routes import admin_bp 
from app.jobs.routes import jobs_bp 

# Initialize Flask-Mail ONCE
mail = Mail()

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

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
    
    # If it's already a dict, return it directly
    if isinstance(compressed, dict):
        return compressed
    
    # If it's a string, try to decompress
    if isinstance(compressed, str):
        # Try base64 decode first
        try:
            decoded = base64.b64decode(compressed.encode('utf-8'))
            data = pickle.loads(decoded)
            if isinstance(data, dict):
                return data
        except:
            pass
        
        # Try JSON
        try:
            data = json.loads(compressed)
            if isinstance(data, dict):
                return data
        except:
            pass
        
        # Try ast.literal_eval for Python dict strings
        if compressed.startswith('{') and compressed.endswith('}'):
            try:
                data = ast.literal_eval(compressed)
                if isinstance(data, dict):
                    return data
            except:
                pass
        
        # If all else fails, return empty dict
        print(f"⚠️ Could not decompress data, returning empty dict")
        return {}
    
    # Fallback
    return {}


def allowed_file(filename):
    """Check if file has allowed extension"""
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
    if data:
        return decompress_parsed_data(data)
    return None


def clear_parsed_data_from_session():
    """Clear parsed data from session"""
    if 'parsed_cv' in session:
        session.pop('parsed_cv', None)
    if 'cv_filename' in session:
        session.pop('cv_filename', None)


# ========== HELPER FUNCTIONS ==========
def get_department_performance():
    return [
        {'name': 'Computer Science', 'employability': 92, 'students': 340},
        {'name': 'Business Administration', 'employability': 78, 'students': 280},
        {'name': 'Engineering', 'employability': 85, 'students': 210},
        {'name': 'Information Technology', 'employability': 81, 'students': 190},
        {'name': 'Data Science', 'employability': 88, 'students': 140},
        {'name': 'Cybersecurity', 'employability': 76, 'students': 87}
    ]


def get_top_skill_gaps(parsed_data):
    print(f"DEBUG: parsed_data received: {parsed_data is not None}")
    
    if parsed_data and parsed_data.get('skills'):
        all_skills = []
        for category, skills in parsed_data['skills'].items():
            all_skills.extend(skills)
        
        print(f"DEBUG: all_skills extracted: {all_skills}")
        
        detected_sector = SkillAnalyzer.detect_sector(all_skills)
        market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
            detected_sector, 
            SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
        )
        
        gaps = SkillAnalyzer.analyze_gaps(all_skills, market_demands)
        print(f"DEBUG: gaps found: {len(gaps)}")
        
        formatted_gaps = []
        for gap in gaps[:5]:
            formatted_gaps.append({
                'skill': gap.get('skill', 'Unknown'),
                'demand': gap.get('demand', 0),
                'priority': gap.get('priority', 'Medium'),
                'growth': gap.get('growth', '+0%')
            })
        
        return formatted_gaps
    
    print("DEBUG: No parsed_data, using mock data")
    return [
        {'skill': 'Machine Learning', 'demand': 88, 'priority': 'Critical', 'growth': '+45%'},
        {'skill': 'Cloud Computing', 'demand': 85, 'priority': 'High', 'growth': '+35%'},
        {'skill': 'Python Programming', 'demand': 92, 'priority': 'Critical', 'growth': '+25%'},
        {'skill': 'Data Analysis', 'demand': 82, 'priority': 'High', 'growth': '+20%'},
        {'skill': 'Cybersecurity', 'demand': 78, 'priority': 'Medium', 'growth': '+30%'}
    ]


def get_industry_trends():
    return [
        {'sector': 'Fintech', 'growth': 45, 'demand': 92},
        {'sector': 'HealthTech', 'growth': 38, 'demand': 85},
        {'sector': 'EdTech', 'growth': 32, 'demand': 78},
        {'sector': 'AgriTech', 'growth': 28, 'demand': 72},
        {'sector': 'E-commerce', 'growth': 25, 'demand': 68}
    ]


def get_curriculum_recommendations(parsed_data):
    if parsed_data and parsed_data.get('skills'):
        all_skills = []
        for category, skills in parsed_data['skills'].items():
            all_skills.extend(skills)
        
        detected_sector = SkillAnalyzer.detect_sector(all_skills)
        market_demands = SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get(
            detected_sector, 
            SkillAnalyzer.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
        )
        
        gaps = SkillAnalyzer.analyze_gaps(all_skills, market_demands)
        
        recommendations = []
        
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
        for gap in gaps[:10]:
            dept = skill_departments.get(gap['skill'], 'General')
            if dept not in dept_gaps:
                dept_gaps[dept] = []
            dept_gaps[dept].append(gap['skill'])
        
        for dept, skills in dept_gaps.items():
            priority = 'High' if len(skills) >= 3 else 'Medium'
            recommendations.append({
                'department': dept,
                'add_skills': skills[:3],
                'remove_skills': [],
                'priority': priority
            })
        
        return recommendations
    
    return get_curriculum_recommendations_default()


def get_curriculum_recommendations_default():
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
        },
        {
            'department': 'Agriculture',
            'add_skills': ['Crop Production', 'Livestock Management', 'Fisheries and Aquaculture', 'Forestry and Logging', 'Allied Services and Agribusiness'],
            'remove_skills': ['Soil Erosion Management'],
            'priority': 'High'
        },
        {
            'department': 'Medicine and Surgery',
            'add_skills': ['Clinical Rotation', 'Human Anatomy'],
            'remove_skills': ['Clinical Basics'],
            'priority': 'Low'
        },
        {
            'department': 'Nursing and Midwifery',
            'add_skills': ['Public Health', 'Paediatric Care', 'Clinical Practice'],
            'remove_skills': ['Paediatric Care Basics'],
            'priority': 'Low'
        },
        {
            'department': 'Pharmacy',
            'add_skills': ['Pharmacotherapeutics', 'Pharmaceutical Technology'],
            'remove_skills': ['Massage'],
            'priority': 'Medium'
        },
        {
            'department': 'Law',
            'add_skills': ['Bachelor of Laws'],
            'priority': 'Medium'
        },
        {
            'department': 'Social Science',
            'add_skills': ['Psychology', 'Sociology', 'Political Science', 'Anthropology', 'Criminology', 'Economics', 'International Relations', 'Geography'],
            'remove_skills': ['Social Work'],
            'priority': 'High'
        },
        {
            'department': 'Art and Languages',
            'add_skills': ['Music', 'Sculpture', 'Painting', 'Literature', 'Architecture', 'Performing Arts', 'Cinema', 'French', 'Spanish', 'Chinese', 'English'],
            'remove_skills': ['Dancing'],
            'priority': 'Medium'
        }
    ]


# ========== RECRUITER HUB HELPER FUNCTIONS ==========
def get_recruiter_stats(recruiter_id):
    from models import Job, Placement
    
    total_jobs = Job.query.filter_by(recruiter_id=recruiter_id).count()
    active_jobs = Job.query.filter_by(recruiter_id=recruiter_id, status='published').count()
    total_placements = Placement.query.filter_by(recruiter_id=recruiter_id).count()
    
    from sqlalchemy import func
    total_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter_id, commission_paid=True).scalar() or 0
    
    pending_earnings = db.session.query(func.sum(Placement.commission_amount))\
        .filter_by(recruiter_id=recruiter_id, commission_paid=False)\
        .filter(Placement.status == 'hired').scalar() or 0
    
    return {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_placements': total_placements,
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings
    }


def register_routes(app):
    """Register all application routes"""
    
    # ========== PUBLIC ROUTES ==========
    @app.route('/')
    def index():
        return render_template('base.html')
    
    @app.route('/privacy-policy')
    def privacy_policy():
        return render_template('privacy_policy.html')
    
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
            
            if not allowed_file(file.filename):
                flash('Invalid file type. Please upload PDF or DOCX', 'error')
                return redirect(url_for('upload_cv'))
            
            filename = secure_filename(f"{current_user.id}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            flash('Processing CV... Please wait.', 'info')
            
            try:
                parsed_data = hybrid_parser.parse_hybrid(filepath, current_user.id)
                
                if parsed_data:
                    user = User.query.get(current_user.id)
                    if user:
                        all_skills = []
                        for category, skills in parsed_data.get('skills', {}).items():
                            all_skills.extend(skills)
                        
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
                    
                    # Store in session as JSON instead of compressed pickle
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                        session['cv_filename'] = file.filename
                        session['parsing_status'] = parsed_data.get('status', 'processing')
                        print(f"✅ Stored CV data as JSON in session")
                    except Exception as e:
                        print(f"❌ Error storing session data: {e}")
                        flash('Error storing CV data. Please try again.', 'error')
                        return redirect(url_for('upload_cv'))
                    
                    flash(f'✅ CV uploaded! Quick analysis complete. Found {parsed_data["total_skills"]} skills.', 'success')
                    return redirect(url_for('skill_analysis'))
                else:
                    flash('Could not parse CV. Please ensure it\'s readable.', 'error')
                    return redirect(url_for('upload_cv'))
            except Exception as e:
                print(f"Error: {e}")
                flash(f'Error parsing CV: {str(e)}', 'error')
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
        
        parsed_data = get_parsed_data_from_session()
        
        # Ensure parsed_data is a dictionary
        if not parsed_data or not isinstance(parsed_data, dict):
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data and isinstance(parsed_data, dict):
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                        session['cv_filename'] = user.cv_filename
                    except:
                        pass
                else:
                    parsed_data = {}
        
        if not isinstance(parsed_data, dict):
            parsed_data = {}
        
        if not parsed_data.get('skills'):
            parsed_data['skills'] = {}
        
        if not parsed_data:
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
                                 no_cv=True)
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                all_skills.extend(skills)
            
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
            job_matches = SkillAnalyzer.get_job_recommendations(all_skills)
            
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
                                 no_cv=False)
        
        return render_template('skill_analysis.html', 
                             user=current_user, 
                             parsed_data={'skills': {}},
                             is_processing=False, 
                             no_cv=True)
    
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
        if current_user.is_recruiter():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            flash('This feature is for job seekers only.', 'warning')
            return redirect(url_for('admin.index'))
        
        # DIRECT FIX: Get raw data from session and force it to be a dict
        raw_data = session.get('parsed_cv', None)
        
        parsed_data = {}
        
        if raw_data:
            # If it's already a dict, use it
            if isinstance(raw_data, dict):
                parsed_data = raw_data
                print(f"✅ parsed_data is already a dict")
            # If it's a string, try to parse it
            elif isinstance(raw_data, str):
                print(f"🔍 Raw data is a string, attempting to parse...")
                # Try base64 decode first (our compression format)
                try:
                    decoded = base64.b64decode(raw_data.encode('utf-8'))
                    parsed_data = pickle.loads(decoded)
                    if isinstance(parsed_data, dict):
                        print(f"✅ Successfully decompressed from base64")
                    else:
                        parsed_data = {}
                except:
                    # Try JSON
                    try:
                        parsed_data = json.loads(raw_data)
                        if isinstance(parsed_data, dict):
                            print(f"✅ Successfully parsed from JSON")
                        else:
                            parsed_data = {}
                    except:
                        # Try ast.literal_eval
                        try:
                            parsed_data = ast.literal_eval(raw_data)
                            if isinstance(parsed_data, dict):
                                print(f"✅ Successfully parsed from literal_eval")
                            else:
                                parsed_data = {}
                        except:
                            print(f"❌ Could not parse string data")
                            parsed_data = {}
        
        # If still no data, try database
        if not parsed_data or not isinstance(parsed_data, dict):
            print("🔍 Trying to get from database...")
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data and isinstance(parsed_data, dict):
                    # Re-compress and store in session as JSON string (clean format)
                    try:
                        session['parsed_cv'] = json.dumps(parsed_data)
                        print(f"✅ Stored JSON in session")
                    except:
                        pass
                else:
                    parsed_data = {}
        
        # FINAL SAFETY: Ensure it's a dict with 'skills'
        if not isinstance(parsed_data, dict):
            print(f"⚠️ WARNING: parsed_data is {type(parsed_data)}, using empty dict")
            parsed_data = {}
        
        if 'skills' not in parsed_data:
            parsed_data['skills'] = {}
        
        print(f"✅ Final parsed_data type: {type(parsed_data)}")
        print(f"✅ Skills count: {len(parsed_data.get('skills', {}))}")
        
        # Now safely use it
        if parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                if isinstance(skills, list):
                    all_skills.extend(skills)
                elif isinstance(skills, str):
                    all_skills.append(skills)
            
            job_matches = SkillAnalyzer.get_job_recommendations(all_skills)
            return render_template('job_matches.html', 
                                 user=current_user, 
                                 job_matches=job_matches,
                                 parsed_data=parsed_data,
                                 skill_analyzer=SkillAnalyzer,
                                 no_cv=False)
        
        # No data or empty skills
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
                user_skills.extend(skills)
            experience = parsed_data.get('experience_years', 0)
            sector = SkillAnalyzer.detect_sector(user_skills)
        
        assistant = OpenAIAssistant()
        response = assistant.get_response(question, user_skills, experience, sector)
        
        return jsonify(response)
    
    # ========== DASHBOARD ROUTE ==========
    @app.route('/dashboard')
    @login_required
    def dashboard():
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
        
        if current_user.is_recruiter():
            return redirect(url_for('recruiter.dashboard'))
        if current_user.is_admin():
            return redirect(url_for('admin.index'))
        
        return render_template('dashboard.html', user=current_user, parsed_data=parsed_data)
    
    # ========== PROFILE ROUTE ==========
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
            
            user = User.query.get(current_user.id)
            if user:
                user.fullname = fullname or user.fullname
                user.email = email or user.email
                user.bio = bio or user.bio
                user.location = location or user.location
                user.phone = phone or user.phone
                
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
    
    # ========== PROFILE PICTURE UPLOAD ==========
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
            if os.path.exists(old_path):
                os.remove(old_path)
        
        file.save(filepath)
        
        current_user.profile_image = filename
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile picture updated successfully!'})
    
    # ========== CHANGE PASSWORD ==========
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
    
    # ========== UNIVERSITY DASHBOARD ==========
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
            'total_students': 1247,
            'employability_rate': 87,
            'skill_gaps_identified': 15,
            'partners': 32,
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
    
    # ========== PARSING STATUS API ==========
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
        """Manage job alerts page"""
        alerts = JobAlert.query.filter_by(user_id=current_user.id).all()
        return render_template('job_alerts.html', user=current_user, alerts=alerts)

    @app.route('/job-alerts/create', methods=['GET', 'POST'])
    @login_required
    def create_job_alert():
        """Create a new job alert"""
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
        
        # Get unique categories from jobs
        categories = db.session.query(Job.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        return render_template('create_job_alert.html', 
                             user=current_user, 
                             categories=categories)

    @app.route('/job-alerts/<int:alert_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_job_alert(alert_id):
        """Edit an existing job alert"""
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
        
        categories = db.session.query(Job.category).distinct().all()
        categories = [c[0] for c in categories if c[0]]
        
        return render_template('edit_job_alert.html', 
                             user=current_user, 
                             alert=alert,
                             categories=categories)

    @app.route('/job-alerts/<int:alert_id>/delete', methods=['POST'])
    @login_required
    def delete_job_alert(alert_id):
        """Delete a job alert"""
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
        """Toggle alert active status"""
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

    @app.route('/api/job-alerts/check-new')
    @login_required
    def check_new_jobs_for_alerts():
        """Check if there are new jobs for user's alerts"""
        alerts = JobAlert.query.filter_by(user_id=current_user.id, is_active=True).all()
        
        results = []
        for alert in alerts:
            last_sent = alert.last_sent_at or datetime.utcnow() - timedelta(days=7)
            # Find matching jobs posted after last_sent
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
    
    # ========== CLEAR SESSION ==========
    @app.route('/clear-session')
    @login_required
    def clear_session():
        clear_parsed_data_from_session()
        session.pop('parsing_status', None)
        flash('Session cleared successfully!', 'success')
        return redirect(url_for('dashboard'))


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                static_folder='../static',
                static_url_path='/static')
    app.config.from_object('config.Config')
    
    # Initialize Flask-Mail
    mail.init_app(app)
    app.mail = mail
    
    # Configure upload
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Set session configuration
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)
    
    # Configure login manager
    configure_login_manager()
    
    # Initialize OAuth
    from app.utils.oauth import configure_oauth
    configure_oauth(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register routes
    register_routes(app)
    
    # Register blueprints
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp) 
    app.register_blueprint(jobs_bp) 
    
    return app