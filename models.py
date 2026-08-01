from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
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
    
    # Application retention settings
    retention_days = db.Column(db.Integer, default=30)  # Days to keep applications
    
    # ========== NOTIFICATION PREFERENCES ==========
    receive_notifications = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    notification_frequency = db.Column(db.String(20), default='daily')  # 'realtime', 'daily', 'weekly'
    
    # Relationships - ALL BACKREF NAMES ARE UNIQUE
    profile = db.relationship('Profile', backref='user_profile', uselist=False, cascade='all, delete-orphan')
    
    recruiter_profile = db.relationship(
        'RecruiterProfile', 
        backref='user_recruiter_profile', 
        uselist=False, 
        cascade='all, delete-orphan',
        foreign_keys='RecruiterProfile.user_id'
    )
    
    jobs = db.relationship(
        'Job', 
        backref='job_poster', 
        lazy=True, 
        foreign_keys='Job.poster_id'
    )
    
    candidates = db.relationship('Candidate', backref='user_candidate', lazy=True)
    applications = db.relationship('JobApplication', backref='user_applicant', lazy=True)
    
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
            'total_placements': self.total_placements,
            'retention_days': self.retention_days,
            # Notification preferences
            'receive_notifications': self.receive_notifications,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'notification_frequency': self.notification_frequency
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
    retention_days = db.Column(db.Integer, default=30)  # Application retention period
    
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
    jobs = db.relationship('Job', backref='recruiter_jobs', lazy=True, foreign_keys='Job.recruiter_id')
    placements = db.relationship('Placement', backref='recruiter_placements', lazy=True, foreign_keys='Placement.recruiter_id')
    verified_by_user = db.relationship('User', foreign_keys=[verified_by])
    shortlists = db.relationship('Shortlist', backref='recruiter_shortlists', lazy=True, foreign_keys='Shortlist.recruiter_id')
    
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
            'rating': self.rating,
            'retention_days': self.retention_days
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
    cv_path = db.Column(db.String(500))
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
    placements = db.relationship('Placement', backref='candidate_placements', lazy=True, foreign_keys='Placement.candidate_id')
    shortlists = db.relationship('Shortlist', backref='candidate_shortlists', lazy=True, foreign_keys='Shortlist.candidate_id')
    
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
    placements = db.relationship('Placement', backref='job_placements', lazy=True, foreign_keys='Placement.job_id')
    shortlists = db.relationship('Shortlist', backref='job_shortlists', lazy=True, foreign_keys='Shortlist.job_id')
    applications = db.relationship('JobApplication', backref='job_applications', lazy=True)
    
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
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recruiter = db.relationship('RecruiterProfile', backref='shortlist_recruiter', lazy=True)
    candidate = db.relationship('Candidate', backref='shortlist_candidate', lazy=True)
    job = db.relationship('Job', backref='shortlist_job', lazy=True)
    
    def __repr__(self):
        return f'<Shortlist {self.recruiter.company_name if self.recruiter else "Unknown"} - {self.candidate.name if self.candidate else "Unknown"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'recruiter_id': self.recruiter_id,
            'candidate_id': self.candidate_id,
            'candidate_name': self.candidate.name if self.candidate else None,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ============================================
# JOB APPLICATION MODEL - UPDATED
# ============================================

