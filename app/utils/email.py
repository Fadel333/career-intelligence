import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        # Use environment variables for security
        self.email = os.environ.get('EMAIL_USER')
        self.password = os.environ.get('EMAIL_PASS')
    
    def send_welcome_email(self, to_email, name):
        """Send welcome email to new users"""
        subject = "Welcome to FADTECH Labs Career Intelligence!"
        
        body = f"""
        <h2>Welcome {name}!</h2>
        <p>Thank you for joining FADTECH Labs Career Intelligence System.</p>
        <p>Here's what you can do:</p>
        <ul>
            <li>📄 Upload your CV for AI analysis</li>
            <li>📊 Get personalized skill gap analysis</li>
            <li>🎯 Receive job matches based on your skills</li>
            <li>🤖 Chat with our AI career assistant</li>
        </ul>
        <p>Get started by uploading your CV!</p>
        <a href="https://fadtech.xyz/upload-cv">Upload CV Now →</a>
        """
        
        self._send_email(to_email, subject, body)
    
    def send_password_reset(self, to_email, reset_link):
        """Send password reset email"""
        subject = "Reset Your Password - FADTECH Labs"
        
        body = f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password →</a>
        <p>This link expires in 1 hour.</p>
        """
        
        self._send_email(to_email, subject, body)
    
    def send_job_alert(self, to_email, jobs):
        """Send job alert email"""
        subject = "New Job Matches Found!"
        
        jobs_html = ""
        for job in jobs[:5]:
            jobs_html += f"""
            <div style="padding: 10px; margin: 10px 0; background: #f5f5f5;">
                <h3>{job['role']}</h3>
                <p>Match: {job['match_percentage']}% | Salary: GHS {job['salary_range'][0]}-{job['salary_range'][1]}</p>
            </div>
            """
        
        body = f"""
        <h2>New Job Matches for You!</h2>
        {jobs_html}
        <a href="https://fadtech.xyz/job-matches">View All Matches →</a>
        """
        
        self._send_email(to_email, subject, body)
    
    def _send_email(self, to_email, subject, html_body):
        """Internal method to send email"""
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = to_email
        message["Subject"] = subject
        
        message.attach(MIMEText(html_body, "html"))
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False