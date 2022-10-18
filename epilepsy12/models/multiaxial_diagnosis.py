from django.db import models
from django.contrib.postgres.fields import ArrayField

from epilepsy12.models.help_text_mixin import HelpTextMixin
from .registration import Registration
from .time_and_user_abstract_base_classes import *
from ..general_functions import *


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
            'label': "Is there an identifiable cause?",
            'reference': "Is there an identifiable cause?",
        },
        null=True,
        blank=True,
        default=None
    )

    epilepsy_cause = models.CharField(
        help_text={
            'label': "What is the main identified cause of the seizure(s)?",
            'reference': "What is the main identified cause of the seizure(s)?",
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
            'label': "Are there any relevant impairments (behavioural or educational)?",
            'reference': "Are there any relevant impairments (behavioural or educational)?",
        },
        max_length=50,
        default=None,
        blank=True,
        null=True
    )

    # relationships
    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='registration'
    )

    # Meta class

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def __str__(self) -> str:
        return f"Multaxial diagnosis for {self.registration.case}"
