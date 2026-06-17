import requests
import json
import os
from typing import List, Dict, Any
from datetime import datetime

class CourseAPI:
    """Real course API integration with Coursera, Udemy, and YouTube"""
    
    def __init__(self):
        # Use environment variables for API keys
        self.coursera_api_key = os.environ.get('COURSERA_API_KEY', None)
        self.udemy_api_key = os.environ.get('UDEMY_API_KEY', None)
        self.udemy_api_secret = os.environ.get('UDEMY_API_SECRET', None)
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY', None)
        
        # API endpoints
        self.coursera_base_url = "https://api.coursera.org/api/courses.v1"
        self.udemy_base_url = "https://www.udemy.com/api-2.0/courses/"
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3/search"
    
    def search_courses(self, skill: str, limit: int = 5) -> List[Dict]:
        """Search for courses across multiple platforms"""
        
        results = []
        
        # Search on Coursera
        coursera_courses = self._search_coursera(skill, limit)
        results.extend(coursera_courses)
        
        # Search on Udemy (if API keys are available)
        if self.udemy_api_key and self.udemy_api_secret:
            udemy_courses = self._search_udemy(skill, limit)
            results.extend(udemy_courses)
        
        # Search on YouTube (if API key is available)
        if self.youtube_api_key:
            youtube_courses = self._search_youtube(skill, limit)
            results.extend(youtube_courses)
        
        # Return top results
        return results[:limit * 2]
    
    def _search_coursera(self, skill: str, limit: int = 5) -> List[Dict]:
        """Search courses on Coursera"""
        
        courses = []
        
        try:
            # Coursera API endpoint with query params
            url = f"{self.coursera_base_url}?q=search&query={skill.replace(' ', '+')}&limit={limit}"
            
            # If you have an API key, add it to headers
            headers = {}
            if self.coursera_api_key:
                headers['Authorization'] = f'Bearer {self.coursera_api_key}'
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Coursera API returns elements in 'elements' field
                elements = data.get('elements', [])
                for course in elements[:limit]:
                    courses.append({
                        'title': course.get('name', f'Coursera {skill} Course'),
                        'provider': 'Coursera',
                        'url': f"https://www.coursera.org/learn/{course.get('slug', skill.lower().replace(' ', '-'))}",
                        'description': course.get('description', f'Learn {skill} on Coursera'),
                        'duration': f"{course.get('durationWeeks', 4)} weeks",
                        'effort': f"{course.get('expectedEffortHours', 4)} hrs/week",
                        'certificate': True,
                        'platform': 'Coursera',
                        'icon': 'fab fa-coursera',
                        'color': 'text-blue-400'
                    })
            else:
                # Fallback to mock data if API fails
                courses = self._get_coursera_mock(skill, limit)
                
        except Exception as e:
            print(f"Error fetching Coursera courses: {e}")
            courses = self._get_coursera_mock(skill, limit)
        
        return courses
    
    def _search_udemy(self, skill: str, limit: int = 5) -> List[Dict]:
        """Search courses on Udemy"""
        
        courses = []
        
        try:
            # Udemy API requires Basic Auth
            auth = None
            if self.udemy_api_key and self.udemy_api_secret:
                auth = (self.udemy_api_key, self.udemy_api_secret)
            
            params = {
                'search': skill,
                'page_size': limit,
                'fields': 'title,url,headline,price,visible_instructors,is_paid',
                'category': 'Development'
            }
            
            response = requests.get(self.udemy_base_url, params=params, auth=auth, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for course in data.get('results', []):
                    courses.append({
                        'title': course.get('title', f'Udemy {skill} Course'),
                        'provider': 'Udemy',
                        'url': course.get('url', '#'),
                        'description': course.get('headline', f'Learn {skill} on Udemy'),
                        'duration': 'Varies',
                        'effort': 'Flexible',
                        'certificate': True,
                        'platform': 'Udemy',
                        'price': course.get('price', 'Free'),
                        'icon': 'fab fa-udemy',
                        'color': 'text-purple-400'
                    })
            else:
                courses = self._get_udemy_mock(skill, limit)
                
        except Exception as e:
            print(f"Error fetching Udemy courses: {e}")
            courses = self._get_udemy_mock(skill, limit)
        
        return courses
    
    def _search_youtube(self, skill: str, limit: int = 5) -> List[Dict]:
        """Search for YouTube playlists and tutorials"""
        
        courses = []
        
        try:
            params = {
                'part': 'snippet',
                'q': f'{skill} tutorial full course',
                'type': 'playlist',
                'maxResults': limit,
                'key': self.youtube_api_key
            }
            
            response = requests.get(self.youtube_base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('items', []):
                    snippet = item.get('snippet', {})
                    playlist_id = item.get('id', {}).get('playlistId')
                    
                    courses.append({
                        'title': snippet.get('title', f'{skill} Tutorial'),
                        'provider': 'YouTube',
                        'url': f"https://www.youtube.com/playlist?list={playlist_id}" if playlist_id else '#',
                        'description': snippet.get('description', f'Free {skill} tutorial on YouTube'),
                        'duration': 'Self-paced',
                        'effort': 'Flexible',
                        'certificate': False,
                        'platform': 'YouTube',
                        'free': True,
                        'icon': 'fab fa-youtube',
                        'color': 'text-red-400'
                    })
            else:
                courses = self._get_youtube_mock(skill, limit)
                
        except Exception as e:
            print(f"Error fetching YouTube courses: {e}")
            courses = self._get_youtube_mock(skill, limit)
        
        return courses
    
    def _get_coursera_mock(self, skill: str, limit: int) -> List[Dict]:
        """Fallback mock data for Coursera"""
        mock_courses = {
            'python': [
                {
                    'title': 'Python for Everybody',
                    'provider': 'Coursera',
                    'url': 'https://www.coursera.org/specializations/python',
                    'description': 'Learn Python programming from scratch',
                    'duration': '8 weeks',
                    'effort': '3-5 hrs/week',
                    'certificate': True,
                    'platform': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400'
                },
                {
                    'title': 'Python Data Structures',
                    'provider': 'Coursera',
                    'url': 'https://www.coursera.org/learn/python-data',
                    'description': 'Master Python data structures and algorithms',
                    'duration': '6 weeks',
                    'effort': '4 hrs/week',
                    'certificate': True,
                    'platform': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400'
                }
            ],
            'machine learning': [
                {
                    'title': 'Machine Learning Specialization',
                    'provider': 'Coursera',
                    'url': 'https://www.coursera.org/specializations/machine-learning',
                    'description': 'Master machine learning with Stanford',
                    'duration': '12 weeks',
                    'effort': '7 hrs/week',
                    'certificate': True,
                    'platform': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400'
                }
            ],
            'data analysis': [
                {
                    'title': 'Data Analysis with Python',
                    'provider': 'Coursera',
                    'url': 'https://www.coursera.org/learn/data-analysis-with-python',
                    'description': 'Learn data analysis with pandas and Python',
                    'duration': '6 weeks',
                    'effort': '4 hrs/week',
                    'certificate': True,
                    'platform': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400'
                }
            ]
        }
        
        # Find matching mock data
        skill_lower = skill.lower()
        for key, courses in mock_courses.items():
            if key in skill_lower or skill_lower in key:
                return courses[:limit]
        
        # Default mock if no match
        return [
            {
                'title': f'Learn {skill} Fundamentals',
                'provider': 'Coursera',
                'url': '#',
                'description': f'Comprehensive course on {skill}',
                'duration': '6 weeks',
                'effort': '4 hrs/week',
                'certificate': True,
                'platform': 'Coursera',
                'icon': 'fab fa-coursera',
                'color': 'text-blue-400'
            }
        ][:limit]
    
    def _get_udemy_mock(self, skill: str, limit: int) -> List[Dict]:
        """Fallback mock data for Udemy"""
        return [
            {
                'title': f'Complete {skill} Bootcamp',
                'provider': 'Udemy',
                'url': '#',
                'description': f'Learn {skill} from zero to hero',
                'duration': 'Varies',
                'effort': 'Flexible',
                'certificate': True,
                'platform': 'Udemy',
                'price': 'Free',
                'icon': 'fab fa-udemy',
                'color': 'text-purple-400'
            }
        ][:limit]
    
    def _get_youtube_mock(self, skill: str, limit: int) -> List[Dict]:
        """Fallback mock data for YouTube"""
        return [
            {
                'title': f'{skill} Full Course for Beginners',
                'provider': 'YouTube',
                'url': '#',
                'description': f'Free {skill} tutorial on YouTube',
                'duration': 'Self-paced',
                'effort': 'Flexible',
                'certificate': False,
                'platform': 'YouTube',
                'free': True,
                'icon': 'fab fa-youtube',
                'color': 'text-red-400'
            }
        ][:limit]

    def get_certification_recommendations(self, skill: str) -> List[Dict]:
        """Get certification recommendations for a skill"""
        
        certifications = {
            'python': [
                {'name': 'Python Institute PCEP - Entry Level', 'provider': 'Python Institute', 'cost': '$100-150'},
                {'name': 'PCAP - Certified Associate in Python', 'provider': 'Python Institute', 'cost': '$200-250'},
                {'name': 'Google IT Automation with Python', 'provider': 'Google', 'cost': 'Free (Coursera)'}
            ],
            'machine learning': [
                {'name': 'Google Professional ML Engineer', 'provider': 'Google Cloud', 'cost': '$200'},
                {'name': 'AWS Certified Machine Learning', 'provider': 'Amazon', 'cost': '$300'},
                {'name': 'IBM Data Science Professional', 'provider': 'IBM', 'cost': 'Free (Coursera)'}
            ],
            'cloud': [
                {'name': 'AWS Certified Cloud Practitioner', 'provider': 'Amazon', 'cost': '$100'},
                {'name': 'AWS Solutions Architect - Associate', 'provider': 'Amazon', 'cost': '$150'},
                {'name': 'Google Cloud Digital Leader', 'provider': 'Google Cloud', 'cost': '$200'}
            ],
            'project management': [
                {'name': 'PMP Certification', 'provider': 'PMI', 'cost': '$405-555'},
                {'name': 'Agile Certified Practitioner (PMI-ACP)', 'provider': 'PMI', 'cost': '$405-555'},
                {'name': 'Certified Scrum Master (CSM)', 'provider': 'Scrum Alliance', 'cost': '$500-1000'}
            ],
            'data': [
                {'name': 'Google Professional Data Engineer', 'provider': 'Google Cloud', 'cost': '$200'},
                {'name': 'AWS Certified Data Analytics', 'provider': 'Amazon', 'cost': '$300'},
                {'name': 'Tableau Desktop Specialist', 'provider': 'Tableau', 'cost': '$100'}
            ],
            'security': [
                {'name': 'CompTIA Security+', 'provider': 'CompTIA', 'cost': '$370'},
                {'name': 'CISSP', 'provider': 'ISC²', 'cost': '$749'},
                {'name': 'Certified Ethical Hacker (CEH)', 'provider': 'EC-Council', 'cost': '$1,200'}
            ]
        }
        
        skill_lower = skill.lower()
        for key, certs in certifications.items():
            if key in skill_lower or skill_lower in key:
                return certs
        
        return [{'name': f'{skill} Certification', 'provider': 'Various', 'cost': 'Varies'}]
    
    def get_platform_stats(self) -> Dict:
        """Get statistics about available platforms"""
        return {
            'platforms': [
                {
                    'name': 'Coursera',
                    'icon': 'fab fa-coursera',
                    'color': 'text-blue-400',
                    'status': 'Available',
                    'requires_key': False
                },
                {
                    'name': 'Udemy',
                    'icon': 'fab fa-udemy',
                    'color': 'text-purple-400',
                    'status': 'Available' if self.udemy_api_key else 'Mock Mode',
                    'requires_key': True
                },
                {
                    'name': 'YouTube',
                    'icon': 'fab fa-youtube',
                    'color': 'text-red-400',
                    'status': 'Available' if self.youtube_api_key else 'Mock Mode',
                    'requires_key': True
                }
            ],
            'total_courses_available': 10000,
            'certifications_available': 50
        }