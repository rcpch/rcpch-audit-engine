from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .epilepsy_context import EpilepsyContext


class Comorbidity(models.Model):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    [This class replaces the MentalHealth and Neurodevelopmental tables, conflating options into one list]

    Detail
    The date of onset/diagnosis field has been actively removed as not found helpful
    """

    comorbidity = models.CharField(
        max_length=3,
        choices=COMORBIDITIES
    )
    comorbidity_free_text = models.CharField(  # this is a free text field for 'other' diagnoses not included in the lists provided
        max_length=50,
        default=None
    )
    comorbidity_snomed_code = models.CharField(  # TODO #11 Need to tag Snomed CT terms to all comorbidites @marcusbaw @colindunkley
        max_length=50
    )  # this is a new field - decision not to act on this currently: rare for a formal diagnosis to be give so

    # relationships
    epilepsy_context = models.ForeignKey(
        EpilepsyContext,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='comorbidities'
    )

    class Meta:
        verbose_name = "comorbidity"
        verbose_name_plural = "comorbidities"

    def __str__(self) -> str:
        return self.comorbidity
