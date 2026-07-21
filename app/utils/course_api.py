import requests
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from functools import lru_cache
from flask import current_app

class CourseAPI:
    """Real course API integration - Prioritizes YouTube, Coursera, and Udemy"""
    
    def __init__(self, app=None):
        self.app = app
        self._load_config()
        
        # Cache for course results
        self.cache = {}
        
        # ========== API ENDPOINTS ==========
        self.coursera_base_url = "https://api.coursera.org/api/courses.v1"
        self.udemy_base_url = "https://www.udemy.com/api-2.0/courses/"
        self.youtube_base_url = "https://www.googleapis.com/youtube/v3/search"
        
        # Timeout settings
        self.timeout = 5
        
        # ========== SECTOR MAPPING FOR ICONS ==========
        self.sector_icons = {
            'Technology': {'icon': 'fas fa-code', 'color': 'text-blue-400'},
            'Healthcare': {'icon': 'fas fa-heartbeat', 'color': 'text-red-400'},
            'Law': {'icon': 'fas fa-gavel', 'color': 'text-gold-500'},
            'Finance': {'icon': 'fas fa-chart-line', 'color': 'text-green-600'},
            'Education': {'icon': 'fas fa-chalkboard-teacher', 'color': 'text-blue-500'},
            'Agriculture': {'icon': 'fas fa-seedling', 'color': 'text-green-600'},
            'Business': {'icon': 'fas fa-briefcase', 'color': 'text-blue-700'},
            'Creative Arts': {'icon': 'fas fa-paint-brush', 'color': 'text-purple-500'},
            'Trades': {'icon': 'fas fa-tools', 'color': 'text-yellow-600'},
            'Engineering': {'icon': 'fas fa-cogs', 'color': 'text-gray-700'},
            'Social Services': {'icon': 'fas fa-hand-holding-heart', 'color': 'text-blue-600'}
        }

    def _load_config(self):
        """Load configuration from Flask app or environment"""
        if self.app:
            self.youtube_api_key = self.app.config.get('YOUTUBE_API_KEY')
            self.coursera_client_id = self.app.config.get('COURSERA_CLIENT_ID')
            self.coursera_client_secret = self.app.config.get('COURSERA_CLIENT_SECRET')
            self.udemy_client_id = self.app.config.get('UDEMY_CLIENT_ID')
            self.udemy_client_secret = self.app.config.get('UDEMY_CLIENT_SECRET')
        else:
            # Fallback to environment variables
            self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
            self.coursera_client_id = os.environ.get('COURSERA_CLIENT_ID')
            self.coursera_client_secret = os.environ.get('COURSERA_CLIENT_SECRET')
            self.udemy_client_id = os.environ.get('UDEMY_CLIENT_ID')
            self.udemy_client_secret = os.environ.get('UDEMY_CLIENT_SECRET')
        
        # Check if YouTube API key is set
        if not self.youtube_api_key:
            print("⚠️ YOUTUBE_API_KEY not set in environment")
    
    @lru_cache(maxsize=100)
    def _get_cached_courses(self, skill: str, limit: int) -> str:
        """Cache course results"""
        return json.dumps(self._search_courses_uncached(skill, limit))
    
    def search_courses(self, skill: str, limit: int = 5) -> List[Dict]:
        """Search for courses across reliable platforms with caching"""
        cache_key = f"{skill.lower()}_{limit}"
        
        # Check memory cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Search courses
        results = self._search_courses_uncached(skill, limit)
        
        # Cache for 1 hour (in memory)
        self.cache[cache_key] = results
        if len(self.cache) > 100:  # Limit cache size
            # Remove oldest entry
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        
        return results
    
    def _search_courses_uncached(self, skill: str, limit: int) -> List[Dict]:
        """Actual course search without caching - ONLY RELIABLE PLATFORMS"""
        results = []
        
        # ========== PRIORITY 1: YouTube (Most reliable, free) ==========
        if self.youtube_api_key:
            youtube_courses = self._search_youtube(skill, limit)
            results.extend(youtube_courses)
            print(f"✅ YouTube: Found {len(youtube_courses)} courses for '{skill}'")
        else:
            print(f"⚠️ YouTube API key not configured")
        
        # ========== PRIORITY 2: Coursera Public API (No key needed) ==========
        coursera_courses = self._search_coursera_public(skill, limit)
        results.extend(coursera_courses)
        print(f"✅ Coursera: Found {len(coursera_courses)} courses for '{skill}'")
        
        # ========== PRIORITY 3: Udemy (If credentials exist) ==========
        if self.udemy_client_id and self.udemy_client_secret:
            udemy_courses = self._search_udemy(skill, limit)
            results.extend(udemy_courses)
            print(f"✅ Udemy: Found {len(udemy_courses)} courses for '{skill}'")
        else:
            print(f"⚠️ Udemy credentials not configured")
        
        # ========== FALLBACK: Local mock data ==========
        if not results:
            print(f"⚠️ No API results, using fallback data for '{skill}'")
            results = self._get_fallback_courses(skill, limit)
        
        # Limit results and ensure no duplicates
        seen_titles = set()
        unique_results = []
        for course in results[:limit * 2]:
            title = course.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_results.append(course)
        
        return unique_results[:limit]
    
    # ============================================================
    # YOUTUBE API (MOST RELIABLE)
    # ============================================================
    
    def _search_youtube(self, skill: str, limit: int = 3) -> List[Dict]:
        """Search for YouTube playlists and tutorials"""
        if not self.youtube_api_key:
            return []
        
        courses = []
        try:
            # Search for playlists first
            params = {
                'part': 'snippet',
                'q': f'{skill} tutorial full course',
                'type': 'playlist',
                'maxResults': limit,
                'key': self.youtube_api_key,
                'safeSearch': 'strict'
            }
            response = requests.get(self.youtube_base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    snippet = item.get('snippet', {})
                    playlist_id = item.get('id', {}).get('playlistId')
                    if playlist_id:
                        courses.append({
                            'title': snippet.get('title', f'{skill} Tutorial').replace('"', ''),
                            'provider': 'YouTube',
                            'url': f"https://www.youtube.com/playlist?list={playlist_id}",
                            'description': snippet.get('description', f'Free {skill} tutorial on YouTube')[:200],
                            'duration': 'Self-paced',
                            'effort': 'Flexible',
                            'certificate': False,
                            'platform': 'YouTube',
                            'free': True,
                            'icon': 'fab fa-youtube',
                            'color': 'text-red-500',
                            'sector': self._detect_sector(skill),
                            'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
                        })
            
            # If no playlists, search for individual videos
            if not courses:
                params = {
                    'part': 'snippet',
                    'q': f'{skill} course',
                    'type': 'video',
                    'maxResults': limit,
                    'key': self.youtube_api_key,
                    'safeSearch': 'strict'
                }
                response = requests.get(self.youtube_base_url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        snippet = item.get('snippet', {})
                        video_id = item.get('id', {}).get('videoId')
                        if video_id:
                            courses.append({
                                'title': snippet.get('title', f'{skill} Tutorial').replace('"', ''),
                                'provider': 'YouTube',
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'description': snippet.get('description', f'Free {skill} tutorial on YouTube')[:200],
                                'duration': 'Self-paced',
                                'effort': 'Flexible',
                                'certificate': False,
                                'platform': 'YouTube',
                                'free': True,
                                'icon': 'fab fa-youtube',
                                'color': 'text-red-500',
                                'sector': self._detect_sector(skill),
                                'thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
                            })
        except requests.exceptions.Timeout:
            print(f"⚠️ YouTube API timeout for '{skill}'")
        except Exception as e:
            print(f"⚠️ YouTube API error: {e}")
        
        return courses[:limit]
    
    # ============================================================
    # COURSERA PUBLIC API (NO KEY REQUIRED)
    # ============================================================
    
    def _search_coursera_public(self, skill: str, limit: int = 3) -> List[Dict]:
        """Search Coursera public catalog (no API key required)"""
        courses = []
        try:
            params = {
                'q': 'search',
                'search': skill,
                'limit': limit,
                'fields': 'name,description,photoUrl,slug,partnerIds,primaryLanguages'
            }
            response = requests.get(self.coursera_base_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get('elements', []):
                    courses.append({
                        'title': item.get('name', f'{skill} Course').replace('"', ''),
                        'provider': 'Coursera',
                        'url': f"https://www.coursera.org/learn/{item.get('slug', skill.lower().replace(' ', '-'))}",
                        'description': item.get('description', f'Learn {skill} on Coursera')[:200],
                        'duration': 'Varies',
                        'effort': 'Flexible',
                        'certificate': True,
                        'platform': 'Coursera',
                        'free': False,
                        'icon': 'fas fa-graduation-cap',
                        'color': 'text-blue-500',
                        'sector': self._detect_sector(skill),
                        'thumbnail': item.get('photoUrl', '')
                    })
        except requests.exceptions.Timeout:
            print(f"⚠️ Coursera API timeout for '{skill}'")
        except Exception as e:
            print(f"⚠️ Coursera API error: {e}")
        
        return courses[:limit]
    
    # ============================================================
    # UDEMY API (REQUIRES CREDENTIALS)
    # ============================================================
    
    def _search_udemy(self, skill: str, limit: int = 3) -> List[Dict]:
        """Search courses on Udemy"""
        if not (self.udemy_client_id and self.udemy_client_secret):
            return []
        
        courses = []
        try:
            auth = (self.udemy_client_id, self.udemy_client_secret)
            params = {
                'search': skill,
                'page_size': limit,
                'fields': 'title,url,headline,price,visible_instructors,is_paid,level,image_100x100',
                'category': 'Development'
            }
            response = requests.get(self.udemy_base_url, params=params, auth=auth, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                for course in data.get('results', []):
                    price = course.get('price', 'Free')
                    is_free = price == 'Free' or price == 0
                    
                    courses.append({
                        'title': course.get('title', f'{skill} Course').replace('"', ''),
                        'provider': 'Udemy',
                        'url': course.get('url', '#'),
                        'description': course.get('headline', f'Learn {skill} on Udemy')[:200],
                        'duration': 'Varies',
                        'effort': 'Flexible',
                        'certificate': True,
                        'platform': 'Udemy',
                        'price': str(price),
                        'free': is_free,
                        'icon': 'fas fa-chalkboard-teacher',
                        'color': 'text-purple-500',
                        'sector': self._detect_sector(skill),
                        'thumbnail': course.get('image_100x100', ''),
                        'level': course.get('level', 'All Levels')
                    })
        except requests.exceptions.Timeout:
            print(f"⚠️ Udemy API timeout for '{skill}'")
        except Exception as e:
            print(f"⚠️ Udemy API error: {e}")
        
        return courses[:limit]
    
    # ============================================================
    # FALLBACK COURSES
    # ============================================================
    
    def _get_fallback_courses(self, skill: str, limit: int = 3) -> List[Dict]:
        """Generate fallback courses when all APIs fail"""
        sector = self._detect_sector(skill)
        icon_info = self.sector_icons.get(sector, {'icon': 'fas fa-book', 'color': 'text-gray-400'})
        
        fallbacks = [
            {
                'title': f'Introduction to {skill} - Complete Guide',
                'provider': 'Recommended',
                'url': f'https://www.google.com/search?q={skill.replace(" ", "+")}+course',
                'description': f'A comprehensive introduction to {skill} for beginners',
                'duration': 'Varies',
                'effort': 'Self-paced',
                'certificate': False,
                'platform': 'Recommended',
                'free': True,
                'icon': icon_info['icon'],
                'color': icon_info['color'],
                'sector': sector,
                'thumbnail': ''
            },
            {
                'title': f'Advanced {skill} - Mastery Course',
                'provider': 'Recommended',
                'url': f'https://www.google.com/search?q={skill.replace(" ", "+")}+advanced',
                'description': f'Advanced concepts and techniques for {skill}',
                'duration': 'Varies',
                'effort': 'Self-paced',
                'certificate': False,
                'platform': 'Recommended',
                'free': True,
                'icon': icon_info['icon'],
                'color': icon_info['color'],
                'sector': sector,
                'thumbnail': ''
            },
            {
                'title': f'{skill} for Professionals - Industry Applications',
                'provider': 'Recommended',
                'url': f'https://www.google.com/search?q={skill.replace(" ", "+")}+professional',
                'description': f'Real-world applications and best practices for {skill}',
                'duration': 'Varies',
                'effort': 'Self-paced',
                'certificate': False,
                'platform': 'Recommended',
                'free': True,
                'icon': icon_info['icon'],
                'color': icon_info['color'],
                'sector': sector,
                'thumbnail': ''
            }
        ]
        
        return fallbacks[:limit]
    
    # ============================================================
    # SECTOR DETECTION
    # ============================================================
    
    def _detect_sector(self, skill: str) -> str:
        """Detect the sector based on skill keywords"""
        skill_lower = skill.lower()
        
        # Tech keywords
        tech_keywords = ['python', 'java', 'javascript', 'react', 'angular', 'vue', 'node', 'django',
                        'flask', 'sql', 'postgresql', 'mongodb', 'aws', 'azure', 'docker', 'kubernetes',
                        'devops', 'ci/cd', 'git', 'linux', 'html', 'css', 'sass', 'tailwind', 'bootstrap',
                        'php', 'ruby', 'c++', 'c#', 'swift', 'kotlin', 'typescript', 'web', 'development',
                        'programming', 'software', 'app', 'android', 'ios', 'frontend', 'backend', 'fullstack']
        
        # Healthcare keywords
        healthcare_keywords = ['medical', 'nursing', 'pharmacy', 'clinical', 'patient', 'health', 'medicine',
                              'surgery', 'diagnosis', 'treatment', 'care', 'public health', 'epidemiology',
                              'nutrition', 'mental health', 'psychology', 'psychiatry', 'dental', 'pediatric']
        
        # Law keywords
        law_keywords = ['law', 'legal', 'constitution', 'criminal', 'civil', 'corporate', 'contract',
                       'tort', 'property', 'evidence', 'procedure', 'litigation', 'arbitration',
                       'mediation', 'human rights', 'international law', 'regulatory']
        
        # Finance keywords
        finance_keywords = ['accounting', 'finance', 'investment', 'banking', 'audit', 'tax', 'budget',
                           'financial', 'corporate finance', 'personal finance', 'wealth', 'portfolio',
                           'risk', 'insurance', 'actuarial', 'cfa', 'acca', 'cpa', 'bookkeeping']
        
        # Education keywords
        education_keywords = ['teaching', 'curriculum', 'instruction', 'pedagogy', 'learning', 'education',
                             'educational', 'lesson', 'classroom', 'assessment', 'student', 'teacher',
                             'training', 'mentoring', 'coaching', 'tutoring']
        
        # Agriculture keywords
        agriculture_keywords = ['agriculture', 'farming', 'crop', 'livestock', 'agribusiness', 'irrigation',
                               'soil', 'harvest', 'plant', 'animal', 'veterinary', 'food', 'nutrition',
                               'fisheries', 'forestry', 'sustainable', 'organic']
        
        # Business keywords
        business_keywords = ['business', 'management', 'strategy', 'marketing', 'sales', 'leadership',
                            'entrepreneurship', 'startup', 'innovation', 'project', 'operations',
                            'supply chain', 'logistics', 'hr', 'human resources', 'organizational']
        
        # Creative Arts keywords
        creative_keywords = ['design', 'art', 'music', 'photography', 'video', 'animation', 'graphic',
                            'illustration', 'painting', 'sculpture', 'dance', 'theatre', 'film',
                            'creative', 'portfolio', 'adobe', 'behance', 'skillshare']
        
        # Trades keywords
        trades_keywords = ['construction', 'plumbing', 'electrical', 'carpentry', 'welding', 'masonry',
                          'painting', 'roofing', 'hvac', 'mechanic', 'automotive', 'maintenance',
                          'repair', 'installation', 'technician', 'trades', 'vocational']
        
        # Engineering keywords
        engineering_keywords = ['engineering', 'civil', 'mechanical', 'electrical', 'structural', 'geotechnical',
                               'transportation', 'environmental', 'chemical', 'biomedical', 'aerospace',
                               'materials', 'robotics', 'control', 'thermal', 'fluid']
        
        # Social Services keywords
        social_keywords = ['social work', 'community', 'development', 'ngo', 'humanitarian', 'charity',
                          'poverty', 'equality', 'justice', 'human rights', 'welfare', 'advocacy',
                          'counseling', 'rehabilitation', 'children', 'elderly', 'disability']
        
        # Check each sector
        if any(kw in skill_lower for kw in tech_keywords):
            return 'Technology'
        elif any(kw in skill_lower for kw in healthcare_keywords):
            return 'Healthcare'
        elif any(kw in skill_lower for kw in law_keywords):
            return 'Law'
        elif any(kw in skill_lower for kw in finance_keywords):
            return 'Finance'
        elif any(kw in skill_lower for kw in education_keywords):
            return 'Education'
        elif any(kw in skill_lower for kw in agriculture_keywords):
            return 'Agriculture'
        elif any(kw in skill_lower for kw in business_keywords):
            return 'Business'
        elif any(kw in skill_lower for kw in creative_keywords):
            return 'Creative Arts'
        elif any(kw in skill_lower for kw in trades_keywords):
            return 'Trades'
        elif any(kw in skill_lower for kw in engineering_keywords):
            return 'Engineering'
        elif any(kw in skill_lower for kw in social_keywords):
            return 'Social Services'
        else:
            return 'Technology'  # Default
    
    # ============================================================
    # PLATFORM STATS
    # ============================================================
    
    def get_platform_stats(self) -> Dict:
        """Get statistics about available platforms by sector"""
        return {
            'platforms_by_sector': {
                'Technology': ['YouTube', 'Coursera', 'Udemy'],
                'Healthcare': ['YouTube', 'Coursera'],
                'Law': ['YouTube', 'Coursera'],
                'Finance': ['YouTube', 'Coursera', 'Udemy'],
                'Education': ['YouTube', 'Coursera'],
                'Agriculture': ['YouTube', 'Coursera'],
                'Business': ['YouTube', 'Coursera', 'Udemy'],
                'Creative Arts': ['YouTube', 'Coursera'],
                'Trades': ['YouTube', 'Coursera'],
                'Engineering': ['YouTube', 'Coursera'],
                'Social Services': ['YouTube', 'Coursera']
            },
            'total_platforms': 3,
            'total_sectors': 11,
            'total_courses_available': 50000,
            'certifications_available': 50,
            'free_courses': True
        }
    
    def get_certification_recommendations(self, skill: str) -> List[Dict]:
        """Get certification recommendations for a skill"""
        sector = self._detect_sector(skill)
        
        certs = {
            'Technology': [
                {'name': f'{skill} Certification', 'provider': 'Google', 'cost': 'Free-$299'},
                {'name': f'Professional {skill} Developer', 'provider': 'Microsoft', 'cost': '$99-$165'},
                {'name': f'{skill} Specialist', 'provider': 'AWS', 'cost': '$150-$300'}
            ],
            'Healthcare': [
                {'name': f'Certified {skill} Professional', 'provider': 'WHO', 'cost': 'Free'},
                {'name': f'{skill} Specialist', 'provider': 'Medscape', 'cost': 'Free'}
            ],
            'Business': [
                {'name': f'Certified {skill} Professional', 'provider': 'Google', 'cost': 'Free-$299'},
                {'name': f'{skill} Specialist', 'provider': 'HBR', 'cost': 'Varies'}
            ],
            'Finance': [
                {'name': f'Certified {skill} Professional', 'provider': 'CFA Institute', 'cost': 'Varies'},
                {'name': f'{skill} Specialist', 'provider': 'ACCA', 'cost': 'Varies'}
            ]
        }
        
        return certs.get(sector, [
            {'name': f'{skill} Certification', 'provider': 'Various', 'cost': 'Varies'}
        ])