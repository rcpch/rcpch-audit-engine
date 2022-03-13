from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from django.contrib.auth.models import User
import uuid
from ..constants import *
from .time_and_user_abstract_base_classes import *

# other tables
from .case import Case


class Registration(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    A record is created in the Registration class every time a case is registered for the audit
    A case can be registered only once - TODO Merge Registration with Case class
    """

    def _close_registration_after_one_year(self):
        # this currently is unlikely to work TODO #19 set locked to true if registered > 1 y
        today = datetime.now
        if (self.registration_date_one_year_on is not None and self.registration_date_one_year_on > today):
            return True
        else:
            return False

    registration_date = models.DateField(
        "Date on which registered for the the Epilepsy12 audit"
    )

    @property
    def registration_date_one_year_on(self):
        if (self.registration_date):
            return self.registration_date+relativedelta(years=1)
        else:
            return None

    locked_at = models.DateTimeField(
        "The date and time at which the registration was locked from further data entry.",
        default=None
    )
    locked = property(
        # Case is locked from further data entry. This occurs automatically if a year has passed since the registration date.
        _close_registration_after_one_year
    )
    referring_clinician = models.CharField(
        max_length=50,
        default=None
    )

    # relationships
    case = models.OneToOneField(
        Case,
        on_delete=CASCADE,
        verbose_name="Related child/young person"
    )
    locked_by = models.OneToOneField(
        User,
        on_delete=CASCADE,
        verbose_name="The user who locked the registration from further data entry."
    )

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def __str__(self) -> str:
        return self.registration_date
