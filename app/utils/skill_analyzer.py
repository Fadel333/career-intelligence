import json
import re
from typing import Dict, List, Tuple
from app.utils.course_api import CourseAPI

class SkillAnalyzer:
    """Analyzes user skills against market demands"""
    
    # Initialize course API
    course_api = CourseAPI()
    
    # Market demand database (in production, this would come from scraped data)
    MARKET_DEMANDS = {
        'Python': {'demand': 92, 'salary_range': [4500, 8000], 'growth': '+25%'},
        'Machine Learning': {'demand': 88, 'salary_range': [6000, 12000], 'growth': '+40%'},
        'Cloud Computing': {'demand': 85, 'salary_range': [7000, 15000], 'growth': '+35%'},
        'Data Analysis': {'demand': 82, 'salary_range': [5000, 10000], 'growth': '+20%'},
        'SQL': {'demand': 78, 'salary_range': [4000, 7000], 'growth': '+15%'},
        'JavaScript': {'demand': 75, 'salary_range': [4500, 8500], 'growth': '+18%'},
        'React': {'demand': 70, 'salary_range': [5000, 9000], 'growth': '+22%'},
        'AWS': {'demand': 80, 'salary_range': [6500, 14000], 'growth': '+30%'},
        'Docker': {'demand': 65, 'salary_range': [5500, 10000], 'growth': '+28%'},
        'TensorFlow': {'demand': 60, 'salary_range': [6000, 11000], 'growth': '+32%'},
        'Django': {'demand': 55, 'salary_range': [4500, 8000], 'growth': '+15%'},
        'Flask': {'demand': 50, 'salary_range': [4000, 7500], 'growth': '+12%'},
        'PostgreSQL': {'demand': 68, 'salary_range': [5000, 9000], 'growth': '+20%'},
        'Git': {'demand': 85, 'salary_range': [4000, 7000], 'growth': '+10%'},
        'Agile': {'demand': 70, 'salary_range': [4500, 8000], 'growth': '+12%'},
        'Project Management': {'demand': 65, 'salary_range': [5000, 10000], 'growth': '+15%'},
    }
    
    # Course recommendations for each skill
    COURSE_RECOMMENDATIONS = {
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
        }
    }
    
    @classmethod
    def calculate_employability_score(cls, user_skills: List[str], experience_years: int = 0) -> Dict:
        """Calculate employability score based on skills and experience"""
        
        if not user_skills:
            return {'score': 0, 'level': 'Beginner', 'color': 'red'}
        
        total_score = 0
        max_possible = 0
        skill_contributions = []
        
        for skill, data in cls.MARKET_DEMANDS.items():
            max_possible += data['demand']
            if any(skill.lower() in user_skill.lower() or user_skill.lower() in skill.lower() 
                   for user_skill in user_skills):
                # User has this skill
                score = data['demand']
                total_score += score
                skill_contributions.append({
                    'skill': skill,
                    'score': score,
                    'status': 'matched',
                    'demand': data['demand']
                })
            else:
                skill_contributions.append({
                    'skill': skill,
                    'score': 0,
                    'status': 'missing',
                    'demand': data['demand']
                })
        
        # Calculate percentage score
        if max_possible > 0:
            base_score = (total_score / max_possible) * 100
        else:
            base_score = 0
        
        # Add experience bonus (up to 15%)
        experience_bonus = min(experience_years * 2, 15)
        final_score = min(base_score + experience_bonus, 100)
        
        # Determine level
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
    def analyze_gaps(cls, user_skills: List[str]) -> List[Dict]:
        """Analyze skill gaps and prioritize missing skills"""
        
        gaps = []
        
        # If no user skills, return all skills as gaps
        if not user_skills:
            for skill, data in cls.MARKET_DEMANDS.items():
                gaps.append({
                    'skill': skill,
                    'demand': data['demand'],
                    'priority': 'Critical' if data['demand'] >= 80 else 'High',
                    'salary_range': data['salary_range'],
                    'growth': data['growth'],
                    'course': cls.COURSE_RECOMMENDATIONS.get(skill, {
                        'coursera': f'{skill} Fundamentals',
                        'duration': '4 weeks',
                        'effort': '4 hrs/week',
                        'certification': False
                    })
                })
            return gaps
        
        # Convert user skills to lowercase for comparison
        user_skills_lower = [s.lower() for s in user_skills]
        
        for skill, data in cls.MARKET_DEMANDS.items():
            # Check if user has this skill (case-insensitive, partial match)
            has_skill = False
            for user_skill in user_skills_lower:
                if skill.lower() in user_skill or user_skill in skill.lower():
                    has_skill = True
                    break
            
            # If user doesn't have the skill, it's a gap
            if not has_skill:
                # Determine priority based on demand
                if data['demand'] >= 80:
                    priority = 'Critical'
                elif data['demand'] >= 70:
                    priority = 'High'
                elif data['demand'] >= 60:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                gaps.append({
                    'skill': skill,
                    'demand': data['demand'],
                    'priority': priority,
                    'salary_range': data['salary_range'],
                    'growth': data['growth'],
                    'course': cls.COURSE_RECOMMENDATIONS.get(skill, {
                        'coursera': f'{skill} Fundamentals',
                        'duration': '4 weeks',
                        'effort': '4 hrs/week',
                        'certification': False
                    })
                })
        
        # Sort by demand (highest first)
        gaps.sort(key=lambda x: x['demand'], reverse=True)
        
        return gaps
    
    @classmethod
    def generate_learning_roadmap(cls, gaps: List[Dict]) -> Dict:
        """Generate personalized learning roadmap with real courses"""
        
        roadmap = {
            'immediate': [],      # 0-2 weeks
            'short_term': [],     # 2-6 weeks
            'medium_term': [],    # 6-12 weeks
            'long_term': []       # 3+ months
        }
        
        # Get real courses for each gap
        for idx, gap in enumerate(gaps[:10]):  # Top 10 gaps
            priority = gap['priority']
            skill = gap['skill']
            
            # Fetch real courses for this skill
            courses = cls.course_api.search_courses(skill, limit=2)
            
            # Get certifications for this skill
            certifications = cls.course_api.get_certification_recommendations(skill)
            
            # If no courses found, use the course recommendation from COURSE_RECOMMENDATIONS
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
            }
        }
        
        recommendations = []
        
        for role, data in job_roles.items():
            required = set(data['required_skills'])
            user_skill_set = set([s.lower() for s in user_skills])
            
            # Calculate match percentage
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
        
        # Sort by match percentage
        recommendations.sort(key=lambda x: x['match_percentage'], reverse=True)
        
        return recommendations[:5]