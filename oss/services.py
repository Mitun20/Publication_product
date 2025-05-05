# services.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
from django.utils.timezone import now 
from .models import Email

logger = logging.getLogger(__name__)

def send_email(to_email, subject, template_name,user, context):
    """
    Send an email using a template.
    
    :param to_email: Recipient's email address
    :param subject: Subject of the email
    :param template_name: Name of the template file to render the email body
    :param context: Context to render the template
    """
    try:
        html_message = render_to_string(template_name, context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=html_message,  # Send both HTML and plain text versions
        )
        datetime= now()
        
        email=Email.objects.create(
            
            from_user=settings.DEFAULT_FROM_EMAIL,
            to_user=user,
            subject=subject,
            content=plain_message,
            datetime=datetime ,# You can also save the HTML content if needed
        )
        
        logger.info(f'Email sent to {to_email}')
    except Exception as e:
        logger.error(f'Error sending email to {to_email}: {str(e)}')
        raise
