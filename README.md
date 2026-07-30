# 🧠 FADTECH Labs Career Intelligence System

 https://img.shields.io/badge/License-MIT-yellow.svg
https://img.shields.io/badge/Python-3.11+-blue.svg
https://img.shields.io/badge/Flask-3.1.3-green.svg
https://img.shields.io/badge/Status-MVP-brightgreen.svg
https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg

AI-Powered Employability Intelligence · Labor-Market Analysis · Skill-Gap Engine · Personalized Career Roadmaps

📖 Overview
The Career Intelligence System is Africa's first deeply localized AI-powered employability platform, built to close the skills gap between education and industry.

Developed by FADTECH LABS, this platform bridges the critical disconnect between what students learn and what employers actually need by providing real-time labor market intelligence, personalized skill-gap analysis, and actionable career roadmaps.

🌟 Key Features
✅ Completed Features (MVP)
Feature	Status	Description
📄 AI CV Parsing	✅ Complete	Extract skills from PDF/DOCX with 300+ skill detection
📊 Skill-Gap Analysis	✅ Complete	Compare your skills against real market demands
🎯 Employability Score	✅ Complete	AI-calculated score (0-100) for your target role
🗺️ Learning Roadmap	✅ Complete	Personalized course recommendations from 10+ platforms
💼 Job Matching	✅ Complete	Role-based job recommendations with salary insights
🤖 AI Career Assistant	✅ Complete	RAG-powered conversational AI for career questions
🏫 University Dashboard	✅ Complete	Analytics for educational institutions
🏢 Recruiter Dashboard	✅ Complete	Post jobs, manage applications, find candidates
📝 Application Management	✅ Complete	Track and manage job applications
🎙️ Interview Practice	✅ Complete	AI-generated questions with feedback
🔔 Job Alerts	✅ Complete	Email notifications for matching jobs
🔐 OAuth 2.0	✅ Complete	Login with Google, LinkedIn, or GitHub
🔑 Password Reset	✅ Complete	Secure email-based password recovery
📱 Mobile Responsive	✅ Complete	Works on all devices
🎨 Dark Theme UI	✅ Complete	Modern glass-morphism design
📧 Email Notifications	✅ Complete	Welcome emails, application updates, password reset
🚧 In Progress / Planned Features
Feature	Status	Description
📱 SMS Notifications	🚧 Planned	Twilio/Africa's Talking integration
🎨 AI Resume Builder	🚧 Planned	Generate optimized resumes with AI
📊 Advanced Analytics	🚧 Planned	Enhanced reporting and insights
🤝 Mentor Matching	🚧 Planned	Connect students with industry professionals
📅 Future Roadmap
🌍 Pan-African Expansion (Nigeria, Kenya, South Africa)

📱 Mobile App (iOS/Android)

🏛️ Government Workforce Analytics

🎓 Certification Verification

🔗 Blockchain Credentials

🧠 Advanced AI Career Simulation

🛠️ Technology Stack
Layer	Technology
Backend	Flask 3.1.3 (Python)
Database	PostgreSQL (Supabase)
ORM	SQLAlchemy
Migrations	Flask-Migrate (Alembic)
Frontend	HTML5, Tailwind CSS, JavaScript, Font Awesome
AI/NLP	spaCy 3.7.2, Sentence Transformers, OpenAI API
Vector Search	ChromaDB
OAuth	Authlib (Google, LinkedIn, GitHub)
Email	Flask-Mail (Gmail / SendGrid)
Course APIs	YouTube, Coursera, Udemy
SMS (Planned)	Twilio / Africa's Talking
Deployment	Render.com
Version Control	Git / GitHub
📂 Project Structure
text
career-intelligence/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # Authentication & OAuth routes
│   ├── jobs/
│   │   └── routes.py            # Job board & application routes
│   ├── recruiter/
│   │   ├── __init__.py
│   │   └── routes.py            # Recruiter dashboard routes
│   ├── admin/
│   │   └── routes.py            # Admin routes
│   ├── templates/
│   │   ├── base.html            # Base template with dark theme
│   │   ├── login.html           # Login with OAuth
│   │   ├── register.html        # Registration with OAuth
│   │   ├── dashboard.html       # User dashboard with real stats
│   │   ├── upload_cv.html       # CV upload with progress bar
│   │   ├── skill_analysis.html  # Skill gap analysis
│   │   ├── learning_roadmap.html # Personalized learning roadmap
│   │   ├── job_matches.html     # Job recommendations
│   │   ├── career_assistant.html # AI chat assistant
│   │   ├── university_dashboard.html # University analytics
│   │   ├── forgot_password.html # Password reset request
│   │   ├── reset_password.html  # Password reset form
│   │   ├── profile.html         # User profile
│   │   ├── privacy_policy.html  # Privacy policy
│   │   ├── terms_of_use.html    # Terms of use
│   │   ├── email/
│   │   │   ├── job_alert.html   # Job alert email template
│   │   │   └── reset_password.html # Password reset email
│   │   ├── interview/
│   │   │   ├── hub.html         # Interview practice hub
│   │   │   ├── setup.html       # Setup interview session
│   │   │   ├── session.html     # Active interview session
│   │   │   └── summary.html     # Interview summary
│   │   └── recruiter/
│   │       ├── dashboard.html   # Recruiter dashboard
│   │       ├── applications.html # Manage applications
│   │       ├── application_detail.html # Application details
│   │       ├── create_job.html  # Post a job
│   │       ├── edit_job.html    # Edit job
│   │       ├── jobs.html        # Manage jobs
│   │       ├── candidates.html  # Browse candidates
│   │       ├── candidate_detail.html # Candidate profile
│   │       ├── shortlist.html   # Shortlisted candidates
│   │       ├── placements.html  # Track placements
│   │       ├── analytics.html   # Recruiter analytics
│   │       ├── settings.html    # Recruiter settings
│   │       ├── verification.html # Company verification
│   │       └── application_settings.html # Retention settings
│   └── utils/
│       ├── advanced_cv_parser.py # Advanced NLP parsing (spaCy)
│       ├── hybrid_parser.py    # Hybrid CV parser (quick + deep)
│       ├── cv_parser.py        # CV parsing interface
│       ├── skill_analyzer.py   # Skill gap analysis engine
│       ├── openai_assistant.py # AI career assistant
│       ├── course_api.py       # Course API integration
│       ├── email.py            # Email functions
│       ├── job_alert_checker.py # Job alert notification system
│       ├── job_notifier.py     # Job notification engine
│       ├── notification_service.py # SMS/Email notifications
│       └── oauth.py            # OAuth configuration
├── static/
│   ├── images/
│   │   ├── logo.svg            # Brain logo
│   │   └── background.jpg      # Background image
│   └── applications/           # Uploaded CV files
├── uploads/                    # CV upload directory
├── migrations/                 # Database migrations
├── config.py                   # Flask configuration
├── extensions.py               # Flask extensions (db, login_manager, mail)
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── wsgi.py                     # WSGI for production
├── Procfile                    # Render deployment
├── runtime.txt                 # Python version for Render
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore file
├── LICENSE                     # MIT License
└── README.md                   # This file
🚀 Installation & Setup
Prerequisites
Python 3.11+

