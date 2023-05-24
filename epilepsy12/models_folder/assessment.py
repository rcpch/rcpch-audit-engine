from datetime import date

from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords
from .help_text_mixin import HelpTextMixin

from epilepsy12.general_functions import stringify_time_elapsed
from .time_and_user_abstract_base_classes import *


class Assessment(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class stores information on each assessment performed during the registration period.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """

    childrens_epilepsy_surgical_service_referral_criteria_met = models.BooleanField(
        help_text={
            "label": "Are ANY of these criteria present?",
            "reference": "Have ANY of the criteria for referral to a children's epilepsy surgery service been met?",
        },
        blank=True,
        default=None,
        null=True,
    )
    consultant_paediatrician_referral_made = models.BooleanField(
        help_text={
            "label": "Has a referral been made to a consultant paediatrician with expertise in epilepsies?",
            "reference": "Has a referral been made to a consultant paediatrician with expertise in epilepsies?",
        },
        blank=True,
        default=None,
        null=True,
    )
    consultant_paediatrician_referral_date = models.DateField(
        help_text={
            "label": "Date of referral to a consultant paediatrician with expertise in epilepsies.",
            "reference": "Has a referral been made to a consultant paediatrician with expertise in epilepsies?",
        },
        blank=True,
        null=True,
        default=None,
    )
    consultant_paediatrician_input_date = models.DateField(
        help_text={
            "label": "Date seen by a consultant paediatrician with expertise in epilepsies.",
            "reference": "Date seen by a consultant paediatrician with expertise in epilepsies.",
        },
        blank=True,
        default=None,
        null=True,
    )
    paediatric_neurologist_referral_made = models.BooleanField(
        help_text={
            "label": "Has a referral to a consultant paediatric neurologist been made?",
            "reference": "Has a referral to a consultant paediatric neurologist been made?",
        },
        blank=True,
        default=None,
        null=True,
    )
    paediatric_neurologist_referral_date = models.DateField(
        help_text={
            "label": "Date of referral to a consultant paediatric neurologist.",
            "reference": "Date of referral to a consultant paediatric neurologist.",
        },
        blank=True,
        default=None,
        null=True,
    )
    paediatric_neurologist_input_date = models.DateField(
        help_text={
            "label": "Date seen by consultant paediatric neurologist.",
            "reference": "Date seen by consultant paediatric neurologist.",
        },
        blank=True,
        null=True,
        default=None,
    )
    childrens_epilepsy_surgical_service_referral_made = models.BooleanField(
        help_text={
            "label": "Has a referral to a children's epilepsy surgery service been made?",
            "reference": "Has a referral to a children's epilepsy surgery service been made?",
        },
        blank=True,
        default=None,
        null=True,
    )
    childrens_epilepsy_surgical_service_referral_date = models.DateField(
        help_text={
            "label": "Date of referral to a children's epilepsy surgery service",
            "reference": "Date of referral to a children's epilepsy surgery service",
        },
        blank=True,
        default=None,
        null=True,
    )
    childrens_epilepsy_surgical_service_input_date = models.DateField(
        help_text={
            "label": "Date seen by children's epilepsy surgery service",
            "reference": "Date seen by children's epilepsy surgery service",
        },
        blank=True,
        default=None,
        null=True,
    )
    epilepsy_specialist_nurse_referral_made = models.BooleanField(
        help_text={
            "label": "Has a referral to an epilepsy nurse specialist been made?",
            "reference": "Has a referral to an epilepsy nurse specialist been made?",
        },
        blank=True,
        default=None,
        null=True,
    )
    epilepsy_specialist_nurse_referral_date = models.DateField(
        help_text={
            "label": "Date of referral to an epilepsy nurse specialist",
            "reference": "Date of referral to an epilepsy nurse specialist",
        },
        blank=True,
        default=None,
        null=True,
    )
    epilepsy_specialist_nurse_input_date = models.DateField(
        help_text={
            "label": "Date seen by an epilepsy nurse specialist",
            "reference": "Date seen by an epilepsy nurse specialist",
        },
        blank=True,
        default=None,
        null=True,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value
    
    def get_current_date(self):
        return date.today()

    def consultant_paediatrician_wait(self):
        """
        Calculated field. Returns time elapsed between date consultant paediatrician review requested and performed as a string.
        """
        if (
            self.consultant_paediatrician_referral_date
            and self.consultant_paediatrician_input_date
        ):
            return stringify_time_elapsed(
                self.consultant_paediatrician_referral_date,
                self.consultant_paediatrician_input_date,
            )
        else:
            return None  # raise ValueError("Both referral and input dates must be provided")

    def paediatric_neurologist_wait(self):
        """
        Calculated field. Returns time elapsed between date paediatric neurologist review requested and performed as a string.
        """
        if (
            self.paediatric_neurologist_referral_date
            and self.paediatric_neurologist_input_date
        ):
            return stringify_time_elapsed(
                self.paediatric_neurologist_referral_date,
                self.paediatric_neurologist_input_date,
            )
        else:
            return None  # raise ValueError("Both referral and input dates must be provided")

    def childrens_epilepsy_surgery_wait(self):
        """
        Calculated field. Returns time elapsed between date children's epilepsy surgery service review requested and performed as a string.
        """
        if (
            self.childrens_epilepsy_surgical_service_referral_date
            and self.childrens_epilepsy_surgical_service_input_date
        ):
            return stringify_time_elapsed(
                self.childrens_epilepsy_surgical_service_referral_date,
                self.childrens_epilepsy_surgical_service_input_date,
            )
        else:
            return None  # raise ValueError("Both referral and input dates must be provided")

    def epilepsy_nurse_specialist_wait(self):
        """
        Calculated field. Returns time elapsed between date children's epilepsy surgery service review requested and performed as a string.
        """
        if (
            self.epilepsy_specialist_nurse_referral_date
            and self.epilepsy_specialist_nurse_input_date
        ):
            return stringify_time_elapsed(
                self.epilepsy_specialist_nurse_referral_date,
                self.epilepsy_specialist_nurse_input_date,
            )
        else:
            return None  # raise ValueError("Both referral and input dates must be provided")

    registration = models.OneToOneField(
        "epilepsy12.Registration",
        on_delete=models.CASCADE,
        verbose_name="related registration",
    )

    class Meta:
        verbose_name = "Assessment"
        verbose_name_plural = "Assessment"

    def __str__(self) -> str:
        return f"Assessment Milestones for {self.registration.case}"

    def save(self, *args, **kwargs) -> None:
        # called on save of a record

        return super().save(*args, **kwargs)
