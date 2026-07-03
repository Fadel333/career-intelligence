from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from extensions import db, login_manager
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
import os
import sys
import pickle
import base64
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blueprints and utils
from app.auth.routes import auth_bp
from app.utils.cv_parser import CVParser
from app.utils.skill_analyzer import SkillAnalyzer
from app.utils.course_api import CourseAPI
from app.utils.hybrid_parser import HybridParser
from app.utils.openai_assistant import OpenAIAssistant
from models import User, Profile

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
    
    # If it's already a dict, return it directly (handles old session data)
    if isinstance(compressed, dict):
        return compressed
    
    try:
        decoded = base64.b64decode(compressed.encode('utf-8'))
        return pickle.loads(decoded)
    except Exception as e:
        print(f"Decompression error: {e}")
        # If decompression fails, try to return as-is (might be old format)
        return compressed


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


# ========== HELPER FUNCTIONS FOR UNIVERSITY DASHBOARD ==========
def get_department_performance():
    """Get department performance data"""
    return [
        {'name': 'Computer Science', 'employability': 92, 'students': 340},
        {'name': 'Business Administration', 'employability': 78, 'students': 280},
        {'name': 'Engineering', 'employability': 85, 'students': 210},
        {'name': 'Information Technology', 'employability': 81, 'students': 190},
        {'name': 'Data Science', 'employability': 88, 'students': 140},
        {'name': 'Cybersecurity', 'employability': 76, 'students': 87}
    ]


def get_top_skill_gaps(parsed_data):
    """Get top skill gaps from parsed CV data"""
    print(f"DEBUG: parsed_data received: {parsed_data is not None}")
    
    if parsed_data and parsed_data.get('skills'):
        all_skills = []
        for category, skills in parsed_data['skills'].items():
            all_skills.extend(skills)
        
        print(f"DEBUG: all_skills extracted: {all_skills}")
        
        # Detect sector for better analysis
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
    """Get industry trends data"""
    return [
        {'sector': 'Fintech', 'growth': 45, 'demand': 92},
        {'sector': 'HealthTech', 'growth': 38, 'demand': 85},
        {'sector': 'EdTech', 'growth': 32, 'demand': 78},
        {'sector': 'AgriTech', 'growth': 28, 'demand': 72},
        {'sector': 'E-commerce', 'growth': 25, 'demand': 68}
    ]


def get_curriculum_recommendations(parsed_data):
    """Get curriculum recommendations based on actual skill gaps"""
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
    """Default curriculum recommendations when no CV data available"""
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


