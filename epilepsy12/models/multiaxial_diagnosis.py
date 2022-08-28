from operator import itemgetter
from django.db import models
from django.contrib.postgres.fields import ArrayField

from epilepsy12.models.registration import Registration, Episode
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

    syndrome = models.IntegerField(
        "Select an identifiable epilepsy syndrome?",
        choices=sorted(SYNDROMES, key=itemgetter(1)),
        null=True,
        blank=True,
        default=None
    )

    # Cause

    seizure_cause_main = models.CharField(
        "main identified cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_CAUSES,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_structural = models.CharField(
        "main identified structural cause of seizure(s)",
        max_length=3,
        choices=sorted(EPILEPSY_STRUCTURAL_CAUSE_TYPES, key=itemgetter(1)),
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_genetic = models.CharField(
        "main identified genetic cause of seizure(s)",
        max_length=3,
        choices=sorted(EPILEPSY_GENETIC_CAUSE_TYPES),
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_gene_abnormality = models.CharField(  # would be good to pull in known genetic abnormalities
        "main identified gene abnormality cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_GENE_DEFECTS,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_genetic_other = models.CharField(
        "other identified genetic cause of seizure(s) not previously specified.",
        max_length=250,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_chromosomal_abnormality = models.CharField(  # would be good to pull in known chromosomal abnormalities
        "main identified chromosomal cause of seizure(s)",
        max_length=200,
        default=None,
        blank=True,
        null=True
    )

    seizure_cause_infectious = models.CharField(
        "main identified infectious cause of seizure(s)",
        max_length=250,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_metabolic = models.CharField(
        "main identified metabolic cause of seizure(s)",
        max_length=3,
        choices=METABOLIC_CAUSES,
        default=None,
        blank=True,
        null=True
    )

    seizure_cause_metabolic_other = models.CharField(
        "other identified metabolic cause of seizure(s) not previously specified.",
        max_length=250,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_immune = models.CharField(
        "main identified immune cause of seizure(s).",
        max_length=3,
        choices=IMMUNE_CAUSES,
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_immune_antibody = models.CharField(
        "autoantibody identified as cause of seizure(s).",
        max_length=3,
        choices=sorted(AUTOANTIBODIES),
        default=None,
        blank=True,
        null=True
    )
    seizure_cause_immune_antibody_other = models.CharField(
        "other identified antibody not previously specified causing seizure(s).",
        max_length=250,
        default=None,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Multiaxial diagnosis"
        verbose_name_plural = "Multiaxial diagnoses"


# IBE

    relevant_impairments_behavioural_educational = models.BooleanField(
        "Are there any relevant impairments: behavioural or educational, emotional problems?",
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='registration'
    )

    # relationships

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE
    )

    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE
    )

    # Meta class

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def __str__(self) -> str:
        return "Multaxial diagnosis for "+self.registration.case
