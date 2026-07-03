import re
import random
from typing import Dict, List, Any

class CareerAssistant:
    """Advanced AI Career Assistant - ALL SECTORS (Works like ChatGPT for careers)"""
    
    def __init__(self):
        self.context_memory = {}
    
    def get_response(self, question: str, user_skills: List[str] = None, experience: int = 0) -> Dict:
        """Generate intelligent response based on question type"""
        
        question_lower = question.lower()
        
        # Detect sector and intent
        sector = self._detect_sector(question_lower)
        intent = self._detect_intent(question_lower)
        
        # Generate response based on sector + intent
        response = self._generate_response(question_lower, sector, intent, user_skills, experience)
            
        return {
            'response': response,
            'intent': intent,
            'sector': sector,
            'suggested_followups': self._get_suggested_followups(intent, sector)
        }
    
    def _detect_sector(self, question: str) -> str:
        """Detect which sector the question is about"""
        
        sector_keywords = {
            'technology': ['programming', 'software', 'developer', 'coding', 'data science', 'ai', 'ml', 'cloud', 'python', 'java', 'react', 'django', 'flask', 'aws', 'docker', 'kubernetes', 'git', 'linux', 'devops', 'cybersecurity', 'full stack', 'frontend', 'backend', 'api', 'machine learning', 'artificial intelligence', 'tech'],
            'healthcare': ['doctor', 'nurse', 'medical', 'patient', 'hospital', 'pharmacy', 'diagnosis', 'surgery', 'clinical', 'medicine', 'health', 'cardiology', 'pediatrics', 'obstetrics', 'gynecology', 'orthopedics', 'neurology', 'oncology', 'psychiatry', 'patient care', 'public health', 'epidemiology', 'radiology', 'pathology'],
            'law': ['lawyer', 'attorney', 'legal', 'court', 'contract', 'litigation', 'compliance', 'corporate law', 'criminal law', 'family law', 'property law', 'tax law', 'human rights', 'international law', 'legal research', 'advocate', 'barrister', 'solicitor'],
            'finance': ['banking', 'investment', 'accounting', 'finance', 'tax', 'audit', 'financial', 'risk management', 'fintech', 'financial modeling', 'corporate finance', 'portfolio management', 'wealth management', 'cfa', 'acca', 'aicpa', 'accountant', 'auditor', 'financial analyst'],
            'education': ['teacher', 'teaching', 'school', 'curriculum', 'education', 'professor', 'lecturer', 'academic', 'student assessment', 'educational leadership', 'special education', 'edtech', 'classroom management', 'lesson planning'],
            'agriculture': ['agriculture', 'farming', 'crop', 'livestock', 'agribusiness', 'agritech', 'irrigation', 'soil science', 'agronomy', 'animal science', 'fisheries', 'aquaculture', 'food processing', 'farm management', 'agricultural economics'],
            'business': ['management', 'hr', 'marketing', 'sales', 'operations', 'business', 'strategy', 'brand management', 'customer relations', 'digital marketing', 'human resources', 'recruitment', 'talent management', 'employee relations', 'project management'],
            'creative': ['design', 'art', 'animation', 'music', 'content', 'creative', 'graphic design', 'video production', 'photography', 'illustration', 'multimedia', 'motion graphics', 'ui/ux', 'art direction', 'brand identity', 'visual design'],
            'trades': ['carpentry', 'plumbing', 'electrical', 'welding', 'automotive', 'construction', 'masonry', 'mechanic', 'electrician', 'plumber', 'carpenter', 'hvac', 'maintenance', 'repair', 'trades'],
            'social': ['social work', 'community development', 'counseling', 'nonprofit', 'ngo', 'social services', 'advocacy', 'social worker', 'counselor', 'mental health', 'child protection', 'human rights', 'community organizing'],
            'engineering': ['civil engineering', 'structural engineering', 'mechanical engineering', 'electrical engineering', 'construction', 'cad', 'bim', 'site supervision', 'quantity surveying', 'project engineering', 'environmental engineering', 'geotechnical engineering']
        }
        
        question_lower = question.lower()
        sector_scores = {}
        for sector, keywords in sector_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            sector_scores[sector] = score
        
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            if sector_scores[best_sector] > 0:
                return best_sector
        
        return 'general'
    
    def _detect_intent(self, question: str) -> str:
        """Detect the intent of the question"""
        
        intents = {
            'skill_recommendation': ['skill', 'learn', 'study', 'what should i learn', 'which skill', 'upskill', 'what to study', 'recommendation'],
            'interview_prep': ['interview', 'prepare for interview', 'technical interview', 'coding interview', 'interview questions', 'how to prepare'],
            'salary_info': ['salary', 'pay', 'compensation', 'how much', 'earn', 'paid', 'wage', 'income'],
            'career_path': ['career path', 'career growth', 'promotion', 'advance', 'senior', 'lead', 'progression', 'future', 'roadmap'],
            'certification': ['certification', 'certificate', 'certified', 'credential', 'exam', 'qualification', 'cert'],
            'cv_tips': ['cv', 'resume', 'curriculum vitae', 'application', 'cover letter', 'cv tips', 'resume tips'],
            'portfolio': ['portfolio', 'project', 'github', 'showcase', 'demo', 'portfolio tips'],
            'networking': ['network', 'connect', 'linkedin', 'mentor', 'community', 'networking', 'connections'],
            'job_search': ['job search', 'find job', 'apply', 'application', 'hiring', 'job hunting', 'where to find'],
            'remote_work': ['remote', 'work from home', 'wfh', 'distributed', 'virtual', 'remote work'],
            'soft_skills': ['soft skill', 'communication', 'leadership', 'teamwork', 'problem solving', 'emotional intelligence', 'soft skills'],
            'trends': ['trend', 'future', 'emerging', 'latest', 'new technology', 'in demand', 'hot skills'],
            'salary_negotiation': ['negotiate', 'negotiation', 'ask for more', 'counter offer', 'how to negotiate'],
            'work_life_balance': ['balance', 'stress', 'burnout', 'overwork', 'healthy', 'work life'],
            'university': ['university', 'college', 'degree', 'program', 'course', 'study', 'education', 'school'],
            'job_market': ['job market', 'market trends', 'demand', 'opportunities', 'growth sector'],
            'entrepreneurship': ['entrepreneur', 'startup', 'business', 'founder', 'launch', 'own business']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in question for keyword in keywords):
                return intent
                
        return 'general'
    
    def _generate_response(self, question: str, sector: str, intent: str, user_skills: List[str] = None, experience: int = 0) -> str:
        """Generate intelligent response based on sector and intent"""
        
        # Route to sector-specific handlers
        if sector == 'technology':
            return self._handle_tech_question(question, intent, user_skills, experience)
        elif sector == 'healthcare':
            return self._handle_healthcare_question(question, intent, user_skills, experience)
        elif sector == 'law':
            return self._handle_law_question(question, intent, user_skills, experience)
        elif sector == 'finance':
            return self._handle_finance_question(question, intent, user_skills, experience)
        elif sector == 'education':
            return self._handle_education_question(question, intent, user_skills, experience)
        elif sector == 'agriculture':
            return self._handle_agriculture_question(question, intent, user_skills, experience)
        elif sector == 'business':
            return self._handle_business_question(question, intent, user_skills, experience)
        elif sector == 'creative':
            return self._handle_creative_question(question, intent, user_skills, experience)
        elif sector == 'trades':
            return self._handle_trades_question(question, intent, user_skills, experience)
        elif sector == 'social':
            return self._handle_social_question(question, intent, user_skills, experience)
        elif sector == 'engineering':
            return self._handle_engineering_question(question, intent, user_skills, experience)
        else:
            return self._handle_general_question(question, sector, intent, user_skills, experience)
    
    # ============================================================
    # SECTOR-SPECIFIC HANDLERS
    # ============================================================
    
    def _handle_tech_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Handle technology sector questions"""
        
        if intent == 'skill_recommendation':
            return self._handle_tech_skill_recommendation(user_skills, experience)
        elif intent == 'salary_info':
            return self._handle_tech_salary(question, experience)
        elif intent == 'career_path':
            return self._handle_tech_career_path(question, user_skills)
        elif intent == 'interview_prep':
            return self._handle_interview_prep(question)
        elif intent == 'trends':
            return self._handle_tech_trends()
        else:
            return self._handle_tech_general(question, intent, user_skills, experience)
    
    def _handle_tech_skill_recommendation(self, user_skills: List[str], experience: int) -> str:
        """Tech skill recommendations"""
        
        if not user_skills:
            return """💻 **Top Tech Skills for 2026 in Africa:**

