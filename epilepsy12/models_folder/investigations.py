# TODO: attribute names inconsistent e.g. eeg_indicatED & eeg_performED_date (past tense) but eeg_request_date (present tense); and mri_indicated but mri_BRAIN_requested_date & mri_BRAIN_reported_date; and perhaps eeg_PERFORMED but mri_BRAIN_REPORTED Should refactor

# standard imports
from datetime import date
from dateutil.relativedelta import relativedelta

# 3rd party
from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords

# rcpch
from .help_text_mixin import HelpTextMixin
from ..general_functions import stringify_time_elapsed
from .time_and_user_abstract_base_classes import *


class Investigations(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    eeg_indicated = models.BooleanField(
        help_text={
            "label": "Has a first EEG been requested?",
            "reference": "If a diagnosis of epilepsy is suspected, a routine EEG should be carried out to support the diagnosis. CYP undergoing initial investigations for epilepsy should have tests within 4 weeks of being requested.",
        },
        default=None,
        null=True,
        blank=True,
    )
    eeg_request_date = models.DateField(
        help_text={
            "label": "Date EEG requested",
            "reference": "Date EEG requested. Even if the EEG was not performed, a request date is still required.",
        },
        default=None,
        null=True,
        blank=True,
    )

    eeg_performed_date = models.DateField(
        help_text={
            "label": "Date EEG performed",
            "reference": "Date EEG performed",
        },
        default=None,
        null=True,
        blank=True,
    )

    twelve_lead_ecg_status = models.BooleanField(
        help_text={
            "label": "Has a 12-Lead ECG been performed?",
            "reference": "The Epilepsy12 standard is that all children with an convulsive episode should have a 12 lead ECG",
        },
        default=None,
        null=True,
        blank=True,
    )

    ct_head_scan_status = models.BooleanField(
        help_text={
            "label": "Has a CT head been performed?",
            "reference": "NICE states if MRI is contraindicated, consider a CT scan for children, young people and adults with epilepsy.",
        },
        default=None,
        null=True,
        blank=True,
    )

    mri_indicated = models.BooleanField(
        help_text={
            "label": "Has a brain MRI been requested?",
            "reference": "NICE recommends that an MRI scan should be offered to children, young people and adults diagnosed with epilepsy, unless they have idiopathic generalised epilepsy or self-limited epilepsy with centrotemporal spikes. The MRI should be carried out within 6 weeks of the MRI referral.",
        },
        default=None,
        null=True,
        blank=True,
    )

    mri_brain_requested_date = models.DateField(
        help_text={
            "label": "MRI brain requested date",
            "reference": "MRI brain requested date",
        },
        default=None,
        null=True,
        blank=True,
    )

    mri_brain_reported_date = models.DateField(
        help_text={
            "label": "Date MRI brain reported",
            "reference": "Date MRI brain reported",
        },
        default=None,
        null=True,
        blank=True,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    def mri_wait(self):
        """
        Calculated field. Returns time elapsed between date EEG requested and performed as a string.
        """
        if self.mri_brain_reported_date and self.mri_brain_requested_date:
            return (self.mri_brain_reported_date - self.mri_brain_requested_date).days

    def eeg_wait(self):
        """
        Calculated field. Returns time elapsed between date EEG requested and performed as a string.
        """
        if self.eeg_performed_date and self.eeg_request_date:
            return (self.eeg_performed_date - self.eeg_request_date).days

    def get_current_date(self):
        return date.today()

    # relationships
    registration = models.OneToOneField(
        "epilepsy12.Registration",
        on_delete=models.CASCADE,
        verbose_name="Related Registration",
        null=True,
    )

    class Meta:
        verbose_name = "Investigations"
        verbose_name_plural = "Investigations"

    def __str__(self) -> str:
        return f"Investigations for {self.registration.case}"
