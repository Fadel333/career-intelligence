# update_cv_paths.py
from app import create_app
from extensions import db  # Add this import
from models import JobApplication
import os

app = create_app()

with app.app_context():
    apps = JobApplication.query.all()
    
    if not apps:
        print("No applications found.")
        exit()
    
    updated = 0
    for app_obj in apps:
        if not app_obj.cv_filepath:
            continue
        
        filename = os.path.basename(app_obj.cv_filepath)
        
        # Correct path
        correct_path = f"static/applications/{filename}".replace('\\', '/')
        
        if app_obj.cv_filepath != correct_path:
            app_obj.cv_filepath = correct_path
            updated += 1
            print(f"✅ Updated: {filename}")
            print(f"   New path: {correct_path}")
    
    db.session.commit()  # Now db is defined
    print(f"\n✅ Updated {updated} records with correct paths.")