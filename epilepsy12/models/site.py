from django.db import models

from epilepsy12.models.hospital_trust import HospitalTrust
from ..constants import *
# other tables
from .registration import Registration


class Site(models.Model):
    """
    This class records information about each site that oversees the epilepsy care of each case.
    This class references the HospitalTrust class, as one hospital trust may reference multiple sites
    This class references the Case class, as each case may have multiple sites.
    """

    site_is_actively_involved_in_epilepsy_care = models.BooleanField(
        default=False,
        null=True
    )
    site_is_primary_centre_of_epilepsy_care = models.BooleanField(
        default=False,
        null=True
    )
    site_is_childrens_epilepsy_surgery_centre = models.BooleanField(
        default=False,
        null=True
    )
    site_is_paediatric_neurology_centre = models.BooleanField(
        default=False,
        null=True
    )
    site_is_general_paediatric_centre = models.BooleanField(
        default=False,
        null=True
    )

    hospital_trust = models.OneToOneField(
        default=1,
        to=HospitalTrust,
        related_name="hospital_site",
        on_delete=models.DO_NOTHING
    )

    # Relationships
    registration = models.ForeignKey(
        to=Registration,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'site'
        verbose_name_plural = 'sites'

    def __str__(self) -> str:
        return self.hospital_trust.ParentName
