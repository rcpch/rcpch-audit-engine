from dateutil.relativedelta import relativedelta
from django.db import models
from .case import Case
from ..constants import *
from ..general_functions import *
from .time_and_user_abstract_base_classes import *


class Registration(models.Model):
    """
    A record is created in the Registration class every time a case is registered for the audit
    """

    # def close_registration_after_one_year(self):
    #     # this currently is unlikely to work TODO #19 set locked to true if registered > 1 y
    #     today = datetime.now
    #     if (self.registration_date is not None):
    #         return True
    #     else:
    #         return False

    registration_date = models.DateField(
        "Date on which registered for the the Epilepsy12 audit"
    )

    registration_close_date = models.DateField(
        "Date at which the registration is due to close",
        default=None
    )

    def registration_date_one_year_on(self):
        "Date at which registration ends for the the Epilepsy12 audit"
        if (self.registration_date):
            return self.registration_date+relativedelta(years=1)
        else:
            return None

    referring_clinician = models.CharField(
        max_length=50,
        default=None
    )

    cohort = models.PositiveSmallIntegerField(
        default=None,
        null=True
    )

    initial_assessment_complete = models.BooleanField(
        default=False
    )
    epilepsy_context_complete = models.BooleanField(
        default=False
    )
    multiaxial_description_complete = models.BooleanField(
        default=False
    )
    investigation_management_complete = models.BooleanField(
        default=False
    )

    # relationships
    case = models.OneToOneField(
        Case,
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def save(self, *args, **kwargs) -> None:
        self.registration_close_date = self.registration_date_one_year_on()
        self.cohort = cohort_number_from_enrolment_date(self.registration_date)
        return super().save(*args, **kwargs)
