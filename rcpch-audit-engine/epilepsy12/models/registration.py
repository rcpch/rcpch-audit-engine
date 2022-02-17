from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from django.contrib.auth.models import User
import uuid
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .hospital_trust import HospitalTrust
from .case import Case
from .site import Site

class Registration(TimeAndUserStampMixin):
    """
    A record is created in the Registration class every time a case is registered for the audit
    A case can be registered only once - TODO Merge Registration with Case class
    """
    registration_uuid=models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    case=models.models.ForeignKey(
        Case, 
        on_delete=CASCADE,
        primary_key=True)
    site=models.ForeignKey(
        Site, 
        on_delete=CASCADE,
        primary_key=True)
    locked=models.BooleanField( # this determines if the case is locked from editing ? are cases or only registrations locked?
        "Locked", 
        default=False
    )
    locked_at = models.DateTimeField(auto_now_add=True)
    locked_by = models.ForeignKey(
        User, 
        on_delete=CASCADE
    )
    closed=models.BooleanField( # this determines if the case is closed? ARE CASES CLOSED AS WELL AS LOCKED OR REGISTRATIONS?
        "Closed", 
        default=False
    )
    referring_hospital = models.ForeignKey(
        HospitalTrust, 
        on_delete=CASCADE
    )
    referring_clinician = models.CharField(max_length=50)
    diagnostic_status = models.CharField( # This currently essential - used to exclude nonepilepic kids
        max_length=1,
        choices=DIAGNOSTIC_STATUS
    )