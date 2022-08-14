from django.db import models

from epilepsy12.models.site import Site

from ..general_functions import calculate_time_elapsed
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration


class Assessment(models.Model):
    """
    This class stores information on each assessment performed during the registration period.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """
    lead_hospital = models.CharField(
        "lead_hospital",
        max_length=100,
        default=None,
        null=True
    )
    childrens_epilepsy_surgical_service_referral_criteria_met = models.BooleanField(
        "Have the criteria for referral to a children's epilepsy surgery service been met?",
        default=None,
        null=True,
    )
    consultant_paediatrician_referral_made = models.BooleanField(
        "Has a referral been made to a consultant paediatrician with an interest in epilepsy?",
        default=None,
        null=True
    )
    consultant_paediatrician_referral_date = models.DateField(
        "Date of referral to a consultant paediatrician with expertise in epilepsy.",
        null=True,
        default=None
    )
    consultant_paediatrician_input_date = models.DateField(
        "Date seen by a consultant paediatrician with expertise in epilepsy.",
        default=None,
        null=True
    )
    paediatric_neurologist_referral_made = models.BooleanField(
        "Has a referral to a consultant paediatric neurologist been made?",
        default=None,
        null=True
    )
    paediatric_neurologist_referral_date = models.DateField(
        "Date of referral to a consultant paediatric neurologist.",
        default=None,
        null=True
    )
    paediatric_neurologist_input_date = models.DateField(
        "Date seen by consultant paediatric neurologist.",
        null=True,
        default=None
    )
    childrens_epilepsy_surgical_service_referral_made = models.BooleanField(
        "Has a referral to a children's epilepsy surgery service been made?",
        default=None,
        null=True
    )
    childrens_epilepsy_surgical_service_referral_date = models.DateField(
        "Date of referral to a children's epilepsy surgery service",
        blank=True,
        default=None,
        null=True
    )
    childrens_epilepsy_surgical_service_input_date = models.DateField(
        "Date seen by children's epilepsy surgery service",
        blank=True,
        default=None,
        null=True
    )
    epilepsy_specialist_nurse_referral_made = models.BooleanField(
        "Has a referral to an epilepsy nurse specialist been made?",
        default=None,
        null=True
    )
    epilepsy_specialist_nurse_referral_date = models.DateField(
        "Date of referral to an epilepsy nurse specialist",
        blank=True,
        default=None,
        null=True
    )
    epilepsy_specialist_nurse_input_date = models.DateField(
        "Date seen by an epilepsy nurse specialist",
        blank=True,
        default=None,
        null=True
    )
    were_any_of_the_epileptic_seizures_convulsive = models.BooleanField(
        "Were any of the epileptic seizures convulsive?",
        default=None,
        null=True
    )
    prolonged_generalized_convulsive_seizures = models.BooleanField(
        "Were there any prolonged generalised epileptic seizures?",
        default=None,
        null=True
    )
    experienced_prolonged_focal_seizures = models.BooleanField(
        "Were there any prolonged focal seizures?",
        default=None,
        null=True
    )

    """
    calculated fields
    """

    def consultant_paediatrician_wait(self):
        """
        Calculated field. Returns time elapsed between date consultant paediatrician review requested and performed as a string.
        """
        if self.consultant_paediatrician_referral_date and self.consultant_paediatrician_input_date:
            return calculate_time_elapsed(self.consultant_paediatrician_referral_date, self.consultant_paediatrician_input_date)

    def paediatric_neurologist_wait(self):
        """
        Calculated field. Returns time elapsed between date paediatric neurologist review requested and performed as a string.
        """
        if self.paediatric_neurologist_referral_date and self.paediatric_neurologist_input_date:
            return calculate_time_elapsed(self.paediatric_neurologist_referral_date, self.paediatric_neurologist_input_date)

    def childrens_epilepsy_surgery_wait(self):
        """
        Calculated field. Returns time elapsed between date children's epilepsy surgery service review requested and performed as a string.
        """
        if self.childrens_epilepsy_surgical_service_referral_date and self.childrens_epilepsy_surgical_service_input_date:
            return calculate_time_elapsed(self.childrens_epilepsy_surgical_service_referral_date, self.childrens_epilepsy_surgical_service_input_date)

    def epilepsy_nurse_specialist_wait(self):
        """
        Calculated field. Returns time elapsed between date children's epilepsy surgery service review requested and performed as a string.
        """
        if self.epilepsy_specialist_nurse_referral_date and self.epilepsy_specialist_nurse_input_date:
            return calculate_time_elapsed(self.epilepsy_specialist_nurse_referral_date, self.epilepsy_specialist_nurse_input_date)

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="related registration"
    )

    # tertiary_paediatric_neurology_centre = models.OneToOneField(
    #     Site,
    #     on_delete=models.CASCADE,
    #     verbose_name="related paediatric neurology centre",
    #     default=None,
    #     null=True
    # )
    # epilepsy_surgery_centre = models.OneToOneField(
    #     Site,
    #     on_delete=models.CASCADE,
    #     verbose_name="related children's epilepsy surgery centre",
    #     default=None,
    #     null=True
    # )

    class Meta:
        verbose_name = "assessment",
        verbose_name_plural = "assessments"

    def __str__(self) -> str:
        return "assessment"

    # TODO #14 Class function to calculate cohort based on first paediatric assessment date
    # this creates a cohort number (integer) based on where in the year they are
