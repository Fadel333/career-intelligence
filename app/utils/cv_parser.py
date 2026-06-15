import os
import re
from PyPDF2 import PdfReader
from docx import Document
import spacy

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

class CVParser:
    """Extract text and skills from CV files"""
    
    # Common tech skills to look for
    SKILLS_DB = {
        'Programming': ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Swift', 'Kotlin', 'PHP', 'R', 'MATLAB'],
        'Web Development': ['React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring Boot', 'HTML', 'CSS', 'Bootstrap', 'Tailwind'],
        'Data Science': ['Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas', 'NumPy'],
        'Database': ['SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Firebase', 'Redis', 'Oracle', 'SQLite'],
        'Cloud & DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'CI/CD', 'Terraform', 'Linux'],
        'Mobile Development': ['Android', 'iOS', 'React Native', 'Flutter', 'Xamarin', 'Kotlin', 'Swift'],
        'Soft Skills': ['Project Management', 'Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking', 'Time Management']
    }
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF file"""
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text
    
    @staticmethod
    def extract_skills_from_text(text):
        """Extract skills from text using keyword matching and NLP"""
        found_skills = {
            'Programming': [],
            'Web Development': [],
            'Data Science': [],
            'Database': [],
            'Cloud & DevOps': [],
            'Mobile Development': [],
            'Soft Skills': []
        }
        
        text_lower = text.lower()
        
        for category, skills in CVParser.SKILLS_DB.items():
            for skill in skills:
                # Check for exact match or word boundary
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
        
        # Remove empty categories
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills
    
    @staticmethod
    def extract_email(text):
        """Extract email from text"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None
    
    @staticmethod
    def extract_phone(text):
        """Extract phone number from text"""
        # Ghana phone numbers and international formats
        phone_patterns = [
            r'(\+233|0)[0-9]{9}',
            r'\(\+233\)[0-9]{9}',
            r'[0-9]{3}[-. ]?[0-9]{3}[-. ]?[0-9]{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        return None
    
    @staticmethod
    def extract_experience_years(text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*years?\s+of\s+experience',
            r'experience\s+of\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+exp'
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        return 0
    
    @staticmethod
    def parse_cv(file_path):
        """Main method to parse CV and extract all information"""
        # Determine file type and extract text
        if file_path.endswith('.pdf'):
            text = CVParser.extract_text_from_pdf(file_path)
        elif file_path.endswith('.docx'):
            text = CVParser.extract_text_from_docx(file_path)
        else:
            return None
        
        if not text:
            return None
        
        # Extract information
        skills = CVParser.extract_skills_from_text(text)
        email = CVParser.extract_email(text)
        phone = CVParser.extract_phone(text)
        experience_years = CVParser.extract_experience_years(text)
        
        # Count total skills
        total_skills = sum(len(skills[cat]) for cat in skills)
        
        return {
            'text': text[:500] + '...' if len(text) > 500 else text,  # Preview
            'skills': skills,
            'total_skills': total_skills,
            'email': email,
            'phone': phone,
            'experience_years': experience_years,
            'word_count': len(text.split())
        }