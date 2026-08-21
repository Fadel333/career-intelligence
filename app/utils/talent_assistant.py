# app/utils/talent_assistant.py

import os
import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# ✅ NEW: Use the new google.genai SDK
try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️ Google GenAI not installed. Run: pip install google-genai")

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-3.6-flash"


class TalentAssistant:
    """
    Advanced AI Career Assistant with Gemini Integration
    Covers 25+ sectors with intelligent, context-aware responses
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize TalentAssistant with Gemini API (FREE tier)"""
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.gemini_enabled = False
        self.gemini_client = None
        self.context_memory = {}
        
        # ✅ NEW: Initialize Gemini with the new SDK
        if self.api_key and GENAI_AVAILABLE:
            try:
                self.gemini_client = genai.Client(api_key=self.api_key)
                
                # Test the connection with a quick request
                test_response = self.gemini_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents="test"
                )
                
                self.gemini_enabled = True
                print("✅ Gemini API initialized successfully! (FREE tier)")
                print("📊 Daily limit: 1,500 requests | Rate: 60/min")
                
            except Exception as e:
                self.gemini_enabled = False
                print(f"⚠️ Gemini initialization failed: {e}")
                print("🔄 Falling back to rule-based responses")
        else:
            if not GENAI_AVAILABLE:
                print("⚠️ Please install: pip install google-genai")
            if not self.api_key:
                print("⚠️ No API key provided - using rule-based responses")
                print("💡 Get free API key: https://makersuite.google.com/app/apikey")
    
    # ============================================================
    # MAIN RESPONSE METHOD
    # ============================================================
    
    def get_response(self, question: str, user_skills: List[str] = None, 
                    experience: int = 0, education: str = None) -> Dict:
        """
        Generate intelligent response - ALWAYS returns a response!
        Priority: Gemini (if available) → Rule-based (fallback)
        """
        
        question_lower = question.lower()
        
        # Detect sector and intent
        sector = self._detect_sector(question_lower)
        intent = self._detect_intent(question_lower)
        
        # Build user context
        user_context = {
            'skills': user_skills or [],
            'experience': experience,
            'education': education or 'Not specified'
        }
        
        # === TRY GEMINI FIRST (FREE TIER) ===
        if self.gemini_enabled and self.gemini_client:
            gemini_response = self._get_gemini_response(
                question, sector, intent, user_context
            )
            
            if gemini_response:
                return {
                    'response': gemini_response,
                    'intent': intent,
                    'sector': sector,
                    'suggested_followups': self._get_suggested_followups(intent, sector),
                    'source': 'gemini'
                }
        
        # === FALLBACK: Rule-based responses (GUARANTEED) ===
        response = self._generate_rule_response(
            question_lower, sector, intent, user_context
        )
        
        return {
            'response': response,
            'intent': intent,
            'sector': sector,
            'suggested_followups': self._get_suggested_followups(intent, sector),
            'source': 'rule_based'
        }
    
    # ============================================================
    # GEMINI INTEGRATION - UPDATED FOR NEW SDK
    # ============================================================
    
    def _get_gemini_response(self, question: str, sector: str, intent: str, 
                             user_context: Dict) -> Optional[str]:
        """Get response from Gemini API - returns None if fails"""
        try:
            # Build comprehensive prompt with context
            prompt = f"""You are TalentAssistant, an expert career advisor for the African/Ghanaian job market.

CONTEXT:
- Sector: {sector}
- Intent: {intent}
- Experience: {user_context.get('experience', 0)} years
- Skills: {', '.join(user_context.get('skills', [])) or 'Not specified'}
- Education: {user_context.get('education', 'Not specified')}

USER QUESTION: {question}

INSTRUCTIONS:
1. Provide practical, specific advice for the African/Ghanaian job market
2. Include salary ranges in GHS (Ghana Cedis) when relevant
3. Mention local institutions, certifications, and companies
4. Give actionable steps the user can take
5. Be encouraging and motivational
6. If you don't know something, say so and offer general guidance
7. Use emojis for readability but keep it professional
8. Format with clear sections and bullet points

YOUR RESPONSE:"""
            
            # ✅ NEW: Use the new SDK to generate content
            response = self.gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            
            if response and response.text:
                return response.text
            return None
            
        except Exception as e:
            logger.error(f"⚠️ Gemini API error: {e}")
            return None
    
    # ============================================================
    # SECTOR DETECTION - 25 SECTORS
    # ============================================================
    
    def _detect_sector(self, question: str) -> str:
        """Detect which sector the question is about - 25 sectors"""
        
        sector_keywords = {
            # Technology & Digital
            'technology': ['programming', 'software', 'developer', 'coding', 'data science', 'ai', 'ml', 'cloud', 'python', 'java', 'react', 'django', 'flask', 'aws', 'docker', 'kubernetes', 'git', 'linux', 'devops', 'cybersecurity', 'full stack', 'frontend', 'backend', 'api', 'machine learning', 'artificial intelligence', 'tech', 'it', 'information technology', 'web development', 'mobile app', 'software engineer'],
            
            'data_science': ['data scientist', 'data analyst', 'data engineer', 'big data', 'analytics', 'statistics', 'data visualization', 'power bi', 'tableau', 'sql', 'data mining', 'predictive modeling'],
            
            'cybersecurity': ['cyber', 'security', 'ethical hacking', 'penetration testing', 'information security', 'network security', 'security analyst', 'risk assessment', 'compliance', 'iso 27001'],
            
            'fintech': ['fintech', 'mobile money', 'digital payments', 'blockchain', 'cryptocurrency', 'financial technology', 'payment systems', 'mobile banking', 'microfinance technology'],
            
            # Healthcare
            'healthcare': ['doctor', 'nurse', 'medical', 'patient', 'hospital', 'pharmacy', 'diagnosis', 'surgery', 'clinical', 'medicine', 'health', 'cardiology', 'pediatrics', 'obstetrics', 'gynecology', 'orthopedics', 'neurology', 'oncology', 'psychiatry', 'patient care', 'public health', 'epidemiology', 'radiology', 'pathology', 'healthcare'],
            
            'mental_health': ['psychologist', 'psychiatrist', 'counselor', 'therapy', 'mental health', 'wellness', 'trauma', 'ptsd', 'anxiety', 'depression', 'mental wellness', 'clinical psychology', 'behavioral health'],
            
            'pharmacy': ['pharmacist', 'pharmacy', 'pharmaceutical', 'drug', 'medicine', 'clinical pharmacy', 'community pharmacy', 'hospital pharmacy', 'pharmaceutical industry'],
            
            'nursing': ['nurse', 'nursing', 'rn', 'registered nurse', 'patient care', 'critical care', 'icu nurse', 'pediatric nurse', 'maternity nurse'],
            
            'public_health': ['public health', 'community health', 'health promotion', 'disease prevention', 'epidemiology', 'health education', 'global health', 'health policy'],
            
            # Legal
            'law': ['lawyer', 'attorney', 'legal', 'court', 'contract', 'litigation', 'compliance', 'corporate law', 'criminal law', 'family law', 'property law', 'tax law', 'human rights', 'international law', 'legal research', 'advocate', 'barrister', 'solicitor'],
            
            'corporate_law': ['corporate lawyer', 'company law', 'mergers', 'acquisitions', 'securities', 'commercial law', 'business law', 'contract law'],
            
            'human_rights': ['human rights', 'advocacy', 'ngo law', 'international law', 'legal aid', 'social justice', 'civil rights', 'constitutional law'],
            
            # Finance & Business
            'finance': ['banking', 'investment', 'accounting', 'finance', 'tax', 'audit', 'financial', 'risk management', 'financial modeling', 'corporate finance', 'portfolio management', 'wealth management', 'cfa', 'acca', 'aicpa', 'accountant', 'auditor', 'financial analyst'],
            
            'investment_banking': ['investment banking', 'investment banker', 'capital markets', 'mergers and acquisitions', 'corporate finance', 'ipo', 'private equity', 'venture capital'],
            
            'accounting': ['accountant', 'accounting', 'audit', 'tax', 'bookkeeping', 'financial reporting', 'cpa', 'acca', 'cima', 'chartered accountant', 'accounts'],
            
            'business': ['management', 'hr', 'marketing', 'sales', 'operations', 'business', 'strategy', 'brand management', 'customer relations', 'digital marketing', 'human resources', 'recruitment', 'talent management', 'employee relations', 'project management', 'business analyst', 'consulting'],
            
            'marketing': ['marketing', 'digital marketing', 'seo', 'social media', 'content marketing', 'brand management', 'advertising', 'pr', 'public relations', 'market research', 'campaign management'],
            
            'hr': ['hr', 'human resources', 'recruitment', 'talent acquisition', 'employee relations', 'hr management', 'people management', 'organizational development', 'payroll', 'compensation', 'benefits'],
            
            'entrepreneurship': ['entrepreneur', 'startup', 'business owner', 'founder', 'launch', 'small business', 'scale up', 'business growth', 'venture', 'bootstrapping'],
            
            # Education
            'education': ['teacher', 'teaching', 'school', 'curriculum', 'education', 'professor', 'lecturer', 'academic', 'student assessment', 'educational leadership', 'special education', 'edtech', 'classroom management', 'lesson planning', 'education consultant', 'principal', 'headmaster'],
            
            'edtech': ['edtech', 'education technology', 'online learning', 'e-learning', 'learning management system', 'educational app', 'digital education', 'virtual classroom'],
            
            # Agriculture
            'agriculture': ['agriculture', 'farming', 'crop', 'livestock', 'agribusiness', 'agritech', 'irrigation', 'soil science', 'agronomy', 'animal science', 'fisheries', 'aquaculture', 'food processing', 'farm management', 'agricultural economics', 'farmer', 'cocoa', 'maize', 'rice', 'cassava', 'poultry', 'cattle'],
            
            'agritech': ['agritech', 'agtech', 'precision farming', 'drones', 'agricultural technology', 'smart farming', 'digital agriculture', 'farm automation'],
            
            # Creative Arts
            'creative': ['design', 'art', 'animation', 'music', 'content', 'creative', 'graphic design', 'video production', 'photography', 'illustration', 'multimedia', 'motion graphics', 'ui/ux', 'art direction', 'brand identity', 'visual design', 'creative director', 'digital artist'],
            
            'music': ['music', 'musician', 'producer', 'audio', 'recording', 'sound design', 'music production', 'artist', 'singer', 'performer', 'record label', 'music business'],
            
            'filmmaking': ['film', 'movie', 'cinema', 'director', 'producer', 'screenwriter', 'actor', 'acting', 'film production', 'cinematography', 'editing', 'video production'],
            
            # Trades & Technical
            'trades': ['carpentry', 'plumbing', 'electrical', 'welding', 'automotive', 'construction', 'masonry', 'mechanic', 'electrician', 'plumber', 'carpenter', 'hvac', 'maintenance', 'repair', 'trades', 'technician'],
            
            'construction': ['construction', 'building', 'civil', 'structural', 'site supervisor', 'project manager', 'quantity surveyor', 'architect', 'building inspector', 'construction manager'],
            
            # Engineering
            'engineering': ['civil engineering', 'structural engineering', 'mechanical engineering', 'electrical engineering', 'construction', 'cad', 'bim', 'site supervision', 'quantity surveying', 'project engineering', 'environmental engineering', 'geotechnical engineering', 'engineer', 'engineering'],
            
            'software_engineering': ['software engineer', 'software development', 'software engineering', 'application development', 'systems engineering', 'software architect'],
            
            # Social Services
            'social_work': ['social work', 'community development', 'counseling', 'nonprofit', 'ngo', 'social services', 'advocacy', 'social worker', 'counselor', 'mental health', 'child protection', 'human rights', 'community organizing'],
            
            'nonprofit': ['nonprofit', 'ngo', 'charity', 'development', 'humanitarian', 'international development', 'project management', 'fundraising', 'grant writing', 'program officer'],
            
            # Hospitality & Tourism
            'hospitality': ['hotel', 'restaurant', 'hospitality', 'tourism', 'travel', 'event planning', 'catering', 'guest service', 'tourism management', 'travel agency', 'lodging', 'food service'],
            
            'tourism': ['tourism', 'travel', 'tour guide', 'travel agent', 'tour operator', 'travel management', 'ecotourism', 'cultural tourism', 'destination management'],
            
            # Real Estate
            'real_estate': ['real estate', 'property', 'estate agent', 'appraisal', 'property management', 'construction', 'development', 'realtor', 'land acquisition', 'property valuation'],
            
            # Transportation & Logistics
            'logistics': ['logistics', 'supply chain', 'transport', 'shipping', 'warehouse', 'distribution', 'freight', 'procurement', 'inventory management', 'operations', 'fleet management'],
            
            # Media & Journalism
            'media': ['journalism', 'media', 'news', 'reporter', 'editor', 'broadcast', 'radio', 'television', 'journalist', 'content creator', 'news anchor', 'media production', 'journalism'],
            
            # Sports
            'sports': ['sports', 'coach', 'athlete', 'fitness', 'gym', 'training', 'sports management', 'physical education', 'sports science', 'football', 'basketball', 'soccer', 'athletics', 'physical therapist', 'sports coach'],
            
            # Environmental
            'environmental': ['environmental', 'sustainability', 'climate', 'conservation', 'renewable energy', 'environmental science', 'ecology', 'green energy', 'sustainable development', 'climate change', 'environmental management']
        }
        
        question_lower = question.lower()
        sector_scores = {}
        
        for sector, keywords in sector_keywords.items():
            score = sum(1 for keyword in keywords if keyword in question_lower)
            if score > 0:
                sector_scores[sector] = score
        
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            if sector_scores[best_sector] > 0:
                return best_sector
        
        return 'general'
    
    # ============================================================
    # INTENT DETECTION
    # ============================================================
    
    def _detect_intent(self, question: str) -> str:
        """Detect the intent of the question"""
        
        intents = {
            'skill_recommendation': ['skill', 'learn', 'study', 'what should i learn', 'which skill', 'upskill', 'what to study', 'recommendation', 'should i learn', 'need to learn'],
            
            'interview_prep': ['interview', 'prepare for interview', 'technical interview', 'coding interview', 'interview questions', 'how to prepare', 'interview tips', 'interviewer'],
            
            'salary_info': ['salary', 'pay', 'compensation', 'how much', 'earn', 'paid', 'wage', 'income', 'money', 'what salary', 'pay scale'],
            
            'career_path': ['career path', 'career growth', 'promotion', 'advance', 'senior', 'lead', 'progression', 'future', 'roadmap', 'where to go', 'next step', 'career journey'],
            
            'certification': ['certification', 'certificate', 'certified', 'credential', 'exam', 'qualification', 'cert', 'professional certification', 'certification program'],
            
            'cv_tips': ['cv', 'resume', 'curriculum vitae', 'application', 'cover letter', 'cv tips', 'resume tips', 'how to write cv', 'cv review'],
            
            'portfolio': ['portfolio', 'project', 'github', 'showcase', 'demo', 'portfolio tips', 'build portfolio', 'personal projects'],
            
            'networking': ['network', 'connect', 'linkedin', 'mentor', 'community', 'networking', 'connections', 'professional network', 'networking tips'],
            
            'job_search': ['job search', 'find job', 'apply', 'application', 'hiring', 'job hunting', 'where to find', 'job board', 'job site', 'looking for job'],
            
            'remote_work': ['remote', 'work from home', 'wfh', 'distributed', 'virtual', 'remote work', 'telecommuting', 'online work'],
            
            'soft_skills': ['soft skill', 'communication', 'leadership', 'teamwork', 'problem solving', 'emotional intelligence', 'soft skills', 'interpersonal skills', 'people skills'],
            
            'trends': ['trend', 'future', 'emerging', 'latest', 'new technology', 'in demand', 'hot skills', 'market trends', 'industry trends', 'growing field'],
            
            'salary_negotiation': ['negotiate', 'negotiation', 'ask for more', 'counter offer', 'how to negotiate', 'negotiate salary', 'salary talk'],
            
            'work_life_balance': ['balance', 'stress', 'burnout', 'overwork', 'healthy', 'work life', 'wellness', 'mental health at work'],
            
            'university': ['university', 'college', 'degree', 'program', 'course', 'study', 'education', 'school', 'graduate', 'undergraduate', 'masters', 'phd', 'admission'],
            
            'job_market': ['job market', 'market trends', 'demand', 'opportunities', 'growth sector', 'job outlook', 'employment', 'hiring trends'],
            
            'entrepreneurship': ['entrepreneur', 'startup', 'business', 'founder', 'launch', 'own business', 'side hustle', 'self-employed', 'business owner'],
            
            'career_change': ['career change', 'switch career', 'transition', 'changing career', 'new field', 'move to', 'shift to', 'career shift'],
            
            'mentorship': ['mentor', 'mentorship', 'coach', 'career coach', 'guidance', 'mentor program', 'professional mentor'],
            
            'freelance': ['freelance', 'freelancer', 'gig', 'contract', 'independent', 'self-employed', 'consultant', 'contract work'],
            
            'international': ['abroad', 'overseas', 'international', 'foreign', 'moving abroad', 'work visa', 'international opportunity', 'expat']
        }
        
        question_lower = question.lower()
        
        for intent, keywords in intents.items():
            if any(keyword in question_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    # ============================================================
    # RULE-BASED RESPONSE GENERATOR (FALLBACK)
    # ============================================================
    
    def _generate_rule_response(self, question: str, sector: str, intent: str, 
                                user_context: Dict) -> str:
        """Generate rule-based response - GUARANTEED to work"""
        
        # Sector-specific responses
        sector_responses = {
            'technology': self._handle_tech_response,
            'data_science': self._handle_data_science_response,
            'cybersecurity': self._handle_cybersecurity_response,
            'fintech': self._handle_fintech_response,
            'software_engineering': self._handle_software_engineering_response,
            'healthcare': self._handle_healthcare_response,
            'mental_health': self._handle_mental_health_response,
            'pharmacy': self._handle_pharmacy_response,
            'nursing': self._handle_nursing_response,
            'public_health': self._handle_public_health_response,
            'law': self._handle_law_response,
            'corporate_law': self._handle_corporate_law_response,
            'human_rights': self._handle_human_rights_response,
            'finance': self._handle_finance_response,
            'investment_banking': self._handle_investment_banking_response,
            'accounting': self._handle_accounting_response,
            'business': self._handle_business_response,
            'marketing': self._handle_marketing_response,
            'hr': self._handle_hr_response,
            'entrepreneurship': self._handle_entrepreneurship_response,
            'education': self._handle_education_response,
            'edtech': self._handle_edtech_response,
            'agriculture': self._handle_agriculture_response,
            'agritech': self._handle_agritech_response,
            'creative': self._handle_creative_response,
            'music': self._handle_music_response,
            'filmmaking': self._handle_filmmaking_response,
            'trades': self._handle_trades_response,
            'construction': self._handle_construction_response,
            'engineering': self._handle_engineering_response,
            'social_work': self._handle_social_work_response,
            'nonprofit': self._handle_nonprofit_response,
            'hospitality': self._handle_hospitality_response,
            'tourism': self._handle_tourism_response,
            'real_estate': self._handle_real_estate_response,
            'logistics': self._handle_logistics_response,
            'media': self._handle_media_response,
            'sports': self._handle_sports_response,
            'environmental': self._handle_environmental_response
        }
        
        # If sector has handler, use it
        if sector in sector_responses:
            return sector_responses[sector](question, intent, user_context)
        
        # Generic response for unknown sectors
        return self._handle_general_response(question, sector, intent, user_context)
    
    # ============================================================
    # SECTOR-SPECIFIC RULE RESPONSES (25+ SECTORS)
    # ============================================================
    
    # ===== TECHNOLOGY & DIGITAL =====
    
    def _handle_tech_response(self, question: str, intent: str, user_context: Dict) -> str:
        """Technology sector rule response"""
        
        if intent == 'skill_recommendation':
            return self._tech_skills_recommendation(user_context)
        elif intent == 'salary_info':
            return self._tech_salary(user_context)
        elif intent == 'career_path':
            return self._tech_career_path(user_context)
        elif intent == 'interview_prep':
            return self._tech_interview_prep()
        elif intent == 'trends':
            return self._tech_trends()
        else:
            return self._tech_general(question, intent, user_context)
    
    def _tech_skills_recommendation(self, user_context: Dict) -> str:
        skills = user_context.get('skills', [])
        experience = user_context.get('experience', 0)
        
        if not skills:
            return """💻 **Top Tech Skills in Ghana (2026):**

🔥 **Most In-Demand:**
1. **Python** - Data Science, AI, Backend (GHS 5k-12k/month)
2. **Cloud Computing** - AWS, Azure (GHS 7k-15k/month)
3. **React/Next.js** - Frontend Development (GHS 4k-10k/month)
4. **Data Science/AI** - 40% growth (GHS 6k-15k/month)
5. **Cybersecurity** - 30% growth (GHS 6k-12k/month)

📚 **Start Here:**
• Python → Django/Flask OR Data Science
• JavaScript → React/Next.js
• SQL → Database Management

💡 **Free Resources:**
• Python.org, freeCodeCamp
• YouTube (free tutorials)
• Google Digital Garage

🎯 **Suggested Path (6 months):**
1. Month 1-2: Python Fundamentals
2. Month 3-4: Choose Specialty
3. Month 5-6: Build Projects & Portfolio

Want personalized advice? Upload your CV! 🚀"""
        
        # Personalized recommendations
        recommendations = []
        skills_lower = [s.lower() for s in skills]
        
        if 'python' in ' '.join(skills_lower):
            recommendations.append("🔥 **Advanced Python** → AI/ML, Data Engineering")
            recommendations.append("🤖 **Machine Learning** → Natural next step")
        else:
            recommendations.append("🐍 **Python** → Foundation for all tech roles")
        
        if any(s in ' '.join(skills_lower) for s in ['javascript', 'react']):
            recommendations.append("⚛️ **React/Next.js** → Modern full-stack")
        else:
            recommendations.append("🌐 **JavaScript/React** → Essential for web dev")
        
        if any(s in ' '.join(skills_lower) for s in ['cloud', 'aws', 'azure']):
            recommendations.append("☁️ **Advanced Cloud** → DevOps, Architecture")
        else:
            recommendations.append("☁️ **Cloud Computing** → AWS Solutions Architect")
        
        recommendations.append("🔒 **Cybersecurity** → Growing demand")
        recommendations.append("🤝 **Soft Skills** → Communication, Leadership")
        
        return f"""🎯 **Your Personalized Tech Path:**

Based on your skills ({', '.join(skills[:3])}) and {experience}+ years:

{chr(10).join(recommendations)}

📊 **Priority Learning:**
1. {recommendations[0] if recommendations else 'Core skills'}
2. {recommendations[1] if len(recommendations) > 1 else 'Specialization'}

🎯 **Goal:** 40% employability increase in 6 months!

Need a weekly plan? Just ask! 🚀"""
    
    def _tech_salary(self, user_context: Dict) -> str:
        experience = user_context.get('experience', 0)
        
        if experience <= 2:
            level = 'Entry'
            multiplier = 0.8
        elif experience <= 5:
            level = 'Mid'
            multiplier = 1.0
        else:
            level = 'Senior'
            multiplier = 1.3
        
        base_min, base_max = 4500, 8000
        min_salary = int(base_min * multiplier)
        max_salary = int(base_max * multiplier)
        
        return f"""💰 **Tech Salaries in Ghana:**

**{level} Level** ({experience} years)

• 💵 Min: GHS {min_salary:,}/month
• 📈 Average: GHS {(min_salary + max_salary)//2:,}/month
• 🚀 Max: GHS {max_salary:,}/month

**Top-Paying Skills:**
1. AWS/Azure: +35%
2. AI/ML: +30%
3. Cybersecurity: +25%
4. DevOps: +25%

**Company Types:**
• Multinational: GHS 8k-18k
• Local Companies: GHS 4k-10k
• Remote (International): USD 3k-8k+

💡 **Boost your salary:**
• Get AWS certified (+25%)
• Learn AI/ML (+30%)
• Build portfolio projects

Want negotiation tips? Ask! 💪"""
    
    def _tech_career_path(self, user_context: Dict) -> str:
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
✅ AWS/GCP certified
✅ Open source contributions
✅ Personal brand building
✅ Active networking
✅ Public speaking

**Fastest Growing Roles:**
1. AI/ML Engineer (+45%)
2. Cloud Architect (+35%)
3. Cybersecurity (+30%)
4. Data Engineer (+28%)"""
    
    def _tech_interview_prep(self) -> str:
        return """🎤 **Tech Interview Prep:**

**📚 4-Week Study Plan:**
• Week 1-2: Data Structures & Algorithms
• Week 3: System Design basics
• Week 4: Practice (LeetCode Easy/Medium)

**Key Topics:**
• Big O Notation
• Recursion & DP
• Trees & Graphs
• Sorting & Searching

**Practice Resources:**
• LeetCode (50+ problems)
• HackerRank
• AlgoExpert

**💰 Salary Negotiation:**
• Know your worth (research salaries)
• Ask for 10-20% more
• Consider total compensation

💡 **Pro Tip:** Explain your thought process out loud!"""
    
    def _tech_trends(self) -> str:
        return """📊 **Tech Trends in Africa (2026):**

**Hottest Skills:**
1. 🤖 AI/ML (+45% growth)
2. ☁️ Cloud Computing (+35%)
3. 🔒 Cybersecurity (+30%)
4. 📊 Data Science (+28%)

**Emerging Roles:**
• AI/ML Engineer (GHS 8k-15k)
• Cloud Architect (GHS 10k-18k)
• Security Analyst (GHS 6k-12k)
• Data Engineer (GHS 7k-14k)

**Growing Industries:**
💳 Fintech (Mobile money)
🏥 HealthTech (Telemedicine)
📚 EdTech (Online learning)
🛒 E-commerce (Logistics)
🌾 AgriTech (Farming tech)

**Future Predictions:**
• Remote work becomes standard
• AI tools boost productivity
• Green tech emerges
• Cross-border collaboration"""
    
    def _tech_general(self, question: str, intent: str, user_context: Dict) -> str:
        return f"""💻 **Technology Career Guidance:**

I can help you with:
• 📚 **Skills** - What to learn
• 💰 **Salaries** - Tech earnings
• 🎯 **Career Path** - How to advance
• 📝 **CV Tips** - Stand out
• 🏆 **Certifications** - What to get
• 💼 **Job Search** - Where to apply
• 🔍 **Interview Prep** - How to prepare

**Your question:** "{question}"

💡 Tip: Be specific about your tech stack! 🚀"""

    # ===== DATA SCIENCE =====
    
    def _handle_data_science_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📊 **Data Science Career in Ghana:**

**Skills to Learn:**
1. Python (pandas, numpy, scikit-learn)
2. SQL (PostgreSQL, MySQL)
3. Statistics & Probability
4. Machine Learning
5. Data Visualization (Tableau, Power BI)

**Certifications:**
• Google Data Analytics Professional
• IBM Data Science
• AWS Machine Learning

**Salaries in Ghana:**
• Junior: GHS 5k-7k/month
• Mid: GHS 7k-12k/month
• Senior: GHS 12k-18k/month

**Companies Hiring:**
• Fintech companies
• Banks (GCB, Stanbic)
• Telecom (MTN, Vodafone)
• Startups (Hubtel, MEST)

💡 **Start:** Kaggle challenges + portfolio projects! 📊"""

    # ===== CYBERSECURITY =====
    
    def _handle_cybersecurity_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🔒 **Cybersecurity Career in Ghana:**

**Career Path:**
1. Security Analyst → Engineer → Architect
2. GRC (Governance, Risk, Compliance)
3. Security Operations (SOC)

**Essential Skills:**
• Network security
• Ethical hacking (CEH)
• Risk management
• ISO 27001
• Firewalls & SIEM

**Certifications:**
• CompTIA Security+
• Certified Ethical Hacker (CEH)
• CISSP (Senior)
• ISO 27001 Lead Implementer

**Salaries:**
• Junior: GHS 4k-6k/month
• Mid: GHS 6k-10k/month
• Senior: GHS 10k-16k/month

**Companies:**
• Banks (GCB, Stanbic)
• Telecom (MTN)
• Government agencies
• Fintech companies

💡 **Start with:** Security+ certification! 🔐"""

    # ===== FINTECH =====
    
    def _handle_fintech_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """💳 **Fintech Career in Ghana:**

**Skills Needed:**
• Mobile Money (MoMo)
• Payment systems
• Blockchain
• API development
• Compliance/RegTech

**Roles:**
• Fintech Product Manager
• Mobile Money Specialist
• Payment Engineer
• Compliance Officer

**Salaries:**
• Junior: GHS 5k-8k/month
• Mid: GHS 8k-14k/month
• Senior: GHS 14k-20k/month

**Top Employers:**
• MTN MoMo
• Tigo Cash
• E-Cash
• ExpressPay
• Credit Bureau

💡 **Growth:** Fintech is #1 in Africa! 📱"""

    # ===== SOFTWARE ENGINEERING =====
    
    def _handle_software_engineering_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """💻 **Software Engineering Career in Ghana:**

**Career Paths:**
1. Full-Stack Development
2. Backend Engineering
3. Frontend Engineering
4. Mobile Development

**Must-Have Skills:**
• Git & Version Control
• API Development (REST/GraphQL)
• Database Management
• Testing & Debugging
• Cloud (AWS/Azure)

**Salaries:**
• Junior: GHS 4k-6k/month
• Mid: GHS 6k-10k/month
• Senior: GHS 10k-16k/month

**Certifications:**
• AWS Developer
• Google Associate Engineer

**Top Tech Hubs:**
• Accra (MEST, Hubtel)
• Kumasi
• Tema

💡 **Build portfolio:** 3-5 projects on GitHub! 🚀"""

    # ===== HEALTHCARE =====
    
    def _handle_healthcare_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏥 **Healthcare Careers in Ghana:**

**Most In-Demand Roles:**
1. 🩺 Medical Doctors (Specialists)
2. 💉 Registered Nurses
3. 💊 Pharmacists
4. 🔬 Lab Scientists
5. 🏥 Public Health Specialists

**Specializations:**
• Surgery, Internal Medicine
• Pediatrics, OB/GYN
• Cardiology, Neurology

**Salaries:**
• Medical Officer: GHS 5k-8k/month
• Specialist: GHS 8k-15k/month
• Consultant: GHS 15k-25k/month

**Institutions:**
• University of Ghana Medical School
• KNUST School of Medicine
• UCC Medical School

💡 **Fastest Growing:** Telemedicine + HealthTech! 🩺"""

    # ===== MENTAL HEALTH =====
    
    def _handle_mental_health_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🧠 **Mental Health Career in Ghana:**

**Roles:**
1. Clinical Psychologist
2. Psychiatrist (Medical)
3. Counselor (Therapist)
4. Mental Health Nurse
5. Community Mental Health Worker

**Certifications:**
• Master's in Clinical Psychology
• Psychiatry (Medical)
• Counseling Certification

**Salaries:**
• Counselor: GHS 3k-5k/month
• Psychologist: GHS 5k-8k/month
• Psychiatrist: GHS 8k-15k/month

**Institutions:**
• University of Ghana - Psychology
• KNUST - Psychology
• Mental Health Authority of Ghana

💡 **Growing Need:** Mental health awareness is increasing! 🧠"""

    # ===== PHARMACY =====
    
    def _handle_pharmacy_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """💊 **Pharmacy Career in Ghana:**

**Career Path:**
1. Doctor of Pharmacy (PharmD) - 6 years
2. BSc Pharmacy - 4 years
3. Internship (1 year)
4. Licensed Pharmacist

**Practice Areas:**
• Community Pharmacy
• Hospital Pharmacy
• Clinical Pharmacy
• Pharmaceutical Industry
• Regulatory Affairs

**Salaries:**
• Entry: GHS 3k-5k/month
• Experienced: GHS 5k-8k/month
• Hospital: GHS 6k-9k/month
• Industry: GHS 8k-15k/month

**Institutions:**
• KNUST - Pharmacy
• University of Ghana - Pharmacy

💡 **Tip:** Industrial pharmacy pays the highest! 💰"""

    # ===== NURSING =====
    
    def _handle_nursing_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🩺 **Nursing Career in Ghana:**

**Career Path:**
1. Nursing Diploma/BSc (3-4 years)
2. Registered Nurse (RN)
3. Specialization
4. Advanced Practice

**Specializations:**
• Critical Care (ICU/CCU)
• Pediatric Nursing
• Maternity/OB
• Cardiac Nursing
• Mental Health

**Certifications:**
• BLS (Basic Life Support)
• ACLS (Advanced Cardiac)
• PALS (Pediatric)

**Salaries:**
• Entry RN: GHS 3k-4k/month
• Experienced: GHS 4k-7k/month
• Nurse Manager: GHS 7k-10k/month

💡 **Boost:** BLS/ACLS adds 20-30%! 🏥"""

    # ===== PUBLIC HEALTH =====
    
    def _handle_public_health_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏛️ **Public Health Career in Ghana:**

**Roles:**
1. Epidemiologist
2. Health Educator
3. Program Manager
4. Health Policy Analyst
5. Community Health Officer

**Skills:**
• Epidemiology & Biostatistics
• Health Policy
• Program Evaluation
• Community Engagement

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-15k/month

**Employers:**
• Ghana Health Service
• WHO, UNICEF
• Ministry of Health
• NGOs

💡 **Opportunity:** Public Health is growing! 🌍"""

    # ===== LAW =====
    
    def _handle_law_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """⚖️ **Law Career in Ghana:**

**Career Path:**
1. LLB (4 years)
2. Ghana School of Law (2 years)
3. Call to Bar
4. Pupillage (1 year)
5. → Solicitor/Barrister

**Practice Areas:**
• Corporate/Commercial Law
• Criminal Law
• Human Rights
• Family Law
• Property Law

**Salaries:**
• Pupil: GHS 2k-3k/month
• Junior Associate: GHS 4k-6k/month
• Associate: GHS 7k-10k/month
• Senior/Partner: GHS 12k-20k+

**Institutions:**
• University of Ghana - Faculty of Law
• KNUST - Faculty of Law
• Ghana School of Law

💡 **Tip:** Corporate/Intellectual Property pay highest! ⚖️"""

    # ===== CORPORATE LAW =====
    
    def _handle_corporate_law_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏢 **Corporate Law Career:**

**Practice Areas:**
• Mergers & Acquisitions
• Securities Law
• Commercial Contracts
• Corporate Governance
• Compliance

**Skills:**
• Contract Drafting
• Due Diligence
• Corporate Law Knowledge
• Negotiation Skills

**Salaries:**
• Junior: GHS 5k-8k/month
• Mid: GHS 8k-15k/month
• Senior: GHS 15k-25k/month

**Top Employers:**
• Top Law Firms (BLA, SAM)
• Banks
• Multinationals
• Corporate Legal Departments

💡 **High Demand:** Corporate lawyers are well-paid! 💰"""

    # ===== HUMAN RIGHTS =====
    
    def _handle_human_rights_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🕊️ **Human Rights Career:**

**Roles:**
1. Human Rights Lawyer
2. Advocacy Officer
3. Legal Aid Lawyer
4. Policy Analyst
5. NGO Director

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-12k/month

**Organizations:**
• CHRAJ
• NGOs
• UN Agencies
• Legal Aid

💡 **Tip:** Combine law with advocacy! 🕊️"""

    # ===== FINANCE =====
    
    def _handle_finance_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """💰 **Finance Careers in Ghana:**

**Career Paths:**
1. Banking (Retail/Corporate)
2. Investment Banking
3. Accounting
4. Risk Management
5. Fintech

**Key Certifications:**
• ACCA (Highly recommended!)
• CPA
• CFA
• CIMA

**Salaries:**
• Junior: GHS 3k-5k/month
• Mid: GHS 6k-12k/month
• Senior: GHS 15k-40k/month

**Top Employers:**
• GCB Bank, Stanbic
• PwC, KPMG, Deloitte
• Bank of Ghana
• Fintech Companies

💡 **Hottest:** Fintech is growing fast! 💳"""

    # ===== INVESTMENT BANKING =====
    
    def _handle_investment_banking_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📈 **Investment Banking Career:**

**Roles:**
1. Investment Banking Analyst
2. Associate
3. Vice President
4. Managing Director

**Skills Needed:**
• Financial Modeling
• Valuation
• Excel (Advanced)
• Mergers & Acquisitions
• Capital Markets

**Salaries:**
• Analyst: GHS 8k-12k/month
• Associate: GHS 12k-20k/month
• VP: GHS 20k-35k/month

**Employers:**
• Investment Banks
• Private Equity Firms
• Corporate Finance Departments

💡 **Requirements:** CFA or Finance degree! 📊"""

    # ===== ACCOUNTING =====
    
    def _handle_accounting_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🧾 **Accounting Career in Ghana:**

**Roles:**
1. Accountant
2. Auditor
3. Tax Consultant
4. Financial Controller
5. CFO

**Certifications:**
• ACCA (Most recognized!)
• CPA
• CIMA
• ICAEW

**Salaries:**
• Junior: GHS 3k-5k/month
• Mid: GHS 5k-10k/month
• Senior: GHS 10k-20k/month
• CFO: GHS 20k-40k/month

**Employers:**
• Big 4 (PwC, KPMG, EY, Deloitte)
• Banks
• Corporate Accounting

💡 **Tip:** ACCA opens doors everywhere! 📚"""

    # ===== BUSINESS =====
    
    def _handle_business_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏢 **Business Career in Ghana:**

**Career Paths:**
1. Management
2. Marketing
3. HR
4. Operations
5. Consulting

**MBA Programs:**
• University of Ghana Business School
• KNUST School of Business
• GIMPA
• UCC Business School

**Salaries:**
• Entry: GHS 3k-5k/month
• Manager: GHS 5k-10k/month
• Director: GHS 10k-20k/month

💡 **Hot Skills:**
• Digital Marketing
• Data Analytics
• Project Management (PMP) 📊"""

    # ===== MARKETING =====
    
    def _handle_marketing_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📢 **Marketing Career in Ghana:**

**Roles:**
1. Marketing Executive
2. Brand Manager
3. Digital Marketing Specialist
4. Social Media Manager
5. Marketing Director

**Skills:**
• Digital Marketing (SEO, Google Ads)
• Social Media Management
• Content Creation
• Brand Strategy
• Analytics

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-15k/month

💡 **Growth:** Digital Marketing is exploding! 📱"""

    # ===== HR =====
    
    def _handle_hr_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """👥 **Human Resources Career:**

**Roles:**
1. HR Officer
2. Recruitment Specialist
3. Talent Manager
4. HR Director
5. Organizational Development

**Certifications:**
• CIPD
• SHRM
• HRCI

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-15k/month

💡 **Growing:** Talent Management & AI in HR! 🤖"""

    # ===== ENTREPRENEURSHIP =====
    
    def _handle_entrepreneurship_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🚀 **Entrepreneurship in Ghana:**

**Steps to Start:**
1. Validate your idea
2. Create business plan
3. Register (Registrar General)
4. Open bank account
5. Start small, scale fast

**Funding Sources:**
• Personal savings
• Family & Friends
• Government programs
• Angel investors
• Venture Capital

**Resources:**
• NBSSI
• Ghana Enterprise Agency
• MEST Incubator
• Tony Elumelu Foundation

💡 **Tip:** Start with Minimum Viable Product (MVP)! 🚀"""

    # ===== EDUCATION =====
    
    def _handle_education_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📚 **Education Careers in Ghana:**

**Roles:**
1. Teacher (Primary/JHS/SHS)
2. University Lecturer
3. School Administrator
4. Education Officer
5. EdTech Specialist

**Teacher Licensure:**
• GES Licensure Exam
• Teacher Professional Development
• Continuing Education

**Salaries:**
• Teacher: GHS 3.5k-5k/month
• Senior Teacher: GHS 5k-7k/month
• Lecturer: GHS 6k-15k/month

💡 **Growth:** EdTech is booming! 📱"""

    # ===== EDTECH =====
    
    def _handle_edtech_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📱 **EdTech Career in Ghana:**

**Roles:**
1. Education Technology Specialist
2. Learning Experience Designer
3. Educational App Developer
4. Online Learning Manager

**Skills:**
• Instructional Design
• Learning Management Systems (Moodle)
• Educational Content Creation
• UX/UI Design for Education

**Salaries:**
• Entry: GHS 4k-6k/month
• Mid: GHS 6k-10k/month
• Senior: GHS 10k-15k/month

💡 **Growing:** Education + Technology = Future! 🚀"""

    # ===== AGRICULTURE =====
    
    def _handle_agriculture_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🌾 **Agriculture Careers in Ghana:**

**Career Paths:**
1. Crop Production
2. Agribusiness
3. Agricultural Extension
4. Animal Science
5. Food Processing

**Specializations:**
• Cocoa, Maize, Rice
• Poultry, Livestock
• Fisheries
• Irrigation

**Salaries:**
• Extension Officer: GHS 3.5k-5k/month
• Agronomist: GHS 4.5k-8k/month
• Agribusiness Manager: GHS 8k-15k/month

💡 **Hot Trend:** AgriTech is booming! 🌱"""

    # ===== AGRITECH =====
    
    def _handle_agritech_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🌱 **AgriTech Career in Ghana:**

**Roles:**
1. AgriTech Specialist
2. Precision Agriculture Expert
3. Data Scientist (Agriculture)
4. Drone Pilot (Agriculture)
5. Digital Extension Officer

**Skills:**
• GIS & Remote Sensing
• IoT for Agriculture
• Data Analytics
• Mobile Apps for Farmers

**Salaries:**
• Entry: GHS 5k-7k/month
• Mid: GHS 7k-12k/month
• Senior: GHS 12k-18k/month

💡 **Growing:** Agriculture meets Technology! 🚜"""

    # ===== CREATIVE =====
    
    def _handle_creative_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🎨 **Creative Arts Career in Ghana:**

**Roles:**
1. Graphic Designer
2. Art Director
3. Creative Director
4. UI/UX Designer
5. Visual Artist

**Tools:**
• Adobe Creative Suite
• Figma
• Blender (3D)
• Canva

**Salaries:**
• Entry: GHS 2k-3.5k/month
• Senior: GHS 4k-7k/month
• Art Director: GHS 6k-10k/month

💡 **Success:** Build a strong portfolio! 🎨"""

    # ===== MUSIC =====
    
    def _handle_music_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🎵 **Music Career in Ghana:**

**Roles:**
1. Music Producer
2. Audio Engineer
3. Recording Artist
4. Sound Designer
5. Music Business Manager

**Salaries:**
• Music Producer: GHS 5k-15k/month
• Sound Engineer: GHS 4k-8k/month
• Artist: Varies widely

💡 **Growth:** Digital distribution is growing! 🎧"""

    # ===== FILMMAKING =====
    
    def _handle_filmmaking_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🎬 **Filmmaking Career in Ghana:**

**Roles:**
1. Film Director
2. Producer
3. Cinematographer
4. Editor
5. Screenwriter

**Skills:**
• Camera Operation
• Video Editing (Premiere, Final Cut)
• Scriptwriting
• Production Management

**Salaries:**
• Entry: GHS 2k-4k/month
• Mid: GHS 4k-8k/month
• Senior: GHS 8k-15k/month

💡 **Opportunity:** Ghana's film industry is growing! 🎥"""

    # ===== TRADES =====
    
    def _handle_trades_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🛠️ **Trades Career in Ghana:**

**Career Paths:**
1. Carpentry → Contractor
2. Plumbing → Plumbing Contractor
3. Electrical → Electrical Contractor
4. Welding → Workshop Owner
5. Automotive → Workshop Owner

**Certifications:**
• City & Guilds
• NVTI Apprenticeship
• Sector Skills Council

**Salaries:**
• Apprentice: GHS 500-1k/month
• Journeyman: GHS 1.5k-2.5k/month
• Master: GHS 3k-5k/month
• Contractor: GHS 5k-15k/month

💡 **Tip:** Start your own business! 🔧"""

    # ===== CONSTRUCTION =====
    
    def _handle_construction_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏗️ **Construction Career in Ghana:**

**Roles:**
1. Construction Manager
2. Site Supervisor
3. Quantity Surveyor
4. Architect
5. Building Inspector

**Salaries:**
• Supervisor: GHS 4k-7k/month
• Quantity Surveyor: GHS 6k-10k/month
• Project Manager: GHS 10k-18k/month

💡 **Growth:** Construction is booming in Ghana! 🏗️"""

    # ===== ENGINEERING =====
    
    def _handle_engineering_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏗️ **Engineering Careers in Ghana:**

**Fields:**
1. Civil Engineering
2. Mechanical Engineering
3. Electrical Engineering
4. Chemical Engineering
5. Environmental Engineering

**Professional Registration:**
• Graduate Engineer (GEng)
• Professional Engineer (PEng)
• EIB Registration

**Salaries:**
• Graduate: GHS 3.5k-5k/month
• Engineer: GHS 5k-8k/month
• Senior: GHS 8k-12k/month
• Consultant: GHS 15k-25k/month

💡 **Tip:** Get your PEng certification! 📐"""

    # ===== SOCIAL WORK =====
    
    def _handle_social_work_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏛️ **Social Work Career in Ghana:**

**Roles:**
1. Social Worker
2. Community Officer
3. Child Protection Specialist
4. Mental Health Counselor
5. Program Manager

**Salaries:**
• Entry: GHS 2.5k-3.5k/month
• Mid: GHS 4k-6k/month
• Senior: GHS 6k-10k/month

💡 **Tip:** NGOs & International orgs pay highest! 🤝"""

    # ===== NONPROFIT =====
    
    def _handle_nonprofit_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🌍 **Nonprofit Career in Ghana:**

**Roles:**
1. Program Officer
2. Project Manager
3. Fundraising Specialist
4. Grant Writer
5. Country Director

**Skills:**
• Project Management
• Fundraising & Grant Writing
• Monitoring & Evaluation
• Community Engagement

**Salaries:**
• Program Officer: GHS 4k-7k/month
• Manager: GHS 7k-12k/month
• Director: GHS 15k-25k/month

💡 **Organizations:** UNICEF, WHO, CARE, World Vision 🌍"""

    # ===== HOSPITALITY =====
    
    def _handle_hospitality_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏨 **Hospitality Career in Ghana:**

**Roles:**
1. Hotel Manager
2. Restaurant Manager
3. Guest Service Manager
4. Event Planner
5. Hospitality Consultant

**Salaries:**
• Entry: GHS 2.5k-4k/month
• Mid: GHS 4k-7k/month
• Senior: GHS 7k-12k/month

💡 **Growth:** Tourism is recovering strongly! 🏖️"""

    # ===== TOURISM =====
    
    def _handle_tourism_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """✈️ **Tourism Career in Ghana:**

**Roles:**
1. Tour Guide
2. Travel Agent
3. Tour Operator
4. Destination Manager
5. Ecotourism Specialist

**Salaries:**
• Guide: GHS 2k-4k/month
• Agent: GHS 3k-5k/month
• Manager: GHS 5k-8k/month

💡 **Opportunity:** Ghana's tourism is growing! 🇬🇭"""

    # ===== REAL ESTATE =====
    
    def _handle_real_estate_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🏠 **Real Estate Career in Ghana:**

**Roles:**
1. Estate Agent
2. Property Manager
3. Real Estate Developer
4. Appraisal Specialist
5. Land Acquisition Specialist

**Salaries:**
• Agent: GHS 3k-6k/month
• Manager: GHS 6k-10k/month
• Developer: GHS 10k-20k/month

💡 **Growth:** Real estate is booming in Accra! 🏙️"""

    # ===== LOGISTICS =====
    
    def _handle_logistics_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📦 **Logistics Career in Ghana:**

**Roles:**
1. Logistics Manager
2. Supply Chain Analyst
3. Warehouse Manager
4. Procurement Specialist
5. Fleet Manager

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-15k/month

💡 **Opportunity:** E-commerce is driving logistics growth! 🚚"""

    # ===== MEDIA =====
    
    def _handle_media_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """📺 **Media Career in Ghana:**

**Roles:**
1. Journalist
2. News Reporter
3. Editor
4. Broadcaster
5. Media Producer

**Salaries:**
• Entry: GHS 2.5k-4k/month
• Mid: GHS 4k-7k/month
• Senior: GHS 7k-12k/month

💡 **Growth:** Digital media is expanding! 📱"""

    # ===== SPORTS =====
    
    def _handle_sports_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """⚽ **Sports Career in Ghana:**

**Roles:**
1. Sports Coach
2. Personal Trainer
3. Sports Manager
4. Physical Education Teacher
5. Sports Analyst

**Salaries:**
• Coach: GHS 2k-5k/month
• Trainer: GHS 3k-6k/month
• Manager: GHS 5k-10k/month

💡 **Growth:** Sports management is growing! 🏆"""

    # ===== ENVIRONMENTAL =====
    
    def _handle_environmental_response(self, question: str, intent: str, user_context: Dict) -> str:
        return """🌿 **Environmental Career in Ghana:**

**Roles:**
1. Environmental Scientist
2. Conservation Officer
3. Environmental Manager
4. Sustainability Consultant
5. Climate Change Specialist

**Salaries:**
• Entry: GHS 3k-5k/month
• Mid: GHS 5k-8k/month
• Senior: GHS 8k-15k/month

💡 **Growing:** Climate action is creating jobs! 🌍"""

    # ===== GENERAL =====
    
    def _handle_general_response(self, question: str, sector: str, intent: str, user_context: Dict) -> str:
        sector_names = {
            'technology': 'Technology',
            'data_science': 'Data Science',
            'cybersecurity': 'Cybersecurity',
            'fintech': 'Fintech',
            'software_engineering': 'Software Engineering',
            'healthcare': 'Healthcare',
            'mental_health': 'Mental Health',
            'pharmacy': 'Pharmacy',
            'nursing': 'Nursing',
            'public_health': 'Public Health',
            'law': 'Law',
            'corporate_law': 'Corporate Law',
            'human_rights': 'Human Rights',
            'finance': 'Finance',
            'investment_banking': 'Investment Banking',
            'accounting': 'Accounting',
            'business': 'Business',
            'marketing': 'Marketing',
            'hr': 'Human Resources',
            'entrepreneurship': 'Entrepreneurship',
            'education': 'Education',
            'edtech': 'EdTech',
            'agriculture': 'Agriculture',
            'agritech': 'AgriTech',
            'creative': 'Creative Arts',
            'music': 'Music',
            'filmmaking': 'Filmmaking',
            'trades': 'Trades',
            'construction': 'Construction',
            'engineering': 'Engineering',
            'social_work': 'Social Work',
            'nonprofit': 'Nonprofit',
            'hospitality': 'Hospitality',
            'tourism': 'Tourism',
            'real_estate': 'Real Estate',
            'logistics': 'Logistics',
            'media': 'Media',
            'sports': 'Sports',
            'environmental': 'Environmental'
        }
        
        sector_name = sector_names.get(sector, 'Career')
        
        return f"""🤖 **TalentAssistant - Your Career Guide!**

I help with questions about **{sector_name}** and more.

**I can help with:**
• 📚 **Skills** - "What should I learn?"
• 💰 **Salaries** - "How much can I earn in Ghana?"
• 🎯 **Career Path** - "How to advance?"
• 📝 **CV Tips** - "How to stand out?"
• 🏆 **Certifications** - "What's valuable?"
• 💼 **Job Search** - "Where to find jobs?"
• 🤝 **Networking** - "How to connect?"
• 🌍 **Remote Work** - "Tips for working remote?"

**Your question:** "{question}"

💡 **Pro Tip:** Tell me more about your experience and skills for personalized advice!

What else would you like to know? 🚀"""
    
    # ============================================================
    # SUGGESTED FOLLOW-UPS
    # ============================================================
    
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
                "What questions should I ask the interviewer?"
            ],
            'salary_info': [
                "How can I negotiate a higher salary?",
                "What benefits should I ask for?",
                "What skills increase salary most?"
            ],
            'career_path': [
                "How long to reach senior level?",
                "What's the fastest way to advance?",
                "Should I get a master's degree?"
            ],
            'certification': [
                "Which cert is best for beginners?",
                "How to prepare for the exam?",
                "What's the ROI of certification?"
            ],
            'general': [
                "What skills are in demand now?",
                "How to find a mentor?",
                "Tips for remote work?"
            ]
        }
        
        sector_followups = {
            'technology': [
                "What programming language should I learn first?",
                "How to get a remote tech job?"
            ],
            'healthcare': [
                "How to become a specialist doctor?",
                "What are the best nursing schools?"
            ],
            'finance': [
                "Is ACCA better than CPA?",
                "How to get into investment banking?"
            ],
            'business': [
                "Should I get an MBA?",
                "How to start a consulting career?"
            ]
        }
        
        result = followups.get(intent, followups['general'])
        if sector in sector_followups:
            result = result + sector_followups[sector]
        
        return result[:5]