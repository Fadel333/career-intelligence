from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(50), default='student', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    # CV Analysis Data (stored as JSON)
    cv_analysis = db.Column(db.Text, nullable=True)  # JSON string of parsed CV data
    cv_filename = db.Column(db.String(255), nullable=True)
    cv_uploaded_at = db.Column(db.DateTime, nullable=True)
    employability_score = db.Column(db.Integer, default=0)
    detected_sector = db.Column(db.String(50), nullable=True)
    
    # Relationships
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_fullname(self):
        return self.fullname
    
    def is_student(self):
        return self.user_type == 'student'
    
    def is_professional(self):
        return self.user_type == 'professional'
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def save_cv_analysis(self, parsed_data: dict):
        """Save CV analysis results to database"""
        self.cv_analysis = json.dumps(parsed_data)
        self.cv_uploaded_at = datetime.utcnow()
        self.employability_score = parsed_data.get('employability_score', 0)
        self.detected_sector = parsed_data.get('detected_sector', 'general')
        db.session.commit()
    
    def get_cv_analysis(self):
        """Get CV analysis from database"""
        if self.cv_analysis:
            return json.loads(self.cv_analysis)
        return None
    
    def get_skills(self):
        """Get extracted skills from CV analysis"""
        analysis = self.get_cv_analysis()
        if analysis and 'skills' in analysis:
            return analysis['skills']
        return {}
    
    def get_total_skills(self):
        """Get total number of skills"""
        skills = self.get_skills()
        return sum(len(s) for s in skills.values())
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'user_type': self.user_type,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'location': self.location,
            'bio': self.bio,
            'phone': self.phone,
            'employability_score': self.employability_score,
            'detected_sector': self.detected_sector,
            'total_skills': self.get_total_skills(),
            'cv_uploaded': bool(self.cv_analysis)
        }


class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)
    portfolio_url = db.Column(db.String(255), nullable=True)
    current_job = db.Column(db.String(100), nullable=True)
    company = db.Column(db.String(100), nullable=True)
    education = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)
    experience_years = db.Column(db.Integer, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Profile for User {self.user_id}>'
    
    def get_skills_list(self):
        if self.skills:
            return [skill.strip() for skill in self.skills.split(',')]
        return []
    
    def set_skills_list(self, skills_list):
        self.skills = ', '.join(skills_list)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))