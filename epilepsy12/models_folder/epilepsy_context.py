
# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import OPT_OUT_UNCERTAIN
from .time_and_user_abstract_base_classes import *


class EpilepsyContext(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class records contextual information that defines epilepsy risk.
    It references the FirstPaediatricAssessment class, as each case optionally has a single epilepsy context.
    """

    previous_febrile_seizure = models.CharField(
        help_text={
            'label': "At any point in time has the child had febrile seizure(s)?",
            'reference': "At any point in time has the child had febrile seizure(s)?",
        },
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    previous_acute_symptomatic_seizure = models.CharField(
        help_text={
            'label': "At any point in time has the child had acute symptomatic seizure(s)?",
            'reference': "At any point in time has the child had acute symptomatic seizure(s)?"
        },
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    is_there_a_family_history_of_epilepsy = models.CharField(
        help_text={
            'label': "Is there a family history of epilepsy?",
            'reference': "Is there a family history of epilepsy?"
        },
        max_length=3,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    previous_neonatal_seizures = models.CharField(
        help_text={
            'label': 'Were there seizures in the neonatal period?',
            'reference': 'Were there seizures in the neonatal period?'
        },
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=None,
        null=True
    )
    diagnosis_of_epilepsy_withdrawn = models.BooleanField(
        help_text={
            'label': "Has the diagnosis of epilepsy been withdrawn?",
            'reference': 'In the first year after first assessment, has a diagnosis of epilepsy been withdrawn because it has been subsequently deemed incorrect?'
        },
        null=True,
        default=None,
    )

    were_any_of_the_epileptic_seizures_convulsive = models.BooleanField(
        help_text={
            'label': "Were any of the epileptic seizures convulsive?",
            'reference': "Were any of the epileptic seizures convulsive?",
        },
        default=None,
        null=True
    )

    experienced_prolonged_generalized_convulsive_seizures = models.CharField(
        help_text={
            'label': "Has the child at any point in time experienced prolonged generalised seizures?",
            'reference': "Has the child at any point in time experienced prolonged generalised convulsive seizures > 5 min duration (or successive continuing > 5min)?",
        },
        max_length=2,
        default=None,
        null=True,
        choices=OPT_OUT_UNCERTAIN,
    )
    experienced_prolonged_focal_seizures = models.CharField(
        help_text={
            'label': "Has the child at any point in time experienced prolonged focal seizures?",
            'reference': "Has the child at any point in time experienced prolonged focal seizures > 5 min duration (or successive continuing > 5min)?",
        },

        max_length=2,
        default=None,
        null=True,
        choices=OPT_OUT_UNCERTAIN,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    # relationships
    registration = models.OneToOneField(
        'epilepsy12.Registration',
        on_delete=models.CASCADE,
        # verbose_name="Related Registration",
        null=True
    )

    class Meta:
        verbose_name = 'Epilepsy Context'
        verbose_name_plural = 'Epilepsy Contexts'

    def save(
            self,
            *args, **kwargs) -> None:
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.previous_neonatal_seizures or self.diagnosis_of_epilepsy_withdrawn or self.previous_acute_symptomatic_seizure or self.previous_febrile_seizure:
            return 'This child has had previous symptomatic or neonatal or febrile seizures.'
        else:
            return 'This child has never had epileptic seizures or a previous diagnosis has been withdrawn.'
