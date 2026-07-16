from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json
import enum


# ============================================
# ENUMS
# ============================================

class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    RECRUITER = "recruiter"
    STUDENT = "student"
    PROFESSIONAL = "professional"
    UNIVERSITY = "university"


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    CLOSED = "closed"
    FILLED = "filled"


class PlacementStatus(str, enum.Enum):
    """Placement status enumeration"""
    PENDING = "pending"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"


class EmploymentType(str, enum.Enum):
    """Employment type enumeration"""
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"


# ============================================
# USER MODEL
# ============================================

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
    cv_analysis = db.Column(db.Text, nullable=True)
    cv_filename = db.Column(db.String(255), nullable=True)
    cv_uploaded_at = db.Column(db.DateTime, nullable=True)
    employability_score = db.Column(db.Integer, default=0)
    detected_sector = db.Column(db.String(50), nullable=True)
    
    # Recruiter-specific fields
    company_name = db.Column(db.String(255), nullable=True)
    company_registration = db.Column(db.String(255), nullable=True)
    recruiter_commission_rate = db.Column(db.Integer, default=10)
    total_earnings = db.Column(db.Float, default=0.0)
    total_placements = db.Column(db.Integer, default=0)
    
    # Relationships - WITH foreign_keys specified
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    recruiter_profile = db.relationship(
        'RecruiterProfile', 
        backref='user', 
        uselist=False, 
        cascade='all, delete-orphan',
        foreign_keys='RecruiterProfile.user_id'
    )
    
    jobs = db.relationship(
        'Job', 
        backref='poster', 
        lazy=True, 
        foreign_keys='Job.poster_id'
    )
    
    candidates = db.relationship('Candidate', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def get_fullname(self):
        return self.fullname
    
    def is_student(self):
        return self.user_type == 'student'
    
    def is_professional(self):
        return self.user_type == 'professional'
    
    def is_recruiter(self):
        return self.user_type == 'recruiter'
    
    def is_partner(self):
        return self.user_type == 'partner'
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_university(self):
        return self.user_type == 'university'
    
    def get_role(self):
        try:
            return UserRole(self.user_type)
        except ValueError:
            return UserRole.STUDENT
    
    def update_last_login(self):
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def save_cv_analysis(self, parsed_data: dict):
        self.cv_analysis = json.dumps(parsed_data)
        self.cv_uploaded_at = datetime.utcnow()
        self.employability_score = parsed_data.get('employability_score', 0)
        self.detected_sector = parsed_data.get('detected_sector', 'general')
        db.session.commit()
    
    def get_cv_analysis(self):
        if self.cv_analysis:
            return json.loads(self.cv_analysis)
        return None
    
    def get_skills(self):
        analysis = self.get_cv_analysis()
        if analysis and 'skills' in analysis:
            return analysis['skills']
        return {}
    
    def get_total_skills(self):
        skills = self.get_skills()
        return sum(len(s) for s in skills.values())
    
    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'user_type': self.user_type,
            'role': self.user_type,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'location': self.location,
            'bio': self.bio,
            'phone': self.phone,
            'employability_score': self.employability_score,
            'detected_sector': self.detected_sector,
            'total_skills': self.get_total_skills(),
            'cv_uploaded': bool(self.cv_analysis),
            'is_recruiter': self.is_recruiter(),
            'company_name': self.company_name,
            'total_earnings': self.total_earnings,
            'total_placements': self.total_placements
        }


# ============================================
# PROFILE MODEL
# ============================================

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


# ============================================
# RECRUITER PROFILE MODEL
# ============================================

