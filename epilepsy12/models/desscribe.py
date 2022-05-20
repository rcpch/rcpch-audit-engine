from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.deletion import CASCADE
from django.forms import CharField

from epilepsy12.models.registration import Registration
from ..constants import *
from .time_and_user_abstract_base_classes import *


class DESSCRIBE(models.Model):
    # Summarises a child or young person's epilepsy in a multiaxial way.
    # It is a standard tool for clinicians when describing or discussing a person's epilepsy and is taught nationally
    # There is one record per case.

    description = models.CharField(
        help_text="What is the episode(s) like and is the description adequate?",
        max_length=500,
        default=None
    )
    description_keywords = ArrayField(
        models.CharField(
            help_text="add a key word",
            max_length=100
        ),
        blank=True,
        null=True
    )

    epilepsy_or_nonepilepsy_status = models.CharField(
        "Is a diagnosis of epilepsy definite, or uncertain.",
        max_length=3,
        choices=EPILEPSY_DIAGNOSIS_STATUS
    )

    # type
    epileptic_seizure_type = models.CharField(
        "If epileptic, what is the seizure type (s)?",
        max_length=3,
        choices=EPILEPSY_SEIZURE_TYPE
    )
    non_epileptic_seizure_type = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_TYPE,
        default=None
    )
    focal_onset_impaired_awareness = models.BooleanField(
        default=None
    )
    focal_onset_automatisms = models.BooleanField(
        default=None
    )
    focal_onset_atonic = models.BooleanField(
        default=None
    )
    focal_onset_clonic = models.BooleanField(
        default=None
    )
    focal_onset_left = models.BooleanField(
        default=None
    )
    focal_onset_right = models.BooleanField(
        default=None
    )
    focal_onset_epileptic_spasms = models.BooleanField(
        default=None
    )
    focal_onset_hyperkinetic = models.BooleanField(
        default=None
    )
    focal_onset_myoclonic = models.BooleanField(
        default=None
    )
    focal_onset_tonic = models.BooleanField(
        default=None
    )
    focal_onset_autonomic = models.BooleanField(
        default=None
    )
    focal_onset_behavioural_arrest = models.BooleanField(
        default=None
    )
    focal_onset_cognitive = models.BooleanField(
        default=None
    )
    focal_onset_emotional = models.BooleanField(
        default=None
    )
    focal_onset_sensory = models.BooleanField(
        default=None
    )
    focal_onset_centrotemporal = models.BooleanField(
        default=None
    )
    focal_onset_temporal = models.BooleanField(
        default=None
    )
    focal_onset_frontal = models.BooleanField(
        default=None
    )
    focal_onset_parietal = models.BooleanField(
        default=None
    )
    focal_onset_occipital = models.BooleanField(
        default=None
    )
    focal_onset_gelastic = models.BooleanField(
        default=None
    )
    focal_onset_focal_to_bilateral_tonic_clonic = models.BooleanField(
        default=None
    )
    focal_onset_other = models.BooleanField(
        default=None
    )
    focal_onset_other_details = models.CharField(max_length=250)
    generalised_onset = models.CharField(
        max_length=3,
        choices=GENERALISED_SEIZURE_TYPE,
        default=None
    )
    generalised_onset_other_details = models.CharField(max_length=250)
    nonepileptic_seizure_unknown_onset = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_ONSET,
        default=None
    )
    nonepileptic_seizure_unknown_onset_other_details = models.CharField(
        max_length=250)
    nonepileptic_seizure_syncope = models.CharField(
        max_length=3,
        choices=NON_EPILEPTIC_SYNCOPES,
        default=None
    )
    nonepileptic_seizure_behavioural = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS,
        default=None
    )
    nonepileptic_seizure_sleep = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS,
        default=None
    )
    nonepileptic_seizure_paroxysmal = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_PAROXYSMS,
        default=None
    )
    nonepileptic_seizure_migraine = models.CharField(
        max_length=3,
        choices=MIGRAINES,
        default=None
    )
    nonepileptic_seizure_miscellaneous = models.CharField(
        max_length=3,
        choices=EPIS_MISC,
        default=None
    )
    nonepileptic_seizure_other = models.CharField(max_length=250)

    # Syndrome

    syndrome = models.CharField(
        "Is there an identifiable epilepsy syndrome?",
        max_length=50
    )

    # Cause

    seizure_cause_main = models.CharField(
        "main identified cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_CAUSES
    )
    seizure_cause_main_snomed_code = models.CharField(
        "SNOMED-CT code for main identified cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_CAUSES,
        default=None
    )
    seizure_cause_structural = models.CharField(
        "main identified structural cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES,
        default=None
    )
    seizure_cause_structural_snomed_code = models.CharField(
        "SNOMED-CT code for main identified structural cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES,
        default=None
    )
    seizure_cause_genetic = models.CharField(
        "main identified genetic cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_GENETIC_CAUSE_TYPES,
        default=None
    )
    seizure_cause_gene_abnormality = models.CharField(  # would be good to pull in known genetic abnormalities
        "main identified gene abnormality cause of seizure(s)",
        max_length=3,
        choices=EPILEPSY_GENE_DEFECTS,
        default=None
    )
    seizure_cause_genetic_other = models.CharField(
        "other identified genetic cause of seizure(s) not previously specified.",
        max_length=250,
        default=None
    )
    seizure_cause_gene_abnormality_snomed_code = models.CharField(
        "SNOMED-CT code for main identified genetic cause of seizure(s)",
        max_length=50,
        default=None
    )
    seizure_cause_chromosomal_abnormality = models.CharField(  # would be good to pull in known chromosomal abnormalities
        "main identified chromosomal cause of seizure(s)",
        max_length=200,
        default=None
    )

    seizure_cause_infectious = models.CharField(
        "main identified infectious cause of seizure(s)",
        max_length=250,
        default=None
    )
    seizure_cause_infectious_snomed_code = models.CharField(
        "SNOMED-CT code for main identified infectious cause of seizure(s)",
        max_length=250,
        default=None
    )
    seizure_cause_metabolic = models.CharField(
        "main identified metabolic cause of seizure(s)",
        max_length=3,
        choices=METABOLIC_CAUSES,
        default=None
    )
    seizure_cause_metabolic_other = models.CharField(
        "other identified metabolic cause of seizure(s) not previously specified.",
        max_length=250,
        default=None
    )
    seizure_cause_metabolic_snomed_code = models.CharField(
        "SNOMED-CT code for other identified metabolic cause of seizure(s) not previously specified.",
        max_length=250,
        default=None
    )
    seizure_cause_immune = models.CharField(
        "main identified immune cause of seizure(s).",
        max_length=3,
        choices=IMMUNE_CAUSES,
        default=None
    )
    seizure_cause_immune_antibody = models.CharField(
        "autoantibody identified as cause of seizure(s).",
        max_length=3,
        choices=AUTOANTIBODIES,
        default=None
    )
    seizure_cause_immune_antibody_other = models.CharField(
        "other identified antibody not previously specified causing seizure(s).",
        max_length=250,
        default=None
    )
    seizure_cause_immune_snomed_code = models.CharField(
        "SNOMED-CT code for main identified immune cause of seizure(s).",
        max_length=250,
        default=None
    )

# IBE

    relevant_impairments_behavioural_educational = models.BooleanField(
        "Are there any relevant impairments: behavioural or educational, emotional problems?",
        max_length=50
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='registration'
    )

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def __str__(self) -> str:
        return self.epilepsy_status
