# app/cli.py
import click
from flask.cli import with_appcontext
from app.utils.job_alert_checker import check_job_alerts
from app.utils.email import send_test_email
from models import db, User

@click.command('check-alerts')
@with_appcontext
def check_alerts_command():
    """Check and send job alerts."""
    print("🚀 Running job alert checker...")
    try:
        sent, errors = check_job_alerts()
        click.echo(f"✅ Complete: {sent} alerts sent, {errors} errors")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

@click.command('test-email')
@with_appcontext
@click.argument('email')
def test_email_command(email):
    """Send a test email to verify email configuration."""
    print(f"📧 Sending test email to {email}...")
    try:
        from app.utils.email import send_test_email
        result = send_test_email(email)
        if result:
            click.echo(f"✅ Test email sent successfully to {email}")
        else:
            click.echo(f"❌ Failed to send test email to {email}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")

def register_commands(app):
    """Register CLI commands."""
    app.cli.add_command(check_alerts_command)
    app.cli.add_command(test_email_command)