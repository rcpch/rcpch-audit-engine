# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from ..help_text_mixin import HelpTextMixin
from ..time_and_user_abstract_base_classes import *


class Medicine(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class stores information on each medicine and serves as a look up for the medicine link table
    """

    medicine_name = models.CharField(
        help_text={
            "label": "Medicine Name",
            "reference": "Please enter the medicine.",
        },
        null=True,
        blank=True,
        default=None,
    )
    conceptId = models.CharField(default=None, null=True, blank=True)
    term = models.CharField(default=None, null=True, blank=True)
    preferredTerm = models.CharField(default=None, null=True, blank=True)
    is_rescue = models.BooleanField(default=None, null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = "Medicine"
        verbose_name_plural = "Medicines"

    def __str__(self) -> str:
        return f"{self.medicine_name}"