🔥 **Most In-Demand:**
1. **Python** - 92% of job postings (GHS 5k-12k/month)
2. **Machine Learning/AI** - 40% growth (GHS 7k-15k/month)
3. **Cloud Computing (AWS/Azure)** - Highest salaries (GHS 8k-18k/month)
4. **Data Science** - 28% growth (GHS 6k-14k/month)
5. **Cybersecurity** - 30% growth (GHS 6k-12k/month)
6. **DevOps** - 25% growth (GHS 7k-15k/month)

📚 **Learning Path:**
1. Start with Python (4-6 weeks)
2. Then choose: Data Science OR Web Development OR Cloud
3. Build projects (2-3 months)
4. Get certified (AWS, Google, Microsoft)

💡 **Quick Start:** 
• Free: Python.org, freeCodeCamp, YouTube
• Paid: Coursera, Udemy, DataCamp

Want a personalized plan? Upload your CV! 🎯"""
        
        skills_set = [s.lower() for s in user_skills]
        recommendations = []
        
        if 'python' in str(skills_set):
            recommendations.append("🔥 **Advanced Python** → Django/FastAPI, Data Science, ML")
            recommendations.append("🧠 **Machine Learning** → Natural next step with Python")
        else:
            recommendations.append("🐍 **Python** → Foundation for all tech roles")
        
        if 'javascript' in str(skills_set):
            recommendations.append("⚛️ **React/Next.js** → Modern frontend development")
        else:
            recommendations.append("🌐 **JavaScript/React** → Essential for web dev")
        
        if any(skill in str(skills_set) for skill in ['cloud', 'aws', 'azure']):
            recommendations.append("☁️ **AWS/Azure** → Advanced cloud architecture")
        else:
            recommendations.append("☁️ **Cloud Computing** → AWS Solutions Architect cert")
        
        recommendations.append("🔒 **Cybersecurity** → Growing demand in fintech")
        recommendations.append("🤝 **Soft Skills** → Communication, Leadership, Problem-solving")
        
        return f"""🎯 **Your Personalized Tech Path:**

