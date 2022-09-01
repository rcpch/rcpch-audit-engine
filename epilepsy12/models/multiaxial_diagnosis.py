from operator import itemgetter
from django.db import models
from django.contrib.postgres.fields import ArrayField
from .registration import Registration
from ..constants import *
from .time_and_user_abstract_base_classes import *


class MultiaxialDiagnosis(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    Replace the DESSCRIBE class 
    One MultiaxialDiagnosis relates to one Registration
    One MultiaxialDiagnosis relates to many Episodes
    """

    # Syndrome

    syndrome_present = models.BooleanField(
        "Is there an identifiable epilepsy syndrome?",
        null=True,
        blank=True,
        default=None
    )

    # Cause
    epilepsy_cause = models.CharField(
        "main identified cause of seizure(s)",
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    epilepsy_cause_categories = ArrayField(
        models.CharField(
            help_text="add a category",
            max_length=500
        ),
        blank=True,
        null=True,
        default=list
    )

    relevant_impairments_behavioural_educational = models.BooleanField(
        "Are there any relevant impairments: behavioural or educational, emotional problems?",
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='registration'
    )

    # Meta class

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def __str__(self) -> str:
        return "Multaxial diagnosis for "+self.registration.case
