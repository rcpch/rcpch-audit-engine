from django.db import models
from ..constants import *
from ..general_functions import calculate_time_elapsed

from .registration import Registration
from .time_and_user_abstract_base_classes import *


class Investigations(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):

    eeg_indicated = models.BooleanField(
        "Is an EEG indicated?",
        default=None,
        null=True,
        blank=True
    )
    eeg_request_date = models.DateField(
        "Date EEG requested",
        default=None,
        null=True,
        blank=True
    )

    eeg_performed_date = models.DateField(
        "Date EEG performed",
        default=None,
        null=True,
        blank=True
    )

    twelve_lead_ecg_status = models.BooleanField(
        default=None,
        null=True,
        blank=True
    )

    ct_head_scan_status = models.BooleanField(
        "Has a CT head been performed?",
        default=None,
        null=True,
        blank=True
    )

    mri_indicated = models.BooleanField(
        "Is an MRI brain indicated?",
        default=None,
        null=True,
        blank=True
    )

    mri_brain_requested_date = models.DateField(
        "MRI brain requested date",
        default=None,
        null=True,
        blank=True
    )

    mri_brain_performed_date = models.DateField(
        "MRI brain performed date",
        default=None,
        null=True,
        blank=True
    )

    def mri_wait(self):
        """
        Calculated field. Returns time elapsed between date EEG requested and performed as a string.
        """
        if self.mri_brain_performed_date and self.mri_brain_requested_date:
            return calculate_time_elapsed(self.mri_brain_requested_date, self.mri_brain_performed_date)

    def eeg_wait(self):
        """
        Calculated field. Returns time elapsed between date EEG requested and performed as a string.
        """
        if self.eeg_performed_date and self.eeg_request_date:
            return calculate_time_elapsed(self.eeg_request_date, self.eeg_performed_date)

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
        return f"Investigations for {self.registration.case}"
