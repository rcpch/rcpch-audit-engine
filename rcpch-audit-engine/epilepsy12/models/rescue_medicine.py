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
        "Type of rescue medicine prescribed",
        max_length=3,
        choices=BENZODIAZEPINE_TYPES
    )
    rescue_medicine_other=models.CharField(
        "Other documented rescue medicine previously not specified.",
        max_length=100
    )
    rescue_medicine_start_date=models.DateField(
        "date rescue medicine prescribed/given."
    )
    rescue_medicine_stop_date=models.DateField(
        "date rescue medicine stopped if known.",
        default=None
    )
    rescue_medicine_status=models.BooleanField(
        "status of rescue medicine prescription."
    )
    rescue_medicine_notes=models.CharField(
        "additional notes relating to rescue medication.",
        max_length=250
    )

    # relationships
    assessment=models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        primary_key=True
    )

    class Meta:
        ordering = ['rescue_medicine_type']
        verbose_name = 'Rescue Medicine',
        verbose_name_plural="Rescue Medicines"
        
    
    def __str__(self) -> str:
        return self.rescue_medicine_type