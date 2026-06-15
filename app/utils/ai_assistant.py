import re
import random
from typing import Dict, List, Any

class CareerAssistant:
    """Advanced AI Career Assistant with intelligent responses"""
    
    def __init__(self):
        self.context_memory = {}
        
    def get_response(self, question: str, user_skills: List[str] = None, experience: int = 0) -> Dict:
        """Generate intelligent response based on question type"""
        
        question_lower = question.lower()
        
        # Determine intent
        intent = self._detect_intent(question_lower)
        
        # Generate response based on intent
        if intent == 'skill_recommendation':
            response = self._handle_skill_recommendation(user_skills, experience)
        elif intent == 'interview_prep':
            response = self._handle_interview_prep(question_lower)
        elif intent == 'salary_info':
            response = self._handle_salary_info(question_lower, experience)
        elif intent == 'career_path':
            response = self._handle_career_path(question_lower, user_skills)
        elif intent == 'certification':
            response = self._handle_certification(question_lower)
        elif intent == 'cv_tips':
            response = self._handle_cv_tips()
        elif intent == 'portfolio':
            response = self._handle_portfolio_advice()
        elif intent == 'networking':
            response = self._handle_networking_tips()
        elif intent == 'job_search':
            response = self._handle_job_search_tips()
        elif intent == 'remote_work':
            response = self._handle_remote_work()
        elif intent == 'soft_skills':
            response = self._handle_soft_skills()
        elif intent == 'tech_trends':
            response = self._handle_tech_trends()
        elif intent == 'salary_negotiation':
            response = self._handle_salary_negotiation()
        elif intent == 'work_life_balance':
            response = self._handle_work_life_balance()
        else:
            response = self._handle_general_question(question_lower)
            
        return {
            'response': response,
            'intent': intent,
            'suggested_followups': self._get_suggested_followups(intent)
        }
    
    def _detect_intent(self, question: str) -> str:
        """Detect the intent of the question"""
        
        intents = {
            'skill_recommendation': ['skill', 'learn', 'study', 'what should i learn', 'which skill', 'upskill'],
            'interview_prep': ['interview', 'prepare for interview', 'technical interview', 'coding interview'],
            'salary_info': ['salary', 'pay', 'compensation', 'how much', 'earn', 'paid'],
            'career_path': ['career path', 'career growth', 'promotion', 'advance', 'senior', 'lead'],
            'certification': ['certification', 'certificate', 'certified', 'credential', 'exam'],
            'cv_tips': ['cv', 'resume', 'curriculum vitae', 'application', 'cover letter'],
            'portfolio': ['portfolio', 'project', 'github', 'showcase', 'demo'],
            'networking': ['network', 'connect', 'linkedin', 'mentor', 'community'],
            'job_search': ['job search', 'find job', 'apply', 'application', 'hiring'],
            'remote_work': ['remote', 'work from home', 'wfh', 'distributed', 'virtual'],
            'soft_skills': ['soft skill', 'communication', 'leadership', 'teamwork', 'problem solving'],
            'tech_trends': ['trend', 'future', 'emerging', 'latest', 'new technology'],
            'salary_negotiation': ['negotiate', 'negotiation', 'ask for more', 'counter offer'],
            'work_life_balance': ['balance', 'stress', 'burnout', 'overwork', 'healthy']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in question for keyword in keywords):
                return intent
                
        return 'general'
    
    def _handle_skill_recommendation(self, user_skills: List[str], experience: int) -> str:
        """Generate personalized skill recommendations"""
        
        if not user_skills:
            return """Based on current market trends in Africa, here are the top skills you should consider learning:

🔥 **Hot Skills for 2026:**
1. **Python** - Most in-demand (92% of job postings)
2. **Machine Learning/AI** - 40% job growth in Africa
3. **Cloud Computing (AWS/Azure)** - Highest salaries (GHS 15k+)
4. **Data Analysis** - Needed across all industries
5. **Cybersecurity** - Growing demand in fintech

💡 **Quick Start:** Begin with Python fundamentals (4 weeks), then specialize based on your interest.

Want me to create a personalized learning plan for you? Upload your CV first! 📄"""
        
        # Personalized recommendations based on user's existing skills
        skills_set = [s.lower() for s in user_skills]
        
        recommendations = []
        if 'python' in str(skills_set):
            recommendations.append("• **Advanced Python** → Move to frameworks like Django/FastAPI")
            recommendations.append("• **Machine Learning** → Natural next step with your Python skills")
        else:
            recommendations.append("• **Python Programming** → Foundation for all tech roles")
            
        if any(skill in str(skills_set) for skill in ['data', 'analysis']):
            recommendations.append("• **Advanced Data Science** → Deepen with ML and AI")
        else:
            recommendations.append("• **Data Analysis** → Pandas, SQL, Visualization")
            
        recommendations.append("• **Cloud Computing** → AWS or Azure certification")
        recommendations.append("• **Soft Skills** → Communication, Leadership, Problem-solving")
        
        return f"""🎯 **Personalized Skill Recommendations for You:**

Based on your profile with skills in {', '.join(user_skills[:3])} and {experience}+ years experience:

{chr(10).join(recommendations)}

📊 **Priority Order:**
1. Focus on {recommendations[0].replace('• ', '')} first
2. Then add {recommendations[1].replace('• ', '')}
3. Finally, pursue certifications in {recommendations[2].replace('• ', '')}

🎯 **Goal:** Complete these in 3-6 months for 40% employability increase!

Would you like me to create a detailed weekly learning plan?"""
    
    def _handle_interview_prep(self, question: str) -> str:
        """Provide interview preparation advice"""
        
        if 'technical' in question or 'coding' in question:
            return """💻 **Technical Interview Preparation:**

📚 **Study Plan:**
• **Week 1-2:** Data Structures & Algorithms (Arrays, Strings, Hash Tables)
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

💡 **Pro Tip:** Focus on solving problems and explaining your thought process out loud!"""
        
        return """🎤 **Complete Interview Preparation Guide:**

**Before Interview (Week 1-2):**
✅ Research company and role thoroughly
✅ Review your CV and prepare stories using STAR method
✅ Practice common behavioral questions
✅ Prepare 5-7 questions to ask the interviewer

**Technical Prep:**
✅ Review core concepts in your tech stack
✅ Practice coding challenges (30 mins daily)
✅ Build a small demo project if needed

**Day of Interview:**
✅ Test your tech setup (camera, mic, internet)
✅ Dress professionally (even for remote)
✅ Have water and notes ready
✅ Arrive 5 minutes early

**Sample Questions to Prepare:**
• "Tell me about yourself" (2-min version)
• "Why do you want this role?"
• "Describe a challenge you overcame"
• "Where do you see yourself in 5 years?"

Need specific practice questions for your role? Just ask! 🚀"""
    
    def _handle_salary_info(self, question: str, experience: int) -> str:
        """Provide salary information"""
        
        role = self._extract_role(question)
        
        salaries = {
            'entry': {'min': 2500, 'max': 4500},
            'mid': {'min': 5000, 'max': 8500},
            'senior': {'min': 9000, 'max': 15000}
        }
        
        if experience <= 2:
            level = 'entry'
        elif experience <= 5:
            level = 'mid'
        else:
            level = 'senior'
            
        return f"""💰 **Salary Guide for {role if role else 'Tech Roles'} in Ghana/West Africa:**

**{level.upper()} Level** ({experience} years experience)
• Minimum: GHS {salaries[level]['min']:,}/month
• Average: GHS {(salaries[level]['min'] + salaries[level]['max']) // 2:,}/month
• Maximum: GHS {salaries[level]['max']:,}/month

**Factors Affecting Salary:**
• Company size (Startup vs Enterprise)
• Location (Accra has highest rates)
• Specific skills (Cloud/AI add 20-30%)
• Certifications (AWS adds +25%)
• Negotiation skills

**Top Paying Skills:**
1. Cloud Computing (+35%)
2. Machine Learning (+30%)
3. Cybersecurity (+25%)

💡 **Tip:** Always negotiate! Most companies expect it. Would you like negotiation tips?"""
    
    def _handle_career_path(self, question: str, user_skills: List[str]) -> str:
        """Provide career path guidance"""
        
        return """🎯 **Career Progression Roadmap:**

**Years 0-2 (Junior):**
• Master fundamentals
• Build portfolio projects
• Get first certification
• 💰 GHS 2.5k-4.5k/month

**Years 2-5 (Mid-Level):**
• Specialize in 1-2 areas
• Mentor juniors
• Lead small projects
• 💰 GHS 5k-8.5k/month

**Years 5-8 (Senior):**
• Architecture decisions
• Team leadership
• Strategic planning
• 💰 GHS 9k-12k/month

**Years 8+ (Lead/Principal):**
• Technical strategy
• Cross-team initiatives
• Industry influence
• 💰 GHS 12k-15k+/month

**Fast-Track Tips:**
• Get certified (AWS, Google, Azure)
• Contribute to open source
• Build a personal brand
• Network actively

What stage are you currently at? I can give more specific advice! 🚀"""
    
    def _handle_certification(self, question: str) -> str:
        """Provide certification advice"""
        
        return """🏆 **Most Valuable Certifications in Africa:**

**Cloud Certifications (Highest ROI):**
• AWS Certified Cloud Practitioner (Beginner) - GHS +25%
• AWS Solutions Architect (Advanced) - GHS +40%
• Microsoft Azure Fundamentals
• Google Cloud Associate

**Data & AI:**
• Google Data Analytics Professional
• IBM Data Science
• TensorFlow Developer Certificate
• Microsoft Azure AI Fundamentals

**Development:**
• Meta Backend/Frontend Certificates
• freeCodeCamp Certifications
• Oracle Java/MySQL Certifications

**Project Management:**
• PMP (Project Management Professional)
• Scrum Master Certification
• Agile Certified Practitioner

**Cost-Effective Options:**
• Coursera ($39-59/month with financial aid)
• edX (Free audit option)
• LinkedIn Learning (Free with Premium trial)
• YouTube (Free tutorials)

🎯 **Recommended Path:**
1. Start with AWS Cloud Practitioner (2 months)
2. Then Google Data Analytics (3 months)
3. Finally, PMP or Scrum (2 months)

Which field interests you most? I can provide specific exam tips!"""
    
    def _handle_cv_tips(self) -> str:
        """Provide CV writing tips"""
        
        return """📝 **Professional CV Tips for African Market:**

**Format & Structure:**
✅ Keep to 2 pages maximum
✅ Use professional fonts (Arial, Calibri)
✅ Save as PDF
✅ Include LinkedIn and GitHub links

**Must-Have Sections:**
1. **Professional Summary** (3-4 lines, keyword-rich)
2. **Technical Skills** (Categorized: Languages, Tools, Soft Skills)
3. **Work Experience** (STAR format - Situation, Task, Action, Result)
4. **Projects** (Live links if possible)
5. **Education & Certifications**
6. **Languages & Interests**

**Avoid:**
❌ Photos (may lead to bias)
❌ Personal details (age, marital status)
❌ Unnecessary formatting
❌ Spelling errors

**African Market Tips:**
• Highlight remote work experience
• Include local project examples
• Mention community involvement
• Show language skills (English, French)

**Quick Wins:**
• Use action verbs (Led, Developed, Managed)
• Quantify achievements (Increased by 30%)
• Tailor for each application
• Get feedback from mentors

Want me to review your CV? Upload it and I'll provide specific feedback! 📄"""
    
    def _handle_portfolio_advice(self) -> str:
        """Provide portfolio building advice"""
        
        return """💼 **Building an Impressive Portfolio:**

**Platforms to Use:**
• GitHub (Code repository)
• Personal website (Name.com, Netlify)
• LinkedIn (Projects section)
• Medium/Blog (Write about your work)

**What to Include:**
✅ 3-5 complete projects
✅ Live demos (Vercel/Netlify)
✅ Clean README files
✅ Code documentation
✅ Project screenshots/videos

**Project Ideas for Africa:**
1. **E-commerce platform** for local market
2. **Job portal** for Ghanaian companies
3. **Educational app** for students
4. **Healthcare booking system**
5. **Agricultural marketplace**

**Standout Features:**
• Real users/usage data
• Testimonials
• Case studies
• Performance metrics
• Mobile-responsive design

**Pro Tips:**
• Start with 1 solid project
• Deploy everything (no local-only)
• Get code reviews from seniors
• Contribute to open source

Need project ideas based on your skills? Share what you know! 🚀"""
    
    def _handle_networking_tips(self) -> str:
        """Provide networking advice"""
        
        return """🤝 **Networking Strategies for African Tech:**

**Online Platforms:**
• LinkedIn (Optimize profile, post weekly)
• Twitter/X (Follow industry leaders)
• GitHub (Contribute to repos)
• Slack/Discord communities

**Local Communities:**
• Google Developer Groups (GDG)
• Facebook Developer Circles
• Women in Tech chapters
• University alumni groups

**Events to Attend:**
• Tech conferences (Africa Tech Summit)
• Hackathons (Major League Hacking)
• Meetups (Find on Meetup.com)
• Webinars (Free learning)

**Networking Tips:**
✅ Send personalized connection requests
✅ Engage with posts (comment meaningfully)
✅ Share your work and learnings
✅ Ask for informational interviews
✅ Follow up after conversations

**Cold Outreach Template:**
"Hi [Name], I admire your work at [Company]. I'm a [Role] interested in [Field]. Would you have 15 mins for a quick chat about [Specific Topic]?"

**Build Your Brand:**
• Write on LinkedIn/Medium
• Speak at local events
• Mentor junior developers
• Start a study group

Remember: Quality > Quantity. Build genuine relationships! 🤝"""
    
    def _handle_job_search_tips(self) -> str:
        """Provide job search advice"""
        
        return """🔍 **Effective Job Search Strategy in Africa:**

**Where to Find Jobs:**
• Jobberman Ghana/Nigeria
• LinkedIn Jobs (Best for tech)
• Indeed Africa
• Brighter Monday (East Africa)
• Company career pages
• Remote Africa (RemoteOK, We Work Remotely)

**Application Strategy:**
📊 **Apply to 15-20 jobs/week**
• Customize CV for each
• Write tailored cover letters
• Track applications in spreadsheet
• Follow up after 1 week

**When to Apply:**
• Best days: Tuesday-Thursday
• Best time: 9-11 AM
• Avoid weekends and holidays
• Apply within 24 hours of posting

**Before Applying:**
✅ Research company thoroughly
✅ Network with employees
✅ Prepare portfolio samples
✅ Practice interview questions

**Red Flags to Avoid:**
❌ Unpaid "internships" with no learning
❌ Pyramid schemes
❌ Jobs requiring payment to apply
❌ Vague job descriptions

**Negotiation Tips:**
• Know your worth (research salaries)
• Get multiple offers if possible
• Consider total compensation (benefits, learning)
• Be professional but firm

Want me to review your job search strategy? 🎯"""
    
    def _handle_remote_work(self) -> str:
        """Provide remote work advice"""
        
        return """🏠 **Remote Work Success Guide:**

**Setup Your Workspace:**
✅ Dedicated desk/area
✅ Good lighting
✅ Ergonomic chair
✅ Noise-cancelling headphones
✅ Reliable internet (backup plan)

**Tools You Need:**
• Zoom/Google Meet (Video calls)
• Slack/Teams (Communication)
• Trello/Asana (Task management)
• Google Drive (Collaboration)
• Clockify (Time tracking)

**Remote Work Best Practices:**
📅 Maintain regular hours
🎥 Always use video for meetings
📝 Over-communicate clearly
⏰ Respect time zones
💪 Take real breaks

**Finding Remote Jobs:**
• We Work Remotely
• Remote OK
• AngelList (Startups)
• LinkedIn (Filter: Remote)
• FlexJobs (Curated)

**Stay Productive:**
• Get dressed for work
• Use Pomodoro technique
• Set daily/weekly goals
• Avoid social media during work
• End day with a routine

**Build Connections:**
• Join remote work communities
• Schedule virtual coffee chats
• Participate in team building
• Share wins and challenges

**Challenges & Solutions:**
• Loneliness → Join co-working spaces
• Distractions → Create boundaries
• Burnout → Strict work hours
• Communication → Over-communicate

Remote work can boost your career! Ready to find your first remote role? 🌍"""
    
    def _handle_soft_skills(self) -> str:
        """Provide soft skills advice"""
        
        return """⭐ **Essential Soft Skills for Career Growth:**

**Most Valued Soft Skills:**
1. **Communication** (Clear, concise, active listening)
2. **Problem-Solving** (Analytical, creative thinking)
3. **Teamwork** (Collaboration, conflict resolution)
4. **Adaptability** (Learn fast, embrace change)
5. **Leadership** (Mentor, take initiative)
6. **Time Management** (Prioritize, meet deadlines)
7. **Emotional Intelligence** (Self-awareness, empathy)

**How to Develop Them:**
📚 **Communication:**
• Join Toastmasters
• Practice presentations
• Write daily on LinkedIn
• Seek feedback

🎯 **Problem-Solving:**
• Solve puzzles daily
• Take on challenging tasks
• Learn root cause analysis
• Participate in hackathons

🤝 **Teamwork:**
• Volunteer for group projects
• Practice active listening
• Give constructive feedback
• Celebrate team wins

🔄 **Adaptability:**
• Learn new tools monthly
• Accept stretch assignments
• Embrace feedback
• Stay curious

**Showcase in Interviews:**
• STAR method examples
• Quantify achievements
• Share specific stories
• Demonstrate self-awareness

**Fast-Track Tips:**
• Take online courses (Coursera: "Learning How to Learn")
• Get a mentor
• Record yourself speaking
• Ask for 360-degree feedback

Soft skills + Technical skills = Unstoppable career! 💪"""
    
    def _handle_tech_trends(self) -> str:
        """Provide technology trends"""
        
        return """📊 **Top Tech Trends in Africa (2026):**

**Hottest Skills:**
1. **Artificial Intelligence/Machine Learning** (+45% growth)
   • Natural Language Processing
   • Computer Vision
   • Generative AI

2. **Cloud Computing** (+35% growth)
   • AWS, Azure, GCP
   • Serverless architecture
   • Cloud security

3. **Cybersecurity** (+30% growth)
   • Fintech security
   • Data privacy
   • Threat detection

4. **Data Science** (+28% growth)
   • Big Data analytics
   • Business intelligence
   • Data engineering

5. **Blockchain/Web3** (+25% growth)
   • Cryptocurrency
   • Smart contracts
   • DeFi applications

**Emerging Roles:**
• AI/ML Engineer (GHS 8k-15k)
• Cloud Architect (GHS 10k-18k)
• Security Analyst (GHS 6k-12k)
• Data Engineer (GHS 7k-14k)

**Industries Growing Fast:**
💳 **Fintech** (Mobile money, payments)
🏥 **HealthTech** (Telemedicine, records)
📚 **EdTech** (Online learning)
🛒 **E-commerce** (Logistics, payments)
🌾 **AgriTech** (Farmer solutions)

**Learning Resources:**
• Coursera Specializations
• AWS Training
• Google Digital Skills
• Local bootcamps (MEST, ALX)

**Future Predictions:**
• Remote work becomes standard
• AI tools boost productivity
• Green tech emerges
• Cross-border collaboration grows

Which trend excites you most? I can provide learning resources! 🚀"""
    
    def _handle_salary_negotiation(self) -> str:
        """Provide salary negotiation tips"""
        
        return """💰 **Salary Negotiation Masterclass:**

**Before Negotiation (Research Phase):**
✅ Know market rates (Glassdoor, LinkedIn)
✅ Understand your worth (skills, experience)
✅ Calculate minimum acceptable offer
✅ Prepare your case with evidence
✅ Practice with a friend

**The Negotiation Script:**

**When They Ask "What's your salary expectation?":**
*"Based on my skills and market research, I'm looking for GHS [X] - [Y]. However, I'm open to discussing total compensation including benefits and growth opportunities."*

**If Offer is Too Low:**
*"Thank you for the offer! I'm excited about the role. Based on my experience in [skills] and market rates, I was expecting GHS [higher amount]. Could we explore meeting somewhere in the middle?"*

**What to Negotiate (Beyond Salary):**
• Signing bonus
• Annual bonus potential
• Stock options/equity
• Vacation days
• Remote work flexibility
• Professional development budget
• Flexible hours
• Home office stipend

**Power Phrases:**
💪 "Based on my track record of [achievement]..."
💪 "Market data for this role shows..."
💪 "Given my experience with [skill]..."
💪 "I'm very interested, but the offer is below market..."

**Red Flags (Walk Away):**
• Company refuses to negotiate
• Salary below minimum needs
• Unclear growth path
• Toxic culture signs

**After Negotiation:**
• Get everything in writing
• Thank them professionally
• Consider the full package
• Trust your instincts

**Pro Tips:**
• Never give first number if possible
• Always negotiate (90% expect it)
• Be professional, not aggressive
• Have a BATNA (Best Alternative)

Want to role-play a negotiation? I can help you practice! 💪"""
    
    def _handle_work_life_balance(self) -> str:
        """Provide work-life balance advice"""
        
        return """⚖️ **Work-Life Balance for Tech Professionals:**

**Warning Signs of Burnout:**
• Constantly tired
• Lack of motivation
• Reduced performance
• Irritability
• Physical symptoms (headaches)

**Prevention Strategies:**

📅 **Set Boundaries:**
• Define work hours strictly
• Turn off notifications after hours
• Use separate devices if possible
• Learn to say "no" politely

⏰ **Time Management:**
• Use Pomodoro technique (25 min work, 5 min break)
• Take real lunch breaks (away from screen)
• Schedule focused work blocks
• Prioritize important tasks

💪 **Health Habits:**
• Exercise 30 mins daily
• Sleep 7-8 hours
• Stay hydrated
• Take vacation days

🧠 **Mental Health:**
• Practice mindfulness/meditation
• Talk to someone about stress
• Seek therapy if needed
• Join support groups

**Daily Routine Example:**
08:00 - Wake up, exercise
09:00 - Start work
12:00 - Lunch break (no screens)
13:00 - Resume work
17:00 - End work (strictly!)
18:00 - Hobbies/family time
22:00 - Wind down, no screens
23:00 - Sleep

**Remote Work Balance:**
• Create physical separation (different room)
• Get dressed for "work"
• Take walking breaks
• Have social connections

**Company Red Flags:**
• Expecting 24/7 availability
• No vacation policy
• Constant overtime
• Guilt for taking breaks

**Remember:**
• You're replaceable at work, not at home
• Rest increases productivity
• Happiness matters
• It's okay to disconnect

Need specific strategies for your situation? Let's talk! 🌟"""
    
    def _handle_general_question(self, question: str) -> str:
        """Handle general career questions"""
        
        return f"""🤖 **Great question! Here's what I can help with:**

**Career Paths:**
• "What skills should I learn for [role]?"
• "How do I become a [job title]?"
• "What's the career progression for [field]?"

**Job Search:**
• "Where can I find remote jobs?"
• "How to prepare for interviews?"
• "What should be in my portfolio?"

**Skills & Learning:**
• "Which certifications are valuable?"
• "How long to learn [skill]?"
• "Best resources for [topic]?"

**Salary & Negotiation:**
• "What's the salary for [role]?"
• "How to negotiate higher pay?"
• "Freelance vs full-time?"

**African Market Specific:**
• "Tech trends in Ghana/Nigeria"
• "Local companies hiring"
• "Remote work opportunities"

**Your question: "{question}"**

Could you be more specific about what you'd like to know? For example:
• "What skills do I need for a Data Science role in Accra?"
• "How much do Python developers earn in Ghana?"
• "What certifications should I get for cloud computing?"

I'm here to help with detailed, personalized advice! 🎯"""
    
    def _get_suggested_followups(self, intent: str) -> List[str]:
        """Get suggested follow-up questions based on intent"""
        
        followups = {
            'skill_recommendation': [
                "How long will it take to learn Python?",
                "What's the best way to practice coding?",
                "Can you create a weekly learning plan?"
            ],
            'interview_prep': [
                "Can you give me sample interview questions?",
                "How should I answer 'Tell me about yourself'?",
                "What questions should I ask the interviewer?"
            ],
            'salary_info': [
                "How can I negotiate a higher salary?",
                "What benefits should I ask for?",
                "Salary comparison between Accra and Lagos?"
            ],
            'certification': [
                "Which certification is best for beginners?",
                "How to prepare for AWS exam?",
                "Are free certifications worth it?"
            ],
            'general': [
                "What skills are in demand now?",
                "How to find a mentor?",
                "Tips for remote interviews?"
            ]
        }
        
        return followups.get(intent, followups['general'])

    def _extract_role(self, question: str) -> str:
        """Extract job role from question"""
        
        roles = ['developer', 'engineer', 'scientist', 'analyst', 'architect', 
                 'manager', 'consultant', 'designer', 'tester', 'admin']
        
        for role in roles:
            if role in question.lower():
                return role.capitalize()
        return "Tech Professional"