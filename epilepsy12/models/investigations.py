import math
from dateutil import relativedelta
from django.db import models
from ..constants import *

from .registration import Registration


class Investigation(models.Model):

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

    mri_brain_date = models.DateField(
        "MRI brain date",
        default=None,
        null=True,
        blank=True
    )

    def eeg_time(self):
        """
        Calculated field. Returns time elapsed between date EEG requested and performed as a string.
        """
        if self.eeg_performed_date and self.eeg_request_date:
            calculated_age = relativedelta.relativedelta(
                self.eeg_performed_date, self.eeg_request_date)
            months = calculated_age.months
            years = calculated_age.years
            weeks = calculated_age.weeks
            days = calculated_age.days
            final = ''
            if years == 1:
                final += f'{calculated_age.years} year'
                if (months/12) - years == 1:
                    final += f'{months} month'
                elif (months/12)-years > 1:
                    final += f'{math.floor((months*12)-years)} months'
                else:
                    return final

            elif years > 1:
                final += f'{calculated_age.years} years'
                if (months/12) - years == 1:
                    final += f', {months} month'
                elif (months/12)-years > 1:
                    final += f', {math.floor((months*12)-years)} months'
                else:
                    return final
            else:
                # under a year of age
                if months == 1:
                    final += f'{months} month'
                elif months > 0:
                    final += f'{months} months, '
                    if weeks >= (months*4):
                        if (weeks-(months*4)) == 1:
                            final += '1 week'
                        else:
                            final += f'{math.floor(weeks-(months*4))} weeks'
                else:
                    if weeks > 0:
                        if weeks == 1:
                            final += f'{math.floor(weeks)} week'
                        else:
                            final += f'{math.floor(weeks)} weeks'
                    else:
                        if days > 0:
                            if days == 1:
                                final += f'{math.floor(days)} day'
                            if days > 1:
                                final += f'{math.floor(days)} days'
                        else:
                            final += 'Performed today'
            return final

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
