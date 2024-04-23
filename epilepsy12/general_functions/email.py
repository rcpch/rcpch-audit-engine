# Django Imports
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


def send_email_to_recipients(recipients: list, subject: str, message: str):
    """
    Sends emails
    """
    send_mail(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
        message=strip_tags(message),
        html_message=message,
    )
