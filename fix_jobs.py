# fix_jobs.py
from app import create_app
from extensions import db
from models import Job, JobStatus

app = create_app()

with app.app_context():
    print("🔍 Checking all jobs...")
    
    # Show all jobs
    all_jobs = Job.query.all()
    print(f"Total jobs: {len(all_jobs)}")
    
    if all_jobs:
        for job in all_jobs:
            print(f"  ID: {job.id} - {job.title}")
            print(f"    Status: {job.status.value}")
            print(f"    Recruiter ID: {job.recruiter_id}")
    else:
        print("❌ No jobs found in database!")
        print("   Try creating a job through the recruiter portal.")
    
    # Publish all draft jobs
    draft_jobs = Job.query.filter_by(status=JobStatus.DRAFT).all()
    if draft_jobs:
        print(f"\n📦 Found {len(draft_jobs)} draft jobs. Publishing them...")
        for job in draft_jobs:
            job.status = JobStatus.PUBLISHED
            print(f"  ✅ Published: {job.title}")
        db.session.commit()
        print("✅ All draft jobs published!")
    else:
        print("\n✅ No draft jobs found.")
    
    # Verify published jobs
    published_jobs = Job.query.filter_by(status=JobStatus.PUBLISHED).all()
    print(f"\n📋 Published jobs: {len(published_jobs)}")
    for job in published_jobs:
        print(f"  - {job.id}: {job.title}")