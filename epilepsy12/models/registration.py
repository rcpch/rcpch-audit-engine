from dateutil.relativedelta import relativedelta
from django.db import models
from epilepsy12.models.audit_progress import AuditProgress

from .case import Case
from ..constants import *
from ..general_functions import *
from .time_and_user_abstract_base_classes import *


class Registration(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
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
        "Date on which registered for the the Epilepsy12 audit",
        null=True,
        default=None
    )

    registration_close_date = models.DateField(
        "Date at which the registration is due to close",
        default=None,
        null=True
    )

    def registration_date_one_year_on(self):
        "Date at which registration ends for the the Epilepsy12 audit"
        if (self.registration_date):
            return self.registration_date+relativedelta(years=1)
        else:
            return None

    referring_clinician = models.CharField(
        max_length=50,
        default=None,
        null=True
    )

    eligibility_criteria_met = models.BooleanField(
        default=None,
        null=True
    )

    cohort = models.PositiveSmallIntegerField(
        default=None,
        null=True
    )

    # relationships
    case = models.OneToOneField(
        Case,
        on_delete=models.PROTECT,
        null=True
    )

    audit_progress = models.OneToOneField(
        AuditProgress,
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def save(self, *args, **kwargs) -> None:
        if self.registration_date and self.registration_close_date is not None:
            self.registration_close_date = self.registration_date_one_year_on()
            self.cohort = cohort_number_from_enrolment_date(
                self.registration_date)
        return super().save(*args, **kwargs)
