from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration


class Management(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class stores information on steps in managment.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """

    has_an_aed_been_given = models.BooleanField(
        "Has an antiepilepsy medicine been prescribed?",
        default=None,
        null=True,
        blank=True
    )
    has_rescue_medication_been_prescribed = models.BooleanField(
        "Has a rescue medicine been prescribed?",
        default=None,
        null=True,
        blank=True,
    )
    is_a_pregnancy_prevention_programme_in_place = models.BooleanField(
        "Is there a pregnancy prevention programme (PPP) in place?",
        default=None,
        null=True,
        blank=True
    )
    individualised_care_plan_in_place = models.BooleanField(
        "Has an individualised care plan been put in place?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_date = models.DateField(
        "On what date was the individualised care plan put in place?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_has_parent_carer_child_agreement = models.BooleanField(
        "Has the parent or carer and child agreement to an individualised care plan been documented?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_service_contact_details = models.BooleanField(
        "Does the individualised care plan include service contact details?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_include_first_aid = models.BooleanField(
        "Does the individualised care plan include first aid advice?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_parental_prolonged_seizure_care = models.BooleanField(
        "Does the individualised care plan include parental advice on managing prolonged seizures?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_general_participation_risk = models.BooleanField(
        "Does the individualised care plan include general participation and risk assessment?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_addresses_water_safety = models.BooleanField(
        "Does the individualised care plan address water safety?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_addresses_sudep = models.BooleanField(
        "Does the individualised care plan address sudden unexplained death in epilepsy?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_aihp = models.BooleanField(
        "Does the individualised care plan include AIHP?",
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_ehcp = models.BooleanField(
        "Does the individualised care plan include an educational health care plan (EHCP)?",
        default=None,
        null=True,
        blank=True,
    )
    has_individualised_care_plan_been_updated_in_the_last_year = models.BooleanField(
        "Has the individualised care plan been updated in the last year?",
        default=None,
        null=True,
        blank=True,
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        verbose_name="related registration"
    )

    class Meta:
        verbose_name = "management",
        verbose_name_plural = "managements"

    def __str__(self) -> str:
        return self.pk
