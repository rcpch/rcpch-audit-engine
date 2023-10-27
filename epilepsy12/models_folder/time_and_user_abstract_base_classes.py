from django.contrib.gis.db import models
from django.conf import settings


# TODO #12 Mixin breaks build currently
class TimeStampAbstractBaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserStampAbstractBaseClass(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_%(class)s",
        verbose_name="record created by user in %(class)",
        null=True,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="updated_%(class)s",
        verbose_name="record updated by user in %(class)",
        null=True,
    )

    class Meta:
        abstract = True
