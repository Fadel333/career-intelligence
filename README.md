# 🧠 FADTECH Labs Career Intelligence System

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![Status](https://img.shields.io/badge/Status-MVP-brightgreen.svg)

> **AI-Powered Employability Intelligence · Labor-Market Analysis · Skill-Gap Engine · Personalized Career Roadmaps**

---

## 📖 Overview

The **Career Intelligence System** is Africa's first deeply localized AI-powered employability platform, built to close the skills gap between education and industry.

Across Ghana and West Africa, thousands of graduates enter the job market every year — but what they learned and what employers actually need are two different things. This platform fixes that.

**Key Capabilities:**

- 📄 **AI CV Parsing** - Extract skills from PDF/DOCX with 300+ skill detection
- 📊 **Skill-Gap Analysis** - Compare your skills against real market demands
- 🎯 **Employability Score** - AI-calculated score (0-100) for your target role
- 🗺️ **Learning Roadmap** - Personalized course recommendations from real platforms
- 💼 **Job Matching** - Role-based job recommendations with salary insights
- 🤖 **AI Career Assistant** - Conversational AI for career questions
- 🏫 **University Dashboard** - Analytics for educational institutions (partially done, 73%)
- 🔐 **OAuth 2.0** - Login with Google, LinkedIn, or GitHub
- **AI CV generator: yet to be develop** Help Student with no CV generate one with Moern AI assisant
- **Employers Dashboard** Help job seekers land a legid jobs base on their details in some partners companies(yet to be added)
-

---

## 🎯 Live Demo

**Local Development:**
http://127.0.0.1:10000

text

---

## 🛠️ Technology Stack

| Layer               | Technology                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Frontend**        | HTML5, Tailwind CSS, JavaScript, Font Awesome                                                                       |
| **Backend**         | Flask 3.1.3 (Python)                                                                                                |
| **Database**        | SQLite (development) / PostgreSQL (production)                                                                      |
| **AI/NLP**          | spaCy 3.7.2, Sentence Transformers                                                                                  |
| **OAuth**           | Authlib (Google, LinkedIn, GitHub)                                                                                  |
| **Course APIs**     | Coursera, Udemy, YouTube, W3schools, Pluralsight, LYNDA, Skillshare, Khan Academy, CODEACADEMY, DATACAMP, TREEHOUSE |
| **Deployment**      | Render.com (Free Tier)                                                                                              |
| **Version Control** | Git / GitHub                                                                                                        |

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
│ │ └── profile.html # User profile
│ └── utils/
│ ├── advanced_cv_parser.py # Advanced NLP parsing (spaCy)
│ ├── cv_parser.py # CV parsing interface
│ ├── skill_analyzer.py # Skill gap analysis engine
│ ├── ai_assistant.py # AI career assistant
│ ├── course_api.py # Course API integration
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

text

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.11+**
- **pip** (Python package manager)
- **Git** (optional, for cloning)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Fadel333/career-intelligence.git
cd career-intelligence
```
