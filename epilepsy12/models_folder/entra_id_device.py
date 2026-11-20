# django
from django.db import models

# third party
from django_otp.models import Device, TimestampMixin


class EntraIDDevice(TimestampMixin, Device):
    """
    Records that a user has signed in with Microsoft Entra ID.

    Entra ID enforces RCPCH's own multi-factor authentication policy, so a
    successful Entra ID sign in is treated as a verified second factor. Logging
    the user in against this device (django_otp.login) makes user.is_verified()
    True for the session, so the existing login_and_otp_required checks work
    unchanged.

    This device can never verify a one-time code typed into the password login,
    so it cannot be used to bypass Entra ID.
    """

    entra_object_id = models.CharField(
        max_length=64,
        help_text="The immutable Entra ID object id (oid claim) of the Microsoft account bound to this user.",
    )

    class Meta(Device.Meta):
        verbose_name = "Entra ID sign in"
        verbose_name_plural = "Entra ID sign ins"

    def verify_token(self, token):
        return False
