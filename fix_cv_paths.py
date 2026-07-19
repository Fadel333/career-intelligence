# fix_cv_paths.py
import os
import shutil
from app import create_app
from models import JobApplication

app = create_app()

with app.app_context():
    apps = JobApplication.query.all()
    
    if not apps:
        print("No applications found.")
        exit()
    
    for app_obj in apps:
        if not app_obj.cv_filepath:
            continue
        
        filename = os.path.basename(app_obj.cv_filepath)
        
        # Check where the file actually is
        possible_locations = [
            os.path.join('static', 'applications', filename),
            os.path.join('app', 'static', 'applications', filename),
            os.path.join('..', 'static', 'applications', filename),
        ]
        
        found = False
        for loc in possible_locations:
            if os.path.exists(loc):
                print(f"✅ Found file: {loc}")
                # Update the database with the correct path
                app_obj.cv_filepath = loc.replace('\\', '/')
                found = True
                break
        
        if not found:
            print(f"❌ File not found: {filename}")
            print(f"   Looking in: {possible_locations}")