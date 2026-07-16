# seed_jobs.py
from app import create_app
from extensions import db
from models import Job, RecruiterProfile, JobStatus, EmploymentType
from datetime import datetime, timedelta

app = create_app()

def create_jobs():
    with app.app_context():
        # Find a recruiter
        recruiter = RecruiterProfile.query.first()
        if not recruiter:
            print('❌ No recruiter found. Please create a recruiter first.')
            print('   Run: python create_recruiter.py')
            return
        
        print(f'✅ Found recruiter: {recruiter.company_name} (ID: {recruiter.id})')
        
        # List of jobs to create
        jobs_data = [
            {
                'title': 'Senior Software Engineer',
                'description': 'We are looking for an experienced Senior Software Engineer to join our team. You will be responsible for building and maintaining our core products, leading development efforts, and mentoring junior developers.',
                'requirements': [
                    "Bachelor's degree in Computer Science or related field",
                    '5+ years of experience in software development',
                    'Strong problem-solving skills',
                    'Experience with Python, Django, and React'
                ],
                'responsibilities': [
                    'Lead development of new features',
                    'Mentor junior developers',
                    'Architect scalable solutions',
                    'Code review and quality assurance'
                ],
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'senior',
                'salary_min': 8000,
                'salary_max': 12000,
                'currency': 'GHS',
                'location': 'Accra, Ghana',
                'remote_available': True,
                'required_skills': ['Python', 'Django', 'React', 'AWS', 'Docker'],
                'preferred_skills': ['TypeScript', 'GraphQL', 'Kubernetes']
            },
            {
                'title': 'UI/UX Designer',
                'description': 'We are seeking a creative UI/UX Designer to design beautiful and intuitive user interfaces for our products. You will work closely with product managers and developers to create exceptional user experiences.',
                'requirements': [
                    '3+ years of experience in UI/UX design',
                    'Strong portfolio required',
                    'Experience with Figma or Sketch',
                    'Understanding of user-centered design principles'
                ],
                'responsibilities': [
                    'Design user interfaces for web and mobile',
                    'Create wireframes, prototypes, and mockups',
                    'Conduct user research and usability testing',
                    'Collaborate with developers on implementation'
                ],
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'mid',
                'salary_min': 5000,
                'salary_max': 8000,
                'currency': 'GHS',
                'location': 'Remote',
                'remote_available': True,
                'required_skills': ['Figma', 'UI Design', 'UX Research', 'Prototyping'],
                'preferred_skills': ['Adobe XD', 'Animation', 'Design Systems']
            },
            {
                'title': 'DevOps Engineer',
                'description': 'We are looking for a DevOps Engineer to help us build and maintain our cloud infrastructure. You will be responsible for CI/CD pipelines, monitoring, and infrastructure automation.',
                'requirements': [
                    '3+ years of experience in DevOps',
                    'Experience with AWS or Azure',
                    'Knowledge of Docker and Kubernetes',
                    'Strong scripting skills (Python/Bash)'
                ],
                'responsibilities': [
                    'Build and maintain CI/CD pipelines',
                    'Manage cloud infrastructure',
                    'Implement monitoring and alerting',
                    'Automate deployment processes'
                ],
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'mid',
                'salary_min': 7000,
                'salary_max': 10000,
                'currency': 'GHS',
                'location': 'Accra, Ghana',
                'remote_available': True,
                'required_skills': ['AWS', 'Docker', 'Kubernetes', 'Jenkins', 'Terraform'],
                'preferred_skills': ['Ansible', 'Prometheus', 'Grafana']
            },
            {
                'title': 'Data Scientist',
                'description': 'We are seeking a Data Scientist to help us extract insights from our data. You will work on machine learning models, data analysis, and predictive analytics.',
                'requirements': [
                    'Master\'s degree in Data Science or related field',
                    '2+ years of experience in data science',
                    'Experience with Python, Pandas, and Scikit-learn',
                    'Knowledge of machine learning algorithms'
                ],
                'responsibilities': [
                    'Build and train machine learning models',
                    'Perform exploratory data analysis',
                    'Create data visualizations',
                    'Collaborate with product and engineering teams'
                ],
                'employment_type': EmploymentType.FULL_TIME,
                'experience_level': 'mid',
                'salary_min': 6000,
                'salary_max': 9000,
                'currency': 'GHS',
                'location': 'Remote',
                'remote_available': True,
                'required_skills': ['Python', 'Pandas', 'Scikit-learn', 'TensorFlow', 'SQL'],
                'preferred_skills': ['PyTorch', 'Spark', 'Tableau']
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for job_data in jobs_data:
            # Check if job already exists
            existing = Job.query.filter_by(title=job_data['title']).first()
            if existing:
                print(f'⏭️  Job already exists: {existing.title}')
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
                remote_available=job_data['remote_available'],
                required_skills=job_data['required_skills'],
                preferred_skills=job_data['preferred_skills'],
                status=JobStatus.PUBLISHED,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(job)
            created_count += 1
        
        db.session.commit()
        
        print(f'\n✅ Summary:')
        print(f'   Created: {created_count} jobs')
        print(f'   Skipped: {skipped_count} jobs (already exist)')
        
        # Show all jobs
        all_jobs = Job.query.all()
        print(f'\n📋 All jobs in database:')
        for job in all_jobs:
            print(f'   {job.id}: {job.title} - {job.location} - {job.status.value}')

if __name__ == '__main__':
    create_jobs()