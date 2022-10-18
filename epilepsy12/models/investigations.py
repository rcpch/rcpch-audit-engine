from django.db import models

from epilepsy12.models.help_text_mixin import HelpTextMixin
from ..general_functions import *

from .registration import Registration
from .time_and_user_abstract_base_classes import *


class Investigations(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):

    eeg_indicated = models.BooleanField(
        help_text={
            'label': "Is an EEG indicated?",
            'reference': "Is an EEG indicated?",
        },
        default=None,
        null=True,
        blank=True
    )
    eeg_request_date = models.DateField(
        help_text={
            'label': "Date EEG requested",
            'reference': "Date EEG requested",
        },
        default=None,
        null=True,
        blank=True
    )

    eeg_performed_date = models.DateField(
        help_text={
            'label': "Date EEG performed",
            'reference': "Date EEG performed",
        },
        default=None,
        null=True,
        blank=True
    )

    twelve_lead_ecg_status = models.BooleanField(
        help_text={
            'label': "Has a 12-Lead ECG been performed",
            'reference': "Has a 12-Lead ECG been performed",
        },
        default=None,
        null=True,
        blank=True
    )

    ct_head_scan_status = models.BooleanField(
        help_text={
            'label': "Has a CT head been performed?",
            'reference': "Has a CT head been performed?",
        },
        default=None,
        null=True,
        blank=True
    )

    mri_indicated = models.BooleanField(
        help_text={
            'label': "Is an MRI brain indicated?",
            'reference': "Is an MRI brain indicated?",
        },
        default=None,
        null=True,
        blank=True
    )

    mri_brain_requested_date = models.DateField(
        help_text={
            'label': "MRI brain requested date",
            'reference': "MRI brain requested date",
        },
        default=None,
        null=True,
        blank=True
    )

    mri_brain_performed_date = models.DateField(
        help_text={
            'label': "MRI brain performed date",
            'reference': "MRI brain performed date",
        },
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