Based on your skills ({', '.join(user_skills[:3])}) and {experience}+ years:

{chr(10).join(recommendations)}

📊 **Priority:**
1. {recommendations[0]}
2. {recommendations[1]}
3. {recommendations[2]}

🎯 **Goal:** 40% employability increase in 6 months!

Need a weekly plan? Just ask! 🚀"""
    
    def _handle_tech_salary(self, question: str, experience: int) -> str:
        """Tech salary information"""
        
        roles = {
            'python developer': [4500, 8000],
            'data scientist': [6000, 12000],
            'cloud engineer': [7000, 15000],
            'full stack developer': [5000, 10000],
            'devops engineer': [6500, 14000],
            'ai engineer': [7000, 15000],
            'software engineer': [4500, 9500],
            'frontend developer': [4000, 8500],
            'backend developer': [4500, 9000],
            'security analyst': [5000, 10000]
        }
        
        role = 'Software Engineer'
        for key in roles:
            if key in question.lower():
                role = key.title()
                break
        
        if experience <= 2:
            level = 'Entry'
            multiplier = 0.8
        elif experience <= 5:
            level = 'Mid'
            multiplier = 1.0
        else:
            level = 'Senior'
            multiplier = 1.3
        
        base = roles.get(role.lower(), [4500, 8000])
        min_salary = int(base[0] * multiplier)
        max_salary = int(base[1] * multiplier)
        
        return f"""💰 **{role} Salary in Ghana:**

