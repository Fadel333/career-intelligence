# check_jobs.py
from app import create_app
from extensions import db
from models import Job, JobStatus

app = create_app()

with app.app_context():
    all_jobs = Job.query.all()
    print(f'Total jobs: {len(all_jobs)}')
    
    if all_jobs:
        for job in all_jobs:
            print(f'  ID: {job.id} - {job.title}')
            print(f'    Status: {job.status.value}')
            print(f'    Recruiter ID: {job.recruiter_id}')
            print(f'    Posted: {job.posted_at}')
            print('---')
    else:
        print('No jobs found in database!')