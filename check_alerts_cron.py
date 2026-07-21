# check_alerts_cron.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.utils.job_alert_checker import check_job_alerts

app = create_app()
with app.app_context():
    print("🚀 Starting job alert check...")
    sent, errors = check_job_alerts()
    print(f"✅ Done: {sent} sent, {errors} errors")