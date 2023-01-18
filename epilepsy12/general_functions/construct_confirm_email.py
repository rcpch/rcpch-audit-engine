from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site


def construct_confirm_email(request, user):
    email_template_name = "registration/admin_reset_password.html"
    c = {
        "email": user.email,
        'domain': get_current_site(request),
        'site_name': 'Website',
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        'token': default_token_generator.make_token(user),
        'protocol': 'http',
    }
    email = render_to_string(email_template_name, c)

    return email
