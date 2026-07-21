import json
import re
from typing import Dict, List, Tuple
from app.utils.course_api import CourseAPI

class SkillAnalyzer:
    """Analyzes user skills against market demands - ALL SECTORS"""
    
    # Initialize course API
    course_api = CourseAPI()
    
    # ========== MARKET DEMANDS BY SECTOR ==========
    MARKET_DEMANDS_BY_SECTOR = {
        'technology': {
            'Python': 92, 'Java': 85, 'JavaScript': 80, 'SQL': 78,
            'Machine Learning': 88, 'Cloud Computing': 85, 'DevOps': 82,
            'Data Science': 84, 'Cybersecurity': 80, 'AI': 86,
            'React': 75, 'Django': 70, 'Flask': 68, 'Docker': 72,
            'Kubernetes': 70, 'AWS': 82, 'Git': 85, 'Linux': 78
        },
        'healthcare': {
            'Patient Care': 95, 'Medical Diagnosis': 90, 'Pharmacy': 85,
            'Nursing Care': 88, 'Public Health': 80, 'Clinical Research': 75,
            'Emergency Medicine': 82, 'Surgery': 85, 'Radiology': 78,
            'Pediatrics': 80, 'Obstetrics': 78, 'Cardiology': 82,
            'Neurology': 76, 'Oncology': 78, 'Psychiatry': 72
        },
        'law': {
            'Legal Research': 85, 'Contract Law': 82, 'Corporate Law': 80,
            'Compliance': 78, 'Litigation': 75, 'Intellectual Property': 72,
            'Human Rights Law': 70, 'International Law': 68,
            'Family Law': 72, 'Criminal Law': 70, 'Tax Law': 65
        },
        'finance': {
            'Financial Analysis': 90, 'Accounting': 85, 'Risk Management': 82,
            'Investment Banking': 78, 'Auditing': 80, 'Taxation': 75,
            'Fintech': 88, 'Financial Modeling': 80, 'Corporate Finance': 78,
            'Portfolio Management': 76, 'Wealth Management': 72
        },
        'education': {
            'Teaching': 90, 'Curriculum Development': 85, 'Educational Admin': 80,
            'Research': 78, 'EdTech': 82, 'Student Assessment': 75,
            'Educational Leadership': 72, 'Special Education': 78,
            'Early Childhood Education': 80, 'Higher Education': 76
        },
        'agriculture': {
            'Crop Production': 85, 'Agribusiness': 82, 'Agricultural Tech': 80,
            'Supply Chain': 78, 'Irrigation': 75, 'Soil Science': 72,
            'Livestock Management': 78, 'Fisheries': 70, 'Agronomy': 80,
            'Food Processing': 76, 'Farm Management': 74
        },
        'business': {
            'Business Administration': 85, 'Human Resources': 82,
            'Marketing': 80, 'Sales': 78, 'Operations Management': 82,
            'Project Management': 85, 'Strategic Planning': 80,
            'Digital Marketing': 82, 'Brand Management': 76, 'Customer Relations': 78
        },
        'creative': {
            'Graphic Design': 82, 'Video Production': 78, 'Animation': 75,
            'Music Production': 70, 'Content Creation': 80, 'Photography': 65,
            'UI/UX Design': 80, 'Motion Graphics': 72, 'Art Direction': 76
        },
        'trades': {
            'Carpentry': 78, 'Plumbing': 80, 'Electrical Work': 82,
            'Welding': 75, 'Automotive Repair': 78, 'Construction': 85,
            'Masonry': 76, 'HVAC': 80, 'Maintenance': 78
        },
        'social': {
            'Social Work': 85, 'Community Development': 80, 'Counseling': 78,
            'Project Management': 75, 'Grant Writing': 70, 'Advocacy': 76,
            'Mental Health Counseling': 82, 'Child Protection': 78
        },
        'engineering': {
            'Civil Engineering': 85, 'Structural Engineering': 82,
            'Mechanical Engineering': 80, 'Electrical Engineering': 82,
            'Construction Management': 80, 'Environmental Engineering': 75,
            'Project Engineering': 78, 'CAD': 80, 'AutoCAD': 78
        }
    }
    
    # ========== COURSE RECOMMENDATIONS ==========
    COURSE_RECOMMENDATIONS = {
        # Tech Courses
        'Python': {
            'coursera': 'Python for Everybody',
            'udemy': 'Complete Python Bootcamp',
            'duration': '4 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Machine Learning': {
            'coursera': 'Machine Learning Specialization',
            'udemy': 'Machine Learning A-Z',
            'duration': '11 weeks',
            'effort': '7 hrs/week',
            'certification': True
        },
        'Cloud Computing': {
            'aws': 'AWS Cloud Practitioner',
            'coursera': 'Cloud Computing Specialization',
            'duration': '6 weeks',
            'effort': '6 hrs/week',
            'certification': True
        },
        'Data Analysis': {
            'coursera': 'Data Analysis with Python',
            'udemy': 'Data Analysis Bootcamp',
            'duration': '5 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'SQL': {
            'coursera': 'SQL for Data Science',
            'udemy': 'The Complete SQL Bootcamp',
            'duration': '3 weeks',
            'effort': '3 hrs/week',
            'certification': True
        },
        'React': {
            'coursera': 'Frontend Development with React',
            'udemy': 'React - The Complete Guide',
            'duration': '6 weeks',
            'effort': '6 hrs/week',
            'certification': True
        },
        'AWS': {
            'aws': 'AWS Certified Solutions Architect',
            'udemy': 'AWS Certified Developer',
            'duration': '8 weeks',
            'effort': '8 hrs/week',
            'certification': True
        },
        'Docker': {
            'udemy': 'Docker Mastery',
            'coursera': 'Docker for Beginners',
            'duration': '2 weeks',
            'effort': '3 hrs/week',
            'certification': False
        },
        # Healthcare Courses
        'Patient Care': {
            'coursera': 'Patient Care Fundamentals',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Medical Diagnosis': {
            'coursera': 'Clinical Diagnosis Skills',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Nursing Care': {
            'coursera': 'Nursing Practice Fundamentals',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Pharmacy': {
            'coursera': 'Pharmacy Practice',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Public Health': {
            'coursera': 'Public Health Foundations',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        # Law Courses
        'Legal Research': {
            'coursera': 'Legal Research Methods',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Contract Law': {
            'coursera': 'Contract Law Fundamentals',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Corporate Law': {
            'coursera': 'Corporate Law Essentials',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        # Finance Courses
        'Financial Analysis': {
            'coursera': 'Financial Analysis Skills',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Accounting': {
            'coursera': 'Accounting Fundamentals',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Risk Management': {
            'coursera': 'Risk Management Principles',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        # Education Courses
        'Teaching': {
            'coursera': 'Teaching Methods and Strategies',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Curriculum Development': {
            'coursera': 'Curriculum Design and Development',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        # Agriculture Courses
        'Crop Production': {
            'coursera': 'Crop Production Techniques',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Agribusiness': {
            'coursera': 'Agribusiness Management',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        # Business Courses
        'Business Administration': {
            'coursera': 'Business Administration Fundamentals',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        'Project Management': {
            'coursera': 'Project Management Professional',
            'udemy': 'PMP Exam Prep',
            'duration': '8 weeks',
            'effort': '6 hrs/week',
            'certification': True
        },
        'Marketing': {
            'coursera': 'Digital Marketing Strategy',
            'udemy': 'Digital Marketing Masterclass',
            'duration': '6 weeks',
            'effort': '4 hrs/week',
            'certification': True
        },
        # Trades Courses
        'Carpentry': {
            'udemy': 'Carpentry and Woodworking',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': False
        },
        'Plumbing': {
            'udemy': 'Plumbing Basics',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': False
        },
        'Electrical Work': {
            'udemy': 'Electrical Work Fundamentals',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': False
        },
        # Engineering Courses
        'Civil Engineering': {
            'coursera': 'Civil Engineering Principles',
            'duration': '10 weeks',
            'effort': '6 hrs/week',
            'certification': True
        },
        'Construction': {
            'coursera': 'Construction Management',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        # Social Services Courses
        'Social Work': {
            'coursera': 'Social Work Practice',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        },
        'Counseling': {
            'coursera': 'Counseling Fundamentals',
            'duration': '8 weeks',
            'effort': '5 hrs/week',
            'certification': True
        }
    }
    
    # ========== SECTOR KEYWORDS ==========
    SECTOR_KEYWORDS = {
        'technology': ['python', 'java', 'javascript', 'react', 'django', 'flask', 'aws', 'docker', 'kubernetes', 'tensorflow', 'pytorch', 'sql', 'mongodb', 'git', 'linux', 'cloud', 'devops', 'machine learning', 'data science', 'ai', 'cybersecurity', 'programming', 'software', 'developer', 'coding', 'full stack', 'frontend', 'backend', 'api', 'microservices'],
        'healthcare': ['patient care', 'medical diagnosis', 'surgery', 'nursing', 'pharmacy', 'public health', 'emergency medicine', 'radiology', 'clinical', 'hospital', 'doctor', 'nurse', 'pharmacist', 'care', 'medicine', 'health', 'cardiology', 'pediatrics', 'obstetrics', 'gynecology', 'orthopedics', 'neurology', 'oncology', 'psychiatry'],
        'law': ['legal research', 'contract law', 'corporate law', 'compliance', 'litigation', 'intellectual property', 'human rights', 'lawyer', 'attorney', 'legal', 'court', 'bar', 'advocate', 'criminal law', 'family law', 'property law', 'tax law'],
        'finance': ['financial analysis', 'accounting', 'risk management', 'investment', 'banking', 'auditing', 'taxation', 'fintech', 'financial modeling', 'accountant', 'finance', 'bank', 'investment', 'audit', 'corporate finance', 'portfolio management', 'wealth management'],
        'education': ['teaching', 'curriculum development', 'education', 'teacher', 'professor', 'school', 'classroom', 'lesson plan', 'educational', 'academic', 'student assessment', 'educational leadership', 'special education', 'edtech'],
        'agriculture': ['crop production', 'livestock', 'agribusiness', 'agriculture', 'farming', 'irrigation', 'soil science', 'agritech', 'farm', 'agronomy', 'animal science', 'fisheries', 'aquaculture', 'food processing', 'farm management'],
        'business': ['business administration', 'human resources', 'marketing', 'sales', 'operations', 'project management', 'management', 'hr', 'recruitment', 'business', 'strategy', 'brand management', 'customer relations', 'digital marketing'],
        'creative': ['graphic design', 'animation', 'video production', 'music', 'content creation', 'art', 'design', 'creative', 'photography', 'illustration', 'multimedia', 'motion graphics', 'ui/ux', 'art direction'],
        'trades': ['carpentry', 'plumbing', 'electrical', 'welding', 'automotive', 'construction', 'masonry', 'trades', 'mechanic', 'electrician', 'plumber', 'carpenter', 'hvac', 'maintenance', 'repair'],
        'social': ['social work', 'community development', 'counseling', 'nonprofit', 'ngo', 'social services', 'advocacy', 'social worker', 'counselor', 'mental health', 'child protection', 'human rights'],
        'engineering': ['civil engineering', 'structural engineering', 'mechanical engineering', 'electrical engineering', 'construction', 'cad', 'bim', 'site supervision', 'quantity surveying', 'project engineering', 'environmental engineering', 'geotechnical engineering']
    }
    
    @classmethod
    def detect_sector(cls, user_skills: List[str]) -> str:
        """Detect which sector the user belongs to based on their skills"""
        if not user_skills:
            return 'general'
        
        user_skills_lower = [s.lower() for s in user_skills]
        sector_scores = {}
        for sector, keywords in cls.SECTOR_KEYWORDS.items():
            score = 0
            for skill in user_skills_lower:
                for keyword in keywords:
                    if keyword in skill or skill in keyword:
                        score += 1
            sector_scores[sector] = score
        
        if sector_scores:
            best_sector = max(sector_scores, key=sector_scores.get)
            if sector_scores[best_sector] > 0:
                return best_sector
        
        return 'general'
    
    @classmethod
    def calculate_employability_score(cls, user_skills: List[str], experience_years: int = 0, market_demands: Dict = None) -> Dict:
        """Calculate employability score based on skills and experience"""
        if not user_skills:
            return {'score': 0, 'level': 'Beginner', 'color': 'red'}
        
        if market_demands is None:
            market_demands = cls.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
        
        total_score = 0
        max_possible = 0
        skill_contributions = []
        
        for skill, demand in market_demands.items():
            max_possible += demand
            has_skill = any(skill.lower() in user_skill.lower() or user_skill.lower() in skill.lower() 
                           for user_skill in user_skills)
            
            if has_skill:
                total_score += demand
                skill_contributions.append({
                    'skill': skill,
                    'score': demand,
                    'status': 'matched',
                    'demand': demand
                })
            else:
                skill_contributions.append({
                    'skill': skill,
                    'score': 0,
                    'status': 'missing',
                    'demand': demand
                })
        
        if max_possible > 0:
            base_score = (total_score / max_possible) * 100
        else:
            base_score = 0
        
        experience_bonus = min(experience_years * 2, 15)
        final_score = min(base_score + experience_bonus, 100)
        
        if final_score >= 80:
            level = 'Expert'
            color = 'green'
        elif final_score >= 60:
            level = 'Advanced'
            color = 'teal'
        elif final_score >= 40:
            level = 'Intermediate'
            color = 'yellow'
        elif final_score >= 20:
            level = 'Beginner'
            color = 'orange'
        else:
            level = 'Novice'
            color = 'red'
        
        return {
            'score': round(final_score),
            'level': level,
            'color': color,
            'base_score': round(base_score),
            'experience_bonus': experience_bonus,
            'skill_contributions': skill_contributions,
            'total_skills_matched': len([s for s in skill_contributions if s['status'] == 'matched']),
            'total_skills_missing': len([s for s in skill_contributions if s['status'] == 'missing'])
        }
    
    @classmethod
    def analyze_gaps(cls, user_skills: List[str], market_demands: Dict = None) -> List[Dict]:
        """Analyze skill gaps and prioritize missing skills"""
        gaps = []
        
        if market_demands is None:
            market_demands = cls.MARKET_DEMANDS_BY_SECTOR.get('technology', {})
        
        if not user_skills:
            for skill, demand in market_demands.items():
                gaps.append({
                    'skill': skill,
                    'demand': demand,
                    'priority': 'Critical' if demand >= 80 else 'High' if demand >= 70 else 'Medium' if demand >= 60 else 'Low',
                    'salary_range': [0, 0],
                    'growth': '+0%',
                    'course': cls.COURSE_RECOMMENDATIONS.get(skill, {
                        'coursera': f'{skill} Fundamentals',
                        'duration': '4 weeks',
                        'effort': '4 hrs/week',
                        'certification': False
                    })
                })
            return gaps
        
        user_skills_lower = [s.lower() for s in user_skills]
        
        for skill, demand in market_demands.items():
            has_skill = any(skill.lower() in user_skill or user_skill in skill.lower() 
                          for user_skill in user_skills_lower)
            
            if not has_skill:
                if demand >= 80:
                    priority = 'Critical'
                elif demand >= 70:
                    priority = 'High'
                elif demand >= 60:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                gaps.append({
                    'skill': skill,
                    'demand': demand,
                    'priority': priority,
                    'salary_range': [0, 0],
                    'growth': '+0%',
                    'course': cls.COURSE_RECOMMENDATIONS.get(skill, {
                        'coursera': f'{skill} Fundamentals',
                        'duration': '4 weeks',
                        'effort': '4 hrs/week',
                        'certification': False
                    })
                })
        
        gaps.sort(key=lambda x: x['demand'], reverse=True)
        return gaps
    
    @classmethod
    def generate_learning_roadmap(cls, gaps: List[Dict]) -> Dict:
        """Generate personalized learning roadmap with real courses"""
        roadmap = {
            'immediate': [],
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }
        
        for idx, gap in enumerate(gaps[:10]):
            priority = gap['priority']
            skill = gap['skill']
            
            courses = cls.course_api.search_courses(skill, limit=2)
            certifications = cls.course_api.get_certification_recommendations(skill)
            
            if not courses:
                course_data = cls.COURSE_RECOMMENDATIONS.get(skill, {})
                courses = [{
                    'title': course_data.get('coursera', f'{skill} Fundamentals'),
                    'provider': 'Coursera',
                    'url': '#',
                    'description': f'Learn {skill} on Coursera',
                    'duration': course_data.get('duration', '4 weeks'),
                    'effort': course_data.get('effort', '4 hrs/week'),
                    'certificate': course_data.get('certification', False),
                    'platform': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400'
                }]
            
            item = {
                'id': idx + 1,
                'skill': skill,
                'priority': priority,
                'courses': courses,
                'certifications': certifications[:2] if certifications else []
            }
            
            if priority == 'Critical':
                roadmap['immediate'].append(item)
            elif priority == 'High':
                roadmap['short_term'].append(item)
            elif priority == 'Medium':
                roadmap['medium_term'].append(item)
            else:
                roadmap['long_term'].append(item)
        
        return roadmap
    
    @classmethod
    def get_job_recommendations(cls, user_skills: List[str]) -> List[Dict]:
        """Get job recommendations based on user skills"""
        
        job_roles = {
            # Tech Jobs
            'Python Developer': {
                'required_skills': ['Python', 'SQL', 'Git', 'Django'],
                'salary_range': [4500, 8000],
                'growth': '+25%'
            },
            'Data Scientist': {
                'required_skills': ['Python', 'Machine Learning', 'SQL', 'Data Analysis'],
                'salary_range': [6000, 12000],
                'growth': '+40%'
            },
            'Cloud Engineer': {
                'required_skills': ['Cloud Computing', 'AWS', 'Docker', 'Python'],
                'salary_range': [7000, 15000],
                'growth': '+35%'
            },
            'Full Stack Developer': {
                'required_skills': ['Python', 'JavaScript', 'React', 'SQL'],
                'salary_range': [5000, 10000],
                'growth': '+30%'
            },
            'DevOps Engineer': {
                'required_skills': ['AWS', 'Docker', 'Git', 'Cloud Computing'],
                'salary_range': [6500, 14000],
                'growth': '+32%'
            },
            'AI Engineer': {
                'required_skills': ['Machine Learning', 'Python', 'TensorFlow', 'Data Analysis'],
                'salary_range': [7000, 15000],
                'growth': '+45%'
            },
            # Healthcare Jobs
            'Medical Doctor': {
                'required_skills': ['Medical Diagnosis', 'Patient Care', 'Emergency Medicine', 'Surgery'],
                'salary_range': [8000, 20000],
                'growth': '+20%'
            },
            'Registered Nurse': {
                'required_skills': ['Nursing Care', 'Patient Care', 'Vital Signs Monitoring', 'Patient Education'],
                'salary_range': [4000, 8000],
                'growth': '+25%'
            },
            'Pharmacist': {
                'required_skills': ['Pharmacy', 'Pharmacology', 'Drug Dispensing', 'Medication Therapy Management'],
                'salary_range': [5000, 10000],
                'growth': '+20%'
            },
            'Public Health Specialist': {
                'required_skills': ['Public Health', 'Epidemiology', 'Health Promotion', 'Community Health'],
                'salary_range': [4500, 8500],
                'growth': '+25%'
            },
            # Law Jobs
            'Corporate Lawyer': {
                'required_skills': ['Corporate Law', 'Contract Law', 'Compliance', 'Legal Research'],
                'salary_range': [7000, 15000],
                'growth': '+20%'
            },
            'Legal Consultant': {
                'required_skills': ['Legal Research', 'Legal Writing', 'Contract Law', 'Negotiation'],
                'salary_range': [6000, 12000],
                'growth': '+18%'
            },
            # Finance Jobs
            'Financial Analyst': {
                'required_skills': ['Financial Analysis', 'Financial Modeling', 'Accounting', 'Risk Management'],
                'salary_range': [5500, 11000],
                'growth': '+25%'
            },
            'Accountant': {
                'required_skills': ['Accounting', 'Auditing', 'Taxation', 'Financial Reporting'],
                'salary_range': [4500, 8500],
                'growth': '+20%'
            },
            'Investment Banker': {
                'required_skills': ['Investment Banking', 'Valuation', 'Due Diligence', 'Financial Modeling'],
                'salary_range': [8000, 18000],
                'growth': '+30%'
            },
            # Education Jobs
            'Teacher': {
                'required_skills': ['Teaching', 'Curriculum Development', 'Lesson Planning', 'Student Assessment'],
                'salary_range': [3500, 7000],
                'growth': '+15%'
            },
            'School Administrator': {
                'required_skills': ['Educational Administration', 'Educational Leadership', 'School Leadership', 'Policy'],
                'salary_range': [5000, 10000],
                'growth': '+18%'
            },
            # Agriculture Jobs
            'Agronomist': {
                'required_skills': ['Agronomy', 'Crop Production', 'Soil Science', 'Irrigation'],
                'salary_range': [4000, 8000],
                'growth': '+22%'
            },
            'Agribusiness Manager': {
                'required_skills': ['Agribusiness', 'Supply Chain', 'Agricultural Economics', 'Farm Management'],
                'salary_range': [5000, 10000],
                'growth': '+20%'
            },
            # Business Jobs
            'Business Manager': {
                'required_skills': ['Business Administration', 'Operations Management', 'Strategic Planning', 'Leadership'],
                'salary_range': [5000, 10000],
                'growth': '+20%'
            },
            'HR Manager': {
                'required_skills': ['Human Resources', 'Talent Management', 'Recruitment', 'Employee Relations'],
                'salary_range': [4500, 8500],
                'growth': '+18%'
            },
            'Marketing Manager': {
                'required_skills': ['Marketing', 'Digital Marketing', 'Brand Management', 'Market Research'],
                'salary_range': [5000, 10000],
                'growth': '+22%'
            },
            # Trades Jobs
            'Construction Manager': {
                'required_skills': ['Construction', 'Construction Management', 'Site Supervision', 'Safety'],
                'salary_range': [5000, 10000],
                'growth': '+25%'
            },
            'Master Electrician': {
                'required_skills': ['Electrical Work', 'Wiring', 'Electrical Systems', 'Safety'],
                'salary_range': [4000, 8000],
                'growth': '+20%'
            },
            # Engineering Jobs
            'Civil Engineer': {
                'required_skills': ['Civil Engineering', 'Structural Engineering', 'Construction', 'CAD'],
                'salary_range': [5000, 10000],
                'growth': '+22%'
            },
            'Project Engineer': {
                'required_skills': ['Project Engineering', 'Project Management', 'Construction', 'Quality Assurance'],
                'salary_range': [5500, 11000],
                'growth': '+25%'
            },
            # Social Services Jobs
            'Social Worker': {
                'required_skills': ['Social Work', 'Case Management', 'Community Development', 'Advocacy'],
                'salary_range': [3500, 7000],
                'growth': '+20%'
            },
            'Counselor': {
                'required_skills': ['Counseling', 'Mental Health Counseling', 'Crisis Intervention', 'Active Listening'],
                'salary_range': [4000, 8000],
                'growth': '+22%'
            }
        }
        
        recommendations = []
        
        for role, data in job_roles.items():
            required = set(data['required_skills'])
            user_skill_set = set([s.lower() for s in user_skills])
            
            matched = sum(1 for skill in required if any(skill.lower() in us or us in skill.lower() 
                          for us in user_skill_set))
            match_percentage = (matched / len(required)) * 100
            
            if match_percentage > 0:
                recommendations.append({
                    'role': role,
                    'match_percentage': round(match_percentage),
                    'required_skills': data['required_skills'],
                    'matched_skills': matched,
                    'total_required': len(required),
                    'salary_range': data['salary_range'],
                    'growth': data['growth']
                })
        
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return recommendations[:5]

@staticmethod
def extract_skills_from_text(text):
    """Extract skills from text using the existing skill extraction logic"""
    if not text:
        return []
    
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    # Use the parser's skill extraction
    result = parser.extract_skills(text)
    
    if result and isinstance(result, dict):
        all_skills = []
        for category, skills in result.items():
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.append(skills)
        return all_skills
    
    return []  
     
@staticmethod
def extract_skills_from_text(text):
    """Extract skills from text using hybrid parser"""
    if not text:
        return []
    
    from app.utils.hybrid_parser import HybridParser
    parser = HybridParser()
    
    result = parser.extract_skills(text)
    
    all_skills = []
    if result and isinstance(result, dict):
        for category, skills in result.items():
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.append(skills)
    
    return all_skills