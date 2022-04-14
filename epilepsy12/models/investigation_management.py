from django.db import models
from ..constants import *

from .registration import Registration


class Investigation_Management(models.Model):
    """
    This class records information on rescue medicines used.
    """

    rescue_medicine_type = models.CharField(
        "Type of rescue medicine prescribed",
        max_length=3,
        choices=BENZODIAZEPINE_TYPES
    )
    rescue_medicine_other = models.CharField(
        "Other documented rescue medicine previously not specified.",
        max_length=100
    )
    rescue_medicine_start_date = models.DateField(
        "date rescue medicine prescribed/given."
    )
    rescue_medicine_stop_date = models.DateField(
        "date rescue medicine stopped if known.",
        default=None
    )
    rescue_medicine_status = models.BooleanField(
        "status of rescue medicine prescription."
    )
    rescue_medicine_notes = models.CharField(
        "additional notes relating to rescue medication.",
        max_length=250
    )

    eeg_indicated = models.BooleanField(
        default=True
    )
    eeg_request_date = models.DateTimeField()

    eeg_performed_date = models.DateTimeField()

    twelve_lead_ecg_status = models.BooleanField(
        default=False
    )

    ct_head_scan_status = models.BooleanField(
        default=False
    )

    mri_brain_date = models.DateField()

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration",
        null=True
    )

    class Meta:
        verbose_name = 'Investigations and Managment'
        verbose_name_plural = 'Investigations and Managment Milestones'

    def __str__(self) -> str:
        return self.rescue_medicine_type
