from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .multiaxial_diagnosis import MultiaxialDiagnosis


class Comorbidity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    [This class replaces the MentalHealth and Neurodevelopmental tables, conflating options into one list]

    Detail
    The date of onset/diagnosis field has been actively removed as not found helpful
    """

    comorbidity_diagnosis_date = models.DateField(  # this is a free text field for 'other' diagnoses not included in the lists provided
        max_length=50,
        default=None,
        null=True
    )

    comorbidity_diagnosis = models.CharField(  # this is a free text field for 'other' diagnoses not included in the lists provided
        max_length=50,
        default=None,
        null=True
    )

    # relationships
    multiaxial_diagnosis = models.ForeignKey(
        MultiaxialDiagnosis,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='multiaxial_diagnosis'
    )

    class Meta:
        verbose_name = "comorbidity"
        verbose_name_plural = "comorbidities"

    def __str__(self) -> str:
        return self.comorbidity_diagnosis
