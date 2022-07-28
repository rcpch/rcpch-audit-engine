from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration


class InitialAssessment(models.Model):
    """
    This class records information about the initial assessment.
    Whilst other information about the child and their epilepsy may be captured across the audit year
    in the assessment table, this information MUST be collected at the first visit.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    This whole clase might better belong in the initial assessment

    """

    date_of_initial_assessment = models.DateField(
        "On what date did the initial assessment occur?",
        null=True,
        default=None
    )
    general_paediatrics_referral_made = models.BooleanField(
        "date of referral to general paediatrics",
        null=True,
        default=False
    )
    date_of_referral_to_general_paediatrics = models.DateField(
        "date of referral to general paediatrics",
        null=True,
        default=None
    )
    first_paediatric_assessment_in_acute_or_nonacute_setting = models.IntegerField(
        "Is the first paediatric assessment in an acute or nonacute setting?",
        choices=CHRONICITY,
        null=True,
        default=None
    )
    has_description_of_the_episode_or_episodes_been_gathered = models.BooleanField(
        "has a description of the episode or episodes been gathered?",
        null=True,
        default=False
    )
    when_the_first_epileptic_episode_occurred_confidence = models.CharField(
        "how accurate is the date of the first epileptic episode?",
        max_length=3,
        choices=DATE_ACCURACY,
        default=None,
        null=True
    )
    when_the_first_epileptic_episode_occurred = models.DateField(
        "what is the date that the first epileptic episode occurred?",
        null=True,
        default=None
    )
    has_number_of_episodes_since_the_first_been_documented = models.BooleanField(
        "has the frequency of episodes since the first recorded been documented?",
        null=True,
        default=False
    )
    general_examination_performed = models.BooleanField(
        "has a general clinical examination been performed?",
        null=True,
        default=False
    )
    neurological_examination_performed = models.BooleanField(
        "has a neurological examination been performed?",
        null=True,
        default=False
    )
    developmental_learning_or_schooling_problems = models.BooleanField(
        "has the presence or absence of developmental, learning or school-based problems been recorded?",
        null=True,
        default=False
    )
    behavioural_or_emotional_problems = models.BooleanField(
        "are there any behaviour or emotional comorbid conditions present?",
        null=True,
        default=False
    )
    diagnostic_status = models.CharField(  # This currently essential - used to exclude nonepilepic kids
        max_length=1,
        choices=DIAGNOSTIC_STATUS,
        verbose_name="Status of epilepsy diagnosis. Must have epilepsy or probable epilepsy to be included.",
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

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration"
    )

    class Meta:
        indexes = [models.Index(fields=['date_of_initial_assessment'])]
        verbose_name = 'initial assessment'
        verbose_name_plural = 'initial assessments'

    def __str__(self) -> str:
        return f"id: {self.pk}"
