from django.db import models
# other tables
from .case import Case, HospitalTrust
from .time_and_user_abstract_base_classes import *


class Site(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about each site that oversees the epilepsy care of each case.
    This class references the HospitalTrust class, as one hospital trust may reference multiple sites
    One registration can have several sites
    Each registration that has a record in sites that has 
    site_is_actively_involved_in_epilepsy_care as True will have a unique hospital trust, which can
    have more than one role (eg can be neurology and surgery lead together)
    It is possible for a registration to have two sites each with the same hospital_trust, however,
    if one of those hospital trusts is nolonger actively involved in the care.

    Each site can have more than one role
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

    # relationships
    # Site is a link table between Case and Hospital Trust in a many to many relationship

    hospital_trust = models.ForeignKey(
        to=HospitalTrust,
        related_name="site",
        on_delete=models.PROTECT
    )

    case = models.ForeignKey(
        # Note a Case instance can have only one site instance
        # where site_is_actively_involved_in_epilepsy_care. However,
        # it can have multiple instances where site_is_actively_involved_in_epilepsy_care
        # is false.
        Case,
        on_delete=models.CASCADE,
        related_name='site'
    )

    class Meta:
        verbose_name = 'Site'
        verbose_name_plural = 'Sites'

    def __str__(self) -> str:
        return self.hospital_trust.ParentName
