# django
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from epilepsy12.constants import NEUROPSYCHIATRIC, SEVERITY
from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *


class MultiaxialDiagnosis(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    Replace the DESSCRIBE class
    One MultiaxialDiagnosis relates to one Registration
    One MultiaxialDiagnosis relates to many Episodes
    """

    # Syndrome

    syndrome_present = models.BooleanField(
        help_text={
            "label": "Is there an identifiable epilepsy syndrome?",
            "reference": "Is there an identifiable epilepsy syndrome?",
        },
        null=True,
        blank=True,
        default=None,
    )

    # Cause
    epilepsy_cause_known = models.BooleanField(
        help_text={
            "label": "Has a cause for the epilepsy been identified?",
            "reference": "Has a cause for the epilepsy been identified?",
        },
        null=True,
        blank=True,
        default=None,
    )

    epilepsy_cause_categories = ArrayField(
        models.CharField(max_length=500),
        help_text={
            "label": "Which category/categories best apply to this epilepsy?",
            "reference": "Which category/categories best apply to this epilepsy?",
        },
        blank=True,
        null=True,
        default=list,
    )

    relevant_impairments_behavioural_educational = models.BooleanField(
        help_text={
            "label": "Are there any relevant impairment, behavioural, educational or emotional problems?",
            "reference": "Are there any relevant impairment, behavioural, educational or emotional problems?",
        },
        default=None,
        blank=True,
        null=True,
    )

    global_developmental_delay_or_learning_difficulties = models.BooleanField(
        help_text={
            "label": "Has global developmental delay (under 5 years) or learning disability/intellectual disability (over 5 years) been identified?",
            "reference": "Has global developmental delay (under 5 years) or learning disability/intellectual disability (over 5 years) been identified?",
        },
        default=None,
        blank=True,
        null=True,
    )

    global_developmental_delay_or_learning_difficulties_severity = models.CharField(
        choices=SEVERITY,
        help_text={
            "label": "Add details on the severity of the neurodevelopmental condition.",
            "reference": "Add details on the severity of the neurodevelopmental condition.",
        },
        default=None,
        blank=True,
        null=True,
    )

    autistic_spectrum_disorder = models.BooleanField(
        help_text={
            "label": "Has there been a diagnosis of autistic spectrum disorder?",
            "reference": "Has there been a diagnosis of autistic spectrum disorder?",
        },
        default=None,
        blank=True,
        null=True,
    )

    mental_health_screen = models.BooleanField(
        help_text={
            "label": "Has a mental health concern been sought?",
            "reference": "Is there evidence of the child being assessed for mental health problems via clinical enquiry or the use of a screening questionnaire?",
        },
        default=None,
        blank=True,
        null=True,
    )

    mental_health_issue_identified = models.BooleanField(
        help_text={
            "label": "Has a mental health issue been identified?",
            "reference": "Does the child have any mental health issue identified?",
        },
        default=None,
        blank=True,
        null=True,
    )

    mental_health_issues = ArrayField(
        models.CharField(max_length=500),
        help_text={
            "label": "Add details of any known mental health problem(s)",
            "reference": "Add details of any known mental health problem(s)",
        },
        default=list,
        blank=True,
        null=True,
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    # relationships
    registration = models.OneToOneField(
        "epilepsy12.Registration",
        on_delete=models.CASCADE,
        related_name="multiaxialdiagnosis",
    )

    epilepsy_cause = models.ForeignKey(
        "epilepsy12.EpilepsyCause",
        on_delete=models.PROTECT,
        help_text={
            "label": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
            "reference": "Please select the main identified cause of the epilepsy. If the cause is not in this list, please email the Epilepsy12 team",
        },
        max_length=250,
        default=None,
        blank=True,
        null=True,
    )

    # Meta class

    class Meta:
        verbose_name = "Multiaxial Diagnosis"
        verbose_name_plural = "Multiaxial diagnosis assessments"

    def __str__(self) -> str:
        return f"Multaxial diagnosis for {self.registration.case}"
