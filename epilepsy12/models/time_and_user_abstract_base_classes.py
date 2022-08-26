from django.utils import timezone
from django.db import models
from django.conf import settings
from ..constants import *


# TODO #12 Mixin breaks build currently
class TimeStampAbstractBaseClass(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=f"record created on {timezone.now}",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=f"record updated on {timezone.now}",
    )

    class Meta:
        abstract = True


class UserStampAbstractBaseClass(models.Model):

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created%(app_label)s_%(class)s_related",
        verbose_name="record created by user in %(class)",
        null=True
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="updated%(app_label)s_%(class)s_related",
        verbose_name="record updated by user in %(class)",
        null=True
    )

    class Meta:
        abstract = True
