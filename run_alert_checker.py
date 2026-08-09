# run_alert_checker.py
#!/usr/bin/env python
"""
Standalone script for running job alert checker.
Used by Render CRON jobs.
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, '.env'))
except ImportError:
    pass

from app import create_app
from app.utils.job_alert_checker import check_job_alerts

def main():
    print("🔔 Starting job alert checker...")
    app = create_app()
    with app.app_context():
        sent, errors = check_job_alerts()
    print(f"✅ Done: {sent} sent, {errors} errors")
    return 0 if errors == 0 else 1

if __name__ == '__main__':
    sys.exit(main())