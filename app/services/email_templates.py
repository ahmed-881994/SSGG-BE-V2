"""Email templates for the application using Jinja2."""

from datetime import datetime
from pathlib import Path
from typing import NamedTuple, Tuple

from jinja2 import Environment, FileSystemLoader, select_autoescape

class EmailContent(NamedTuple):
    """Container for email content."""
    subject: str
    text_body: str
    html_body: str

class EmailTemplates:
    """Collection of email templates using Jinja2."""
    
    def __init__(self):
        """Initialize Jinja2 environment."""
        # Path to email templates directory
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        
        # Configure Jinja2 environment with autoescape for HTML
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _render_template(self, template_name: str, context: dict) -> str:
        """Render a template with given context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary of variables for template rendering
            
        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)
    
    def welcome_email(
        self,
        user_name: str,
        user_id: str,
        temporary_password: str,
        organization_name: str = "Sporting Scout",
        login_url: str = "https://app.sportingscout.org/login"
    ) -> EmailContent:
        """Generate welcome email content.
        
        Args:
            user_name: Name of the new user
            user_id: ID of the new user
            temporary_password: Temporary password for the new user
            organization_name: Name of the organization
            login_url: URL to login page
            
        Returns:
            EmailContent: The email content with subject, plain text body, and HTML body
        """
        subject = f"Welcome to {organization_name}!"
        
        context = {
            "user_name": user_name,
            "user_id": user_id,
            "temporary_password": temporary_password,
            "organization_name": organization_name,
            "login_url": login_url,
            "current_year": datetime.now().year
        }
        
        text_body = self._render_template("welcome.txt", context)
        html_body = self._render_template("welcome.html", context)
        return EmailContent(subject, text_body, html_body)
    
    # def welcome_email_html(
    #     self,
    #     user_name: str,
    #     user_email: str,
    #     organization_name: str = "Sporting Scout",
    #     login_url: str = "https://app.sportingscout.org/login"
    # ) -> Tuple[str, str]:
    #     """Generate HTML welcome email content.
        
    #     Args:
    #         user_name: Name of the new user
    #         user_email: Email address of the new user
    #         organization_name: Name of the organization
    #         login_url: URL to login page
            
    #     Returns:
    #         Tuple of (subject, html_body)
    #     """
    #     subject = f"Welcome to {organization_name}!"
        
    #     context = {
    #         "user_name": user_name,
    #         "user_email": user_email,
    #         "organization_name": organization_name,
    #         "login_url": login_url,
    #         "registration_date": datetime.now().strftime('%B %d, %Y'),
    #         "current_year": datetime.now().year
    #     }
        
    #     html_body = self._render_template("welcome.html", context)
    #     return subject, html_body
    
    def password_reset_email(
        self,
        user_name: str,
        new_password: str,
        organization_name: str = "Sporting Scout"
    ) -> EmailContent:
        """Generate password reset email content.
        
        Args:
            user_name: Name of the user
            new_password: New temporary password for the user
            organization_name: Name of the organization
            
        Returns:
            EmailContent: The email content with subject, plain text body, and HTML body
        """
        subject = f"Password Reset - {organization_name}"
        
        context = {
            "user_name": user_name,
            "organization_name": organization_name,
            "new_password": new_password,
            "login_url": "https://app.sportingscout.org/login",
        }
        
        text_body = self._render_template("password_reset.txt", context)
        html_body = self._render_template("password_reset.html", context)
        return EmailContent(subject, text_body, html_body)
    
    # def password_reset_email_html(
    #     self,
    #     user_name: str,
    #     reset_token: str,
    #     reset_url: str = "https://app.sportingscout.org/reset-password",
    #     organization_name: str = "Sporting Scout"
    # ) -> Tuple[str, str]:
    #     """Generate HTML password reset email content.
        
    #     Args:
    #         user_name: Name of the user
    #         reset_token: Password reset token
    #         reset_url: Base URL for password reset
    #         organization_name: Name of the organization
            
    #     Returns:
    #         Tuple of (subject, html_body)
    #     """
    #     subject = f"Password Reset Request - {organization_name}"
    #     reset_link = f"{reset_url}?token={reset_token}"
        
    #     context = {
    #         "user_name": user_name,
    #         "organization_name": organization_name,
    #         "reset_link": reset_link,
    #         "current_year": datetime.now().year
    #     }
        
    #     html_body = self._render_template("password_reset.html", context)
    #     return subject, html_body


# Convenience instance
email_templates = EmailTemplates()