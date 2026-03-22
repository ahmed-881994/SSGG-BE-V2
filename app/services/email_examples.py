"""Examples of using email templates with the email service.

This file demonstrates how to use the email templates with the email service.
"""

from app.services.email_service import email_service
from app.services.email_templates import email_templates


def send_welcome_email(
    user_name: str, 
    user_email: str, 
    user_id: str,
    temporary_password: str
) -> None:
    """Send a welcome email to a new user.
    
    Args:
        user_name: Name of the new user
        user_email: Email address of the new user
        user_id: ID of the new user
        temporary_password: Temporary password for the new user
        
    Example:
        >>> send_welcome_email("John Doe", "john.doe@example.com", "USR001", "TempPass123!")
    """
    email = email_templates.welcome_email(
        user_name=user_name,
        user_id=user_id,
        temporary_password=temporary_password
    )
    
    email_service.send_email(
        to_email=user_email,
        subject=email.subject,
        body=email.text_body,
        html_body=email.html_body
    )


def send_password_reset_email(
    user_name: str, 
    user_email: str, 
    new_password: str
) -> None:
    """Send a password reset email to a user.
    
    Args:
        user_name: Name of the user
        user_email: Email address of the user
        new_password: New temporary password for the user
        
    Example:
        >>> send_password_reset_email("John Doe", "john.doe@example.com", "NewPass456!")
    """
    email = email_templates.password_reset_email(
        user_name=user_name,
        new_password=new_password
    )
    
    email_service.send_email(
        to_email=user_email,
        subject=email.subject,
        body=email.text_body,
        html_body=email.html_body
    )


# Usage in your application code:
# 
# Example 1: Send welcome email when user is created
# from app.services.email_examples import send_welcome_email
# 
# def create_user(user_data):
#     # ... create user in database ...
#     temp_password = generate_temporary_password()
#     send_welcome_email(user.name, user.email, user.id, temp_password)
#
# Example 2: Send password reset email
# from app.services.email_examples import send_password_reset_email
#
# def reset_user_password(email: str):
#     user = get_user_by_email(email)
#     new_password = generate_temporary_password()
#     # ... update password in database ...
#     send_password_reset_email(user.name, user.email, new_password)