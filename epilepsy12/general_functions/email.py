# Django Imports
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings


def send_email_to_recipients(recipients: list, subject: str, message: str):
    """
    Send emails with formatted recipient names
    """
    formatted_recipients = []

    for recipient in recipients:
        if isinstance(recipient, tuple) and len(recipient) == 2:
            name, email = recipient
            formatted_recipients.append(f"{name} <{email}>")
        else:
            formatted_recipients.append(recipient)

    send_mail(
        subject=subject,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=formatted_recipients,
        fail_silently=False,
        message=strip_tags(message),
        html_message=message,
    )
