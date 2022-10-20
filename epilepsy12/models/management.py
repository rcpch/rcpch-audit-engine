from django.db import models

from epilepsy12.models.help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *

# other tables
from .registration import Registration

from ..general_functions import *


class Management(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class stores information on steps in managment.
    Each Case has only a single initial assessment (the first)
    This class references the Registration class in a one to one relationship
    This class is referenced by the Episode class as one assessment can optionally have many episodes

    Detail
    The cohort number is calculated from the initial date of first paediatric assessment
    """

    has_an_aed_been_given = models.BooleanField(
        help_text={
            'label': "Has an antiseizure medicine been given?",
            'reference': "Has an antiseizure medicine been given?",
        },
        default=None,
        null=True,
        blank=True
    )
    has_rescue_medication_been_prescribed = models.BooleanField(
        help_text={
            'label': "Has a rescue medicine been prescribed?",
            'reference': "Has a rescue medicine been prescribed?",
        },
        default=None,
        null=True,
        blank=True,
    )
    is_a_pregnancy_prevention_programme_in_place = models.BooleanField(
        help_text={
            'label': "Is there a pregnancy prevention programme (PPP) in place?",
            'reference': "Is there a pregnancy prevention programme (PPP) in place?",
        },
        default=None,
        null=True,
        blank=True
    )
    individualised_care_plan_in_place = models.BooleanField(
        help_text={
            'label': 'Has care planning (either an individualised epilepsy document or copy clinic letter including care planning information) commenced?',
            'reference': 'Has care planning (either an individualised epilepsy document or copy clinic letter including care planning information) commenced?',
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_date = models.DateField(
        help_text={
            'label': "On what date was the individualised care plan put in place?",
            'reference': "On what date was the individualised care plan put in place?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_has_parent_carer_child_agreement = models.BooleanField(
        help_text={
            'label': "Parent or carer and child agreement",
            'reference': "Has the parent or carer and child agreement to an individualised care plan been documented?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_service_contact_details = models.BooleanField(
        help_text={
            'label': 'Service contact details',
            'reference': "Does the individualised care plan include service contact details?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_include_first_aid = models.BooleanField(
        help_text={
            'label': 'First aid advice',
            'reference': "Does the individualised care plan include first aid advice?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_parental_prolonged_seizure_care = models.BooleanField(
        help_text={
            'label': 'Parental advice on managing prolonged seizures',
            'reference': "Does the individualised care plan include parental advice on managing prolonged seizures?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_general_participation_risk = models.BooleanField(
        help_text={
            'label': 'General participation and risk assessment',
            'reference': "Does the individualised care plan include general participation and risk assessment?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_addresses_water_safety = models.BooleanField(
        help_text={
            'label': 'Water safety',
            'reference': "Does the individualised care plan address water safety?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_addresses_sudep = models.BooleanField(
        help_text={
            'label': 'Sudden unexplained death in epilepsy (SUDEP)',
            'reference': "Does the individualised care plan address sudden unexplained death in epilepsy?",
        },
        default=None,
        null=True,
        blank=True,
    )
    individualised_care_plan_includes_ehcp = models.BooleanField(
        help_text={
            'label': 'An educational health care plan (EHCP)',
            'reference': "Does the individualised care plan include an educational health care plan (EHCP)?",
        },
        default=None,
        null=True,
        blank=True,
    )
    has_individualised_care_plan_been_updated_in_the_last_year = models.BooleanField(
        help_text={
            'label': 'Being updated as necessary',
            'reference': "Has the individualised care plan been updated in the last year?",
        },
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
        verbose_name = "Management Plan"
        verbose_name_plural = "Management Plans"

    def __str__(self) -> str:
        return f"Management Plans for {self.registration.case}"
