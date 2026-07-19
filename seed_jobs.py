# create_real_jobs.py
from app import create_app
from extensions import db
from models import Job, RecruiterProfile, JobStatus, EmploymentType
from datetime import datetime, timedelta

app = create_app()

def create_real_jobs():
    with app.app_context():
        # Find a recruiter
        recruiter = RecruiterProfile.query.first()
        
        if not recruiter:
            print('❌ No recruiter found. Creating one...')
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Create user
            user = User(
                fullname='FADTECH Labs',
                email='jobs@fadtechlabs.com',
                password=generate_password_hash('recruiter123'),
                user_type='recruiter',
                is_active=True,
                is_verified=True
            )
            db.session.add(user)
            db.session.flush()
            
            # Create recruiter profile
            recruiter = RecruiterProfile(
                user_id=user.id,
                company_name='FADTECH Labs',
                company_description='Building Africa\'s employability intelligence infrastructure.',
                industry='Technology',
                location='Accra, Ghana',
                verification_status='approved'
            )
            db.session.add(recruiter)
            db.session.commit()
            print(f'✅ Created recruiter: {recruiter.company_name}')
        
        print(f'✅ Using recruiter: {recruiter.company_name}')
        
        # ============================================
        # REAL JOB POSTINGS
        # ============================================
        jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'FADTECH Labs',
                'location': 'Accra, Ghana',
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'senior',
                'salary_min': 12000,
                'salary_max': 18000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is looking for a Senior Software Engineer to join our growing team. You will be responsible for building and maintaining our Career Intelligence platform that serves thousands of users across Africa.

This is a hands-on role where you'll work with a modern tech stack, mentor junior developers, and help shape the future of our product.

Key Responsibilities:
• Lead development of new features and services
• Architect scalable solutions using Python and Django
• Mentor and guide junior team members
• Collaborate with product and design teams
• Write clean, maintainable, and well-tested code
• Participate in code reviews and technical planning

Requirements:
• 5+ years of software development experience
• Strong experience with Python, Django, and React
• Experience with PostgreSQL and AWS
• Knowledge of Docker and containerization
• Experience leading technical projects
• Excellent problem-solving skills
• Bachelor's degree in Computer Science or related field

