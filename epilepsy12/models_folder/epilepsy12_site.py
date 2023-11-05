# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from .time_and_user_abstract_base_classes import *
from ..constants import (
    CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE,
    CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE,
    CAN_EDIT_EPILEPSY12_LEAD_CENTRE,
    CAN_DELETE_EPILEPSY12_LEAD_CENTRE,
)


class Site(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information about each site that oversees the epilepsy care of each case.
    This class references the Organisation class, as one organisation trust may reference multiple sites
    One registration can have several sites
    Each registration that has a record in sites that has
    site_is_actively_involved_in_epilepsy_care as True will have a unique organisation trust, which can
    have more than one role (eg can be neurology and surgery lead together)
    It is possible for a registration to have two sites each with the same organisation, however,
    if one of those organisation trusts is nolonger actively involved in the care.

    Each site can have more than one role
    """

    site_is_actively_involved_in_epilepsy_care = models.BooleanField(
        default=False, null=True
    )
    site_is_primary_centre_of_epilepsy_care = models.BooleanField(
        default=False, null=True
    )
    site_is_childrens_epilepsy_surgery_centre = models.BooleanField(
        default=False, null=True
    )
    site_is_paediatric_neurology_centre = models.BooleanField(default=False, null=True)
    site_is_general_paediatric_centre = models.BooleanField(default=False, null=True)

    active_transfer = models.BooleanField(default=False)
    transfer_origin_organisation = models.OneToOneField(
        to="epilepsy12.Organisation",
        on_delete=models.PROTECT,
        default=None,
        null=True,
        blank=True,
        related_name="origin_organisation",
    )
    transfer_request_date = models.DateField(blank=True, null=True, default=None)

    history = HistoricalRecords()

    # relationships
    # Site is a link table between Case and Organisation in a many to many relationship

    organisation = models.ForeignKey(
        to="epilepsy12.Organisation", related_name="site", on_delete=models.PROTECT
    )

    case = models.ForeignKey(
        # Note a Case instance can have only one site instance
        # where site_is_actively_involved_in_epilepsy_care. However,
        # it can have multiple instances where site_is_actively_involved_in_epilepsy_care
        # is false.
        "epilepsy12.Case",
        on_delete=models.CASCADE,
        related_name="site",
    )

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = "Site"
        verbose_name_plural = "Sites"
        permissions = [
            CAN_ALLOCATE_EPILEPSY12_LEAD_CENTRE,
            CAN_TRANSFER_EPILEPSY12_LEAD_CENTRE,
            CAN_EDIT_EPILEPSY12_LEAD_CENTRE,
            CAN_DELETE_EPILEPSY12_LEAD_CENTRE,
        ]

    def __str__(self) -> str:
        return self.organisation.trust.name
