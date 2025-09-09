from django.contrib.gis.db import models
from django.utils import timezone
from django.conf import settings

# Third-party
from simple_history.models import HistoricalRecords


class OrganisationEmployer(models.Model):
    """Intermediate model for the many-to-many relationship between Epilepsy12User and Organisation"""

    epilepsy12_user = models.ForeignKey(
        "epilepsy12.Epilepsy12User",
        on_delete=models.CASCADE,
        related_name="employer_organisations",
    )
    employer_organisation = models.ForeignKey(
        "epilepsy12.Organisation",
        on_delete=models.CASCADE,
        related_name="epilepsy12_users",
    )
    is_primary = models.BooleanField(
        default=True, help_text="Indicates if this is the user's primary organisation"
    )
    date_joined = models.DateTimeField(default=timezone.now)
    date_left = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Tracking fields
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_organisation_employers",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_organisation_employers",
    )

    history = HistoricalRecords(cascade_delete_history=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["epilepsy12_user", "employer_organisation", "is_active"],
                name="unique_active_employment",
            )
        ]

    def __str__(self):
        return f"{self.epilepsy12_user} at {self.employer_organisation} (Primary: {self.is_primary})"
