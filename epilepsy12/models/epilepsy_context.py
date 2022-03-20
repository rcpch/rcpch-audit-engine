from dateutil import relativedelta
from datetime import date
from django.db import models
from django.forms import DecimalField, FloatField
from ..constants import *
from .time_and_user_abstract_base_classes import *


class EpilepsyContext(models.Model):
    """
    This class records contextual information that defines epilepsy risk.
    It references the InitialAssessment class, as each case optionally has a single epilepsy context.
    """

    previous_febrile_seizure = models.CharField(
        "has there been a previous febrile seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_acute_symptomatic_seizure = models.CharField(
        "has there been a previous acute symptomatic seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=OPT_OUT_UNCERTAIN[1][0]
    )
    is_there_a_family_history_of_epilepsy = models.CharField(
        "is there a family history of epilepsy?",
        max_length=3,
        choices=OPT_OUT_UNCERTAIN,
        default=OPT_OUT_UNCERTAIN[1][0]
    )
    previous_neonatal_seizures = models.CharField(
        "were there seizures in the neonatal period?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN,
        default=OPT_OUT_UNCERTAIN[1][0]
    )
    diagnosis_of_epilepsy_withdrawn = models.CharField(
        "has the diagnosis of epilepsy been withdrawn?",
        max_length=2,
        choices=OPT_OUT,
        default=OPT_OUT[1][0]
    )
    date_of_first_epileptic_seizure = models.DateField(
        "What date was the first reported epileptic seizure?"
    )
    epilepsy_decimal_years = DecimalField(
        help_text="The number of decimal years calculated from the first seizure to the present day.",
        decimal_places=1,
        max_digits=5
    )

    class Meta:
        verbose_name = 'epilepsy context'
        verbose_name_plural = 'epilepsy contexts'

    def save(
            self,
            *args, **kwargs) -> None:
        if (self.date_of_first_epileptic_seizure):
            today = date.today()
            calculated_age = relativedelta.relativedelta(
                today, self.date_of_first_epileptic_seizure)
            self.epilepsy_decimal_years = calculated_age.days/365.25
        return super().save(*args, **kwargs)
