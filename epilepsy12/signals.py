# django imports
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver

# RCPCH
from .models import VisitActivity, Epilepsy12User


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print(f"{user} ({user.email}) logged in from {get_client_ip(request)}.")
    VisitActivity.objects.create(
        activity=1, ip_address=get_client_ip(request), epilepsy12user=user
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, request, user=None, **kwargs):
    if user is not None:
        VisitActivity.objects.create(
            activity=2, ip_address=get_client_ip(request), epilepsy12user=user
        )
        print(f"{user} ({user.email}) failed log in from {get_client_ip(request)}.")
    elif "credentials" in kwargs:
        if Epilepsy12User.objects.filter(
            email=kwargs["credentials"]["username"]
        ).exists():
            user = Epilepsy12User.objects.get(email=kwargs["credentials"]["username"])
            VisitActivity.objects.create(
                activity=2, ip_address=get_client_ip(request), epilepsy12user=user
            )
            print(f"{user} ({user.email}) failed log in from {get_client_ip(request)}.")
        else:
            print("Login failure by unknown user")
    else:
        print("Login failure by unknown user")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    print(f"{user} ({user.email}) logged out from {get_client_ip(request)}.")
    VisitActivity.objects.create(
        activity=3, ip_address=get_client_ip(request), epilepsy12user=user
    )


# helper functions
def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")
