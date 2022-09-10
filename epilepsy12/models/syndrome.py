from django.db import models
from operator import itemgetter
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .multiaxial_diagnosis import MultiaxialDiagnosis


class Syndrome(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class stores information on syndromes
    One MultiaxialDescription can have multiple syndromes
    """

    syndrome_diagnosis_date = models.DateField(
        "The date the syndrome diagnosis was made.",
        blank=True,
        default=None,
        null=True
    )

    syndrome_name = models.IntegerField(
        "Select an identifiable epilepsy syndrome?",
        choices=sorted(SYNDROMES, key=itemgetter(1)),
        null=True,
        blank=True,
        default=None
    )

    syndrome_diagnosis_active = models.BooleanField(
        "Is the diagnosis of the syndrome still active?",
        null=True,
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
