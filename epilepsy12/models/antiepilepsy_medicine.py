from django.db import models
from django.forms import ValidationError
from ..constants import *
from .time_and_user_abstract_base_classes import *
from .management import Management


class AntiEpilepsyMedicine(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about antiepilepsy medicines. 
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """
    antiepilepsy_medicine_type = models.IntegerField(
        "antiepilepsy medicine name",
        choices=ANTIEPILEPSY_MEDICINE_TYPES,
        default=None,
        null=True,
        blank=True
    )
    is_rescue_medicine = models.BooleanField(
        "Is the medicine a rescue medicine?",
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_snomed_code = models.CharField(
        "antiepilepsy medicine SNOMED-CT code",
        max_length=50,
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_snomed_preferred_name = models.CharField(
        "antiepilepsy medicine SNOMED-CT preferred name",
        max_length=50,
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_start_date = models.DateField(
        "antiepilepsy medicine start date",
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_stop_date = models.DateField(
        "antiepilepsy medicine start date",
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_risk_discussed = models.BooleanField(
        "have the risks related to the antiepilepsy medicine been discussed?",
        default=False,
        null=True,
        blank=True
    )

    def clean(self):
        if (self.antiepilepsy_medicine_start_date and self.antiepilepsy_medicine_stop_date):
            if (self.antiepilepsy_medicine_stop_date < self.antiepilepsy_medicine_start_date):
                raise ValidationError(
                    "Antiepilepsy medication stop date cannot be before start date")

    # relationships

    management = models.ForeignKey(
        Management,
        on_delete=models.CASCADE,
        verbose_name="related management"
    )

    class Meta:
        verbose_name = "Antiepilepsy Medicine",
        verbose_name_plural = "Antiepilepsy Medicines"

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
        return self.antiepilepsy_medicine_snomed_code
