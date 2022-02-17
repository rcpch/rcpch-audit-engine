from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class AntiEpilepsyDrug(TimeAndUserStampMixin):
    """
    This class records information about antiepilepsy drugs. 
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """
    anti_epileptic_drug_type=models.IntegerField(choices=ANTI_EPILEPTIC_DRUG_TYPES)
    anti_epileptic_drug_type_other=models.CharField(50)
    anti_epileptic_drug_snomed_code=models.CharField(50) # this is a new field
    anti_epileptic_start_date=models.models.DateField()
    anti_epileptic_stop_date=models.models.DateField()
    anti_epilepsy_drug_risk_discussed=models.BooleanField(
        default=False
    )