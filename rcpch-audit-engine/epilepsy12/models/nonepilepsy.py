from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class NonEpilepsy(TimeAndUserStampMixin):
    """
    This class records information about nonepilepsy features of episode.
    This class optionally references the Episode class as one episode can have one set of nonepilepsy features.
    """
    nonepilepsy_type=models.IntegerField(choices=EPIS_TYPE)
    nonepilepsy_syncope=models.CharField(
        max_length=3, 
        choices=NON_EPILEPTIC_SYNCOPES)
    nonepilepsy_behavioural=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    nonepilepsy_sleep=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    nonepilepsy_paroxysmal=models.CharField(
        max_length=3, 
        choices=NON_EPILEPSY_PAROXYSMS)
    nonepilepsy_migraine=models.CharField(
        max_length=3,
        choices=MIGRAINES)
    nonepilepsy_miscellaneous=models.CharField(
        max_length=3, 
        choices=EPIS_MISC)
    nonepilepsy_other=models.CharField(max_length=250)
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.CASCADE,
        primary_key=True
    )