# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from ..help_text_mixin import HelpTextMixin
from ...constants import SYNDROMES
from ..time_and_user_abstract_base_classes import *


class SyndromeList(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    This class stores information on each syndrome and serves as a look up for the syndrome link table
    """

    syndrome_name = models.CharField(
        help_text={
            "label": "The name of a given syndrome",
            "reference": "The name of a given syndrome",
        },
        null=True,
        blank=True,
        default=None,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = "SyndromeList"
        verbose_name_plural = "Syndrome Lists"

    def __str__(self) -> str:
        return f"{self.syndrome_name}"