class JobApplication(db.Model):
    """Job applications submitted by candidates"""
    __tablename__ = 'job_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Applicant info
    applicant_name = db.Column(db.String(255), nullable=False)
    applicant_email = db.Column(db.String(255), nullable=False, index=True)
    applicant_phone = db.Column(db.String(50))
    
    # Application details
    cover_letter = db.Column(db.Text)
    cv_filename = db.Column(db.String(255))
    cv_filepath = db.Column(db.String(500))
    
    # Status
    status = db.Column(db.String(50), default='pending')
    notes = db.Column(db.Text)
    
    # Metadata
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # NEW: Auto-delete expiry and soft delete
    expires_at = db.Column(db.DateTime, nullable=True)  # When this application should be auto-deleted
    is_deleted = db.Column(db.Boolean, default=False)   # Soft delete flag
    
    # Relationships
    job = db.relationship('Job', backref='job_applications', lazy=True)
    applicant = db.relationship('User', backref='user_applications', lazy=True)
    
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
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'is_deleted': self.is_deleted,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    def soft_delete(self):
        """Soft delete the application (can be restored)"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def restore(self):
        """Restore a soft-deleted application"""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_expired(self):
        """Check if the application has expired"""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def get_days_until_expiry(self):
        """Get days until expiry (negative if expired)"""
        if not self.expires_at:
            return None
        delta = self.expires_at - datetime.utcnow()
        return delta.days
    
    @staticmethod
    def create_with_expiry(job_id, user_id, applicant_name, applicant_email, 
                          applicant_phone=None, cover_letter=None, cv_filename=None, 
                          cv_filepath=None, retention_days=30):
        """Create a new application with auto-expiry date"""
        application = JobApplication(
            job_id=job_id,
            user_id=user_id,
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone,
            cover_letter=cover_letter,
            cv_filename=cv_filename,
            cv_filepath=cv_filepath,
            expires_at=datetime.utcnow() + timedelta(days=retention_days)
        )
        return application


# ============================================
# JOB ALERT MODEL
# ============================================

class JobAlert(db.Model):
    """Job alert subscriptions for candidates"""
    __tablename__ = 'job_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Alert criteria
    keywords = db.Column(db.String(500), nullable=True)  # Comma-separated
    job_type = db.Column(db.String(50), nullable=True)  # full_time, part_time, etc.
    location = db.Column(db.String(200), nullable=True)
    salary_min = db.Column(db.Float, nullable=True)
    salary_max = db.Column(db.Float, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    experience_level = db.Column(db.String(50), nullable=True)  # entry, mid, senior
    
    # Notification settings
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, instant
    is_active = db.Column(db.Boolean, default=True)
    
    # Tracking
    last_sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='job_alerts')
    
    def __repr__(self):
        return f'<JobAlert {self.id} - User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'keywords': self.keywords.split(',') if self.keywords else [],
            'job_type': self.job_type,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'category': self.category,
            'experience_level': self.experience_level,
            'frequency': self.frequency,
            'is_active': self.is_active,
            'last_sent_at': self.last_sent_at.strftime('%Y-%m-%d %H:%M') if self.last_sent_at else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None
        }
    
    def matches_job(self, job):
        """Check if a job matches this alert criteria"""
        matches = 0
        total = 0
        
        # Keyword matching
        if self.keywords:
            total += 1
            keywords = [k.strip().lower() for k in self.keywords.split(',')]
            job_text = f"{job.title} {job.description or ''} {' '.join(job.required_skills or [])}".lower()
            if any(k in job_text for k in keywords):
                matches += 1
        
        # Job type
        if self.job_type:
            total += 1
            if job.employment_type and self.job_type == job.employment_type.value:
                matches += 1
        
        # Location
        if self.location:
            total += 1
            if job.location and self.location.lower() in job.location.lower():
                matches += 1
        
        # Category
        # Note: You might need to add a 'category' field to Job model
        # For now, we'll skip if not available
        
        # Experience level
        if self.experience_level:
            total += 1
            if job.experience_level and self.experience_level.lower() in job.experience_level.lower():
                matches += 1
        
        # Salary
        if self.salary_min or self.salary_max:
            total += 1
            if job.salary_min or job.salary_max:
                salary_ok = True
                if self.salary_min and job.salary_max and job.salary_max < self.salary_min:
                    salary_ok = False
                if self.salary_max and job.salary_min and job.salary_min > self.salary_max:
                    salary_ok = False
                if salary_ok:
                    matches += 1
        
        # Return True if at least 50% of criteria match
        if total == 0:
            return True
        return (matches / total) >= 0.5


class JobAlertLog(db.Model):
    """Log of job alerts sent"""
    __tablename__ = 'job_alert_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('job_alerts.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    alert = db.relationship('JobAlert', backref='logs')
    job = db.relationship('Job', backref='alert_logs')
    
    def __repr__(self):
        return f'<JobAlertLog Alert {self.alert_id} -> Job {self.job_id}>'
# ============================================
# INTERVIEW PRACTICE MODELS
# ============================================

class InterviewPractice(db.Model):
    """Interview practice sessions for users"""
    __tablename__ = 'interview_practices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Session details
    job_title = db.Column(db.String(255), nullable=False)
    industry = db.Column(db.String(100), nullable=True)
    experience_level = db.Column(db.String(50), default='mid')
    question_type = db.Column(db.String(50), default='technical')
    
    # Status
    status = db.Column(db.String(50), default='in_progress')
    score = db.Column(db.Float, default=0.0)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Clean approach with unique backrefs
    user = db.relationship('User', backref='interview_practices')
    questions = db.relationship('InterviewQuestion', backref='interview_practice', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('InterviewResponse', backref='interview_practice_responses', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<InterviewPractice {self.job_title} - User {self.user_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'industry': self.industry,
            'experience_level': self.experience_level,
            'question_type': self.question_type,
            'status': self.status,
            'score': self.score,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_questions': len(self.questions) if self.questions else 0,
            'questions_answered': sum(1 for r in self.responses if r.answer is not None) if self.responses else 0
        }


class InterviewQuestion(db.Model):
    """Interview questions for practice"""
    __tablename__ = 'interview_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    practice_id = db.Column(db.Integer, db.ForeignKey('interview_practices.id'), nullable=False)
    
    # Question details
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), default='technical')
    category = db.Column(db.String(100), nullable=True)
    difficulty = db.Column(db.String(20), default='medium')
    order = db.Column(db.Integer, default=0)
    
    # Expected answer (for reference)
    expected_answer = db.Column(db.Text, nullable=True)
    tips = db.Column(db.Text, nullable=True)
    
    # Relationships - Use back_populates for clean bidirectional relationships
    practice = db.relationship('InterviewPractice', back_populates='questions')
    response = db.relationship('InterviewResponse', back_populates='question', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<InterviewQuestion {self.id} - {self.question_text[:50]}...>'


class InterviewResponse(db.Model):
    """User's response to an interview question"""
    __tablename__ = 'interview_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    practice_id = db.Column(db.Integer, db.ForeignKey('interview_practices.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('interview_questions.id'), nullable=False)
    
    # Response details
    answer = db.Column(db.Text, nullable=True)
    audio_url = db.Column(db.String(500), nullable=True)
    time_taken = db.Column(db.Integer, default=0)
    
    # AI Feedback
    feedback = db.Column(db.Text, nullable=True)
    score = db.Column(db.Float, default=0.0)
    strengths = db.Column(db.JSON, default=list)
    improvements = db.Column(db.JSON, default=list)
    key_points = db.Column(db.JSON, default=list)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Clean bidirectional relationships
    practice = db.relationship('InterviewPractice', back_populates='responses')
    question = db.relationship('InterviewQuestion', back_populates='response')
    
    def __repr__(self):
        return f'<InterviewResponse {self.id} - Score: {self.score}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'question_text': self.question.question_text if self.question else None,
            'answer': self.answer,
            'time_taken': self.time_taken,
            'feedback': self.feedback,
            'score': self.score,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'key_points': self.key_points,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ============================================
# USER LOADER
# ============================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))