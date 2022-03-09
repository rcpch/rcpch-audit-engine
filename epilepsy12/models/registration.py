from dateutil.relativedelta import relativedelta
from datetime import date
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
    registration_uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Unique identifier for each registration in the Epilepsy12 audit for a give year."
    )
    registration_date = models.DateField(
        "Date on which registered for the the Epilepsy12 audit"
    )
    locked = models.BooleanField(
        "Case is locked from further data entry. This occurs automatically if a year has passed since the registration date.",
        default=False
    )
    locked_at = models.DateTimeField(
        "The date and time at which the registration was locked from further data entry.",
        auto_now_add=True
    )
    closed = models.BooleanField(
        "Case has been closed and will not participate in audit analysis.",
        default=False
    )
    referring_clinician = models.CharField(max_length=50)
    diagnostic_status = models.CharField(  # This currently essential - used to exclude nonepilepic kids
        max_length=1,
        choices=DIAGNOSTIC_STATUS,
        verbose_name="Status of epilepsy diagnosis. Must have epilepsy or probable epilepsy to be included."
    )

    # relationships
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        verbose_name="Related child/young person"
    )
    locked_by = models.OneToOneField(
        User,
        on_delete=CASCADE,
        verbose_name="The user who locked the registration from further data entry."
    )

    @property
    def close_registration_after_one_year(self):
        # this currently is unlikely to work TODO #19 set locked to true if registered > 1 y
        today = date.today()
        one_year_on = today+relativedelta(years=1)
        if (self.registration_date > one_year_on):
            return True
        else:
            return False

    class Meta:
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'

    def __str__(self) -> str:
        return self.registration_date
