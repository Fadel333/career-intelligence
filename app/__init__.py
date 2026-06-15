from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import login_required, current_user
from extensions import db, login_manager
from werkzeug.utils import secure_filename
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import blueprints and utils
from app.auth.routes import auth_bp
from app.utils.cv_parser import CVParser
from app.utils.skill_analyzer import SkillAnalyzer
from app.utils.ai_assistant import CareerAssistant

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}


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


def register_routes(app):
    """Register all application routes"""
    
    # ========== PUBLIC ROUTES ==========
    @app.route('/')
    def index():
        """Landing page"""
        return render_template('base.html')
    
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
            
            parsed_data = CVParser.parse_cv(filepath)
            
            if parsed_data:
                session['parsed_cv'] = parsed_data
                session['cv_filename'] = file.filename
                flash(f'CV uploaded and parsed successfully! Found {parsed_data["total_skills"]} skills.', 'success')
                return redirect(url_for('skill_analysis'))
            else:
                flash('Could not parse CV. Please ensure it\'s readable.', 'error')
                return redirect(url_for('upload_cv'))
        
        return render_template('upload_cv.html', user=current_user)
    
    # ========== SKILL ANALYSIS ROUTE ==========
    @app.route('/skill-analysis')
    @login_required
    def skill_analysis():
        """Skill gap analysis page"""
        parsed_data = session.get('parsed_cv', None)
        
        if parsed_data and parsed_data.get('skills'):
            all_skills = []
            for category, skills in parsed_data['skills'].items():
                all_skills.extend(skills)
            
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
                                 all_skills=all_skills)
        
        return render_template('skill_analysis.html', user=current_user, parsed_data=None)
    
    # ========== LEARNING ROADMAP ROUTE ==========
    @app.route('/learning-roadmap')
    @login_required
    def learning_roadmap():
        """Personalized learning roadmap page"""
        parsed_data = session.get('parsed_cv', None)
        return render_template('learning_roadmap.html', 
                             user=current_user, 
                             parsed_data=parsed_data,
                             skill_analyzer=SkillAnalyzer)
    
    # ========== JOB MATCHES ROUTE ==========
    @app.route('/job-matches')
    @login_required
    def job_matches():
        """Job recommendations page"""
        parsed_data = session.get('parsed_cv', None)
        
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
        parsed_data = session.get('parsed_cv', None)
        return render_template('career_assistant.html', user=current_user, parsed_data=parsed_data)
    
    @app.route('/api/ask', methods=['POST'])
    @login_required
    def api_ask():
        """API endpoint for career assistant questions"""
        data = request.get_json()
        question = data.get('question', '')
        
        # Get user skills from session
        parsed_data = session.get('parsed_cv', None)
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
        parsed_data = session.get('parsed_cv', None)
        return render_template('dashboard.html', user=current_user, parsed_data=parsed_data)
    
    # ========== PROFILE ROUTE ==========
    @app.route('/profile')
    @login_required
    def profile():
        """User profile page"""
        return render_template('profile.html', user=current_user)


def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Configure upload
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Configure login manager
    configure_login_manager()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register routes
    register_routes(app)
    
    return app