def register_routes(app):
    """Register all application routes"""
    
    # ========== PUBLIC ROUTES ==========
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('base.html')
    
    # ========== PRIVACY POLICY ROUTE ==========
    @app.route('/privacy-policy')
    def privacy_policy():
        """Privacy policy page"""
        return render_template('privacy_policy.html')
    
    # ========== CV UPLOAD ROUTE ==========
    @app.route('/upload-cv', methods=['GET', 'POST'])
    @login_required
    def upload_cv():
        """CV upload and parsing page"""
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
                # Use hybrid parser - quick parse first
                parsed_data = hybrid_parser.parse_hybrid(filepath, current_user.id)
                
                if parsed_data:
                    # Save to database
                    user = User.query.get(current_user.id)
                    if user:
                        # Add additional data to parsed_data
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
                        
                        # Save to database
                        user.save_cv_analysis(parsed_data)
                        user.detected_sector = detected_sector
                        user.employability_score = employability['score']
                        db.session.commit()
                        
                        print(f"✅ CV data saved to database for user {user.email}")
                    
                    # Store in session for display
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
                        session['cv_filename'] = file.filename
                        session['parsing_status'] = parsed_data.get('status', 'processing')
                        
                        flash(f'✅ CV uploaded! Quick analysis complete. Found {parsed_data["total_skills"]} skills. Deep analysis running in background...', 'success')
                        return redirect(url_for('skill_analysis'))
                    else:
                        flash('Error processing CV data. Please try again.', 'error')
                        return redirect(url_for('upload_cv'))
                else:
                    flash('Could not parse CV. Please ensure it\'s readable.', 'error')
                    return redirect(url_for('upload_cv'))
            except Exception as e:
                print(f"Error: {e}")
                flash(f'Error parsing CV: {str(e)}', 'error')
                return redirect(url_for('upload_cv'))
        
        return render_template('upload_cv.html', user=current_user)
    
    # ========== SKILL ANALYSIS ROUTE ==========
    @app.route('/skill-analysis')
    @login_required
    def skill_analysis():
        """Skill gap analysis page with sector detection"""
        
        # First try to get from session (new upload)
        parsed_data = get_parsed_data_from_session()
        
        # If not in session, get from database
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                print(f"📄 Loaded CV data from database for {user.email}")
                
                # Store in session for this request
                if parsed_data:
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
                        session['cv_filename'] = user.cv_filename
        
        # If still no data, show empty state
        if not parsed_data:
            return render_template('skill_analysis.html', 
                                 user=current_user, 
                                 parsed_data=None, 
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
            
            # Get sector-specific market demands
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
        
        return render_template('skill_analysis.html', user=current_user, parsed_data=None, is_processing=False, no_cv=True)
    
    # ========== LEARNING ROADMAP ROUTE ==========
    @app.route('/learning-roadmap')
    @login_required
    def learning_roadmap():
        """Personalized learning roadmap page"""
        parsed_data = get_parsed_data_from_session()
        
        # If no data, show empty state
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data:
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
        
        course_api = CourseAPI()
        
        return render_template('learning_roadmap.html', 
                             user=current_user, 
                             parsed_data=parsed_data,
                             skill_analyzer=SkillAnalyzer,
                             course_api=course_api,
                             no_cv=not parsed_data)
    
    # ========== JOB MATCHES ROUTE ==========
    @app.route('/job-matches')
    @login_required
    def job_matches():
        """Job recommendations page"""
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data:
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                all_skills.extend(skills)
            
            job_matches = SkillAnalyzer.get_job_recommendations(all_skills)
            return render_template('job_matches.html', 
                                 user=current_user, 
                                 job_matches=job_matches,
                                 parsed_data=parsed_data,
                                 skill_analyzer=SkillAnalyzer,
                                 no_cv=False)
        
        return render_template('job_matches.html', user=current_user, job_matches=None, skill_analyzer=SkillAnalyzer, no_cv=True)
    
    # ========== CAREER ASSISTANT ROUTES ==========
    @app.route('/career-assistant')
    @login_required
    def career_assistant():
        """AI career assistant chat page - Powered by OpenAI"""
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data:
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
        
        return render_template('career_assistant.html', user=current_user, parsed_data=parsed_data)
    
    @app.route('/api/ask', methods=['POST'])
    @login_required
    def api_ask():
        """API endpoint for career assistant questions - NOW WITH OPENAI"""
        data = request.get_json()
        question = data.get('question', '')
        
        # Get user skills from session
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
        
        user_skills = []
        experience = 0
        sector = 'general'
        
        if parsed_data:
            for category, skills in parsed_data.get('skills', {}).items():
                user_skills.extend(skills)
            experience = parsed_data.get('experience_years', 0)
            sector = SkillAnalyzer.detect_sector(user_skills)
        
        # Get AI response from OpenAI
        assistant = OpenAIAssistant()
        response = assistant.get_response(question, user_skills, experience, sector)
        
        return jsonify(response)
    
    # ========== DASHBOARD ROUTE ==========
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main user dashboard"""
        parsed_data = get_parsed_data_from_session()
        
        if not parsed_data:
            user = User.query.get(current_user.id)
            if user and user.cv_analysis:
                parsed_data = user.get_cv_analysis()
                if parsed_data:
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
        
        return render_template('dashboard.html', user=current_user, parsed_data=parsed_data)
    
    # ========== PROFILE ROUTE ==========
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        """User profile page"""
        if request.method == 'POST':
            # Get form data
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            bio = request.form.get('bio')
            location = request.form.get('location')
            phone = request.form.get('phone')
            current_job = request.form.get('current_job')
            company = request.form.get('company')
            skills = request.form.get('skills')
            
            # Update user
            user = User.query.get(current_user.id)
            if user:
                user.fullname = fullname or user.fullname
                user.email = email or user.email
                user.bio = bio or user.bio
                user.location = location or user.location
                user.phone = phone or user.phone
                
                # Update or create profile
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
    
    # ========== PROFILE PICTURE UPLOAD ROUTE ==========
    @app.route('/upload-profile-pic', methods=['POST'])
    @login_required
    def upload_profile_pic():
        """Upload profile picture"""
        import os
        from werkzeug.utils import secure_filename
        
        if 'profile_pic' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'})
        
        file = request.files['profile_pic']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        # Check file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            return jsonify({'success': False, 'message': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP.'})
        
        # Save file
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        filepath = os.path.join('static/profile_pics', filename)
        
        # Create directory if it doesn't exist
        os.makedirs('static/profile_pics', exist_ok=True)
        
        # Delete old profile picture if exists
        if current_user.profile_image:
            old_path = os.path.join('static/profile_pics', current_user.profile_image)
            if os.path.exists(old_path):
                os.remove(old_path)
        
        file.save(filepath)
        
        # Update user
        current_user.profile_image = filename
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Profile picture updated successfully!'})
    
    # ========== CHANGE PASSWORD ROUTE ==========
    @app.route('/change-password', methods=['POST'])
    @login_required
    def change_password():
        """Change user password"""
        from werkzeug.security import generate_password_hash, check_password_hash
        
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            flash('All fields are required.', 'error')
            return redirect(url_for('profile'))
        
        # Check current password
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('profile'))
        
        # Check new password length
        if len(new_password) < 8:
            flash('New password must be at least 8 characters long.', 'error')
            return redirect(url_for('profile'))
        
        # Check if passwords match
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('profile'))
        
        # Update password
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('profile'))
    
    # ========== UNIVERSITY DASHBOARD ROUTE ==========
    @app.route('/university-dashboard')
    @login_required
    def university_dashboard():
        """University intelligence dashboard"""
        parsed_data = get_parsed_data_from_session()
        
        print(f"=== UNIVERSITY DASHBOARD ===")
        print(f"parsed_data exists: {parsed_data is not None}")
        if parsed_data:
            print(f"skills keys: {parsed_data.get('skills', {}).keys()}")
            print(f"total_skills: {parsed_data.get('total_skills', 0)}")
        
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
        """Check if deep parsing is complete"""
        parsed_data = get_parsed_data_from_session()
        parsing_status = session.get('parsing_status', 'complete')
        
        if parsed_data:
            status = parsed_data.get('status', parsing_status)
            return jsonify({
                'status': status,
                'total_skills': parsed_data.get('total_skills', 0)
            })
        
        return jsonify({'status': 'unknown'})
    
    # ========== TEMPORARY: Clear Session Route ==========
    @app.route('/clear-session')
    @login_required
    def clear_session():
        """Temporary route to clear session data"""
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
    
    return app