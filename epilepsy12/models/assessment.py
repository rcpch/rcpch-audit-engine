from django.db import models

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
    tertiary_paediatric_neurology_centre = models.CharField(
        "tertiary_paediatric_neurology_centre",
        max_length=100,
        default=None,
        null=True
    )
    epilepsy_surgery_centre = models.CharField(
        "epilepsy_surgery_centre",
        max_length=100,
        null=True
    )

    has_an_aed_been_given = models.BooleanField(
        "Has an antiepilepsy medicine been prescribed?",
        default=False,
        null=True
    )
    rescue_medication_prescribed = models.BooleanField(
        "Has a rescue medicine been prescribed?",
        default=False,
        null=True
    )
    childrens_epilepsy_surgical_service_referral_criteria_met = models.BooleanField(
        "Have the criteria for referral to a children's epilepsy surgery service been met?",
        default=False,
        null=True
    )
    consultant_paediatrician_referral_made = models.BooleanField(
        "Has a referral been made to a consultant paediatrician with an interest in epilepsy?",
        default=False,
        null=True
    )
    consultant_paediatrician_referral_date = models.DateField(
        "Date of referral to a consultant paediatrician with an interest in epilepsy.",
        null=True
    )  # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    consultant_paediatrician_input_date = models.DateField(
        "Date seen by a consultant paediatrician with an interest in epilepsy.",
        null=True
    )  # National guidance is that children should wait nolonger than x weeks
    paediatric_neurologist_referral_made = models.BooleanField(
        "Has a referral to a consultant paediatric neurologist been made?",
        default=False,
        null=True
    )
    paediatric_neurologist_referral_date = models.DateField(
        "Date of referral to a consultant paediatric neurologist.",
        null=True
    )  # National guidance is that children should wait nolonger than x weeks - essential field if has been referred
    paediatric_neurologist_input_date = models.DateField(
        "Date seen by consultant paediatric neurologist.",
        null=True
    )  # National guidance is that children should wait nolonger than x weeks
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
        default=False,
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
        default=False,
        null=True
    )
    prolonged_generalized_convulsive_seizures = models.BooleanField(
        "Were there any prolonged generalised epileptic seizures?",
        default=False,
        null=True
    )
    experienced_prolonged_focal_seizures = models.BooleanField(
        "Were there any prolonged focal seizures?",
        default=False,
        null=True
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="related registration"
    )

    class Meta:
        verbose_name = "assessment",
        verbose_name_plural = "assessments"

    def __str__(self) -> str:
        return "assessment"

    # TODO #14 Class function to calculate cohort based on first paediatric assessment date
    # this creates a cohort number (integer) based on where in the year they are
