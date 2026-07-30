<div align="center">

# 🧠 FADTECH Labs — Career Intelligence System

**AI-Powered Employability Intelligence for Africa's Workforce**

*Closing the gap between what students learn and what employers need*

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![Status](https://img.shields.io/badge/Status-MVP-brightgreen.svg)
![Database](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E.svg)

[Overview](#-overview) • [Features](#-key-features) • [Tech Stack](#️-technology-stack) • [Installation](#-installation--setup) • [Deployment](#-deployment) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

The **Career Intelligence System** is Africa's first deeply localized, AI-powered employability platform — built to close the skills gap between education and industry.

Developed by **FADTECH Labs**, the platform bridges the critical disconnect between what students learn and what employers actually need, by providing real-time labor market intelligence, personalized skill-gap analysis, and actionable career roadmaps.

---

## 🌟 Key Features

### ✅ Completed (MVP)

| Feature | Description |
|---|---|
| 📄 **AI CV Parsing** | Extracts skills from PDF/DOCX files with detection across 300+ skills |
| 📊 **Skill-Gap Analysis** | Compares a user's skills against real, current market demand |
| 🎯 **Employability Score** | AI-calculated score (0–100) benchmarked against a target role |
| 🗺️ **Learning Roadmap** | Personalized course recommendations sourced from 10+ platforms |
| 💼 **Job Matching** | Role-based job recommendations with salary insights |
| 🤖 **AI Career Assistant** | RAG-powered conversational assistant for career guidance |
| 🏫 **University Dashboard** | Analytics for educational institutions |
| 🏢 **Recruiter Dashboard** | Post jobs, manage applications, and discover candidates |
| 📝 **Application Management** | Track and manage job applications end-to-end |
| 🎙️ **Interview Practice** | AI-generated interview questions with real-time feedback |
| 🔔 **Job Alerts** | Automated email notifications for matching roles |
| 🔐 **OAuth 2.0** | Sign in with Google, LinkedIn, or GitHub |
| 🔑 **Password Reset** | Secure, email-based password recovery flow |
| 📱 **Mobile Responsive** | Fully optimized across all device sizes |
| 🎨 **Dark Theme UI** | Modern glass-morphism visual design |
| 📧 **Email Notifications** | Welcome emails, application updates, and reset confirmations |

### 🚧 In Progress / Planned

| Feature | Description |
|---|---|
| 📱 **SMS Notifications** | Twilio / Africa's Talking integration |
| 🎨 **AI Resume Builder** | Generate ATS-optimized resumes with AI |
| 📊 **Advanced Analytics** | Enhanced reporting and institutional insights |
| 🤝 **Mentor Matching** | Connect students with industry professionals |

### 📅 Future Roadmap

- 🌍 **Pan-African Expansion** — Nigeria, Kenya, South Africa
- 📱 **Native Mobile Apps** — iOS and Android
- 🏛️ **Government Workforce Analytics**
- 🎓 **Certification Verification**
- 🔗 **Blockchain-Based Credentials**
- 🧠 **Advanced AI Career Simulation**

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Flask 3.1.3 (Python) |
| **Database** | PostgreSQL (Supabase) |
| **ORM** | SQLAlchemy |
| **Migrations** | Flask-Migrate (Alembic) |
| **Frontend** | HTML5, Tailwind CSS, JavaScript, Font Awesome |
| **AI / NLP** | spaCy 3.7.2, Sentence Transformers, OpenAI API |
| **Vector Search** | ChromaDB |
| **OAuth** | Authlib (Google, LinkedIn, GitHub) |
| **Email** | Flask-Mail (Gmail / SendGrid) |
| **Course APIs** | YouTube, Coursera, Udemy |
| **SMS** *(planned)* | Twilio / Africa's Talking |
| **Deployment** | Render.com |
| **Version Control** | Git / GitHub |

---

## 📂 Project Structure

```
career-intelligence/
├── app/
│   ├── __init__.py                 # Flask app factory
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py                # Authentication & OAuth routes
│   ├── jobs/
│   │   └── routes.py                # Job board & application routes
│   ├── recruiter/
│   │   ├── __init__.py
│   │   └── routes.py                # Recruiter dashboard routes
│   ├── admin/
│   │   └── routes.py                # Admin routes
│   ├── templates/
│   │   ├── base.html                # Base template with dark theme
│   │   ├── login.html               # Login with OAuth
│   │   ├── register.html            # Registration with OAuth
│   │   ├── dashboard.html           # User dashboard with real stats
│   │   ├── upload_cv.html           # CV upload with progress bar
│   │   ├── skill_analysis.html      # Skill gap analysis
│   │   ├── learning_roadmap.html    # Personalized learning roadmap
│   │   ├── job_matches.html         # Job recommendations
│   │   ├── career_assistant.html    # AI chat assistant
│   │   ├── university_dashboard.html # University analytics
│   │   ├── forgot_password.html     # Password reset request
│   │   ├── reset_password.html      # Password reset form
│   │   ├── profile.html             # User profile
│   │   ├── privacy_policy.html      # Privacy policy
│   │   ├── terms_of_use.html        # Terms of use
│   │   ├── email/
│   │   │   ├── job_alert.html       # Job alert email template
│   │   │   └── reset_password.html  # Password reset email
│   │   ├── interview/
│   │   │   ├── hub.html             # Interview practice hub
│   │   │   ├── setup.html           # Setup interview session
│   │   │   ├── session.html         # Active interview session
│   │   │   └── summary.html         # Interview summary
│   │   └── recruiter/
│   │       ├── dashboard.html       # Recruiter dashboard
│   │       ├── applications.html    # Manage applications
│   │       ├── application_detail.html # Application details
│   │       ├── create_job.html      # Post a job
│   │       ├── edit_job.html        # Edit job
│   │       ├── jobs.html            # Manage jobs
│   │       ├── candidates.html      # Browse candidates
│   │       ├── candidate_detail.html # Candidate profile
│   │       ├── shortlist.html       # Shortlisted candidates
│   │       ├── placements.html      # Track placements
│   │       ├── analytics.html       # Recruiter analytics
│   │       ├── settings.html        # Recruiter settings
│   │       ├── verification.html    # Company verification
│   │       └── application_settings.html # Retention settings
│   └── utils/
│       ├── advanced_cv_parser.py    # Advanced NLP parsing (spaCy)
│       ├── hybrid_parser.py         # Hybrid CV parser (quick + deep)
│       ├── cv_parser.py             # CV parsing interface
│       ├── skill_analyzer.py        # Skill gap analysis engine
│       ├── openai_assistant.py      # AI career assistant
│       ├── course_api.py            # Course API integration
│       ├── email.py                 # Email functions
│       ├── job_alert_checker.py     # Job alert notification system
│       ├── job_notifier.py          # Job notification engine
│       ├── notification_service.py  # SMS/Email notifications
│       └── oauth.py                 # OAuth configuration
├── static/
│   ├── images/
│   │   ├── logo.svg                 # Brain logo
│   │   └── background.jpg           # Background image
│   └── applications/                # Uploaded CV files
├── uploads/                          # CV upload directory
├── migrations/                       # Database migrations
├── config.py                         # Flask configuration
├── extensions.py                     # Flask extensions (db, login_manager, mail)
├── models.py                         # Database models
├── requirements.txt                  # Python dependencies
├── run.py                            # Application entry point
├── wsgi.py                           # WSGI entry point for production
├── Procfile                          # Render deployment config
├── runtime.txt                       # Python version for Render
├── .env                               # Environment variables (not committed)
├── .gitignore                        # Git ignore rules
├── LICENSE                           # MIT License
└── README.md                         # This file
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- pip
- Git
- A [Supabase](https://supabase.com) account (for PostgreSQL)
- An OpenAI API key (for AI features)
- Google OAuth credentials (for social login)

### 1. Clone the Repository

```bash
git clone https://github.com/Fadel333/career-intelligence.git
cd career-intelligence
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
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
```

### 5. Initialize the Database

```bash
flask db upgrade
```

### 6. Run the Application

```bash
flask run
```

The application will be available at **http://localhost:5000**.

---

## 📊 Database Schema

| Table | Purpose |
|---|---|
| `users` | User accounts and authentication |
| `profiles` | User profile information |
| `recruiter_profiles` | Recruiter company details |
| `candidates` | CV and candidate skill data |
| `jobs` | Job postings |
| `job_applications` | Job applications |
| `job_alerts` | Job alert subscriptions |
| `placements` | Successful placements |
| `shortlists` | Shortlisted candidates |
| `interview_practices` | Interview practice sessions |
| `interview_questions` | Practice questions |
| `interview_responses` | User responses and feedback |

---

## 🧪 Testing

### Password Reset Flow

```bash
# 1. Navigate to the login page
http://localhost:5000/auth/login

# 2. Click "Forgot Password?"
# 3. Enter your email address
# 4. Check your inbox for the reset link
# 5. Follow the link to set a new password
```

### OAuth Login

```bash
# Google
http://localhost:5000/auth/login/google

# LinkedIn
http://localhost:5000/auth/login/linkedin

# GitHub
http://localhost:5000/auth/login/github
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | Supabase PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Flask secret key |
| `OPENAI_API_KEY` | ✅ | OpenAI API key |
| `GOOGLE_CLIENT_ID` | ✅ | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | ✅ | Google OAuth client secret |
| `LINKEDIN_CLIENT_ID` | ⬜ | LinkedIn OAuth client ID |
| `LINKEDIN_CLIENT_SECRET` | ⬜ | LinkedIn OAuth client secret |
| `GITHUB_CLIENT_ID` | ⬜ | GitHub OAuth client ID |
| `GITHUB_CLIENT_SECRET` | ⬜ | GitHub OAuth client secret |
| `MAIL_USERNAME` | ✅ | Email address used for notifications |
| `MAIL_PASSWORD` | ✅ | Email password / app password |
| `YOUTUBE_API_KEY` | ⬜ | YouTube API key for course recommendations |
| `BASE_URL` | ✅ | Base URL used for email links |
| `TWILIO_ACCOUNT_SID` | ⬜ | Twilio SMS (optional) |
| `TWILIO_AUTH_TOKEN` | ⬜ | Twilio SMS (optional) |
| `TWILIO_PHONE_NUMBER` | ⬜ | Twilio SMS (optional) |
| `AFRICA_TALKING_USERNAME` | ⬜ | Africa's Talking SMS (optional) |
| `AFRICA_TALKING_API_KEY` | ⬜ | Africa's Talking SMS (optional) |

---

## 🌐 Deployment

### Deploy to Render

1. Push your code to GitHub
2. Connect your repository at [Render.com](https://render.com)
3. Configure the service:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
4. Add all required environment variables
5. Click **Deploy**

### Deploy to Heroku

```bash
heroku create career-intelligence
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set OPENAI_API_KEY=sk-xxxxx
git push heroku main
```

---

## 🤝 Contributing

Contributions are welcome! To get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** — AI capabilities
- **Supabase** — PostgreSQL hosting
- **spaCy** — NLP processing
- **Flask community** — excellent documentation
- All contributors and testers

---

## 📞 Contact & Support

<div align="center">

**FADTECH Labs**
*Building Intelligence That Opens Doors*

📍 Ghana · West Africa
📧 [fadiliddrisu24@gmail.com](mailto:fadiliddrisu24@gmail.com)

> This project is not yet publicly hosted — active development is ongoing to enhance the user experience.

---

### ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!

**Built with ❤️ by FADTECH Labs**

</div>