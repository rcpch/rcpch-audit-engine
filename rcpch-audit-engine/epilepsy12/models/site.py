from django.db import models
from django.db.models.deletion import CASCADE
from ..constants import *
from .time_and_user_mixin import TimeAndUserStampMixin

# other tables
from .case import Case
from .hospital_trust import HospitalTrust

class Site(TimeAndUserStampMixin):
    """
    This class records information about each site that oversees the epilepsy care of each case.
    This class references the HospitalTrust class, as one hospital trust may reference multiple sites
    This class references the Case class, as each case may have multiple sites.
    """
    site_is_actively_involved_in_epilepsy_care=models.BooleanField(default=False)
    site_is_primary_centre_of_epilepsy_care=models.BooleanField(
        default=False,
        unique=True
    )
    case = models.ForeignKey(
        Case,
        on_delete=CASCADE,
        primary_key=True
    )

    class Meta:
        ordering = ['-hospital_trust']
        verbose_name = 'site'
        verbose_name_plural = 'sites'

    def __str__(self) -> str:
        return self.hospital_trust
    
    # Relationships
    hospital_trust=models.ForeignKey(
        HospitalTrust, 
        on_delete=models.CASCADE,
        related_name='hospital trusts',
        related_query_name='hospitals'
    )