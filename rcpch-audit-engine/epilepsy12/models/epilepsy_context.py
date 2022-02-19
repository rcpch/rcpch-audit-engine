
from datetime import date
from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .case import Case

class EpilepsyContext(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records contextual information that defines epilepsy risk.
    It references the InitialAssessment class, as each case optionally has a single epilepsy context.
    """
    previous_febrile_seizure=models.CharField(
        "has there been a previous febrile seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    previous_acute_symptomatic_seizure=models.CharField(
        "has there been a previous acute symptomatic seizure?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    is_there_a_family_history_of_epilepsy=models.CharField(
        "is there a family history of epilepsy?",
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    previous_neonatal_seizures=models.CharField(
        "were there seizures in the neonatal period?",
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    diagnosis_of_epilepsy_withdrawn=models.CharField(
        "has the diagnosis of epilepsy been withdrawn?",
        max_length=2, 
        choices=OPT_OUT
    )
    date_of_first_epileptic_seizure=models.DateField(
        "What date was the first reported epileptic seizure?"
    )

    @property
    def calculate_epilepsy_years(self):
        # returns time interval between current date and date of onset of seizures in days
        if (self.date_of_first_epileptic_seizure):
            today = date.today()
            days_between = abs(today-self.date_of_first_epileptic_seizure).days
            return days_between
    class Meta:
        verbose_name = 'epilepsy context'
        verbose_name_plural = 'epilepsy contexts'
    
    def __str__(self) -> str:
        return self.date_of_first_epileptic_seizure
