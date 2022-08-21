
from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

from .registration import Registration


class EpilepsyContext(models.Model):
    """
    This class records contextual information that defines epilepsy risk.
    It references the InitialAssessment class, as each case optionally has a single epilepsy context.
    """

    previous_febrile_seizure = models.CharField(
        "has there been a previous febrile seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    previous_acute_symptomatic_seizure = models.CharField(
        "has there been a previous acute symptomatic seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    is_there_a_family_history_of_epilepsy = models.CharField(
        "is there a family history of epilepsy?",
        max_length=3,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    previous_neonatal_seizures = models.CharField(
        "were there seizures in the neonatal period?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    diagnosis_of_epilepsy_withdrawn = models.BooleanField(
        "has the diagnosis of epilepsy been withdrawn?",
        null=True,
        default=None,
    )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration",
        null=True
    )

    class Meta:
        verbose_name = 'epilepsy context'
        verbose_name_plural = 'epilepsy contexts'

    def save(
            self,
            *args, **kwargs) -> None:
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.previous_neonatal_seizures or self.diagnosis_of_epilepsy_withdrawn or self.previous_acute_symptomatic_seizure or self.previous_febrile_seizure:
            return 'This child has had previous symptomatic or neonatal or febrile seizures.'
        else:
            return 'This child has never had epileptic seizures or a previous diagnosis has been withdrawn.'
