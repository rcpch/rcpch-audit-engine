from django.db import models

from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import *


class Comorbidity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    [This class replaces the MentalHealth and Neurodevelopmental tables, conflating options into one list]

    Detail
    The date of onset/diagnosis field has been actively removed as not found helpful
    """

    comorbidity_diagnosis_date = models.DateField(
        help_text={
            'label': 'What is the date of diagnosis?',
            'reference': 'What is the date of diagnosis?',
        },
        max_length=50,
        default=None,
        null=True
    )

    comorbidity_diagnosis = models.CharField(
        help_text={
            'label': 'What is the comorbidity?',
            'reference': 'What is the comorbidity?',
        },
        max_length=50,
        default=None,
        null=True
    )

    # relationships
    multiaxial_diagnosis = models.ForeignKey(
        'epilepsy12.MultiaxialDiagnosis',
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='multiaxial_diagnosis'
    )

    class Meta:
        verbose_name = "Comorbidity"
        verbose_name_plural = "Comorbidities"

    def __str__(self) -> str:
        return self.comorbidity_diagnosis
