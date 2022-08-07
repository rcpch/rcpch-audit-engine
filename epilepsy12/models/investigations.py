from django.db import models
from ..constants import *

from .registration import Registration


class Investigation(models.Model):

    eeg_indicated = models.BooleanField(
        default=None,
        null=True
    )
    eeg_request_date = models.DateTimeField(
        null=True,
        blank=True
    )

    eeg_performed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    twelve_lead_ecg_status = models.BooleanField(
        default=None,
        null=True,
        blank=True
    )

    ct_head_scan_status = models.BooleanField(
        default=False
    )

    mri_indicated = models.BooleanField(
        default=None,
        null=True,
        blank=True
    )

    mri_brain_date = models.DateField(
        default=None,
        null=True,
        blank=True
    )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="Related Registration",
        null=True
    )

    class Meta:
        verbose_name = 'Investigation Milestones'
        verbose_name_plural = 'Investigation Milestones'

    def __str__(self) -> str:
        return self.pk
