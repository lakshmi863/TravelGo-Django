# flights/utils.py
import os
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from email.mime.image import MIMEImage

def send_branded_email(subject, context, template_name, recipient_email):
    """
    A single, reusable function for all branded emails in TravelGo.
    """
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")

        # Logo Attachment logic
        logo_path = os.path.join(settings.BASE_DIR, 'flights', 'TravelGo_logo.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo = MIMEImage(f.read())
                logo.add_header('Content-ID', '<logo_image>')
                logo.add_header('Content-Disposition', 'inline', filename='logo.png')
                email.attach(logo)

        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"📧 Email Utility Error: {e}")
        return False