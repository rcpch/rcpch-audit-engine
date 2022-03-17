from django.db import models
from django.forms import ValidationError
from ..constants import *
from .time_and_user_abstract_base_classes import *

from .assessment import Assessment


class AntiEpilepsyMedicine(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about antiepilepsy medicines. 
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """
    antiepilepsy_medicine_type = models.IntegerField(
        "antiepilepsy medicine name",
        choices=ANTIEPILEPSY_MEDICINE_TYPES
    )
    antiepilepsy_medicine_type_other = models.CharField(
        "other antiepilepsy medicine name",
        max_length=50,
        blank=True
    )
    antiepilepsy_medicine_snomed_code = models.CharField(
        "antiepilepsy medicine SNOMED-CT code",
        max_length=50,
        blank=True
    )
    antiepilepsy_medicine_start_date = models.DateField(
        "antiepilepsy medicine start date",
    )
    antiepilepsy_medicine_stop_date = models.DateField(
        "antiepilepsy medicine start date",
    )
    antiepilepsy_medicine_risk_discussed = models.BooleanField(
        "have the risks related to the antiepilepsy medicine been discussed?",
        default=False
    )

    def clean(self):
        if (self.antiepilepsy_medicine_start_date and self.antiepilepsy_medicine_stop_date):
            if (self.antiepilepsy_medicine_stop_date < self.antiepilepsy_medicine_start_date):
                raise ValidationError(
                    "Antiepilepsy medication stop date cannot be before start date")

    # relationships

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        verbose_name="related assessment"
    )

    class Meta:
        verbose_name = "antiepilepsy medicine",
        verbose_name_plural = "antiepilepsy medicines"

    @property
    def length_of_treatment(self):
        "Returns length of treatment if dates supplied"
        if (self.antiepilepsy_medicine_start_date and self.antiepilepsy_medicine_stop_date):
            if (self.antiepilepsy_medicine_stop_date > self.antiepilepsy_medicine_start_date):
                raise Exception(
                    "The medication stop date cannot be before the medication start date.")

            else:
                difference = (self.antiepilepsy_medicine_stop_date -
                              self.antiepilepsy_medicine_start_date).days
                return f"{difference} days"
        else:
            raise Exception(
                "Cannot calculate length of treatment without 2 dates.")

    def __str__(self) -> str:
        if (self.antiepilepsy_medicine_type):
            return self.antiepilepsy_medicine_type
        else:
            return self.antiepilepsy_medicine_type_other
