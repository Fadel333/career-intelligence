# app/utils/cv_detector.py
import re
from typing import Tuple, Dict, List

class CVDetector:
    """Detect if a file is a real CV/resume based on content"""
    
    # CV-specific keywords and patterns
    CV_HEADERS = [
        'experience', 'education', 'skills', 'work history', 'employment',
        'professional summary', 'profile', 'objective', 'career objective',
        'certifications', 'languages', 'projects', 'achievements',
        'accomplishments', 'responsibilities', 'references', 'qualifications',
        'work experience', 'technical skills', 'soft skills', 'core competencies',
        'employment history', 'professional experience', 'relevant experience'
    ]
    
    CV_PATTERNS = [
        r'work(?:ing)?\s+experience',
        r'education\s*(?:background|history)?',
        r'skills\s*(?:and\s+qualifications)?',
        r'professional\s+summary',
        r'career\s+objective',
        r'certifications?\s*(?:and\s+licenses?)?',
        r'\d{4}\s*[-–]\s*(?:present|current|\d{4})',  # Date ranges
        r'\w+\s+\d{1,2},\s+\d{4}',  # Month Day, Year
        r'[A-Za-z]+@[A-Za-z]+\.[A-Za-z]{2,}',  # Email
        r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
        r'(?:Bachelor|Master|PhD|B\.Sc|M\.Sc|B\.A|M\.A|MBA|BS|MS|BA|MA)\s*(?:degree)?',  # Degrees
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}',  # Month Year
    ]
    
    # Words that indicate it's NOT a CV - MODIFIED to be less strict
    NON_CV_INDICATORS = [
        # 'assignment',  # Commented out - students mention assignments in resumes
        'homework', 
        # 'exam',  # Commented out - could be in resumes
        # 'test',  # Commented out - could be in resumes  
        'quiz', 
        'syllabus',
        'lecture', 
        'course outline', 
        'reading list', 
        'lab report',
        'thesis proposal', 
        'research proposal', 
        'grant proposal',
        'midterm', 
        'final exam', 
        'pop quiz', 
        'study guide',
        'course syllabus', 
        'class schedule', 
        'office hours'
    ]
    
    # Strong CV indicators (high weight)
    STRONG_INDICATORS = [
        r'work\s+experience',
        r'education\s+background',
        r'skills\s+summary',
        r'professional\s+experience',
        r'employment\s+history'
    ]
    
    @classmethod
    def detect(cls, text: str) -> Tuple[bool, float, str]:
        """
        Detect if text is a CV/resume
        
        Args:
            text: The text content to analyze
            
        Returns:
            (is_cv: bool, confidence: float, reason: str)
        """
        print(f"\n🔍 CV Detection - Analyzing {len(text)} characters, {len(text.split())} words")
        
        if not text or len(text) < 100:
            print(f"❌ File too short: {len(text)} characters")
            return False, 0.0, "File is too short to be a CV (min 100 characters)"
        
        text_lower = text.lower()
        words = text_lower.split()
        word_count = len(words)
        
        print(f"📊 Word count: {word_count}")
        
        # ========== Check 1: Look for non-CV indicators ==========
        non_cv_found = []
        for indicator in cls.NON_CV_INDICATORS:
            if indicator in text_lower:
                non_cv_found.append(indicator)
        
        if non_cv_found:
            print(f"⚠️ Found non-CV indicators: {non_cv_found}")
            # Only reject if there are multiple non-CV indicators
            if len(non_cv_found) >= 2:
                return False, 0.0, f"Contains multiple non-CV indicators: {', '.join(non_cv_found[:3])}"
        
        # ========== Check 2: Look for strong CV indicators ==========
        strong_matches = 0
        for pattern in cls.STRONG_INDICATORS:
            if re.search(pattern, text_lower):
                strong_matches += 1
        
        print(f"✅ Strong indicators found: {strong_matches}")
        
        # If we have at least 2 strong indicators, it's almost certainly a CV
        if strong_matches >= 2:
            print(f"✅ Strong CV indicators found ({strong_matches} matches)")
            return True, 95.0, f"Strong CV indicators found ({strong_matches} matches)"
        
        # ========== Check 3: Look for CV headers ==========
        headers_found = []
        for header in cls.CV_HEADERS:
            if header in text_lower:
                headers_found.append(header)
        
        header_count = len(headers_found)
        header_score = (header_count / len(cls.CV_HEADERS)) * 100
        
        print(f"📋 Headers found: {header_count} - {headers_found[:10]}")  # Show first 10
        
        # ========== Check 4: Look for CV patterns ==========
        patterns_matched = []
        for pattern in cls.CV_PATTERNS:
            if re.search(pattern, text_lower):
                patterns_matched.append(pattern)
        
        pattern_count = len(patterns_matched)
        pattern_score = (pattern_count / len(cls.CV_PATTERNS)) * 100
        
        print(f"🔍 Patterns matched: {pattern_count}")
        
        # ========== Check 5: Structure indicators ==========
        structure_score = 0
        structure_details = []
        
        # Has section-like structure (lines with colon or headers)
        has_sections = any(
            line.strip().endswith(':') or 
            (len(line.strip()) < 50 and line.strip().isupper())
            for line in text.split('\n') if line.strip()
        )
        if has_sections:
            structure_score += 20
            structure_details.append('sections')
        
        # Has bullet points
        has_bullets = any(line.strip().startswith(('•', '-', '*', '·', '►', '▪')) for line in text.split('\n'))
        if has_bullets:
            structure_score += 20
            structure_details.append('bullets')
        
        # Has dates (employment/education)
        has_dates = bool(re.search(r'\d{4}\s*[-–]\s*\d{4}', text))
        if has_dates:
            structure_score += 20
            structure_details.append('dates')
        
        # Has email
        has_email = bool(re.search(r'[A-Za-z]+@[A-Za-z]+\.[A-Za-z]{2,}', text))
        if has_email:
            structure_score += 20
            structure_details.append('email')
        
        # Has phone number
        has_phone = bool(re.search(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text))
        if has_phone:
            structure_score += 20
            structure_details.append('phone')
        
        # Has degree indicators
        has_degree = bool(re.search(r'(?:Bachelor|Master|PhD|B\.Sc|M\.Sc|B\.A|M\.A|MBA|BS|MS|BA|MA)', text))
        if has_degree:
            structure_score += 20
            structure_details.append('degree')
        
        print(f"🏗️ Structure score: {structure_score}, Features: {structure_details}")
        
        # ========== Check 6: Minimum word count ==========
        if word_count < 150:
            structure_score -= 20
            structure_details.append('short_document')
            print(f"⚠️ Short document: {word_count} words < 150")
        
        # Cap structure score at 100
        structure_score = min(100, max(0, structure_score))
        
        # ========== Calculate Final Score ==========
        # Header score: 35% weight, Pattern score: 25% weight, Structure: 40% weight
        final_score = (header_score * 0.35) + (pattern_score * 0.25) + (structure_score * 0.40)
        
        # Bonus: If we have strong indicators, boost score
        if strong_matches >= 1:
            final_score += 15
            structure_details.append('strong_match')
        
        # Penalty: If very short but has good structure
        if word_count < 200 and structure_score > 40:
            final_score -= 10
            print(f"⚠️ Short document penalty applied")
        
        # Determine if it's a CV
        is_cv = final_score >= 30.0
        confidence = min(100, max(0, final_score))
        
        print(f"📊 Final score: {final_score:.1f}%, Is CV: {is_cv}")
        
        # Generate reason
        if is_cv:
            reason = f"CV detected — {header_count} headers, {pattern_count} patterns, {len(structure_details)} features"
        else:
            reason = f"Not a CV — confidence {confidence:.1f}%"
            if header_count == 0:
                reason += " (no CV headers found)"
            elif pattern_count < 2:
                reason += " (too few CV patterns)"
            if non_cv_found:
                reason += f" (non-CV indicators: {', '.join(non_cv_found[:2])})"
        
        print(f"📄 Result: {reason}\n")
        
        return is_cv, confidence, reason
    
    @classmethod
    def get_detailed_report(cls, text: str) -> Dict:
        """
        Get detailed detection report for debugging
        
        Args:
            text: The text content to analyze
            
        Returns:
            Dictionary with detailed analysis results
        """
        is_cv, confidence, reason = cls.detect(text)
        
        text_lower = text.lower()
        
        headers_found = []
        for header in cls.CV_HEADERS:
            if header in text_lower:
                headers_found.append(header)
        
        patterns_matched = []
        for pattern in cls.CV_PATTERNS:
            if re.search(pattern, text_lower):
                patterns_matched.append(pattern)
        
        non_cv_indicators_found = []
        for indicator in cls.NON_CV_INDICATORS:
            if indicator in text_lower:
                non_cv_indicators_found.append(indicator)
        
        strong_indicators_found = []
        for pattern in cls.STRONG_INDICATORS:
            if re.search(pattern, text_lower):
                strong_indicators_found.append(pattern)
        
        return {
            'is_cv': is_cv,
            'confidence': round(confidence, 1),
            'reason': reason,
            'headers_found': headers_found,
            'headers_count': len(headers_found),
            'patterns_matched': patterns_matched[:10],  # Show first 10
            'patterns_count': len(patterns_matched),
            'non_cv_indicators': non_cv_indicators_found,
            'strong_indicators': strong_indicators_found,
            'word_count': len(text.split()),
            'character_count': len(text),
            'has_sections': any(
                line.strip().endswith(':') or 
                (len(line.strip()) < 50 and line.strip().isupper())
                for line in text.split('\n') if line.strip()
            ),
            'has_bullets': any(line.strip().startswith(('•', '-', '*', '·', '►', '▪')) for line in text.split('\n')),
            'has_dates': bool(re.search(r'\d{4}\s*[-–]\s*\d{4}', text)),
            'has_email': bool(re.search(r'[A-Za-z]+@[A-Za-z]+\.[A-Za-z]{2,}', text)),
            'has_phone': bool(re.search(r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)),
            'has_degree': bool(re.search(r'(?:Bachelor|Master|PhD|B\.Sc|M\.Sc|B\.A|M\.A|MBA|BS|MS|BA|MA)', text)),
        }
    
    @classmethod
    def quick_check(cls, text: str) -> bool:
        """
        Quick check if text is a CV - returns boolean only
        
        Args:
            text: The text content to analyze
            
        Returns:
            True if likely a CV, False otherwise
        """
        is_cv, _, _ = cls.detect(text)
        return is_cv