import re
import spacy
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import Counter

class AdvancedCVParser:
    """Advanced CV parsing using spaCy NLP - No external dependencies"""
    
    def __init__(self):
        """Initialize spaCy models"""
        try:
            self.nlp = spacy.load("en_core_web_md")
        except:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                import subprocess
                subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
                self.nlp = spacy.load("en_core_web_sm")
        
        # Load comprehensive skill database
        self.skill_database = self._load_skill_database()
        self.soft_skills = self._load_soft_skills()
        self.certifications = self._load_certifications()
    
    def _load_skill_database(self) -> Dict[str, List[str]]:
        """Comprehensive skill database with expanded categories"""
        return {
            'Programming Languages': [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Ruby',
                'Go', 'Rust', 'Swift', 'Kotlin', 'PHP', 'R', 'MATLAB', 'Scala',
                'Perl', 'Lua', 'Dart', 'Elixir', 'Clojure', 'Haskell', 'Erlang',
                'COBOL', 'Fortran', 'Assembly', 'VBA', 'Groovy', 'PowerShell',
                'Julia', 'Crystal', 'Nim', 'V', 'Zig', 'OCaml', 'F#', 'Ada'
            ],
            'Web Development': [
                'React', 'Angular', 'Vue.js', 'Next.js', 'Nuxt.js', 'Node.js',
                'Django', 'Flask', 'Spring Boot', 'Express.js', 'ASP.NET',
                'FastAPI', 'GraphQL', 'REST APIs', 'WebSockets', 'WebAssembly',
                'Tailwind CSS', 'Bootstrap', 'Sass', 'Webpack', 'Babel',
                'Redux', 'MobX', 'jQuery', 'AJAX', 'JSON', 'XML',
                'HTML5', 'CSS3', 'SCSS', 'LESS', 'Gatsby', 'Remix', 'Svelte'
            ],
            'Mobile Development': [
                'React Native', 'Flutter', 'Android', 'iOS', 'SwiftUI', 'Xamarin',
                'Kotlin', 'Java Android', 'Objective-C', 'Cordova', 'Ionic',
                'Android SDK', 'iOS SDK', 'Mobile UI/UX', 'Cross-platform',
                'Capacitor', 'NativeScript', 'PhoneGap', 'FlutterFlow'
            ],
            'Data Science & AI': [
                'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision',
                'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn', 'Pandas',
                'NumPy', 'SciPy', 'Jupyter', 'Data Analysis', 'Data Visualization',
                'Matplotlib', 'Seaborn', 'Plotly', 'Model Deployment', 'MLOps',
                'Statistical Analysis', 'A/B Testing', 'Predictive Modeling',
                'Reinforcement Learning', 'Generative AI', 'LLM', 'OpenAI',
                'LangChain', 'Hugging Face', 'BERT', 'GPT', 'Stable Diffusion',
                'Data Engineering', 'Feature Engineering', 'Model Tuning'
            ],
            'Databases': [
                'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Firebase',
                'Oracle', 'SQLite', 'Cassandra', 'Elasticsearch', 'DynamoDB',
                'Neo4j', 'MariaDB', 'Azure SQL', 'Google Cloud SQL',
                'Data Warehousing', 'ETL', 'Data Lake', 'Apache Spark',
                'Hadoop', 'Hive', 'Presto', 'Snowflake', 'BigQuery', 'Redshift'
            ],
            'Cloud & DevOps': [
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
                'Git', 'CI/CD', 'Terraform', 'Linux', 'Bash', 'Ansible',
                'Puppet', 'Chef', 'Prometheus', 'Grafana', 'Nginx', 'Apache',
                'CloudFormation', 'AWS Lambda', 'Serverless', 'ECS', 'EKS',
                'S3', 'EC2', 'RDS', 'Route53', 'VPC', 'IAM', 'CloudFront',
                'OpenShift', 'Rancher', 'Helm', 'Istio', 'Linkerd', 'Consul',
                'GitHub Actions', 'GitLab CI', 'CircleCI', 'Travis CI'
            ],
            'Security': [
                'Cybersecurity', 'Ethical Hacking', 'Penetration Testing',
                'Security Auditing', 'Encryption', 'Firewall', 'SIEM',
                'Vulnerability Assessment', 'Security Compliance', 'ISO 27001',
                'GDPR', 'Zero Trust', 'Identity Management', 'OAuth', 'JWT',
                'SSL/TLS', 'Web Security', 'Cloud Security', 'Network Security',
                'DevSecOps', 'Threat Modeling', 'Incident Response', 'SOC',
                'CISSP', 'CEH', 'OSCP', 'Security+', 'PII', 'HIPAA', 'PCI DSS'
            ],
            'Testing & QA': [
                'Unit Testing', 'Integration Testing', 'Selenium', 'Jest',
                'PyTest', 'Mocha', 'Cypress', 'Test Automation', 'QA',
                'Performance Testing', 'Load Testing', 'API Testing',
                'TestNG', 'JUnit', 'Cucumber', 'Postman', 'JMeter',
                'Katalon', 'Appium', 'TestCafe', 'Playwright', 'Cypress'
            ],
            'Design': [
                'UI/UX Design', 'Figma', 'Adobe XD', 'Sketch', 'InVision',
                'Photoshop', 'Illustrator', 'User Research', 'Wireframing',
                'Prototyping', 'Design Thinking', 'Visual Design',
                'Interaction Design', 'User Flow', 'Design Systems',
                'Framer', 'Proto.io', 'Balsamiq', 'Miro', 'Mural'
            ],
            'Business & Product': [
                'Product Management', 'Project Management', 'Agile', 'Scrum',
                'Lean', 'Kanban', 'JIRA', 'Confluence', 'Trello', 'Asana',
                'Business Analysis', 'Market Research', 'Competitive Analysis',
                'Stakeholder Management', 'Product Roadmap', 'Go-to-Market Strategy',
                'Budgeting', 'Financial Analysis', 'Cost Optimization', 'ROI Analysis',
                'Customer Development', 'User Stories', 'Sprint Planning', 'Retrospectives'
            ],
            'Soft Skills': [
                'Leadership', 'Communication', 'Teamwork', 'Problem Solving',
                'Critical Thinking', 'Time Management', 'Adaptability', 'Creativity',
                'Emotional Intelligence', 'Conflict Resolution', 'Project Management',
                'Decision Making', 'Mentoring', 'Strategic Planning', 'Presentation',
                'Negotiation', 'Analytical Thinking', 'Cross-functional Collaboration',
                'Empathy', 'Active Listening', 'Feedback', 'Coaching', 'Delegation',
                'Resilience', 'Growth Mindset', 'Cultural Awareness', 'Storytelling'
            ],
            'African Market Specific': [
                'Mobile Money', 'Fintech', 'USSD', 'SMS Marketing', 'Agent Banking',
                'Microfinance', 'AgriTech', 'HealthTech', 'E-commerce Africa',
                'Logistics Africa', 'Solar Tech', 'Off-grid Solutions',
                'Payments Integration', 'MoMo API', 'Telecom Integration',
                'Local Content', 'Language Localization', 'African User Experience',
                'Informal Economy', 'Cashless Payments', 'Digital Identity'
            ],
            'Career Development': [
                'Career Coaching', 'Resume Writing', 'Interview Preparation',
                'Personal Branding', 'Networking', 'Professional Development',
                'Public Speaking', 'Technical Writing', 'Blogging', 'Mentorship',
                'Teaching', 'Training', 'Curriculum Development', 'Workshop Facilitation',
                'Consulting', 'Advisory', 'Board Membership', 'Speaking Engagements'
            ],
            'Languages': [
                'English', 'French', 'Arabic', 'Chinese', 'Spanish', 'German',
                'Portuguese', 'Twi', 'Ga', 'Ewe', 'Hausa', 'Yoruba', 'Igbo',
                'Swahili', 'Zulu', 'Amharic', 'Somali', 'Oromo', 'Berber'
            ],
            'Project Management Methodologies': [
                'Agile', 'Scrum', 'Kanban', 'Waterfall', 'Lean', 'Six Sigma',
                'PMI', 'Prince2', 'SAFe', 'LeSS', 'Nexus', 'Disciplined Agile',
                'Extreme Programming', 'Crystal', 'Feature-Driven Development'
            ]
        }
    
    def _load_soft_skills(self) -> List[str]:
        """Load expanded soft skills list"""
        return [
            'Leadership', 'Communication', 'Teamwork', 'Problem Solving',
            'Critical Thinking', 'Time Management', 'Adaptability', 'Creativity',
            'Emotional Intelligence', 'Conflict Resolution', 'Project Management',
            'Decision Making', 'Mentoring', 'Strategic Planning', 'Presentation',
            'Negotiation', 'Analytical Thinking', 'Cross-functional Collaboration',
            'Empathy', 'Active Listening', 'Feedback', 'Coaching', 'Delegation',
            'Resilience', 'Growth Mindset', 'Cultural Awareness', 'Storytelling',
            'Influence', 'Persuasion', 'Innovation', 'Risk Management', 'People Management'
        ]
    
    def _load_certifications(self) -> List[str]:
        """Load expanded certifications list"""
        return [
            'AWS Certified', 'Google Cloud Certified', 'Azure Certified',
            'PMP', 'Certified Scrum Master', 'CISSP', 'CEH', 'CISA',
            'CompTIA Security+', 'ITIL Certified', 'Six Sigma', 'Lean',
            'TOGAF', 'Oracle Certified', 'Microsoft Certified', 'Cisco Certified',
            'AWS Solutions Architect', 'AWS Developer', 'AWS SysOps',
            'Google Professional Data Engineer', 'Google Professional Cloud Architect',
            'Azure Solutions Architect', 'Azure DevOps Engineer',
            'Red Hat Certified', 'Linux Professional Institute', 'LPIC',
            'Certified Ethical Hacker', 'OSCP', 'CISM', 'CRISC',
            'SAFe Agilist', 'Prince2 Practitioner', 'Certified Product Owner',
            'Kubernetes Administrator', 'Certified Kubernetes Application Developer',
            'HashiCorp Certified: Terraform Associate', 'Confluent Certified',
            'MongoDB Certified', 'Tableau Certified', 'Power BI Certified',
            'Salesforce Certified', 'SAP Certified', 'IBM Certified'
        ]
    
    def parse_cv(self, text: str) -> Dict[str, Any]:
        """Main parsing function returning comprehensive analysis"""
        
        # Process with spaCy
        doc = self.nlp(text)
        
        # Extract all information
        results = {
            'text': text[:500] + '...' if len(text) > 500 else text,
            'skills': self._extract_skills(doc, text),
            'soft_skills': self._extract_soft_skills(text),
            'experience_years': self._extract_experience_years(text),
            'education': self._extract_education(doc, text),
            'work_experience': self._extract_work_experience(doc, text),
            'certifications': self._extract_certifications(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'current_job_title': self._extract_job_title(doc, text),
            'summary': self._extract_summary(doc, text),
            'word_count': len(text.split()),
            'languages': self._extract_languages(text)
        }
        
        # Calculate skill level
        results['skill_level'] = self._calculate_skill_level(results['skills'])
        results['total_skills'] = sum(len(skills) for skills in results['skills'].values())
        
        return results
    
    def _extract_skills(self, doc: spacy.tokens.doc.Doc, text: str) -> Dict[str, List[str]]:
        """Extract technical skills using multiple methods"""
        
        found_skills = {category: [] for category in self.skill_database.keys()}
        text_lower = text.lower()
        
        # Method 1: Direct keyword matching
        for category, skills in self.skill_database.items():
            for skill in skills:
                # Check for exact match with word boundaries
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_skills[category].append(skill)
                else:
                    # Check for variations
                    variations = self._get_skill_variations(skill)
                    for variation in variations:
                        if variation in text_lower:
                            found_skills[category].append(skill)
                            break
        
        # Method 2: Use spaCy's named entities and context
        for ent in doc.ents:
            if ent.label_ in ['PRODUCT', 'ORG', 'WORK_OF_ART']:
                for category, skills in self.skill_database.items():
                    for skill in skills:
                        if skill.lower() in ent.text.lower():
                            if skill not in found_skills[category]:
                                found_skills[category].append(skill)
        
        # Remove duplicates and empty categories
        for category in found_skills:
            found_skills[category] = list(set(found_skills[category]))
        found_skills = {k: v for k, v in found_skills.items() if v}
        
        return found_skills
    
    def _get_skill_variations(self, skill: str) -> List[str]:
        """Generate common variations of skill names"""
        variations = []
        
        # Common tech variations
        skill_lower = skill.lower()
        
        if skill_lower in ['machine learning', 'ml']:
            variations = ['machine learning engineer', 'ml engineer', 'ai/ml']
        elif skill_lower in ['deep learning', 'dl']:
            variations = ['deep learning engineer', 'neural networks']
        elif skill_lower in ['nlp', 'natural language processing']:
            variations = ['nlp engineer', 'natural language understanding']
        elif skill_lower == 'sql':
            variations = ['structured query language', 'sql developer']
        elif skill_lower == 'aws':
            variations = ['amazon web services', 'aws cloud', 'aws engineer']
        elif skill_lower == 'docker':
            variations = ['containerization', 'docker container', 'docker compose']
        elif skill_lower == 'kubernetes':
            variations = ['k8s', 'container orchestration', 'kubernetes engineer']
        elif skill_lower in ['react', 'reactjs']:
            variations = ['react.js', 'react developer', 'react native']
        elif skill_lower in ['node.js', 'node']:
            variations = ['nodejs', 'node developer']
        elif skill_lower == 'python':
            variations = ['python developer', 'python programming', 'python engineer']
        elif skill_lower == 'javascript':
            variations = ['js', 'javascript developer', 'es6']
        elif skill_lower == 'typescript':
            variations = ['ts', 'typescript developer']
        elif skill_lower == 'django':
            variations = ['django developer', 'django rest framework']
        elif skill_lower == 'flask':
            variations = ['flask developer', 'flask api']
        elif skill_lower == 'tensorflow':
            variations = ['tensorflow developer', 'tf', 'tensorflow engineer']
        elif skill_lower == 'pytorch':
            variations = ['pytorch developer', 'torch']
        elif skill_lower == 'git':
            variations = ['git version control', 'github', 'gitlab']
        elif skill_lower == 'linux':
            variations = ['linux administration', 'linux engineer']
        elif skill_lower == 'bash':
            variations = ['bash scripting', 'shell scripting']
        elif skill_lower in ['jenkins', 'ci/cd']:
            variations = ['jenkins pipeline', 'ci cd pipeline']
        
        return variations
    
    def _extract_soft_skills(self, text: str) -> List[str]:
        """Extract soft skills from text"""
        found_skills = []
        text_lower = text.lower()
        
        for skill in self.soft_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience with improved accuracy"""
        patterns = [
            r'(\d+)\+?\s*years?\s*of\s+experience',
            r'experience\s+of\s+(\d+)\+?\s*years?',
            r'(\d+)\+?\s*yrs?\s+exp',
            r'(\d+)\s*year\s+experience',
            r'(\d+)\s*\+\s*years',
            r'(\d+)\+? years',
            r'(\d+)-(\d+)\s+years'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                # If range (e.g., 5-8 years), take average
                if '-' in match.group(0):
                    years = match.group(1)
                    if years:
                        return int(years)
                return int(match.group(1))
        
        # Try to infer from job dates
        date_pattern = r'(19|20)\d{2}'
        dates = re.findall(date_pattern, text)
        if dates:
            current_year = datetime.now().year
            years = sum(1 for date in dates if int(date) < current_year)
            return min(years, 20)  # Cap at 20 years
        
        return 0
    
    def _extract_education(self, doc: spacy.tokens.doc.Doc, text: str) -> List[Dict]:
        """Extract education information with degree and institution"""
        
        education = []
        
        # Patterns for degree types
        degree_patterns = {
            'PhD': r'(PhD|Ph\.D|Doctor of Philosophy|DPhil|Doctorate|DBA|Dr\.)',
            'Master': r'(Master|MSc|M\.Sc|MS|M\.S|MBA|M\.B\.A|MEng|M\.Eng|MEd|M\.Ed|MA|M\.A|MPH)',
            'Bachelor': r'(Bachelor|BSc|B\.Sc|BS|B\.S|BBA|B\.B\.A|BEng|B\.Eng|BCom|BA|B\.A|BEd|B\.Ed)',
            'Diploma': r'(Diploma|HND|Higher National Diploma|Associate|A-level)',
            'Certificate': r'(Certificate|Cert|Certification|Professional Certificate)',
            'Professional': r'(Professional|Executive|Fellow|Chartered)'
        }
        
        # Extract education using patterns
        for degree_type, pattern in degree_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the degree
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 60)
                context = text[start:end]
                
                # Look for institution names
                institutions = [
                    r'(University|College|Institute|School|Academy|Polytechnic|Business School)\s+of?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                    r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(University|College|Institute)'
                ]
                
                institution = 'Unknown Institution'
                for inst_pattern in institutions:
                    inst_match = re.search(inst_pattern, context, re.IGNORECASE)
                    if inst_match:
                        institution = inst_match.group(0)
                        break
                
                # Look for GPA/grade
                gpa_pattern = r'GPA[:;]?\s*([0-9]+\.[0-9]+)'
                gpa_match = re.search(gpa_pattern, context, re.IGNORECASE)
                gpa = gpa_match.group(1) if gpa_match else None
                
                education.append({
                    'degree': degree_type,
                    'institution': institution,
                    'year': self._extract_year(context),
                    'gpa': gpa,
                    'description': match.group(0)
                })
        
        # Remove duplicates
        seen = set()
        unique_education = []
        for edu in education:
            key = f"{edu['degree']}_{edu['institution']}"
            if key not in seen:
                seen.add(key)
                unique_education.append(edu)
        
        return unique_education
    
    def _extract_work_experience(self, doc: spacy.tokens.doc.Doc, text: str) -> List[Dict]:
        """Extract work experience with job titles and companies"""
        
        experiences = []
        
        # Common job title patterns
        job_patterns = [
            r'(Engineer|Developer|Manager|Analyst|Designer|Architect|Consultant|Director|Lead|Specialist|Administrator|Coordinator|Officer|Assistant|Executive|Principal|Senior|Staff)',
            r'(Software|Data|Security|Network|Systems|Frontend|Backend|Full Stack|DevOps|QA|Product|Project|Program|Technical|Business|Machine Learning|AI|Cloud|Sales)'
        ]
        
        # Extract job titles
        job_titles = []
        for pattern in job_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end]
                
                # Look for company names
                company_patterns = [
                    r'at\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Za-z0-9]+)*)',
                    r'with\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Za-z0-9]+)*)',
                    r'for\s+([A-Z][a-zA-Z0-9]+(?:\s+[A-Za-z0-9]+)*)'
                ]
                
                company = 'Unknown Company'
                for comp_pattern in company_patterns:
                    comp_match = re.search(comp_pattern, context, re.IGNORECASE)
                    if comp_match:
                        company = comp_match.group(1)
                        break
                
                # Look for dates
                date_pattern = r'(19|20)\d{2}'
                years = re.findall(date_pattern, context)
                start_year = years[0] if years else None
                end_year = years[1] if len(years) > 1 else None
                
                experiences.append({
                    'title': match.group(0),
                    'company': company,
                    'start_year': start_year,
                    'end_year': end_year,
                    'description': context.strip()
                })
        
        # Remove duplicates
        seen = set()
        unique_experiences = []
        for exp in experiences:
            key = f"{exp['title']}_{exp['company']}"
            if key not in seen:
                seen.add(key)
                unique_experiences.append(exp)
        
        return unique_experiences
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text"""
        found_certs = []
        text_lower = text.lower()
        
        for cert in self.certifications:
            if cert.lower() in text_lower:
                found_certs.append(cert)
            # Check for variations
            cert_parts = cert.split()
            if len(cert_parts) > 1:
                for part in cert_parts:
                    if part.lower() in text_lower and len(part) > 2:
                        found_certs.append(cert)
                        break
        
        return list(set(found_certs))
    
    def _extract_email(self, text: str) -> str:
        """Extract email addresses"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(pattern, text)
        return matches[0] if matches else None
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone numbers (supports Ghana and international formats)"""
        patterns = [
            r'(\+233|0)[0-9]{9}',
            r'\(\+233\)[0-9]{9}',
            r'[0-9]{3}[-. ]?[0-9]{3}[-. ]?[0-9]{4}',
            r'\+[0-9]{1,3}[0-9]{7,10}',
            r'\([0-9]{3}\)\s*[0-9]{3}[-. ]?[0-9]{4}'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None
    
    def _extract_job_title(self, doc: spacy.tokens.doc.Doc, text: str) -> str:
        """Extract current or primary job title"""
        
        # Look for job titles near "current", "now", "present"
        patterns = [
            r'(current|now|present).{0,50}(Engineer|Developer|Manager|Analyst|Designer|Architect|Consultant|Director|Lead|Specialist)',
            r'(Engineer|Developer|Manager|Analyst|Designer|Architect|Consultant|Director|Lead|Specialist).{0,50}(current|now|present)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Try to find from first position in employment history
        job_titles = self._extract_work_experience(doc, text)
        if job_titles:
            return job_titles[0]['title']
        
        return None
    
    def _extract_summary(self, doc: spacy.tokens.doc.Doc, text: str) -> str:
        """Extract professional summary"""
        
        # Look for summary sections
        patterns = [
            r'(summary|profile|about me).{0,200}',
            r'(professional summary).{0,200}',
            r'(career objective).{0,200}',
            r'(personal statement).{0,200}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()
        
        # Take first paragraph as summary
        paragraphs = text.split('\n\n')
        if paragraphs:
            return paragraphs[0][:500] + '...' if len(paragraphs[0]) > 500 else paragraphs[0]
        
        return None
    
    def _extract_year(self, text: str) -> str:
        """Extract year from text"""
        pattern = r'(19|20)\d{2}'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _calculate_skill_level(self, skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Calculate skill level based on number and variety of skills"""
        
        total_skills = sum(len(skills_list) for skills_list in skills.values())
        
        if total_skills >= 25:
            level = 'Expert'
            percentage = 95
        elif total_skills >= 18:
            level = 'Advanced'
            percentage = 80
        elif total_skills >= 12:
            level = 'Intermediate'
            percentage = 65
        elif total_skills >= 6:
            level = 'Beginner'
            percentage = 45
        else:
            level = 'Novice'
            percentage = 20
        
        return {
            'level': level,
            'percentage': percentage,
            'total_skills': total_skills,
            'categories': len(skills)
        }
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from text"""
        found_languages = []
        text_lower = text.lower()
        
        languages = [
            'English', 'French', 'Arabic', 'Chinese', 'Spanish', 'German',
            'Portuguese', 'Twi', 'Ga', 'Ewe', 'Hausa', 'Yoruba', 'Igbo',
            'Swahili', 'Zulu', 'Amharic', 'Somali', 'Oromo', 'Berber',
            'Italian', 'Dutch', 'Russian', 'Japanese', 'Korean', 'Hindi'
        ]
        
        for lang in languages:
            if lang.lower() in text_lower:
                found_languages.append(lang)
        
        return found_languages

def parse_cv_quick(self, text: str) -> Dict[str, Any]:
    """Quick parse CV - faster but less detailed"""
    
    results = {
        'text': text[:500] + '...' if len(text) > 500 else text,
        'skills': self._extract_skills_fast(text),
        'soft_skills': self._extract_soft_skills(text),
        'experience_years': self._extract_experience_years(text),
        'email': self._extract_email(text),
        'phone': self._extract_phone(text),
        'word_count': len(text.split()),
        'total_skills': 0
    }
    
    # Calculate total skills
    results['total_skills'] = sum(len(skills) for skills in results['skills'].values())
    
    return results

def _extract_skills_fast(self, text: str) -> Dict[str, List[str]]:
    """Fast skill extraction - uses simple matching without spaCy"""
    
    found_skills = {category: [] for category in self.skill_database.keys()}
    text_lower = text.lower()
    
    for category, skills in self.skill_database.items():
        for skill in skills:
            if skill.lower() in text_lower:
                found_skills[category].append(skill)
    
    # Remove duplicates and empty categories
    for category in found_skills:
        found_skills[category] = list(set(found_skills[category]))
    found_skills = {k: v for k, v in found_skills.items() if v}
    
    return found_skills