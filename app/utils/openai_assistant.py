import os
import openai
from typing import Dict, List, Any
from flask import current_app

class OpenAIAssistant:
    """AI Assistant using OpenAI GPT"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            print("⚠️ OPENAI_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def get_response(self, question: str, user_skills: List[str] = None, experience: int = 0, sector: str = None) -> Dict:
        """Get AI response from OpenAI"""
        
        if not self.client:
            return {
                'response': self._get_fallback_response(question, user_skills, experience, sector),
                'intent': 'fallback',
                'sector': sector or 'general',
                'suggested_followups': self._get_fallback_followups()
            }
        
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt(user_skills, experience, sector)
            
            # Build user prompt
            user_prompt = self._build_user_prompt(question, user_skills, experience, sector)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using gpt-4o-mini for cost-effectiveness
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract response
            ai_response = response.choices[0].message.content
            
            # Generate follow-up suggestions
            followups = self._generate_followups(question, ai_response)
            
            return {
                'response': ai_response,
                'intent': self._detect_intent(question),
                'sector': sector or 'general',
                'suggested_followups': followups
            }
            
        except Exception as e:
            print(f"❌ OpenAI API Error: {e}")
            return {
                'response': self._get_fallback_response(question, user_skills, experience, sector),
                'intent': 'error',
                'sector': sector or 'general',
                'suggested_followups': self._get_fallback_followups()
            }
    
    def _build_system_prompt(self, user_skills: List[str], experience: int, sector: str) -> str:
        """Build the system prompt for OpenAI"""
        
        sector_context = {
            'technology': 'Tech/SWE careers, programming, data science, cloud computing, AI/ML, cybersecurity, DevOps.',
            'healthcare': 'Medical, nursing, pharmacy, public health, clinical careers in West Africa.',
            'law': 'Legal careers, corporate law, human rights, litigation, compliance in Ghana/West Africa.',
            'finance': 'Banking, accounting, investment, fintech, financial analysis in West Africa.',
            'education': 'Teaching, academic careers, curriculum development, EdTech.',
            'agriculture': 'Farming, agribusiness, AgriTech, agricultural economics.',
            'business': 'Management, HR, marketing, consulting, entrepreneurship.',
            'creative': 'Design, animation, video production, music, content creation.',
            'trades': 'Carpentry, plumbing, electrical, welding, construction.',
            'social': 'Social work, counseling, NGO work, community development.',
            'engineering': 'Civil, mechanical, electrical, structural engineering.'
        }
        
        sector_info = sector_context.get(sector, 'All career sectors in Ghana/West Africa')
        
        skills_info = ""
        if user_skills:
            skills_info = f"\nUser's existing skills: {', '.join(user_skills[:5])}"
        
        experience_info = f"\nUser's experience level: {experience} years"
        
        return f"""You are **FADTECH AI**, a career assistant focused on the African (specifically Ghana/West Africa) job market.

**Your Role:**
- Provide practical, actionable career advice
- Give specific salary ranges in GHS (Ghana Cedis)
- Suggest relevant skills, certifications, and courses
- Be encouraging and supportive
- Use emojis to make responses engaging

**Context:**
- Sector: {sector_info}
{skills_info}
{experience_info}

**Formatting Guidelines:**
- Use bullet points (•)
- Use bold for important info (text with **)
- Use emojis for visual appeal
- Keep responses concise but detailed
- Always include salary info when relevant

**Important:** Always be honest about your limitations. If you don't know something, say so and suggest how to find out.

**Tone:** Professional, encouraging, practical, African-centric. Be like a wise career mentor who understands the local job market."""
    
    def _build_user_prompt(self, question: str, user_skills: List[str], experience: int, sector: str) -> str:
        """Build the user prompt for OpenAI"""
        
        prompt = f"User asks: {question}"
        
        if user_skills:
            prompt += f"\n\nUser's skills: {', '.join(user_skills)}"
        
        if experience:
            prompt += f"\n\nUser's experience: {experience} years"
        
        if sector:
            prompt += f"\n\nSector: {sector}"
        
        prompt += "\n\nProvide practical, actionable career advice specific to the African job market, especially Ghana/West Africa."
        
        return prompt
    
    def _detect_intent(self, question: str) -> str:
        """Simple intent detection"""
        intents = {
            'skill_recommendation': ['learn', 'study', 'skill', 'what should i learn'],
            'salary_info': ['salary', 'pay', 'earn', 'compensation', 'how much'],
            'career_path': ['career', 'path', 'growth', 'promotion', 'advance'],
            'interview_prep': ['interview', 'prepare', 'technical interview'],
            'certification': ['certification', 'cert', 'certificate', 'exam'],
            'cv_tips': ['cv', 'resume', 'curriculum vitae'],
            'job_search': ['job', 'apply', 'hiring', 'search']
        }
        
        question_lower = question.lower()
        for intent, keywords in intents.items():
            if any(keyword in question_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def _generate_followups(self, question: str, response: str) -> List[str]:
        """Generate suggested follow-up questions"""
        
        followups = [
            "Can you tell me more about the skills I need?",
            "What's the average salary for this role?",
            "How can I prepare for interviews?",
            "What certifications would help me advance?",
            "Can you create a learning roadmap for me?"
        ]
        
        # Add sector-specific followups based on response
        if 'salary' in response.lower():
            followups.insert(0, "How can I negotiate a higher salary?")
        if 'certification' in response.lower():
            followups.insert(0, "Which certification is most recognized here?")
        if 'remote' in response.lower():
            followups.insert(0, "What remote work opportunities exist in this field?")
        
        return followups[:5]  # Return top 5
    
    def _get_fallback_response(self, question: str, user_skills: List[str], experience: int, sector: str) -> str:
        """Fallback response when OpenAI is not available"""
        return """🤖 **I'm your AI Career Assistant!**

I can help with:
• 📚 **Skills** - "What should I learn for [role]?"
• 💰 **Salaries** - "How much do [role] earn in Ghana?"
• 🎯 **Career Path** - "How to become a [role]?"
• 📝 **CV Tips** - "How to improve my CV?"
• 🏆 **Certifications** - "Which certs are valuable?"
• 💼 **Job Search** - "Where to find jobs?"
• 🤝 **Networking** - "How to build connections?"

**Your question:** "{question}"

💡 **Want better answers?** Get an OpenAI API key and add it to your `.env` file!

**Your question has been noted.** I'm here to help! 🚀"""
    
    def _get_fallback_followups(self) -> List[str]:
        """Fallback follow-up suggestions"""
        return [
            "What skills are in demand now?",
            "How to find a mentor?",
            "Tips for remote work?",
            "How to build a portfolio?"
        ]