class RecruiterProfile(db.Model):
    """Extended recruiter profile with company details"""
    __tablename__ = 'recruiter_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Company details
    company_name = db.Column(db.String(255))
    company_description = db.Column(db.Text)
    company_website = db.Column(db.String(255))
    company_logo = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(255))
    
    # Settings
    auto_approve_candidates = db.Column(db.Boolean, default=False)
    min_match_percentage = db.Column(db.Float, default=70.0)
    
    # Stats (cached)
    total_candidates_reviewed = db.Column(db.Integer, default=0)
    total_jobs_posted = db.Column(db.Integer, default=0)
    active_jobs = db.Column(db.Integer, default=0)
    
    # Validation fields
    verification_status = db.Column(db.String(50), default='pending')
    verification_documents = db.Column(db.JSON, default=list)
    license_number = db.Column(db.String(100), nullable=True)
    tax_id = db.Column(db.String(100), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    
    # Performance tracking
    avg_placement_time = db.Column(db.Float, default=0.0)
    success_rate = db.Column(db.Float, default=0.0)
    complaint_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    jobs = db.relationship('Job', backref='recruiter', lazy=True, foreign_keys='Job.recruiter_id')
    placements = db.relationship('Placement', backref='recruiter', lazy=True, foreign_keys='Placement.recruiter_id')
    verified_by_user = db.relationship('User', foreign_keys=[verified_by])
    shortlists = db.relationship('Shortlist', backref='recruiter', lazy=True, foreign_keys='Shortlist.recruiter_id')
    
    def __repr__(self):
        return f'<RecruiterProfile {self.company_name or self.user_id}>'
    
    def is_verified(self):
        return self.verification_status == 'approved'
    
    def can_post_jobs(self):
        return self.is_verified() or self.verification_status == 'pending'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_description': self.company_description,
            'company_website': self.company_website,
            'industry': self.industry,
            'location': self.location,
            'min_match_percentage': self.min_match_percentage,
            'total_candidates_reviewed': self.total_candidates_reviewed,
            'total_jobs_posted': self.total_jobs_posted,
            'active_jobs': self.active_jobs,
            'verification_status': self.verification_status,
            'is_verified': self.is_verified(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'rating': self.rating
        }


# ============================================
# CANDIDATE MODEL
# ============================================

class Candidate(db.Model):
    """CV/Candidate data extracted from uploaded documents"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Personal info
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(50))
    location = db.Column(db.String(255))
    
    # CV data
    cv_filename = db.Column(db.String(255))
    cv_filepath = db.Column(db.String(500))
    cv_text = db.Column(db.Text)
    
    # Extracted fields
    skills = db.Column(db.JSON, default=list)
    experience_years = db.Column(db.Float, default=0.0)
    education = db.Column(db.JSON, default=list)
    certifications = db.Column(db.JSON, default=list)
    languages = db.Column(db.JSON, default=list)
    
    # AI scores
    employability_score = db.Column(db.Integer, default=0)
    skill_match_percentage = db.Column(db.Float, default=0.0)
    
    # Metadata
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = db.Column(db.Boolean, default=False)
    
    # Relationships
    placements = db.relationship('Placement', backref='candidate', lazy=True, foreign_keys='Placement.candidate_id')
    shortlists = db.relationship('Shortlist', backref='candidate', lazy=True, foreign_keys='Shortlist.candidate_id')
    
    def __repr__(self):
        return f'<Candidate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'education': self.education,
            'certifications': self.certifications,
            'languages': self.languages,
            'employability_score': self.employability_score,
            'skill_match_percentage': self.skill_match_percentage,
            'cv_filename': self.cv_filename,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'is_processed': self.is_processed
        }


# ============================================
# JOB MODEL
# ============================================

class Job(db.Model):
    """Job postings by recruiters"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id'), nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Job details
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.JSON, default=list)
    responsibilities = db.Column(db.JSON, default=list)
    employment_type = db.Column(db.Enum(EmploymentType), default=EmploymentType.FULL_TIME)
    experience_level = db.Column(db.String(50), default='mid')
    
    # Salary
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default='GHS')
    
    # Location
    location = db.Column(db.String(255))
    remote_available = db.Column(db.Boolean, default=False)
    
    # Metadata
    status = db.Column(db.Enum(JobStatus), default=JobStatus.DRAFT)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    
    # Skills matching
    required_skills = db.Column(db.JSON, default=list)
    preferred_skills = db.Column(db.JSON, default=list)
    
    # Relationships
    placements = db.relationship('Placement', backref='job', lazy=True, foreign_keys='Placement.job_id')
    shortlists = db.relationship('Shortlist', backref='job', lazy=True, foreign_keys='Shortlist.job_id')
    
    def __repr__(self):
        return f'<Job {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'employment_type': self.employment_type.value if self.employment_type else None,
            'experience_level': self.experience_level,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'currency': self.currency,
            'location': self.location,
            'remote_available': self.remote_available,
            'status': self.status.value if self.status else None,
            'posted_at': self.posted_at.isoformat() if self.posted_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'required_skills': self.required_skills,
            'preferred_skills': self.preferred_skills
        }


# ============================================
# PLACEMENT MODEL
# ============================================

class Placement(db.Model):
    """Candidate placement tracking"""
    __tablename__ = 'placements'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    
    # Match data
    match_percentage = db.Column(db.Float, default=0.0)
    match_details = db.Column(db.JSON, default=dict)
    
    # Status
    status = db.Column(db.Enum(PlacementStatus), default=PlacementStatus.PENDING)
    notes = db.Column(db.Text)
    
    # Commission
    commission_amount = db.Column(db.Float, default=0.0)
    commission_paid = db.Column(db.Boolean, default=False)
    
    # Timeline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hired_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Placement {self.id}: {self.candidate.name if self.candidate else "Unknown"} -> {self.job.title if self.job else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'match_percentage': self.match_percentage,
            'match_details': self.match_details,
            'status': self.status.value if self.status else None,
            'notes': self.notes,
            'commission_amount': self.commission_amount,
            'commission_paid': self.commission_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'hired_at': self.hired_at.isoformat() if self.hired_at else None
        }


# ============================================
# SHORTLIST MODEL
# ============================================

class Shortlist(db.Model):
    """Recruiter shortlisted candidates"""
    __tablename__ = 'shortlists'
    
    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# models.py - Add after the Placement model

class JobApplication(db.Model):
    """Job applications submitted by candidates"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # If logged in
    
    # Applicant info
    applicant_name = db.Column(db.String(255), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False, index=True)
    applicant_phone = db.Column(db.String(50))
    
    # Application details
    cover_letter = db.Column(db.Text)
    cv_filename = db.Column(db.String(255))  # Uploaded CV
    cv_filepath = db.Column(db.String(500))
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, reviewed, shortlisted, rejected, hired
    notes = db.Column(db.Text)
    
    # Metadata
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    job = db.relationship('Job', backref='applications', lazy=True)
    user = db.relationship('User', backref='applications', lazy=True)
    
    def __repr__(self):
        return f'<JobApplication {self.applicant_name} -> {self.job.title if self.job else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'applicant_name': self.applicant_name,
            'applicant_email': self.applicant_email,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
    
    def __repr__(self):
        return f'<Shortlist {self.recruiter.company_name if self.recruiter else "Unknown"} - {self.candidate.name if self.candidate else "Unknown"}>'


# ============================================
# USER LOADER
# ============================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))