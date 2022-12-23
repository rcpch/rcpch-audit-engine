from django.db import models
from operator import itemgetter

from .help_text_mixin import HelpTextMixin
from ..constants import SYNDROMES
from .time_and_user_abstract_base_classes import *
# from ..general_functions import *

# other tables
from .multiaxial_diagnosis import MultiaxialDiagnosis


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

    syndrome_name = models.IntegerField(
        help_text={
            'label': "Select an identifiable epilepsy syndrome?",
            'reference': "Select an identifiable epilepsy syndrome?",
        },
        choices=sorted(SYNDROMES, key=itemgetter(1)),
        null=True,
        blank=True,
        default=None
    )

    # relationships

    multiaxial_diagnosis = models.ForeignKey(
        MultiaxialDiagnosis,
        on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f'{self.get_syndrome_name_display()}'

    class Meta:
        verbose_name = 'Syndrome'
        verbose_name_plural = 'Syndromes'