What We Offer:
• Competitive salary and benefits
• Flexible work arrangements
• Opportunity to make a real impact
• Professional development budget
• Health insurance
• Quarterly team retreats
""",
                'requirements': [
                    "5+ years of software development experience",
                    "Strong experience with Python, Django, and React",
                    "Experience with PostgreSQL and AWS",
                    "Knowledge of Docker and containerization",
                    "Experience leading technical projects",
                    "Bachelor's degree in Computer Science or related field"
                ],
                'responsibilities': [
                    "Lead development of new features and services",
                    "Architect scalable solutions using Python and Django",
                    "Mentor and guide junior team members",
                    "Collaborate with product and design teams",
                    "Write clean, maintainable, and well-tested code",
                    "Participate in code reviews and technical planning"
                ],
                'required_skills': ['Python', 'Django', 'React', 'PostgreSQL', 'AWS', 'Docker', 'Git'],
                'preferred_skills': ['TypeScript', 'GraphQL', 'Kubernetes', 'Redis']
            },
            {
                'title': 'Product Manager',
                'company': 'FADTECH Labs',
                'location': 'Accra, Ghana (Hybrid)',
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'senior',
                'salary_min': 10000,
                'salary_max': 15000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is seeking a Product Manager to lead the development of our Career Intelligence platform. You will be responsible for defining product strategy, gathering requirements, and working with engineering to deliver features that solve real problems for African job seekers and employers.

Key Responsibilities:
• Define product vision and strategy
• Gather and prioritize requirements from users and stakeholders
• Work with engineering to plan and execute releases
• Analyze user data to inform product decisions
• Coordinate with marketing and sales teams
• Monitor product performance and user feedback

Requirements:
• 5+ years of product management experience
• Experience with B2B and B2C products
• Strong analytical and problem-solving skills
• Excellent communication and collaboration skills
• Understanding of the African tech ecosystem
• Experience with agile development methodologies
• Bachelor's degree in Business, Computer Science, or related field

What We Offer:
• Competitive salary and benefits
• Opportunity to shape a high-impact product
• Work with a passionate team
• Professional development opportunities
• Health insurance
• Flexible work arrangements
""",
                'requirements': [
                    "5+ years of product management experience",
                    "Experience with B2B and B2C products",
                    "Strong analytical and problem-solving skills",
                    "Excellent communication and collaboration skills",
                    "Understanding of the African tech ecosystem",
                    "Experience with agile development methodologies"
                ],
                'responsibilities': [
                    "Define product vision and strategy",
                    "Gather and prioritize requirements from users and stakeholders",
                    "Work with engineering to plan and execute releases",
                    "Analyze user data to inform product decisions",
                    "Coordinate with marketing and sales teams",
                    "Monitor product performance and user feedback"
                ],
                'required_skills': ['Product Strategy', 'Agile', 'Analytics', 'Communication', 'Leadership'],
                'preferred_skills': ['UX Design', 'Data Analysis', 'SaaS Experience']
            },
            {
                'title': 'Data Scientist - AI/ML',
                'company': 'FADTECH Labs',
                'location': 'Remote (Africa-based)',
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'mid',
                'salary_min': 9000,
                'salary_max': 14000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is looking for a Data Scientist to join our AI team. You will work on cutting-edge machine learning models for resume parsing, skill gap analysis, and job matching. Your work will directly impact how we help thousands of African job seekers find better career opportunities.

Key Responsibilities:
• Develop and maintain ML models for resume parsing and skill extraction
• Build recommendation systems for job matching
• Analyze labor market data to identify trends
• Collaborate with engineering to deploy models to production
• Research and implement state-of-the-art NLP techniques
• Communicate findings to stakeholders

Requirements:
• 3+ years of experience in Data Science or ML
• Strong experience with Python and ML frameworks (PyTorch, TensorFlow, or scikit-learn)
• Experience with NLP and text processing
• Knowledge of SQL and data analysis
• Experience with deploying ML models
• Strong analytical and communication skills
• Master's or PhD in Computer Science, Data Science, or related field

What We Offer:
• Competitive salary and benefits
• Work on meaningful problems
• Remote-first culture
• Professional development budget
• Flexible work arrangements
• Opportunity to present at conferences
""",
                'requirements': [
                    "3+ years of experience in Data Science or ML",
                    "Strong experience with Python and ML frameworks",
                    "Experience with NLP and text processing",
                    "Knowledge of SQL and data analysis",
                    "Experience with deploying ML models",
                    "Strong analytical and communication skills"
                ],
                'responsibilities': [
                    "Develop and maintain ML models for resume parsing and skill extraction",
                    "Build recommendation systems for job matching",
                    "Analyze labor market data to identify trends",
                    "Collaborate with engineering to deploy models to production",
                    "Research and implement state-of-the-art NLP techniques",
                    "Communicate findings to stakeholders"
                ],
                'required_skills': ['Python', 'Machine Learning', 'NLP', 'PyTorch', 'SQL', 'Data Analysis'],
                'preferred_skills': ['FastAPI', 'Docker', 'AWS', 'Research Background']
            },
            {
                'title': 'Full Stack Developer',
                'company': 'FADTECH Labs',
                'location': 'Accra, Ghana',
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'mid',
                'salary_min': 7000,
                'salary_max': 12000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is seeking a Full Stack Developer to join our engineering team. You will work on both frontend and backend development, building features that help job seekers and employers connect more effectively.

Key Responsibilities:
• Build and maintain web applications using React and Python/Django
• Design and implement RESTful APIs
• Write clean, maintainable, and well-tested code
• Collaborate with product and design teams
• Participate in code reviews and technical discussions
• Troubleshoot and debug production issues

Requirements:
• 3+ years of full stack development experience
• Strong experience with Python (Django/Flask) and React
• Experience with PostgreSQL or other relational databases
• Knowledge of REST APIs and web services
• Familiarity with Git and collaborative development
• Strong problem-solving skills
• Bachelor's degree in Computer Science or related field

What We Offer:
• Competitive salary and benefits
• Opportunity to learn and grow
• Work on a meaningful product
• Health insurance
• Flexible work arrangements
• Regular team events
""",
                'requirements': [
                    "3+ years of full stack development experience",
                    "Strong experience with Python (Django/Flask) and React",
                    "Experience with PostgreSQL or other relational databases",
                    "Knowledge of REST APIs and web services",
                    "Familiarity with Git and collaborative development",
                    "Strong problem-solving skills"
                ],
                'responsibilities': [
                    "Build and maintain web applications using React and Python/Django",
                    "Design and implement RESTful APIs",
                    "Write clean, maintainable, and well-tested code",
                    "Collaborate with product and design teams",
                    "Participate in code reviews and technical discussions",
                    "Troubleshoot and debug production issues"
                ],
                'required_skills': ['Python', 'Django', 'React', 'JavaScript', 'PostgreSQL', 'Git'],
                'preferred_skills': ['TypeScript', 'Flask', 'AWS', 'Tailwind CSS']
            },
            {
                'title': 'DevOps Engineer',
                'company': 'FADTECH Labs',
                'location': 'Remote (Africa-based)',
                'employment_type': EmploymentType.REMOTE,
                'experience_level': 'senior',
                'salary_min': 10000,
                'salary_max': 16000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is looking for a DevOps Engineer to help us scale our infrastructure. You will be responsible for our cloud architecture, CI/CD pipelines, and ensuring our platform is reliable and performant.

Key Responsibilities:
• Design and maintain cloud infrastructure (AWS)
• Build and improve CI/CD pipelines
• Implement monitoring and alerting systems
• Automate deployment processes
• Ensure security best practices
• Troubleshoot production issues

Requirements:
• 4+ years of DevOps experience
• Strong experience with AWS (EC2, S3, RDS, Lambda)
• Experience with Docker and Kubernetes
• Knowledge of CI/CD tools (Jenkins, GitLab CI, or GitHub Actions)
• Experience with infrastructure as code (Terraform or CloudFormation)
• Strong scripting skills (Python/Bash)
• Understanding of networking and security

What We Offer:
• Competitive salary and benefits
• Opportunity to build infrastructure from the ground up
• Remote-first culture
• Professional development budget
• Flexible work arrangements
• Work with a passionate team
""",
                'requirements': [
                    "4+ years of DevOps experience",
                    "Strong experience with AWS (EC2, S3, RDS, Lambda)",
                    "Experience with Docker and Kubernetes",
                    "Knowledge of CI/CD tools",
                    "Experience with infrastructure as code",
                    "Strong scripting skills (Python/Bash)",
                    "Understanding of networking and security"
                ],
                'responsibilities': [
                    "Design and maintain cloud infrastructure (AWS)",
                    "Build and improve CI/CD pipelines",
                    "Implement monitoring and alerting systems",
                    "Automate deployment processes",
                    "Ensure security best practices",
                    "Troubleshoot production issues"
                ],
                'required_skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Terraform', 'Python', 'Bash'],
                'preferred_skills': ['Prometheus', 'Grafana', 'Ansible', 'GitHub Actions']
            },
            {
                'title': 'Technical Writer / Content Creator',
                'company': 'FADTECH Labs',
                'location': 'Accra, Ghana',
                'employment_type': EmploymentType.PART_TIME,
                'experience_level': 'mid',
                'salary_min': 4000,
                'salary_max': 6000,
                'currency': 'GHS',
                'description': """
FADTECH Labs is seeking a talented Technical Writer to create content about career development, technology, and the African tech ecosystem. You will write blog posts, guides, and educational content for our users.

Key Responsibilities:
• Write blog posts and articles about career development and technology
• Create educational content for job seekers
• Develop guides and tutorials
• Collaborate with the team on content strategy
• Edit and proofread content
• Stay up-to-date with industry trends

Requirements:
• 2+ years of technical writing or content creation experience
• Excellent writing and communication skills
• Understanding of the African tech ecosystem
• Ability to explain complex topics simply
• Experience with SEO and content marketing
• Portfolio of published work
• Bachelor's degree in Communications, Journalism, or related field

What We Offer:
• Flexible work arrangements
• Opportunity to build your portfolio
• Work with a passionate team
• Competitive compensation
• Professional development opportunities
""",
                'requirements': [
                    "2+ years of technical writing or content creation experience",
                    "Excellent writing and communication skills",
                    "Understanding of the African tech ecosystem",
                    "Ability to explain complex topics simply",
                    "Experience with SEO and content marketing",
                    "Portfolio of published work"
                ],
                'responsibilities': [
                    "Write blog posts and articles about career development and technology",
                    "Create educational content for job seekers",
                    "Develop guides and tutorials",
                    "Collaborate with the team on content strategy",
                    "Edit and proofread content",
                    "Stay up-to-date with industry trends"
                ],
                'required_skills': ['Writing', 'Editing', 'SEO', 'Research', 'Content Strategy'],
                'preferred_skills': ['HTML', 'Career Development Knowledge', 'Marketing']
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for job_data in jobs:
            # Check if job already exists
            existing = Job.query.filter_by(title=job_data['title']).first()
            if existing:
                print(f'⏭️  Job already exists: {job_data["title"]}')
                skipped_count += 1
                continue
            
            # Create job
            job = Job(
                recruiter_id=recruiter.id,
                poster_id=recruiter.user_id,
                title=job_data['title'],
                description=job_data['description'],
                requirements=job_data['requirements'],
                responsibilities=job_data['responsibilities'],
                employment_type=job_data['employment_type'],
                experience_level=job_data['experience_level'],
                salary_min=job_data['salary_min'],
                salary_max=job_data['salary_max'],
                currency=job_data['currency'],
                location=job_data['location'],
                remote_available=True if 'Remote' in job_data['location'] else False,
                required_skills=job_data['required_skills'],
                preferred_skills=job_data['preferred_skills'],
                status=JobStatus.PUBLISHED,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(job)
            created_count += 1
            print(f'✅ Created job: {job_data["title"]}')
        
        db.session.commit()
        
        print(f'\n📊 Summary:')
        print(f'   Created: {created_count} jobs')
        print(f'   Skipped: {skipped_count} jobs (already exist)')
        print(f'\n📋 All jobs in database:')
        for job in Job.query.all():
            print(f'   {job.id}: {job.title} - {job.location} - {job.status.value}')

if __name__ == '__main__':
    create_real_jobs()