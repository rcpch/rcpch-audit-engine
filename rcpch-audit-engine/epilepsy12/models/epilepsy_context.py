from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .case import Case

class EpilepsyContext(TimeAndUserStampMixin):
    """
    This class records contextual information that defines epilepsy risk.
    It references the InitialAssessment class, as each case optionally has a single epilepsy context.
    """
    previous_febrile_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    previous_acute_symptomatic_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    is_there_a_family_history_of_epilepsy=models.CharField(
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    previous_neonatal_seizures=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    diagnosis_of_epilepsy_withdrawn=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )