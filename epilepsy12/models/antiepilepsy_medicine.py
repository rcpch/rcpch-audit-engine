from django.db import models
from django.forms import ValidationError
from epilepsy12.models.help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *
from .management import Management
from ..general_functions import *


class AntiEpilepsyMedicine(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class records information about antiepilepsy medicines. 
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """
    medicine_id = models.IntegerField(
        help_text={
            'label': "Medicine Name",
            'reference': "Please enter the medicine.",
        },
        default=None,
        null=True,
        blank=True
    )
    medicine_name = models.CharField(
        max_length=200,
        help_text={
            'label': "Medicine name",
            'reference': "Please enter the medicine name.",
        },
        default=None,
        null=True,
        blank=True,
    )
    is_rescue_medicine = models.BooleanField(
        help_text={
            'label': "Is the medicine a rescue medicine?",
            'reference': "Is the medicine a rescue medicine?",
        },
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_snomed_code = models.CharField(
        help_text={
            'label': "Antiseizure/rescue medicine SNOMED-CT code",
            'reference': "Antiseizure medicine SNOMED-CT code",
        },
        max_length=50,
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_snomed_preferred_name = models.CharField(
        help_text={
            'label': "Antiseizure/rescue medicine SNOMED-CT preferred name",
            'reference': "Antiseizure medicine SNOMED-CT preferred name",
        },
        max_length=50,
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_start_date = models.DateField(
        help_text={
            'label': "Medicine start date",
            'reference': "Antiepilepsy medicine start date",
        },
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_stop_date = models.DateField(
        help_text={
            'label': "Medicine discontinued date",
            'reference': "Antiseizure medicine discontinued date",
        },
        default=None,
        null=True,
        blank=True
    )
    antiepilepsy_medicine_risk_discussed = models.BooleanField(
        help_text={
            'label': "Medication risks discussed?",
            'reference': "Have the risks related to the antiseizure medicine been discussed with the child/young person and their family?",
        },
        default=None,
        null=True,
        blank=True
    )
    is_a_pregnancy_prevention_programme_needed = models.BooleanField(
        help_text={
            'label': "Is a pregnancy prevention programme indicated?",
            'reference': "For girls and young women who are presecribed sodium valproate, it is recommended that pregnancy prevention is actively discussed and documented.",
        },
        default=None,
        null=True,
        blank=True
    )
    is_a_pregnancy_prevention_programme_in_place = models.BooleanField(
        help_text={
            'label': "Is a pregnancy prevention programme (PPP) in place?",
            'reference': "For girls and young women who are presecribed sodium valproate, it is recommended that pregnancy prevention is actively discussed and documented.",
        },
        default=None,
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
        verbose_name = "Antiepilepsy Medicine"
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
