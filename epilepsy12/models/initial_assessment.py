from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration
from. epilepsy_context import EpilepsyContext


class InitialAssessment(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about the initial assessment.
    Whilst other information about the child and their epilepsy may be captured across the audit year
    in the assessment table, this information MUST be collected at the first visit.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    This whole clase might better belong in the initial assessment

    """

    date_of_initial_assessment = models.DateField(
        "On what date did the initial assessment occur?"
    )
    date_of_referral_to_general_paediatrics = models.DateField(
        "date of referral to general paediatrics"
    )
    first_paediatric_assessment_in_acute_or_nonacute_setting = models.CharField(
        "Is the first paediatric assessment in an acute or nonacute setting?",
        max_length=2,
        choices=CHRONICITY
    )
    has_description_of_the_episode_or_episodes_been_gathered = models.BooleanField(
        "has a description of the episode or episodes been gathered?",
        default=False
    )
    when_the_first_epileptic_episode_occurred_confidence = models.CharField(
        "how accurate is the date of the first epileptic episode?",
        max_length=3,
        choices=DATE_ACCURACY
    )
    when_the_first_epileptic_episode_occurred = models.DateField(
        "what is the date that the first epileptic episode occurred?"
    )
    has_number_of_episodes_since_the_first_been_documented = models.BooleanField(
        "has the frequency of episodes since the first recorded been documented?",
        default=False
    )
    general_examination_performed = models.BooleanField(
        "has a general clinical examination been performed?",
        default=False
    )
    neurological_examination_performed = models.BooleanField(
        "has a neurological examination been performed?",
        default=False
    )
    developmental_learning_or_schooling_problems = models.BooleanField(
        "has the presence or absence of developmental, learning or school-based problems been recorded?",
        default=False
    )
    behavioural_or_emotional_problems = models.BooleanField(
        "are there any behaviour or emotional comorbid conditions present?",
        default=False
    )
    diagnostic_status = models.CharField(  # This currently essential - used to exclude nonepilepic kids
        max_length=1,
        choices=DIAGNOSTIC_STATUS,
        verbose_name="Status of epilepsy diagnosis. Must have epilepsy or probable epilepsy to be included.",
        default=None
    )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration"
    )
    epilepsy_context = models.OneToOneField(
        EpilepsyContext,
        on_delete=models.CASCADE,
        verbose_name="related epilepsy context"
    )

    class Meta:
        indexes = [models.Index(fields=['date_of_initial_assessment'])]
        verbose_name = 'initial assessment'
        verbose_name_plural = 'initial assessments'

    def __str__(self) -> str:
        return self.date_of_initial_assessment
