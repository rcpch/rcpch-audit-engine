from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required

def login_and_otp_required(view_func):
    # Apply the login_required first and then otp_required decorator
    decorated_view_func = login_required(otp_required(view_func))
    return decorated_view_func