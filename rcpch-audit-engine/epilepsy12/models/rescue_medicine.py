from django.db import models
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class RescueMedicine(TimeAndUserStampMixin):
    """
    This class records information on rescue medicines used.
    It references the Episode class, since one episode can involve the use of several medicines
    """
    rescue_medicine_type=models.CharField(
        max_length=3,
        choices=BENZODIAZEPINE_TYPES
    )
    rescue_medicine_other=models.CharField(max_length=100)
    rescue_medicine_start_date=models.DateField()
    rescue_medicine_stop_date=models.DateField()
    rescue_medicine_status=models.IntegerField(choices=CHECKED_STATUS)
    rescue_medicine_notes=models.CharField(max_length=250)
    assessment=models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        primary_key=True
    )