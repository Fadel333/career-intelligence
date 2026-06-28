from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from extensions import db, login_manager
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
from app.utils.ai_assistant import CareerAssistant
from app.utils.course_api import CourseAPI
from app.utils.hybrid_parser import HybridParser

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
    # Debug: Print to see what's coming in
    print(f"DEBUG: parsed_data received: {parsed_data is not None}")
    
    if parsed_data and parsed_data.get('skills'):
        all_skills = []
        for category, skills in parsed_data['skills'].items():
            all_skills.extend(skills)
        
        print(f"DEBUG: all_skills extracted: {all_skills}")
        
        # Use the actual skill analyzer to get gaps
        gaps = SkillAnalyzer.analyze_gaps(all_skills)
        
        print(f"DEBUG: gaps found: {len(gaps)}")
        
        # Format gaps for display
        formatted_gaps = []
        for gap in gaps[:5]:
            formatted_gaps.append({
                'skill': gap.get('skill', 'Unknown'),
                'demand': gap.get('demand', 0),
                'priority': gap.get('priority', 'Medium'),
                'growth': gap.get('growth', '+0%')
            })
        
        return formatted_gaps
    
    # If no CV data, return mock data (fallback)
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
        
        gaps = SkillAnalyzer.analyze_gaps(all_skills)
        
        # Group gaps by category/department
        recommendations = []
        
        # Map skills to departments
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
            'DevOps': 'Information Technology'
        }
        
        # Group gaps by department
        dept_gaps = {}
        for gap in gaps[:10]:
            dept = skill_departments.get(gap['skill'], 'General')
            if dept not in dept_gaps:
                dept_gaps[dept] = []
            dept_gaps[dept].append(gap['skill'])
        
        # Create recommendations
        for dept, skills in dept_gaps.items():
            priority = 'High' if len(skills) >= 3 else 'Medium'
            recommendations.append({
                'department': dept,
                'add_skills': skills[:3],
                'remove_skills': [],  # Would need real data
                'priority': priority
            })
        
        return recommendations
    
    # Default recommendations if no CV data
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
            
            # Show processing status
            flash('Processing CV... Please wait.', 'info')
            
            try:
                # Use hybrid parser - quick parse first
                parsed_data = hybrid_parser.parse_hybrid(filepath, current_user.id)
                
                if parsed_data:
                    # Compress data before storing in session
                    compressed_data = compress_parsed_data(parsed_data)
                    if compressed_data:
                        session['parsed_cv'] = compressed_data
                        session['cv_filename'] = file.filename
                        session['parsing_status'] = 'processing'
                        flash(f'✅ CV uploaded! Quick analysis complete. Found {parsed_data["total_skills"]} skills. Deep analysis running in background...', 'success')
                        return redirect(url_for('skill_analysis'))
                    else:
                        flash('Error processing CV data. Please try again.', 'error')
                        return redirect(url_for('upload_cv'))
                else:
                    flash('Could not parse CV. Please ensure it\'s readable.', 'error')
                    return redirect(url_for('upload_cv'))
            except Exception as e:
                flash(f'Error parsing CV: {str(e)}', 'error')
                return redirect(url_for('upload_cv'))
        
        return render_template('upload_cv.html', user=current_user)
    
    # ========== SKILL ANALYSIS ROUTE ==========
    @app.route('/skill-analysis')
    @login_required
    def skill_analysis():
        """Skill gap analysis page"""
        parsed_data = get_parsed_data_from_session()
        
        # Check if deep parsing is complete
        parsing_status = session.get('parsing_status', 'complete')
        is_processing = parsing_status == 'processing'
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                all_skills.extend(skills)
            
            # Show progress indicator if still processing
            if is_processing:
                flash('🔄 Deep analysis is still running in the background. Results will update automatically when complete.', 'info')
            
            employability = SkillAnalyzer.calculate_employability_score(
                all_skills, 
                parsed_data.get('experience_years', 0)
            )
            
            gaps = SkillAnalyzer.analyze_gaps(all_skills)
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
                                 is_processing=is_processing)
        
        return render_template('skill_analysis.html', user=current_user, parsed_data=None, is_processing=False)
    
    # ========== LEARNING ROADMAP ROUTE ==========
    @app.route('/learning-roadmap')
    @login_required
    def learning_roadmap():
        """Personalized learning roadmap page"""
        parsed_data = get_parsed_data_from_session()
        course_api = CourseAPI()
        
        return render_template('learning_roadmap.html', 
                             user=current_user, 
                             parsed_data=parsed_data,
                             skill_analyzer=SkillAnalyzer,
                             course_api=course_api)
    
    # ========== JOB MATCHES ROUTE ==========
    @app.route('/job-matches')
    @login_required
    def job_matches():
        """Job recommendations page"""
        parsed_data = get_parsed_data_from_session()
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                all_skills.extend(skills)
            
            job_matches = SkillAnalyzer.get_job_recommendations(all_skills)
            return render_template('job_matches.html', 
                                 user=current_user, 
                                 job_matches=job_matches,
                                 parsed_data=parsed_data,
                                 skill_analyzer=SkillAnalyzer)
        
        return render_template('job_matches.html', user=current_user, job_matches=None, skill_analyzer=SkillAnalyzer)
    
    # ========== CAREER ASSISTANT ROUTES ==========
    @app.route('/career-assistant')
    @login_required
    def career_assistant():
        """AI career assistant chat page"""
        parsed_data = get_parsed_data_from_session()
        return render_template('career_assistant.html', user=current_user, parsed_data=parsed_data)
    
    @app.route('/api/ask', methods=['POST'])
    @login_required
    def api_ask():
        """API endpoint for career assistant questions"""
        data = request.get_json()
        question = data.get('question', '')
        
        # Get user skills from session
        parsed_data = get_parsed_data_from_session()
        user_skills = []
        experience = 0
        
        if parsed_data:
            for category, skills in parsed_data.get('skills', {}).items():
                user_skills.extend(skills)
            experience = parsed_data.get('experience_years', 0)
        
        # Get AI response
        assistant = CareerAssistant()
        response = assistant.get_response(question, user_skills, experience)
        
        return jsonify(response)
    
    # ========== DASHBOARD ROUTE ==========
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main user dashboard"""
        parsed_data = get_parsed_data_from_session()
        return render_template('dashboard.html', user=current_user, parsed_data=parsed_data)
    
    # ========== PROFILE ROUTE ==========
    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        return render_template('profile.html', user=current_user)
    
    # ========== UNIVERSITY DASHBOARD ROUTE ==========
    @app.route('/university-dashboard')
    @login_required
    def university_dashboard():
        """University intelligence dashboard"""
        # Get parsed data from session
        parsed_data = get_parsed_data_from_session()
        
        # Debug: Print to console
        print(f"=== UNIVERSITY DASHBOARD ===")
        print(f"parsed_data exists: {parsed_data is not None}")
        if parsed_data:
            print(f"skills keys: {parsed_data.get('skills', {}).keys()}")
            print(f"total_skills: {parsed_data.get('total_skills', 0)}")
        
        # Get university analytics using helper functions
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
        
        # Get current time for display
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
    # Option 2: Configure Flask to use static folder at root level
    app = Flask(__name__, 
                static_folder='../static',      # Look for static in parent directory
                static_url_path='/static')      # URL path remains /static
    app.config.from_object('config.Config')
    
    # Configure upload
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Set session configuration
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure login manager
    configure_login_manager()
    
    # Initialize OAuth (MUST be called after app is created)
    from app.utils.oauth import configure_oauth
    configure_oauth(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register routes
    register_routes(app)
    
    return app