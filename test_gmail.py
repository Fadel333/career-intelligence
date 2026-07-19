# test_email.py
from app import create_app
from app.utils.email import send_email

app = create_app()

with app.app_context():
    send_email(
        subject='Test Email from FADTECH Labs',
        recipients=['fadiliddrisu24@gmail.com'],
        html_body='<h1>✅ Email Working!</h1><p>Your Mailtrap setup is successful.</p>'
    )
    print('✅ Test email sent! Check your Mailtrap inbox at https://mailtrap.io/inboxes')