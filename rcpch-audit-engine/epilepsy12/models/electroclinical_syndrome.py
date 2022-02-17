from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class ElectroClinicalSyndrome(TimeAndUserStampMixin):
    """
    This class records information on electroclinical syndromes.
    It references the episode class, since one episode can have features of a single electroclinical syndrome.
    """
    electroclinical_syndrome=models.IntegerField(choices=ELECTROCLINICAL_SYNDROMES)
    electroclinical_sydrome_other=models.CharField(max_length=250)
