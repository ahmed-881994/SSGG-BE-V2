import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.config.logging_config import logger
from app.config.settings import settings
from app.core.exceptions import ServiceError


class EmailService:
    """Service class for handling email operations."""
    
    def __init__(self):
        """Initialize EmailService with SMTP settings."""
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email

    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        html_body: Optional[str] = None
    ) -> None:
        """Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Subject of the email
            body: Plain text body content of the email
            html_body: Optional HTML body content (if provided, creates multipart email)
            
        Raises:
            ServiceError: If sending email fails
        """
        try:
            # Create the email message
            msg = MIMEMultipart('alternative') if html_body else MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach plain text version
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach HTML version if provided (email clients will prefer HTML)
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            logger.info(f"Email sent to {to_email} with subject '{subject}'")
        
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise ServiceError(f"Email sending failed: {str(e)}")
        
email_service = EmailService()