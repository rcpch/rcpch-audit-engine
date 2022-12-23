from django.db import models
from django.contrib.postgres.fields import ArrayField
from epilepsy12.constants.comorbidities import NEUROPSYCHIATRIC

from .help_text_mixin import HelpTextMixin
# from .registration import Registration
from .time_and_user_abstract_base_classes import *
# from ..general_functions import *


class MultiaxialDiagnosis(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    Replace the DESSCRIBE class 
    One MultiaxialDiagnosis relates to one Registration
    One MultiaxialDiagnosis relates to many Episodes
    """

    # Syndrome

    syndrome_present = models.BooleanField(
        help_text={
            'label': "Is there an identifiable epilepsy syndrome?",
            'reference': "Is there an identifiable epilepsy syndrome?",
        },
        null=True,
        blank=True,
        default=None
    )

    # Cause
    epilepsy_cause_known = models.BooleanField(
        help_text={
            'label': "Has a cause for the epilepsy been identified?",
            'reference': "Has a cause for the epilepsy been identified?",
        },
        null=True,
        blank=True,
        default=None
    )

    epilepsy_cause = models.CharField(
        help_text={
            'label': "What is the main identified cause of the epilepsy?",
            'reference': "What is the main identified cause of the epilepsy?",
        },
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    epilepsy_cause_categories = ArrayField(
        models.CharField(
            max_length=500
        ),
        help_text={
            'label': "Which category/categories best apply to this epilepsy?",
            'reference': "Which category/categories best apply to this epilepsy?",
        },
        blank=True,
        null=True,
        default=list
    )

    relevant_impairments_behavioural_educational = models.BooleanField(
        help_text={
            'label': "Are there any relevant impairment, behavioural, educational or emotional problems?",
            'reference': "Are there any relevant impairment, behavioural, educational or emotional problems?",
        },
        default=None,
        blank=True,
        null=True
    )

    mental_health_screen = models.BooleanField(
        help_text={
            'label': "Has a mental health concern been sought?",
            'reference': "Is there evidence of the child being assessed for mental health problems via clinical enquiry or the use of a screening questionnaire?",
        },
        default=None,
        blank=True,
        null=True
    )

    mental_health_issue_identified = models.BooleanField(
        help_text={
            'label': "Has a mental health issue been identified?",
            'reference': "Does the child have any mental health issue identified?",
        },
        default=None,
        blank=True,
        null=True
    )

    mental_health_issue = models.CharField(
        choices=NEUROPSYCHIATRIC,
        max_length=3,
        help_text={
            'label': "Add details of any known mental health problem(s)",
            'reference': "Add details of any known mental health problem(s)",
        },
        default=None,
        blank=True,
        null=True
    )

    # relationships
    registration = models.OneToOneField(
        'epilepsy12.Registration',
        on_delete=models.CASCADE,
        related_name='multiaxialdiagnosis'
    )

    # Meta class

    class Meta:
        verbose_name = "Multiaxial Diagnosis"
        verbose_name_plural = "Multiaxial diagnosis assessments"

    def __str__(self) -> str:
        return f"Multaxial diagnosis for {self.registration.case}"
