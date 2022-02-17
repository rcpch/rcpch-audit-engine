from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .case import Case
from .assessment import Assessment
from. epilepsy_context import EpilepsyContext

class InitialAssessment(TimeAndUserStampMixin):
    """
    This class records information about each seizure episode.
    This class references the Case class as a case can have multiple episodes.
    This class references the EEG class as an episode can have multiple EEGs

    This whole clase might better belong in the initial assessment

    On Episode
    """
    
    date_of_referral_to_general_paediatrics=models.DateField()
    first_paediatric_assessment_in_acute_or_nonacute_setting=models.CharField(
        max_length=2, 
        choices=CHRONICITY
    )
    has_description_of_the_episode_or_episodes_been_gathered=models.BooleanField(
        default=False
    )
    when_the_first_epileptic_episode_occurred_confidence=models.CharField(
        max_length=3, 
        choices=DATE_ACCURACY
    )
    when_the_first_epileptic_episode_occurred=models.DateField()
    has_frequency_or_number_of_episodes_since_the_first_episode_been_documented=models.BooleanField(
        default=False
    )
    general_examination_performed=models.BooleanField(
        default=False
    )
    neurological_examination_performed=models.BooleanField(
        default=False
    )
    developmental_learning_or_schooling_problems=models.BooleanField(
        default=False
    )
    behavioural_or_emotional_problems=models.BooleanField(
        default=False
    )
    case = models.OneToOneField(
        Case,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    assessment=models.OneToOneField(
        Assessment,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    epilepsy_context=models.OneToOneField( 
        EpilepsyContext,
        on_delete=models.CASCADE,
        primary_key=True
    )