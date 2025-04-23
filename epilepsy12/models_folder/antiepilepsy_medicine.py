from django.contrib.gis.db import models
from django.forms import ValidationError
from simple_history.models import HistoricalRecords
from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *


class AntiEpilepsyMedicine(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    This class records information about antiepilepsy medicines.
    It references the Episode class, as one episode can involve several antiepilepsy medicines.
    """

    is_rescue_medicine = models.BooleanField(
        help_text={
            "label": "Is the medicine a rescue medicine?",
            "reference": "Is the medicine a rescue medicine?",
        },
        default=None,
        null=True,
        blank=True,
    )
    antiepilepsy_medicine_start_date = models.DateField(
        help_text={
            "label": "Medicine start date",
            "reference": "Antiepilepsy medicine start date",
        },
        default=None,
        null=True,
        blank=True,
    )
    antiepilepsy_medicine_stop_date = models.DateField(
        help_text={
            "label": "Medicine discontinued date",
            "reference": "Antiseizure medicine discontinued date",
        },
        default=None,
        null=True,
        blank=True,
    )
    antiepilepsy_medicine_risk_discussed = models.BooleanField(
        help_text={
            "label": "Medication risks discussed?",
            "reference": "Have the risks related to the antiseizure medicine been discussed with the child/young person and their family?",
        },
        default=None,
        null=True,
        blank=True,
    )
    is_a_pregnancy_prevention_programme_needed = models.BooleanField(
        help_text={
            "label": "Is a pregnancy prevention programme indicated?",
            "reference": "For girls and young women who are prescribed sodium valproate, it is recommended that pregnancy prevention is actively discussed and documented.",
        },
        default=None,
        null=True,
        blank=True,
    )
    has_a_valproate_annual_risk_acknowledgement_form_been_completed = models.BooleanField(
        help_text={
            "label": "Has a Valproate - Annual Risk Acknowledgment Form been completed?",
            "reference": "For girls and young women who are prescribed sodium valproate, it is recommended that Has an annual Valproate - Annual Risk Acknowledgment Form is completed.",
        },
        default=None,
        null=True,
        blank=True,
    )

    is_a_pregnancy_prevention_programme_in_place = models.BooleanField(
        help_text={
            "label": "Is the Valproate Pregnancy Prevention Programme in place?",
            "reference": "For girls and young women who are prescribed sodium valproate, it is recommended that pregnancy prevention is actively discussed and documented.",
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

    def clean(self):
        if (
            self.antiepilepsy_medicine_start_date
            and self.antiepilepsy_medicine_stop_date
        ):
            if (
                self.antiepilepsy_medicine_stop_date
                < self.antiepilepsy_medicine_start_date
            ):
                raise ValidationError(
                    "Antiepilepsy medication stop date cannot be before start date"
                )

    # relationships

    management = models.ForeignKey(
        "epilepsy12.Management",
        on_delete=models.CASCADE,
        verbose_name="related management",
    )

    medicine_entity = models.ForeignKey(
        "epilepsy12.Medicine",
        on_delete=models.PROTECT,
        help_text={
            "label": "Medicine Name",
            "reference": "Please enter the medicine.",
        },
        default=None,
        null=True,
    )

    class Meta:
        verbose_name = "Antiepilepsy Medicine"
        verbose_name_plural = "Antiepilepsy Medicines"
        ordering = ["management__registration__case"]

    @property
    def length_of_treatment(self):
        "Returns length of treatment if dates supplied"
        if (
            self.antiepilepsy_medicine_start_date
            and self.antiepilepsy_medicine_stop_date
        ):
            if (
                self.antiepilepsy_medicine_stop_date
                <= self.antiepilepsy_medicine_start_date
            ):
                raise Exception(
                    "The medication stop date cannot be before or the same as the medication start date."
                )

            else:
                difference = (
                    self.antiepilepsy_medicine_stop_date
                    - self.antiepilepsy_medicine_start_date
                ).days
                return f"{difference} days"
        else:
            raise Exception("Cannot calculate length of treatment without 2 dates.")

    def __str__(self) -> str:
        if self.medicine_entity is not None:
            return f"{self.medicine_entity.medicine_name} for {self.management.registration.case}"
        else:
            return "No medicine supplied"

    def get_has_a_valproate_annual_risk_acknowledgement_form_been_completed_conditional_help_text(
        self,
    ):
        """
        Return conditional help text based on cohort - works in conjunction with HelpTextMixin

        Relates to KPI measure 8 amendment in issue #1215

        This measure has changed to allow a risk acknowledgement form and pregnancy prevention programme to be in place
        to be offered to all girls on valproate (any age) and all girls aged 12 and over on Topiramate.

        This measure is only calculated for cohorts 7 and above, so the old calculation is retained.

        In the user interface, the help text is updated to reflect the new measure, but only for cohorts 7 and above.
        """
        if (
            hasattr(self, "management")
            and self.management
            and hasattr(self.management, "registration")
            and self.management.registration.cohort > 6
        ):
            return {
                "label": "Has the Annual Risk Acknowledgment Form been completed?",
                "reference": "Have the risks related to the antiseizure medicine been discussed with the child/young person and their family?",
            }
        return None

    def get_is_a_pregnancy_prevention_programme_in_place_conditional_help_text(self):
        """
        Return conditional help text based on cohort - works in conjunction with HelpTextMixin

        Relates to KPI measure 8 amendment in issue #1215

        This measure has changed to allow a risk acknowledgement form and pregnancy prevention programme to be in place
        to be offered to all girls on valproate (any age) and all girls aged 12 and over on Topiramate.

        This measure is only calculated for cohorts 7 and above, so the old calculation is retained.

        In the user interface, the help text is updated to reflect the new measure, but only for cohorts 7 and above.
        """
        if (
            hasattr(self, "management")
            and self.management
            and hasattr(self.management, "registration")
            and self.management.registration.cohort > 6
        ):
            return {
                "label": "Is a Pregnancy Prevention Programme in place?",
                "reference": "For girls and young women who are prescribed sodium valproate or topiramate (if > 12y), it is recommended that pregnancy prevention is actively discussed and documented.",
            }
        return None  # Fall back to default help text
