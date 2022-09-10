from tabnanny import verbose
from django.db import models
from django.contrib.postgres.fields import ArrayField
from .multiaxial_diagnosis import MultiaxialDiagnosis
from ..constants import *
from .time_and_user_abstract_base_classes import *


class Episode(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    Summarises each seizure episode.
    Each child may have several seizure episodes, one of which must be epileptic to be included.
    Each episode is dated (with a flag to define confidence in the accuracy of this).
    Each epileptic episode is classified at to whether focal/general or unknown onset, or unclassified.
    For each episode there is one D (description), E (epilepsy definition), S (seizure type).
    """
    seizure_onset_date = models.DateField(
        "Date episode occurred or was witnessed.",
        blank=True,
        default=None,
        null=True
    )

    seizure_onset_date_confidence = models.CharField(
        "how accurate is the date of this episode?",
        max_length=3,
        choices=DATE_ACCURACY,
        default=None,
        null=True
    )

    episode_definition = models.CharField(
        max_length=1,
        choices=EPISODE_DEFINITION,
        verbose_name="Episode definition. Part of case definition and defines if represents a cluster or discrete episodes.",
        default=None,
        null=True
    )

    has_number_of_episodes_since_the_first_been_documented = models.BooleanField(
        "has the frequency of episodes since the first recorded been documented?",
        null=True,
        default=None
    )

    has_description_of_the_episode_or_episodes_been_gathered = models.BooleanField(
        "has a description of the episode or episodes been gathered?",
        null=True,
        default=None
    )

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

    """
    Onset of Seizures
    """

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

    # generalised onset

    epileptic_generalised_onset = models.CharField(
        max_length=3,
        choices=sorted(GENERALISED_SEIZURE_TYPE),
        default=None,
        null=True,
        blank=True,
    )

    # focal onset
    focal_onset_impaired_awareness = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_automatisms = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_atonic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_clonic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_left = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_right = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_epileptic_spasms = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_hyperkinetic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_myoclonic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_tonic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_autonomic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_behavioural_arrest = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_cognitive = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_emotional = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_sensory = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_centrotemporal = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_temporal = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_frontal = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_parietal = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_occipital = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_gelastic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )
    focal_onset_focal_to_bilateral_tonic_clonic = models.BooleanField(
        default=None,
        blank=True,
        null=True
    )

    # nonepileptic seizure onset

    nonepileptic_seizure_unknown_onset = models.CharField(
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_ONSET,
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

    # relationships

    multiaxial_diagnosis = models.ForeignKey(
        MultiaxialDiagnosis,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Episode",
        verbose_name_plural = "Episodes"

    def __str__(self) -> str:
        return f"{self.get_epilepsy_or_nonepilepsy_status_display()} type seizure for  {self.multiaxial_diagnosis.registration.case}"
