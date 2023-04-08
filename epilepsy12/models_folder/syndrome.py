# python
from operator import itemgetter
# django
from django.db import models
# 3rd party
from simple_history.models import HistoricalRecords
# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import SYNDROMES
from .time_and_user_abstract_base_classes import *


class Syndrome(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class stores information on syndromes
    One MultiaxialDescription can have multiple syndromes
    """

    syndrome_diagnosis_date = models.DateField(
        help_text={
            'label': "The date the syndrome diagnosis was made.",
            'reference': "The date the syndrome diagnosis was made.",
        },
        blank=True,
        default=None,
        null=True
    )

    syndrome = models.ForeignKey(
        'epilepsy12.SyndromeEntity',
        help_text={
            'label': "The date the syndrome diagnosis was made.",
            'reference': "The date the syndrome diagnosis was made.",
        },
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        default=None
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    # relationships

    multiaxial_diagnosis = models.ForeignKey(
        'epilepsy12.MultiaxialDiagnosis',
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.syndrome.syndrome_name} on {self.syndrome_diagnosis_date}'

    class Meta:
        verbose_name = 'Syndrome'
        verbose_name_plural = 'Syndromes'
