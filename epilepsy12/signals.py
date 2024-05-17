# python imports
import logging

# django imports
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

# RCPCH
from .models import VisitActivity, Epilepsy12User

# Logging setup
logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"{user} ({user.email}) logged in from {get_client_ip(request)}.")
    VisitActivity.objects.create(
        activity=1, ip_address=get_client_ip(request), epilepsy12user=user
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, request, user=None, **kwargs):
    if user is not None:
        VisitActivity.objects.create(
            activity=2, ip_address=get_client_ip(request), epilepsy12user=user
        )
        logger.info(
            f"{user} ({user.email}) failed log in from {get_client_ip(request)}."
        )
    elif "credentials" in kwargs:
        if Epilepsy12User.objects.filter(
            email=kwargs["credentials"]["username"]
        ).exists():
            user = Epilepsy12User.objects.get(email=kwargs["credentials"]["username"])
            VisitActivity.objects.create(
                activity=2, ip_address=get_client_ip(request), epilepsy12user=user
            )
            logger.info(
                f"{user} ({user.email}) failed log in from {get_client_ip(request)}."
            )
        else:
            logger.info("Login failure by unknown user")
    else:
        logger.info("Login failure by unknown user")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"{user} ({user.email}) logged out from {get_client_ip(request)}.")
    VisitActivity.objects.create(
        activity=3, ip_address=get_client_ip(request), epilepsy12user=user
    )


# Signal handlers
@receiver(pre_save, sender=Epilepsy12User)
def set_updated_by(sender, instance, **kwargs):
    if instance.pk:
        logger.info(f"{instance} ({instance.email}) updated by {instance.updated_by}.")
        instance.updated_by = instance.updated_by


@receiver(post_save, sender=Epilepsy12User)
def set_created_by(sender, instance, created, **kwargs):
    if created:
        instance.created_by = instance.created_by
        instance.save()
        logger.info(f"{instance} ({instance.email}) created by {instance.updated_by}.")


# helper functions
def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")