pip

Git

Supabase account (for PostgreSQL)

OpenAI API key (for AI features)

Google OAuth credentials (for social login)

Step 1: Clone the Repository
bash
git clone https://github.com/Fadel333/career-intelligence.git
cd career-intelligence
Step 2: Create Virtual Environment
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
Step 4: Set Up Environment Variables
Create a .env file in the root directory:

env
# Database
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres

# Flask
SECRET_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# OAuth
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxxxxxxx
LINKEDIN_CLIENT_ID=xxxxx
LINKEDIN_CLIENT_SECRET=xxxxx
GITHUB_CLIENT_ID=xxxxx
GITHUB_CLIENT_SECRET=xxxxx

# Email (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# YouTube API
YOUTUBE_API_KEY=xxxxx

# Base URL
BASE_URL=http://localhost:5000
Step 5: Initialize Database
bash
flask db upgrade
Step 6: Run the Application
bash
flask run
Visit http://localhost:5000 to access the application.

📊 Database Schema
Core Tables
Table	Purpose
users	User accounts and authentication
profiles	User profile information
recruiter_profiles	Recruiter company details
candidates	CV/candidate data and skills
jobs	Job postings
job_applications	Job applications
job_alerts	Job alert subscriptions
placements	Successful placements
shortlists	Shortlisted candidates
interview_practices	Interview practice sessions
interview_questions	Practice questions
interview_responses	User responses and feedback
🧪 Testing
Test Password Reset Flow
bash
# 1. Go to login page
http://localhost:5000/auth/login

# 2. Click "Forgot Password?"
# 3. Enter your email
# 4. Check your inbox for reset link
# 5. Click link and set new password
Test OAuth Login
bash
# Google
http://localhost:5000/auth/login/google

# LinkedIn
http://localhost:5000/auth/login/linkedin

# GitHub
http://localhost:5000/auth/login/github
🔐 Environment Variables
Variable	Required	Description
DATABASE_URL	✅	Supabase PostgreSQL connection string
SECRET_KEY	✅	Flask secret key
OPENAI_API_KEY	✅	OpenAI API key
GOOGLE_CLIENT_ID	✅	Google OAuth client ID
GOOGLE_CLIENT_SECRET	✅	Google OAuth client secret
LINKEDIN_CLIENT_ID	⬜	LinkedIn OAuth client ID
LINKEDIN_CLIENT_SECRET	⬜	LinkedIn OAuth client secret
GITHUB_CLIENT_ID	⬜	GitHub OAuth client ID
GITHUB_CLIENT_SECRET	⬜	GitHub OAuth client secret
MAIL_USERNAME	✅	Email for notifications
MAIL_PASSWORD	✅	Email password/App Password
YOUTUBE_API_KEY	⬜	YouTube API key for courses
BASE_URL	✅	Base URL for email links
TWILIO_ACCOUNT_SID	⬜	Twilio SMS (optional)
TWILIO_AUTH_TOKEN	⬜	Twilio SMS (optional)
TWILIO_PHONE_NUMBER	⬜	Twilio SMS (optional)
AFRICA_TALKING_USERNAME	⬜	Africa's Talking SMS (optional)
AFRICA_TALKING_API_KEY	⬜	Africa's Talking SMS (optional)
🌐 Deployment
Deploy to Render
Push your code to GitHub

Connect your repository to Render.com

Configure:

Build Command: pip install -r requirements.txt

Start Command: gunicorn wsgi:app

Add all environment variables

Click Deploy

Deploy to Heroku
bash
heroku create career-intelligence
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=sk-xxxxx
git push heroku main
🤝 Contributing
We welcome contributions! Please follow these steps:

Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add some amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
OpenAI for AI capabilities

Supabase for PostgreSQL hosting

spaCy for NLP processing

Flask community for excellent documentation

All contributors and testers

📞 Contact & Support
FADTECH LABS
Building Intelligence That Opens Doors

📍 Ghana · West Africa
📧 fadiliddrisu24@gmail.com

⭐ Star History
If you find this project useful, please give it a ⭐ on GitHub!

Built with ❤️ by FADTECH LABS
