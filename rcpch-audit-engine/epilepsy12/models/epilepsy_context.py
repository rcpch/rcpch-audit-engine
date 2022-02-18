
from datetime import date
from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .case import Case

class EpilepsyContext(TimeAndUserStampMixin):
    """
    This class records contextual information that defines epilepsy risk.
    It references the InitialAssessment class, as each case optionally has a single epilepsy context.
    """
    previous_febrile_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    previous_acute_symptomatic_seizure=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    is_there_a_family_history_of_epilepsy=models.CharField(
        max_length=3, 
        choices=OPT_OUT_UNCERTAIN
    )
    previous_neonatal_seizures=models.CharField(
        max_length=2,
        choices=OPT_OUT_UNCERTAIN
    )
    diagnosis_of_epilepsy_withdrawn=models.CharField(
        max_length=2, 
        choices=OPT_OUT
    )
    date_of_first_epileptic_seizure=models.DateField(
        "What date was the first reported epileptic seizure?"
    )


    # TODO #15 Class function to create calculated field epilepsy_years based on current date and date of first seizure in years

    @property
    def calculate_epilepsy_years(self):
        # returns time interval between current date and date of onset of seizures in days
        if (self.date_of_first_epileptic_seizure):
            today = date.today()
            days_between = abs(today-self.date_of_first_epileptic_seizure).days
            return days_between
