from operator import itemgetter
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
        max_length=5000,
        default="",
        blank=True,
        null=True
    )
    description_keywords = ArrayField(
        models.CharField(
            help_text="add a key word",
            max_length=500
        ),
        blank=True,
        null=True
    )

    epilepsy_or_nonepilepsy_status = models.CharField(
        "Is a diagnosis of epilepsy definite, or uncertain.",
        max_length=3,
        choices=EPILEPSY_DIAGNOSIS_STATUS,
        blank=True,
        default=None,
        null=True
    )

    were_any_of_the_epileptic_seizures_convulsive = models.BooleanField(
        "Were any of the epileptic seizures convulsive?",
        default=None,
        null=True
    )
    prolonged_generalized_convulsive_seizures = models.BooleanField(
        "Were there any prolonged generalised epileptic seizures?",
        default=None,
        null=True
    )
    experienced_prolonged_focal_seizures = models.BooleanField(
        "Were there any prolonged focal seizures?",
        default=None,
        null=True
    )

    # onset type
    epileptic_seizure_onset_type = models.CharField(
        "If epileptic, what is the seizure type (s)?",
        max_length=3,
        choices=EPILEPSY_SEIZURE_TYPE,
        default=None,
        null=True
    )
    nonepileptic_seizure_type = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_TYPE,
        default=None,
        blank=True,
        null=True
    )

    # focal onset
    focal_onset_impaired_awareness = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_automatisms = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_atonic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_clonic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_left = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_right = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_epileptic_spasms = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_hyperkinetic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_myoclonic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_tonic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_autonomic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_behavioural_arrest = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_cognitive = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_emotional = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_sensory = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_centrotemporal = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_temporal = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_frontal = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_parietal = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_occipital = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_gelastic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_focal_to_bilateral_tonic_clonic = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_other = models.BooleanField(
        default=False,
        blank=True,
        null=True
    )
    focal_onset_other_details = models.CharField(
        max_length=250,
        null=True,
        default="",
        blank=True,
    )
    epileptic_generalised_onset = models.CharField(
        max_length=3,
        choices=sorted(GENERALISED_SEIZURE_TYPE),
        default=None,
        null=True,
        blank=True,
    )
    epileptic_generalised_onset_other_details = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_unknown_onset = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_ONSET,
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_unknown_onset_other_details = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_syncope = models.CharField(
        max_length=3,
        choices=sorted(NON_EPILEPTIC_SYNCOPES),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_behavioural = models.CharField(
        max_length=3,
        choices=sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_sleep = models.CharField(
        max_length=3,
        choices=sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_paroxysmal = models.CharField(
        max_length=3,
        choices=sorted(NON_EPILEPSY_PAROXYSMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_migraine = models.CharField(
        max_length=3,
        choices=sorted(MIGRAINES),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_miscellaneous = models.CharField(
        max_length=3,
        choices=sorted(EPIS_MISC),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_other = models.CharField(
        max_length=250,
        default=None,
        null=True,
        blank=True
    )

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

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def save(
            self,
            *args, **kwargs) -> None:

        if self.epilepsy_or_nonepilepsy_status == "E":
            # epilepsy
            set_all_nonepilepsy_seizure_onsets_to_none(self)

            if self.focal_onset_left:
                self.focal_onset_right = False
            elif self.focal_onset_right:
                self.focal_onset_left = False

        elif self.epilepsy_or_nonepilepsy_status == "NE":
            self.epileptic_seizure_onset_type = None
            set_all_focal_onset_epilepsy_fields_to_none(self)
            set_all_generalised_onset_fields_to_none(self)
            set_all_epilepsy_causes_to_none(self)
            set_all_epilepsy_syndromes_to_none(self)

        elif self.epilepsy_or_nonepilepsy_status == "U":
            self.epileptic_seizure_onset_type = None
            set_all_focal_onset_epilepsy_fields_to_none(self)
            set_all_generalised_onset_fields_to_none(self)
            set_all_epilepsy_causes_to_none(self)
            set_all_epilepsy_syndromes_to_none(self)
            set_all_nonepilepsy_seizure_onsets_to_none(self)

        set_all_epilepsy_causes_to_none(
            self, except_field=self.seizure_cause_main)

        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.epilepsy_or_nonepilepsy_status


def set_all_focal_onset_epilepsy_fields_to_none(self):
    self.focal_onset_impaired_awareness = None
    self.focal_onset_automatisms = None
    self.focal_onset_atonic = None
    self.focal_onset_clonic = None
    self.focal_onset_left = None
    self.focal_onset_right = None
    self.focal_onset_epileptic_spasms = None
    self.focal_onset_hyperkinetic = None
    self.focal_onset_myoclonic = None
    self.focal_onset_tonic = None
    self.focal_onset_autonomic = None
    self.focal_onset_behavioural_arrest = None
    self.focal_onset_cognitive = None
    self.focal_onset_emotional = None
    self.focal_onset_sensory = None
    self.focal_onset_centrotemporal = None
    self.focal_onset_temporal = None
    self.focal_onset_frontal = None
    self.focal_onset_parietal = None
    self.focal_onset_occipital = None
    self.focal_onset_gelastic = None
    self.focal_onset_focal_to_bilateral_tonic_clonic = None
    self.focal_onset_other = None
    self.focal_onset_other_details = None


def set_all_generalised_onset_fields_to_none(self):
    self.epileptic_generalised_onset = None
    self.epileptic_generalised_onset_other_details = None


def set_all_epilepsy_causes_to_none(self, except_field=None):
    if except_field is None:
        self.seizure_cause_main = None
        self.seizure_cause_main_snomed_code = None
    elif except_field != "Str":
        self.seizure_cause_structural = None
        self.seizure_cause_structural_snomed_code = None
    elif except_field != "Gen":
        self.seizure_cause_genetic = None
        self.seizure_cause_gene_abnormality = None
        self.seizure_cause_genetic_other = None
        self.seizure_cause_gene_abnormality_snomed_code = None
        self.seizure_cause_chromosomal_abnormality = None
    elif except_field != "Inf":
        self.seizure_cause_infectious = None
        self.seizure_cause_infectious_snomed_code = None
    elif except_field != "Met":
        print("metabolic is except field")
        self.seizure_cause_metabolic = None
        self.seizure_cause_metabolic_other = None
        self.seizure_cause_metabolic_snomed_code = None
    elif except_field != "Imm":
        self.seizure_cause_immune = None
        self.seizure_cause_immune_antibody = None
        self.seizure_cause_immune_antibody_other = None
    elif except_field != "NK":
        self.seizure_cause_immune_snomed_code = None


def set_all_epilepsy_syndromes_to_none(self):
    self.syndrome = None


def set_all_nonepilepsy_seizure_onsets_to_none(self):
    self.nonepileptic_seizure_unknown_onset = None
    self.nonepileptic_seizure_unknown_onset_other_details = None
    self.nonepileptic_seizure_syncope = None
    self.nonepileptic_seizure_behavioural = None
    self.nonepileptic_seizure_sleep = None
    self.nonepileptic_seizure_paroxysmal = None
    self.nonepileptic_seizure_migraine = None
    self.nonepileptic_seizure_miscellaneous = None
    self.nonepileptic_seizure_other = None
