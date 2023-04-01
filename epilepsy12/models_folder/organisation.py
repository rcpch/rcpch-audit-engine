# django
from django.db import models
# 3rd party
from simple_history.models import HistoricalRecords
# rcpch
from .time_and_user_abstract_base_classes import *


class Organisation(models.Model):
    """
    This class details information about organisations.
    It represents a list of organisations that can be looked up to populate fields in the Site class
    """

    OrganisationID = models.CharField(
        max_length=50,
        unique=True,
        primary_key=True
    )
    OrganisationCode = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default=None
    )
    OrganisationType = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default=None
    )
    SubType = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default=None
    )
    Sector = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default=None
    )
    OrganisationStatus = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        default=None
    )
    IsPimsManaged = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default=None
    )
    OrganisationName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address1 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address2 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Address3 = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    City = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    County = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Postcode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Latitude = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Longitude = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ParentODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ParentName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OPENUKNetworkName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    OPENUKNetworkCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    NHSEnglandRegion = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    NHSEnglandRegionCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    NHSEnglandRegionONSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ICBName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ICBODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    ICBONSBoundaryCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    LocalAuthorityName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    LocalAuthorityODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    SubICBName = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    SubICBODSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    CountryONSCode = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Email = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Website = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    Fax = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        default=None
    )
    DateValid = models.DateTimeField(
        blank=True,
        null=True,
        default=None
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        indexes = [models.Index(fields=['OrganisationName'])]
        verbose_name = 'Hospital Trust'
        verbose_name_plural = 'Hospital Trusts'
        ordering = ('OrganisationName',)

    def __str__(self) -> str:
        return self.OrganisationName
