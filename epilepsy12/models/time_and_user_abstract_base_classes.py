from django.db import models
from django.contrib.auth.models import User
from ..constants import *


# TODO #12 Mixin breaks build currently
class TimeStampAbstractBaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserStampAbstractBaseClass(models.Model):

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created%(app_label)s_%(class)s_related",
        verbose_name="record created by user in %(class)"
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="updated%(app_label)s_%(class)s_related",
        verbose_name="record updated by user in %(class)"
    )

    class Meta:
        abstract = True
