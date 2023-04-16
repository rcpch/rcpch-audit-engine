# django
from django.db import models
# 3rd party
from simple_history.models import HistoricalRecords
# rcpch
from .help_text_mixin import HelpTextMixin
from ..constants import CHRONICITY
from .time_and_user_abstract_base_classes import *


class FirstPaediatricAssessment(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class records information about the initial assessment.
    Whilst other information about the child and their epilepsy may be captured across the audit year
    in the assessment table, this information MUST be collected at the first visit.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    This whole class might better belong in the initial assessment

    """

    first_paediatric_assessment_in_acute_or_nonacute_setting = models.IntegerField(
        help_text={
            'label': "Was the first paediatric assessment in an acute or nonacute setting?",
            'reference': "Was the first paediatric assessment in an acute or nonacute setting?"
        },
        choices=CHRONICITY,
        null=True,
        default=None
    )
    has_number_of_episodes_since_the_first_been_documented = models.BooleanField(
        help_text={
            'label': 'The approximate frequency or number of episodes since the first episode',
            'reference': "Has the approximate frequency or number of episodes since the first recorded episode been documented?"
        },
        null=True,
        default=None
    )
    general_examination_performed = models.BooleanField(
        help_text={
            'label': 'General examination',
            'reference': "has a general paediatric examination been performed?"
        },
        null=True,
        default=None
    )
    neurological_examination_performed = models.BooleanField(
        help_text={
            'label': 'Neurological examination',
            'reference': "Has a neurological examination been performed?"
        },
        null=True,
        default=None
    )
    developmental_learning_or_schooling_problems = models.BooleanField(
        help_text={
            'label': 'Presence or absence of learning, developmental or educational difficulties',
            'reference': "Has the presence or absence of developmental, learning or school-based problems been recorded?",
        },
        null=True,
        default=None
    )
    behavioural_or_emotional_problems = models.BooleanField(
        help_text={
            'label': 'Presence or absence of emotional or behavioural problems',
            'reference': "Has the presence or absence of emotional or behavioural problems been documented?",
        },
        null=True,
        default=None
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
        verbose_name="Related Registration"
    )

    class Meta:
        verbose_name = 'First Paediatric Assessment'
        verbose_name_plural = 'First Paediatric Assessments'

    def save(
            self,
            *args, **kwargs) -> None:
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"ID:{self.pk} First Paediatric Assessment for {self.registration.case} (ID: {self.registration.case.pk})"
