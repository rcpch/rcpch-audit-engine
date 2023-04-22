
# django
from django.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from ..time_and_user_abstract_base_classes import *


class EpilepsyCauseEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    The model holds the look up values for all epilepsy causes
    It is seeded from SNOMED CT, and updated periodically
    Date of update is stored by the mixin in updated_at
    """
    conceptId = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    term = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    preferredTerm = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    description = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    snomed_ct_edition = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    snomed_ct_version = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    icd_code = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    icd_version = models.IntegerField(
        default=None,
        null=True,
        blank=True
    )
    dsm_code = models.CharField(
        default=None,
        null=True,
        blank=True
    )
    dsm_version = models.IntegerField(
        default=None,
        null=True,
        blank=True
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = "Epilepsy Cause"
        verbose_name_plural = "Epilepsy Causes"

    def __str__(self) -> str:
        return self.preferredTerm
