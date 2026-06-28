# 🧠 FADTECH Labs Career Intelligence System

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![Status](https://img.shields.io/badge/Status-MVP-brightgreen.svg)

> **AI-Powered Employability Intelligence · Labor-Market Analysis · Skill-Gap Engine · Personalized Career Roadmaps**

---

## 📖 Overview

The **Career Intelligence System** is Africa's first deeply localized AI-powered employability platform, built to close the skills gap between education and industry.

---

## 🚀 Features

### ✅ Completed Features

| Feature | Status | Description |
|---------|--------|-------------|
| 📄 **AI CV Parsing** | ✅ Complete | Extract skills from PDF/DOCX with 300+ skill detection |
| 📊 **Skill-Gap Analysis** | ✅ Complete | Compare your skills against real market demands |
| 🎯 **Employability Score** | ✅ Complete | AI-calculated score (0-100) for your target role |
| 🗺️ **Learning Roadmap** | ✅ Complete | Personalized course recommendations from 10+ platforms |
| 💼 **Job Matching** | ✅ Complete | Role-based job recommendations with salary insights |
| 🤖 **AI Career Assistant** | ✅ Complete | Conversational AI for career questions |
| 🏫 **University Dashboard** | ✅ Complete | Analytics for educational institutions |
| 🔐 **OAuth 2.0** | ✅ Complete | Login with Google, LinkedIn, or GitHub |
| 📱 **Mobile Responsive** | ✅ Complete | Works on all devices |
| 🧠 **Brain Logo** | ✅ Complete | Professional branding |

### 🚧 In Progress Features

| Feature | Status | Description |
|---------|--------|-------------|
| 🎨 **AI CV Generator** | 🚧 Planned | Help students without CVs generate one with AI |
| 🏢 **Employer Dashboard** | 🚧 Planned | Help job seekers land jobs based on their skills |
| 🤝 **Partner Companies** | 🚧 Planned | Connect with partner companies for job placements |
| ⚡ **CV Upload Speed** | 🚧 Optimizing | Improving parsing speed for large files |

### 📅 Future Features

- 🌐 LinkedIn Profile Sync
- 📧 Email Notifications
- 📱 Mobile App (iOS/Android)
- 🏛️ Government Workforce Analytics
- 🤝 Mentor Matching
- 🎓 Certification Verification
- 🎨 AI CV Generator

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | HTML5, Tailwind CSS, JavaScript, Font Awesome |
| **Backend** | Flask 3.1.3 (Python) |
| **Database** | SQLite / PostgreSQL |
| **AI/NLP** | spaCy 3.7.2, Sentence Transformers |
| **OAuth** | Authlib (Google, LinkedIn, GitHub) |
| **Course APIs** | Coursera, Udemy, YouTube, edX, W3Schools, Pluralsight, LinkedIn Learning, Skillshare, Khan Academy |
| **Deployment** | Render.com (Free Tier) |
| **Version Control** | Git / GitHub |

---

## 📂 Project Structure

career-intelligence/
├── app/
│ ├── init.py # Flask app factory
│ ├── auth/
│ │ ├── init.py
│ │ └── routes.py # Authentication & OAuth routes
│ ├── templates/
│ │ ├── base.html # Base template with brain logo
│ │ ├── login.html # Login with OAuth
│ │ ├── register.html # Registration with OAuth
│ │ ├── dashboard.html # User dashboard
│ │ ├── upload_cv.html # CV upload with progress bar
│ │ ├── skill_analysis.html # Skill gap analysis
│ │ ├── learning_roadmap.html # Personalized learning roadmap
│ │ ├── job_matches.html # Job recommendations
│ │ ├── career_assistant.html # AI chat assistant
│ │ ├── university_dashboard.html # University analytics
│ │ ├── privacy_policy.html # Privacy policy page
│ │ └── profile.html # User profile
│ └── utils/
│ ├── advanced_cv_parser.py # Advanced NLP parsing (spaCy)
│ ├── hybrid_parser.py # Hybrid CV parser (quick + deep)
│ ├── cv_parser.py # CV parsing interface
│ ├── skill_analyzer.py # Skill gap analysis engine
│ ├── ai_assistant.py # AI career assistant
│ ├── course_api.py # 10+ Course API integration
│ └── oauth.py # OAuth configuration
├── static/
│ └── images/
│ └── logo.svg # Brain logo
├── uploads/ # CV upload directory
├── config.py # Flask configuration
├── extensions.py # Flask extensions (db, login_manager)
├── models.py # Database models
├── requirements.txt # Python dependencies
├── run.py # Application entry point
├── wsgi.py # WSGI for production
├── LICENSE # MIT License
└── README.md # This file


---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.11+
- pip
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/Fadel333/career-intelligence.git
cd career-intelligence