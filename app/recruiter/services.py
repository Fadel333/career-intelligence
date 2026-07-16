# app/recruiter/services.py
import re
import json
from typing import List, Dict, Any
from flask import current_app

# Fix imports - Vacancy is now Job
from models import Candidate, Job  # Renamed from Vacancy


class CandidateMatcher:
    """Match candidates to job requirements"""
    
    @staticmethod
    def calculate_match(candidate: Candidate, job: Job) -> Dict:  # Renamed from vacancy
        """
        Calculate match percentage between candidate and job
        
        Returns:
            {
                "overall": 78.5,
                "skills": 85.0,
                "experience": 70.0,
                "education": 90.0
            }
        """
        scores = {}
        
        # 1. Skills match (40% weight)
        candidate_skills = candidate.skills or []
        required_skills = job.required_skills if job else []
        scores['skills'] = CandidateMatcher._match_skills(candidate_skills, required_skills)
        
        # 2. Experience match (30% weight)
        scores['experience'] = CandidateMatcher._match_experience(
            candidate.experience_years or 0,
            job.experience_level if job else 'entry'
        )
        
        # 3. Education match (20% weight)
        candidate_education = candidate.education or []
        scores['education'] = CandidateMatcher._match_education(candidate_education, job.requirements or [] if job else [])
        
        # 4. Overall weighted score
        scores['overall'] = (
            scores['skills'] * 0.40 +
            scores['experience'] * 0.30 +
            scores['education'] * 0.30
        )
        
        return scores
    
    @staticmethod
    def _match_skills(candidate_skills: List[str], required_skills: List[str]) -> float:
        """Match skills using simple overlap"""
        if not required_skills:
            return 100.0
        if not candidate_skills:
            return 0.0
        
        # Normalize skills
        candidate_skills = [s.lower().strip() for s in candidate_skills]
        required_skills = [s.lower().strip() for s in required_skills]
        
        # Find matches
        matches = sum(1 for skill in required_skills if skill in candidate_skills)
        
        return min(100.0, (matches / len(required_skills)) * 100)
    
    @staticmethod
    def _match_experience(candidate_years: float, required_level: str) -> float:
        """Match experience level"""
        level_requirements = {
            'entry': 0,
            'junior': 1,
            'mid': 2,
            'senior': 4,
            'lead': 6,
            'manager': 7
        }
        
        required_years = level_requirements.get(required_level, 0)
        
        if candidate_years >= required_years:
            return 100.0
        elif candidate_years >= required_years * 0.7:
            return 70.0
        elif candidate_years >= required_years * 0.4:
            return 40.0
        else:
            return 20.0
    
    @staticmethod
    def _match_education(candidate_education: List[Dict], requirements: List[str]) -> float:
        """Match education level"""
        if not candidate_education:
            return 0.0
        
        # Get highest degree
        degree_levels = {
            'phd': 5,
            'master': 4,
            'bachelor': 3,
            'diploma': 2,
            'certificate': 1
        }
        
        highest = max(
            candidate_education,
            key=lambda x: degree_levels.get(x.get('degree', '').lower(), 0)
        )
        candidate_level = degree_levels.get(highest.get('degree', '').lower(), 0)
        
        return min(100.0, candidate_level * 25)
    
    @staticmethod
    def rank_candidates_for_job(candidates: List[Candidate], job: Job) -> List[Dict]:
        """AI-powered ranking of candidates for a specific job"""
        ranked_scores = []
        
        for candidate in candidates:
            # Multi-factor scoring
            skill_match = CandidateMatcher._match_skills(candidate.skills or [], job.required_skills or [])
            experience_match = CandidateMatcher._match_experience(candidate.experience_years or 0, job.experience_level or 'entry')
            location_match = CandidateMatcher._match_location(candidate.location or '', job.location or '')
            education_match = CandidateMatcher._match_education(candidate.education or [], job.requirements or [])
            
            # AI-enhanced factors
            culture_fit = CandidateMatcher._calculate_culture_fit(candidate, job)
            growth_potential = CandidateMatcher._calculate_growth_potential(candidate, job)
            
            # Weighted scoring
            total_score = (
                skill_match * 0.35 +
                experience_match * 0.25 +
                location_match * 0.10 +
                education_match * 0.10 +
                culture_fit * 0.10 +
                growth_potential * 0.10
            )
            
            ranked_scores.append({
                'candidate_id': candidate.id,
                'candidate_name': candidate.name or 'Unknown',
                'candidate_email': candidate.email or 'No email',
                'skills': candidate.skills or [],
                'experience_years': candidate.experience_years or 0,
                'location': candidate.location or 'Unknown',
                'match_score': round(total_score, 2),
                'score_breakdown': {
                    'skills': round(skill_match, 2),
                    'experience': round(experience_match, 2),
                    'location': round(location_match, 2),
                    'education': round(education_match, 2),
                    'culture_fit': round(culture_fit, 2),
                    'growth_potential': round(growth_potential, 2)
                }
            })
        
        # Sort by match score descending
        return sorted(ranked_scores, key=lambda x: x['match_score'], reverse=True)
    
    @staticmethod
    def _match_location(candidate_location: str, job_location: str) -> float:
        """Match location preference"""
        if not job_location:
            return 100.0
        if not candidate_location:
            return 50.0
        
        # Simple check: if locations match or candidate is remote
        if job_location.lower() in candidate_location.lower() or candidate_location.lower() == 'remote':
            return 100.0
        
        # If both are in same country (rough check)
        # This can be enhanced with proper geo-matching
        return 50.0
    
    @staticmethod
    def _calculate_culture_fit(candidate: Candidate, job: Job) -> float:
        """AI-enhanced culture fit calculation"""
        # Placeholder: Use simple logic
        # In production, this could use NLP on candidate's CV and job description
        base_score = 70.0
        
        # Boost if candidate has soft skills mentioned in job requirements
        soft_skills = ['team', 'leadership', 'communication', 'collaboration', 'problem-solving']
        for skill in soft_skills:
            if skill.lower() in str(job.description).lower():
                if any(skill.lower() in str(candidate.cv_text or '').lower() for skill in soft_skills):
                    base_score = min(100, base_score + 5)
        
        return min(100, base_score)
    
    @staticmethod
    def _calculate_growth_potential(candidate: Candidate, job: Job) -> float:
        """Calculate growth potential based on skills progression"""
        # Placeholder: Check if candidate has learning mindset
        growth_indicators = [
            'certified', 'certification', 'course', 'training', 
            'workshop', 'conference', 'continuous learning'
        ]
        
        score = 60.0  # Base score
        
        # Check for certifications
        certs = candidate.certifications or []
        if certs:
            score += 10
        
        # Check for learning keywords in CV
        cv_text = str(candidate.cv_text or '').lower()
        if any(indicator in cv_text for indicator in growth_indicators):
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def analyze_skill_gaps(candidates: List[Candidate], job: Job) -> Dict:
        """Analyze what skills candidates are missing"""
        required_skills = set(job.required_skills or [])
        
        if not required_skills:
            return {
                'missing_skills': [],
                'gap_percentage': 0,
                'recommendations': []
            }
        
        # Collect all candidate skills
        candidate_skills = set()
        for candidate in candidates:
            if candidate.skills:
                candidate_skills.update(candidate.skills)
        
        # Find missing skills
        missing_skills = required_skills - candidate_skills
        
        # Calculate gap percentage
        gap_percentage = (len(missing_skills) / len(required_skills)) * 100
        
        # Generate recommendations
        recommendations = []
        for skill in missing_skills:
            recommendations.append(f"Consider candidates with {skill} skills")
        
        return {
            'missing_skills': list(missing_skills),
            'gap_percentage': round(gap_percentage, 2),
            'recommendations': recommendations
        }