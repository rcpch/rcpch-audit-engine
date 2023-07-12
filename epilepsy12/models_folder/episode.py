# django
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# 3rd party
from simple_history.models import HistoricalRecords
# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import DATE_ACCURACY, EPISODE_DEFINITION, EPILEPSY_DIAGNOSIS_STATUS, EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPTIC_SYNCOPES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, MIGRAINES, EPIS_MISC, GENERALISED_SEIZURE_TYPE
from .time_and_user_abstract_base_classes import *


class Episode(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    Summarises each seizure episode.
    Each child may have several seizure episodes, one of which must be epileptic to be included.
    Each episode is dated (with a flag to define confidence in the accuracy of this).
    Each epileptic episode is classified at to whether focal/general or unknown onset, or unclassified.
    For each episode there is one D (description), E (epilepsy definition), S (seizure type).
    """
    expected_score = models.IntegerField(
        # a continuous tally of expected number of scored fields for this episode
        blank=True,
        default=None,
        null=True
    )
    calculated_score = models.IntegerField(
        # a continuous tally of scored fields for this episode
        blank=True,
        default=None,
        null=True
    )
    seizure_onset_date = models.DateField(
        help_text={
            'label': 'When did the first episode of this type happen?',
            'reference': "Date the first episode of this type occurred or was witnessed.",
        },
        blank=True,
        default=None,
        null=True
    )

    seizure_onset_date_confidence = models.CharField(
        help_text={
            'label': 'Confidence in reported date of episode',
            'reference': "How accurate is the date of this episode?",
        },
        max_length=3,
        choices=DATE_ACCURACY,
        default=None,
        null=True
    )

    episode_definition = models.CharField(
        help_text={
            'label': 'Episode definition',
            'reference': "Episode definition. Part of case definition and defines if represents a cluster or discrete episodes.",
        },
        max_length=1,
        choices=EPISODE_DEFINITION,
        verbose_name="Episode definition. Part of case definition and defines if represents a cluster or discrete episodes.",
        default=None,
        null=True
    )

    has_description_of_the_episode_or_episodes_been_gathered = models.BooleanField(
        help_text={
            'label': "Has a description of the episode or episodes been gathered?",
            'reference': "Has a description of the episode or episodes been gathered?",
        },
        null=True,
        default=None
    )

    description = models.TextField(
        help_text={
            'label': "What is the episode(s) like and is the description adequate?",
            'reference': "Glossary of Descriptive Terminology for Ictal Semiology: Report of the ILAE Task Force on Classification and Terminology, 2002",
        },
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
        help_text={
            'label': "Is this episode epileptic, non-epileptic or uncertain?",
            'reference': "Is this episode epileptic, non-epileptic or uncertain?",
        },
        max_length=3,
        choices=EPILEPSY_DIAGNOSIS_STATUS,
        blank=True,
        default=None,
        null=True
    )

    """
    Onset of Seizures
    """

    # onset type

    epileptic_seizure_onset_type = models.CharField(
        help_text={
            'label': "How best would describe the onset of the epileptic episode?",
            'reference': "Operational classification of seizure types by the International League Against Epilepsy: Position Paper of the ILAE Commission for Classification and Terminology. Epilepsia, 58(4):522–530, 2017.",
        },
        max_length=3,
        choices=EPILEPSY_SEIZURE_TYPE,
        default=None,
        null=True
    )
    nonepileptic_seizure_type = models.CharField(
        help_text={
            'label': "How best describes the generalised nature of the nonepileptic episode(s)?",
            'reference': "How best describes the generalised nature of the nonepileptic episode(s)?",
        },
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_TYPE,
        default=None,
        blank=True,
        null=True
    )

    # generalised onset

    epileptic_generalised_onset = models.CharField(
        help_text={
            'label': "How best describes the generalised nature of the epileptic episode(s)?",
            'reference': "How best describes the generalised nature of the epileptic episode(s)?",
        },
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
    # TODO: is this the correct name for field? Should it be 'nonepileptic_seizure_onset' 
    nonepileptic_seizure_unknown_onset = models.CharField(
        help_text={
            'label': 'How best describes the onset of the nonepileptic episode(s)?',
            'reference': 'Operational classification of seizure types by the International League Against Epilepsy: Position Paper of the ILAE Commission for Classification and Terminology. Epilepsia, 58(4):522–530, 2017.',
        },
        max_length=3,
        choices=NON_EPILEPSY_SEIZURE_ONSET,
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_syncope = models.CharField(
        help_text={
            'label': 'How best describes the <i>type</i> of syncope?',
            'reference': 'How best describes the <i>type</i> of syncope?',
        },
        max_length=3,
        choices=sorted(NON_EPILEPTIC_SYNCOPES),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_behavioural = models.CharField(
        help_text={
            'label': 'How best describes the <i>type</i> of behavioural episode?',
            'reference': 'How best describes the <i>type</i> of behavioural episode?',
        },
        max_length=3,
        choices=sorted(NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_sleep = models.CharField(
        help_text={
            'label': 'How best describes the <i>type</i> of sleep event?',
            'reference': 'How best describes the <i>type</i> of sleep event?',
        },
        max_length=3,
        choices=sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_paroxysmal = models.CharField(
        help_text={
            'label': 'How best describes the <i>type</i> of paroxysmal event?',
            'reference': 'How best describes the <i>type</i> of paroxysmal event?',
        },
        max_length=3,
        choices=sorted(NON_EPILEPSY_PAROXYSMS),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_migraine = models.CharField(
        help_text={
            'label': 'How best describes the <i>type</i> of migraine?',
            'reference': 'How best describes the <i>type</i> of migraine?',
        },
        max_length=3,
        choices=sorted(MIGRAINES),
        default=None,
        null=True,
        blank=True
    )
    nonepileptic_seizure_miscellaneous = models.CharField(
        help_text={
            'label': 'How best describes the <i>subtype</i>?',
            'reference': 'How best describes the <i>subtype</i>?',
        },
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

    class Meta:
        verbose_name = "Episode"
        verbose_name_plural = "Episodes"

    def __str__(self) -> str:
        return f"{self.get_epilepsy_or_nonepilepsy_status_display()} type seizure for  {self.multiaxial_diagnosis.registration.case}"
