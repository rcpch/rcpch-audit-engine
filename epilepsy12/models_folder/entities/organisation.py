# django
from django.contrib.gis.db import models
from django.contrib.gis.db.models import (
    PointField,
    CharField,
    FloatField,
    DateTimeField,
)

# 3rd party
from simple_history.models import HistoricalRecords


class Organisation(models.Model):
    """
    This class details information about organisations.
    It represents a list of organisations that can be looked up
    """

    ODSCode = CharField(max_length=100, null=True, blank=True, default=None)
    OrganisationName = CharField(max_length=100, null=True, blank=True, default=None)
    Website = CharField(max_length=100, null=True, blank=True, default=None)
    Address1 = CharField(max_length=100, null=True, blank=True, default=None)
    Address2 = CharField(max_length=100, null=True, blank=True, default=None)
    Address3 = CharField(max_length=100, null=True, blank=True, default=None)
    City = CharField(max_length=100, null=True, blank=True, default=None)
    County = CharField(max_length=100, null=True, blank=True, default=None)
    Latitude = FloatField(max_length=100, null=True, blank=True, default=None)
    Longitude = FloatField(null=True, blank=True, default=None)
    Postcode = CharField(max_length=10, null=True, blank=True, default=None)
    Geocode_Coordinates = PointField(null=True, blank=True, default=None, srid=27700)
    ParentOrganisation_ODSCode = CharField(
        max_length=100, null=True, blank=True, default=None
    )
    ParentOrganisation_OrganisationName = CharField(
        max_length=100, null=True, blank=True, default=None
    )
    LastUpdatedDate = DateTimeField(max_length=100, null=True, blank=True, default=None)

    history = HistoricalRecords()

    # relationships

    nhs_region = models.ForeignKey(
        "epilepsy12.NHSRegionEntity", on_delete=models.PROTECT
    )

    integrated_care_board = models.ForeignKey(
        "epilepsy12.IntegratedCareBoardEntity",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    openuk_network = models.ForeignKey(
        "epilepsy12.OPENUKNetworkEntity", on_delete=models.PROTECT
    )

    ons_region = models.ForeignKey(
        "epilepsy12.ONSRegionEntity", on_delete=models.PROTECT
    )

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        indexes = [models.Index(fields=["OrganisationName"])]
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
        ordering = ("OrganisationName",)

    def __str__(self) -> str:
        return self.OrganisationName
