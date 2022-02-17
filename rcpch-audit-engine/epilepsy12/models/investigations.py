from django.db import models
from django.db.models.fields import BooleanField
from django.contrib.auth.models import User
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .assessment import Assessment

class Investigations(TimeAndUserStampMixin):
    """
    This class records information about any EEG performed.
    It references the Assessment class as each episode may have optionally have several EEGs.
    """
    eeg_indicated = BooleanField(default=True)
    eeg_request_date = models.DateTimeField()
    eeg_performed_date = models.DateTimeField()
    assessment = models.OneToOneField(
        Assessment,
        on_delete=models.DO_NOTHING,
        primary_key=True
    )
    twelve_lead_ecg_status=models.BooleanField(
        default=False
    )
    ct_head_scan_status=models.BooleanField(
        default=False
    )
    mri_brain_date=models.DateField()
    consultant_paediatrician_referral_made=models.BooleanField(
        default=False
    )