**{level} Level** ({experience} years experience)
• 💵 Min: GHS {min_salary:,}/month
• 📈 Average: GHS {(min_salary + max_salary)//2:,}/month
• 🚀 Max: GHS {max_salary:,}/month

**What Affects Your Salary:**
✅ Cloud/AI skills add +25-35%
✅ AWS Certification adds +25%
✅ Company type: Big Tech > Startup
✅ Location: Accra has highest rates

**Top Skills That Pay More:**
1. AWS/Azure: +35%
2. Machine Learning: +30%
3. Cybersecurity: +25%
4. DevOps: +25%

💡 **Want to increase your salary?** Ask me about negotiation tips! 💪"""
    
    def _handle_tech_career_path(self, question: str, user_skills: List[str]) -> str:
        """Tech career path guidance"""
        
        return """🚀 **Tech Career Progression:**

**Years 0-2 (Junior):**
• Master fundamentals
• Build portfolio (3-5 projects)
• Get first certification
• 💰 GHS 3k-5k/month

**Years 2-5 (Mid-Level):**
• Specialize (Data/Cloud/Backend)
• Mentor juniors
• Lead small projects
• 💰 GHS 5k-9k/month

**Years 5-8 (Senior):**
• Architecture decisions
• Team leadership
• Strategic planning
• 💰 GHS 9k-13k/month

**Years 8+ (Lead/Principal):**
• Technical strategy
• Cross-team initiatives
• Industry influence
• 💰 GHS 13k-18k+/month

**Fast-Track Tips:**
✅ Get AWS/GCP/Azure certified
✅ Contribute to open source
✅ Build your personal brand
✅ Network actively
✅ Start speaking at events

**Careers with Fastest Growth:**
1. AI/ML Engineer (+45% growth)
2. Cloud Architect (+35%)
3. Cybersecurity (+30%)
4. Data Engineer (+28%)

**Remote Work Opportunities:**
• Global companies hiring remotely
• Higher salaries (USD rates)
• Flexible schedule

What stage are you at? I can give specific advice! 🎯"""
    
    def _handle_tech_general(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """General tech questions"""
        return f"""💻 **Tech Career Questions:**

I can help you with tech-related questions about:
• 📚 **Skills** - What to learn for your tech career
• 💰 **Salaries** - How much tech professionals earn
• 🎯 **Career Path** - How to advance in tech
• 📝 **CV Tips** - How to stand out in tech
• 🏆 **Certifications** - What tech certs to get
• 💼 **Job Search** - Where to find tech jobs
• 🔍 **Interview Prep** - How to prepare for tech interviews

**Your question:** "{question}"

💡 **Tip:** Be specific about your tech stack and experience for better answers! 🚀"""
    
    def _handle_healthcare_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Healthcare sector questions"""
        
        if 'doctor' in question.lower() or 'physician' in question.lower():
            return self._handle_healthcare_doctor(question, experience)
        elif 'nurse' in question.lower():
            return self._handle_healthcare_nurse(question, experience)
        elif 'pharmacy' in question.lower() or 'pharmacist' in question.lower():
            return self._handle_healthcare_pharmacy(question, experience)
        elif intent == 'salary_info':
            return self._handle_healthcare_salary(question, experience)
        else:
            return self._handle_healthcare_general(question, intent, user_skills, experience)
    
    def _handle_healthcare_doctor(self, question: str, experience: int) -> str:
        """Doctor career path"""
        return """👨‍⚕️ **Becoming a Doctor in West Africa:**

**Career Path:**
1. Medical School (6 years) → MBChB/MD
2. Internship (1 year) → Housemanship
3. Residency (3-5 years) → Specialization
4. Consultant → Senior Specialist

**Top Specializations:**
• Surgery (General, Orthopedic, Neuro)
• Internal Medicine (Cardiology, Nephrology)
• Pediatrics, OB/GYN, Emergency Medicine

**Timeline:**
• Medical School: 6 years
• Internship: 1 year
• Residency: 3-5 years
• Total: 10-12 years

**Salaries in Ghana:**
• Intern: GHS 2,500-3,500/month
• Medical Officer: GHS 4,500-7,000/month
• Specialist: GHS 8,000-12,000/month
• Consultant: GHS 12,000-20,000/month

📚 **Medical Schools in Ghana:**
• University of Ghana Medical School
• KNUST School of Medicine
• University of Cape Coast Medical School
• University of Development Studies (Tamale)

💡 **Tip:** Start preparing early - get good grades in science subjects! 🩺"""
    
    def _handle_healthcare_nurse(self, question: str, experience: int) -> str:
        """Nursing career path"""
        return """🩺 **Nursing Career in West Africa:**

**Career Path:**
1. Nursing Diploma/BSc (3-4 years)
2. Registered Nurse License (NCLEX/Ghana Board)
3. RN → Senior Nurse → Nurse Manager → Director

**Specializations:**
• Pediatric Nursing
• Cardiac Nursing
• Critical Care (ICU/CCU)
• Maternity/OB Nursing
• Public Health Nursing
• Mental Health Nursing

**Certifications:**
• BLS (Basic Life Support)
• ACLS (Advanced Cardiac Life Support)
• PALS (Pediatric Advanced Life Support)

**Salaries in Ghana:**
• Entry Level RN: GHS 2,500-3,500/month
• Experienced RN: GHS 4,000-6,000/month
• Nurse Manager: GHS 6,000-9,000/month
• Director of Nursing: GHS 10,000+

**Institutions:**
• University of Ghana (School of Nursing)
• KNUST (Nursing)
• Nursing Training Colleges nationwide

💡 **Pro Tip:** BLS and ACLS certifications increase salary by 20-30%! 🏥"""
    
    def _handle_healthcare_pharmacy(self, question: str, experience: int) -> str:
        """Pharmacy career path"""
        return """💊 **Pharmacy Career in Ghana:**

**Career Path:**
1. Doctor of Pharmacy (PharmD) - 6 years OR
2. BSc Pharmacy - 4 years
3. Internship (1 year)
4. Licensed Pharmacist

**Practice Areas:**
• Community Pharmacy (Retail)
• Hospital Pharmacy
• Clinical Pharmacy
• Pharmaceutical Industry
• Regulatory Affairs
• Academia

**Salaries:**
• Entry Level: GHS 3,000-5,000/month
• Experienced: GHS 5,000-8,000/month
• Hospital Pharmacist: GHS 6,000-9,000/month
• Industry/Corporate: GHS 8,000-15,000/month

**Institutions:**
• KNUST - Pharmacy
• University of Ghana - Pharmacy
• Central University - Pharmacy
• University of Health and Allied Sciences

💡 **Quick Tip:** Industrial pharmacy pays the highest! 💰"""
    
    def _handle_healthcare_salary(self, question: str, experience: int) -> str:
        """Healthcare salary information"""
        return """💰 **Healthcare Salaries in Ghana:**

**Average Monthly Salaries (GHS):**
• 🩺 Medical Doctor: 5,000-20,000
• 💉 Registered Nurse: 3,000-9,000
• 💊 Pharmacist: 3,000-15,000
• 🔬 Lab Scientist: 2,500-6,000
• 🏥 Public Health: 3,500-7,000
• 🧠 Mental Health Counselor: 3,000-6,000

**Factors Affecting Salary:**
✅ Specialization increases pay significantly
✅ Private hospitals pay more than public
✅ Location: Accra > Kumasi > Other cities
✅ Years of experience (2-5% increase/year)
✅ Additional certifications (BLS, ACLS)

**Top-Paying Specializations:**
1. Surgery: GHS 12,000-20,000
2. Anesthesiology: GHS 10,000-18,000
3. Cardiology: GHS 10,000-16,000
4. Radiology: GHS 9,000-15,000
5. Obstetrics/Gynecology: GHS 8,000-14,000

💡 **Pro Tip:** Private sector and international organizations pay the highest! 🌍"""
    
    def _handle_healthcare_general(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """General healthcare questions"""
        return """🏥 **Healthcare Careers in West Africa:**

**Most In-Demand Healthcare Jobs:**
1. 🩺 Medical Doctors (Specialists especially)
2. 💉 Registered Nurses
3. 💊 Pharmacists
4. 🔬 Medical Laboratory Scientists
5. 🏥 Public Health Specialists
6. 🧠 Mental Health Counselors
7. 👴 Elderly Care Specialists

**Fastest Growing Areas:**
• Telemedicine (+45% growth)
• Health Informatics (+35%)
• Public Health/Epidemiology (+30%)
• Mental Health (+25%)

**Top Employers:**
• Government Hospitals (GHS)
• Private Hospitals
• NGOs (WHO, UNICEF, MSF)
• Pharmaceutical Companies
• Research Institutions

❓ **Ask me about any specific healthcare role!** 🏥"""
    
    def _handle_law_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Law sector questions"""
        
        if 'career path' in question.lower() or 'become' in question.lower():
            return """⚖️ **Law Career in West Africa:**

**Career Path:**
1. Bachelor of Laws (LLB) - 4 years
2. Ghana School of Law (2 years professional)
3. Call to Bar (pass bar exam)
4. Pupillage (1 year)
5. → Solicitor/Barrister → Senior Partner → Judge

**Practice Areas:**
• Corporate/Commercial Law
• Criminal Law
• Human Rights Law
• Family Law
• Property Law
• Tax Law
• Maritime Law
• Intellectual Property

**Institutions:**
• University of Ghana - Faculty of Law
• KNUST - Faculty of Law
• University of Cape Coast - Faculty of Law
• Ghana School of Law (Professional)

**Salaries in Ghana:**
• Pupil: GHS 2,000-3,000/month
• Junior Associate: GHS 4,000-6,000/month
• Associate: GHS 7,000-10,000/month
• Senior Associate/Partner: GHS 12,000-20,000+
• Judge: GHS 15,000-25,000

💡 **Pro Tip:** Specializing in Corporate or Intellectual Property law pays the highest! ⚖️"""
        
        return """⚖️ **Legal Careers in West Africa:**

**Most In-Demand Legal Roles:**
1. ⚖️ Corporate Lawyers
2. 📜 Contract Specialists
3. 🔒 Compliance Officers
4. 🏢 Legal Consultants
5. ⚖️ Human Rights Lawyers
6. 📝 Legal Researchers
7. 🏛️ Litigators

**Top Law Firms in Ghana:**
• Bentsi-Enchill, Letsa & Ankomah
• Sam Okudzeto & Associates
• Akufo-Addo, Prempeh & Co.
• AB & David Law Firm
• Alisa Law Firm

**Average Salaries (GHS/month):**
• Entry Level: 3,000-5,000
• Mid Level: 6,000-10,000
• Senior Level: 12,000-20,000

💡 **Tip:** The LLB is just the beginning - professional development is continuous! ⚖️"""
    
    def _handle_finance_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Finance sector questions"""
        
        if 'career path' in question.lower() or 'become' in question.lower():
            return """💰 **Finance Career in West Africa:**

**Career Paths:**

1. **Banking:**
   • Customer Service → Relationship Manager → Branch Manager
   • Corporate Banking → Investment Banking → Private Banking

2. **Accounting:**
   • Junior Accountant → Finance Manager → CFO
   • Auditor → Audit Manager → Audit Partner

3. **Investment:**
   • Analyst → Associate → Vice President → Managing Director

**Key Certifications:**
• ACCA (Ghanaian Employers love this!)
• CPA
• ICAEW
• CIMA
• CFA

**Certifications Costs:**
• ACCA: GHS 8,000-15,000 total
• CIMA: GHS 10,000-20,000
• CFA: GHS 15,000-25,000

**Salaries in Ghana:**
• Junior Accountant: GHS 3,000-5,000/month
• Finance Manager: GHS 8,000-15,000/month
• Investment Analyst: GHS 6,000-12,000/month
• CFO: GHS 20,000-40,000/month

💡 **Quick Tip:** ACCA is the most recognized qualification in Ghana! 💰"""
        
        return """💰 **Finance Careers in West Africa:**

**Most In-Demand Roles:**
1. 💰 Investment Bankers
2. 📊 Financial Analysts
3. 🧾 Accountants
4. 🏦 Banking Professionals
5. 📈 Risk Managers
6. 💳 Fintech Specialists
7. 📉 Portfolio Managers

**Top Employers:**
• GCB Bank, Stanbic, Standard Chartered
• PwC, KPMG, Deloitte, EY
• CFA Society Ghana
• SEC Ghana, Bank of Ghana
• Fintech Companies (Mobile Money)

**Average Salaries (GHS/month):**
• Entry Level: 3,000-5,000
• Mid Level: 6,000-12,000
• Senior Level: 15,000-40,000

💡 **Tip:** Fintech is the fastest growing area! 💳"""
    
    def _handle_education_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Education sector questions"""
        
        return """📚 **Education Career in West Africa:**

**Career Paths:**
1. Classroom Teacher → Senior Teacher → Head of Department
2. School Administrator → Dean → Principal
3. University Professor → Department Head → Dean/VC

**Teaching Levels:**
• Early Childhood Education (Nursery/Primary)
• Basic Education (JHS)
• Secondary Education (SHS)
• Tertiary Education (University/Polytechnic)

**Teacher Licensure (GES):**
• GES Licensure Exam
• Teacher Professional Development (TPD) credits
• Continuing education required

**Salaries in Ghana (GES):**
• Graduate Teacher: GHS 3,500-4,500/month
• Senior Teacher: GHS 5,000-7,000/month
• Principal Superintendent: GHS 7,000-10,000/month
• University Lecturer: GHS 6,000-15,000/month
• Headmaster/Principal: GHS 10,000-18,000/month

**Institutions:**
• University of Education, Winneba (UEW)
• University of Ghana - Education
• KNUST - Education
• College of Education nationwide

💡 **Pro Tip:** EdTech is growing fast - combine teaching with technology! 📱"""
    
    def _handle_agriculture_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Agriculture sector questions"""
        
        return """🌾 **Agriculture Career in West Africa:**

**Career Paths:**

1. **Crop Production:**
   • Farmer → Large-Scale Farmer → Agro-industrial Owner

2. **Agribusiness:**
   • Agricultural Economist → Agribusiness Manager → Director

3. **Agricultural Extension:**
   • Extension Officer → District Agric Officer → Regional Director

4. **AgriTech:**
   • AgriTech Specialist → Product Manager → Co-Founder

**Specializations:**
• Crop Science (Maize/Cocoa/Rice/Cassava)
• Livestock Management (Poultry/Cattle/Sheep)
• Fisheries & Aquaculture
• Soil Science & Irrigation
• Agricultural Economics
• Food Processing & Storage

**Institutions in Ghana:**
• UCC - Bachelor of Agriculture
• KNUST - BSc Agricultural Science
• University of Ghana - BSc Agriculture

**Salaries in Ghana:**
• Extension Officer: GHS 3,500-5,000/month
• Agronomist: GHS 4,500-8,000/month
• Agricultural Economist: GHS 5,000-10,000/month
• AgriTech Manager: GHS 8,000-15,000/month

💡 **Hot Trend:** AgriTech is booming - combine agriculture with technology! 🌱"""
    
    def _handle_business_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Business sector questions"""
        
        return """🏢 **Business Career in West Africa:**

**Popular Career Paths:**

1. **Management:**
   • Trainee → Supervisor → Manager → Director

2. **Human Resources:**
   • HR Officer → HR Manager → HR Director

3. **Marketing:**
   • Marketing Executive → Marketing Manager → Brand Director

4. **Operations:**
   • Operations Officer → Operations Manager → COO

5. **Consulting:**
   • Junior Consultant → Consultant → Senior Manager → Partner

**Key Certifications:**
• Project Management Professional (PMP)
• Certified Business Professional (CBP)
• Six Sigma (Yellow/Green/Black Belt)

**MBA Programs in Ghana:**
• University of Ghana Business School
• KNUST School of Business
• GIMPA Business School
• UCC School of Business

**Salaries in Ghana:**
• Entry Level: GHS 2,500-4,000/month
• Manager: GHS 5,000-10,000/month
• Senior Manager/Director: GHS 10,000-20,000/month
• Consultant: GHS 8,000-15,000/month
• CEO/MD: GHS 20,000-50,000/month

💡 **Tip:** Digital Marketing and Data Analytics are the hottest skills now! 📊"""
    
    def _handle_creative_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Creative arts sector questions"""
        
        return """🎨 **Creative Arts Career in West Africa:**

**Career Paths:**

1. **Graphic Design:**
   • Designer → Senior Designer → Art Director → Creative Director

2. **Animation & Motion Graphics:**
   • Animator → Senior Animator → Animation Director

3. **Video Production:**
   • Videographer → Video Editor → Production Manager → Director

4. **Music Production:**
   • Music Producer → Senior Producer → Record Label Owner

5. **Content Creation:**
   • Content Creator → Influencer → Brand Partner

**Institutions in Ghana:**
• KNUST - Bachelor of Fine Arts
• UCC - Art Education
• UEW - Visual Arts
• Ghanatta College of Art

**Essential Tools:**
• Adobe Creative Suite (Photoshop, Illustrator, Premiere)
• After Effects (Animation)
• Final Cut Pro (Video Editing)
• Blender (3D Animation)
• Figma (UI/UX Design)

**Salaries in Ghana:**
• Entry Level Designer: GHS 2,000-3,500/month
• Senior Designer: GHS 4,000-7,000/month
• Art Director: GHS 6,000-10,000/month
• Creative Director: GHS 10,000-20,000/month
• Music Producer: GHS 5,000-15,000/month
• Influencer: Varies widely

💡 **Pro Tip:** Build a strong portfolio - it's your most important asset! 🎨"""
    
    def _handle_trades_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Trades sector questions"""
        
        return """🛠️ **Trades Career in West Africa:**

**Career Paths:**

1. **Carpentry:**
   • Apprentice → Journeyman → Master Carpenter → Contractor

2. **Plumbing:**
   • Apprentice → Journeyman → Master Plumber → Plumbing Contractor

3. **Electrical Work:**
   • Apprentice → Journeyman → Electrician → Electrical Contractor

4. **Welding:**
   • Apprentice → Welder → Master Welder → Workshop Owner

5. **Automotive:**
   • Apprentice → Technician → Master Technician → Workshop Owner

**Certifications:**
• City & Guilds Certification
• NVTI Apprenticeship Program
• Ghana National Apprenticeship Program
• Sector Skills Council Certification

**Institutions:**
• NVTI (Nationwide)
• Technical Universities (Kumasi, Tema, Accra)
• Private Technical Institutes

**Salaries in Ghana:**
• Apprentice: GHS 500-1,000/month
• Journeyman: GHS 1,500-2,500/month
• Master Craftsman: GHS 3,000-5,000/month
• Contractor/Owner: GHS 5,000-15,000/month

💡 **Pro Tip:** Start your own business - tradespeople are always in demand! 🔧"""
    
    def _handle_social_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Social services sector questions"""
        
        return """🏛️ **Social Services Career in West Africa:**

**Career Paths:**

1. **Social Work:**
   • Social Worker → Senior Social Worker → Social Services Director

2. **Counseling:**
   • Counselor → Senior Counselor → Clinical Supervisor

3. **Community Development:**
   • Community Officer → Community Manager → Program Director

4. **NGO/Non-Profit:**
   • Program Officer → Program Manager → Country Director

**Specializations:**
• Mental Health Counseling
• Child & Family Services
• Community Health
• International Development
• Human Rights Advocacy

**Institutions in Ghana:**
• University of Ghana - Social Work
• KNUST - Sociology & Social Work
• UCC - Social Sciences
• GIMPA - Development Studies

**Salaries in Ghana:**
• Entry Level Social Worker: GHS 2,500-3,500/month
• Experienced Social Worker: GHS 4,000-6,000/month
• Program Manager: GHS 6,000-10,000/month
• Country Director: GHS 15,000-25,000/month

💡 **Tip:** NGOs and International Organizations pay the highest! 🤝"""
    
    def _handle_engineering_question(self, question: str, intent: str, user_skills: List[str], experience: int) -> str:
        """Engineering sector questions"""
        
        return """🏗️ **Engineering Career in West Africa:**

**Major Engineering Fields:**

1. **Civil Engineering:**
   • Structural Design, Construction, Transportation, Water Resources

2. **Mechanical Engineering:**
   • Manufacturing, Automotive, Energy, HVAC Systems

3. **Electrical Engineering:**
   • Power Systems, Electronics, Telecommunications, Renewable Energy

4. **Chemical Engineering:**
   • Process Engineering, Oil & Gas, Pharmaceuticals, Materials Science

**Professional Registration in Ghana:**
• Graduate Engineer (GEng) - after graduation
• Professional Engineer (PEng) - after 4+ years experience
• Registered through EIB (Engineering Institution of Ghana)

**Institutions in Ghana:**
• KNUST - Engineering (All Branches)
• University of Ghana - Engineering
• UCC - Engineering
• Accra Technical University - Engineering

**Salaries in Ghana:**
• Graduate Engineer: GHS 3,500-5,000/month
• Engineer: GHS 5,000-8,000/month
• Senior Engineer: GHS 8,000-12,000/month
• Project Manager: GHS 12,000-18,000/month
• Consultant Engineer: GHS 15,000-25,000/month

💡 **Pro Tip:** Get your PEng - it significantly boosts your salary! 📐"""
    
    def _handle_tech_trends(self) -> str:
        """Technology trends"""
        
        return """📊 **Top Tech Trends in Africa (2026):**

**Hottest Skills:**
1. 🤖 Artificial Intelligence/Machine Learning (+45% growth)
2. ☁️ Cloud Computing (+35% growth)
3. 🔒 Cybersecurity (+30% growth)
4. 📊 Data Science (+28% growth)
5. 🔗 Blockchain/Web3 (+25% growth)

**Emerging Roles:**
• AI/ML Engineer (GHS 8k-15k)
• Cloud Architect (GHS 10k-18k)
• Security Analyst (GHS 6k-12k)
• Data Engineer (GHS 7k-14k)

**Industries Growing Fast:**
💳 Fintech (Mobile money, payments)
🏥 HealthTech (Telemedicine, records)
📚 EdTech (Online learning)
🛒 E-commerce (Logistics, payments)
🌾 AgriTech (Farmer solutions)

**Future Predictions:**
• Remote work becomes standard
• AI tools boost productivity
• Green tech emerges
• Cross-border collaboration grows

Which trend excites you most? 🚀"""
    
    def _handle_interview_prep(self, question: str) -> str:
        """Interview preparation"""
        
        if 'technical' in question or 'coding' in question:
            return """💻 **Technical Interview Prep:**

📚 **Study Plan:**
• **Week 1-2:** Data Structures & Algorithms
• **Week 3:** System Design basics
• **Week 4:** Practice on LeetCode (Easy/Medium)

🎯 **Key Topics:**
• Big O Notation
• Recursion & Dynamic Programming
• Trees & Graphs
• Sorting & Searching

📝 **Practice Resources:**
• LeetCode (100+ problems)
• HackerRank
• AlgoExpert

💡 **Pro Tip:** Explain your thought process out loud!"""
        
        return """🎤 **Interview Preparation Guide:**

**Before Interview:**
✅ Research company and role thoroughly
✅ Review CV - prepare STAR stories
✅ Practice common behavioral questions
✅ Prepare 5-7 questions to ask

**Technical Prep:**
✅ Review core concepts
✅ Practice coding challenges (30 mins daily)
✅ Build a small demo project

**Day of Interview:**
✅ Test tech setup (camera, mic, internet)
✅ Dress professionally
✅ Have water and notes ready
✅ Arrive 5 minutes early

**Sample Questions:**
• "Tell me about yourself" (2-min version)
• "Why do you want this role?"
• "Describe a challenge you overcame"
• "Where do you see yourself in 5 years?"""
    
    def _handle_general_question(self, question: str, sector: str, intent: str, user_skills: List[str], experience: int) -> str:
        """General question handler"""
        
        sector_names = {
            'technology': 'Tech',
            'healthcare': 'Healthcare',
            'law': 'Law',
            'finance': 'Finance',
            'education': 'Education',
            'agriculture': 'Agriculture',
            'business': 'Business',
            'creative': 'Creative Arts',
            'trades': 'Trades',
            'social': 'Social Services',
            'engineering': 'Engineering'
        }
        
        if sector in sector_names:
            return f"""🤖 **Let me help you with {sector_names[sector]}!**

I can answer questions about:
• 📚 **Skills** - What to learn for your career
• 💰 **Salaries** - How much you can earn
• 🎯 **Career Path** - How to advance
• 📝 **CV Tips** - How to stand out
• 🏆 **Certifications** - What to get
• 💼 **Job Search** - Where to find opportunities

**Your question:** "{question}"

💡 **Tip:** Be specific about your sector, experience, and goals for better answers!

What would you like to know? 🤔"""
        
        return f"""🤖 **I'm your AI Career Assistant!**

I can help with:
• 📚 **Skills** - "What should I learn for [role]?"
• 💰 **Salaries** - "How much do [role] earn in Ghana?"
• 🎯 **Career Path** - "How to become a [role]?"
• 📝 **CV Tips** - "How to improve my CV?"
• 🏆 **Certifications** - "Which certs are valuable?"
• 💼 **Job Search** - "Where to find jobs?"
• 🤝 **Networking** - "How to build connections?"
• 🌍 **Remote Work** - "Tips for working remote?"
• ⚖️ **Work-Life Balance** - "How to avoid burnout?"

**Your question:** "{question}"

💡 **Pro Tip:** Tell me your sector and experience for personalized advice!

What would you like to know? 🚀"""
    
    def _get_suggested_followups(self, intent: str, sector: str) -> List[str]:
        """Get suggested follow-up questions based on intent and sector"""
        
        followups = {
            'skill_recommendation': [
                "How long will it take to learn?",
                "What's the best way to practice?",
                "Can you create a weekly plan?",
                "What certifications should I get?"
            ],
            'interview_prep': [
                "Give me sample interview questions",
                "How to answer 'Tell me about yourself'?",
                "What questions should I ask the interviewer?",
                "How to handle technical interviews?"
            ],
            'salary_info': [
                "How can I negotiate a higher salary?",
                "What benefits should I ask for?",
                "Salary comparison between Accra and other cities?",
                "What skills increase salary most?"
            ],
            'career_path': [
                "How long to reach senior level?",
                "What's the fastest way to advance?",
                "Should I get a master's degree?",
                "How to transition to this career?"
            ],
            'certification': [
                "Which cert is best for beginners?",
                "How to prepare for the exam?",
                "Are free certifications worth it?",
                "What's the ROI of certification?"
            ],
            'general': [
                "What skills are in demand now?",
                "How to find a mentor?",
                "Tips for remote work?",
                "How to build a portfolio?"
            ]
        }
        
        sector_followups = {
            'technology': [
                "What programming language should I learn first?",
                "How to get a remote tech job?",
                "Is a coding bootcamp worth it?"
            ],
            'healthcare': [
                "How to become a specialist doctor?",
                "What are the best nursing schools?",
                "How to get into public health?"
            ],
            'law': [
                "How to become a corporate lawyer?",
                "What's the bar exam like?",
                "How to get a pupillage?"
            ],
            'finance': [
                "Is ACCA better than CPA?",
                "How to get into investment banking?",
                "How to become a CFO?"
            ],
            'education': [
                "How to become a university lecturer?",
                "What's the GES licensure exam?",
                "How to advance in education?"
            ],
            'agriculture': [
                "How to start a farm business?",
                "What's AgriTech all about?",
                "How to get agricultural loans?"
            ],
            'business': [
                "Should I get an MBA?",
                "How to start a consulting career?",
                "What's the best business certification?"
            ],
            'creative': [
                "How to build a design portfolio?",
                "How to get freelance clients?",
                "What design tools to learn?"
            ],
            'trades': [
                "How to start a trades business?",
                "What certifications are needed?",
                "How to get apprenticeships?"
            ],
            'social': [
                "How to work for NGOs?",
                "What's the best social work specialization?",
                "How to get funding for community projects?"
            ],
            'engineering': [
                "What engineering field is most in demand?",
                "How to get PEng certification?",
                "How to transition to construction management?"
            ]
        }
        
        result = followups.get(intent, followups['general'])
        if sector in sector_followups:
            result = result + sector_followups[sector]
        
        return result[:5]