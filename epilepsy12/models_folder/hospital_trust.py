from django.db import models
from .time_and_user_abstract_base_classes import *


class HospitalTrust(models.Model):
    """
    This class details information about hospital trusts.
    It represents a list of hospital trusts that can be looked up to populate fields in the Site class
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

    class Meta:
        indexes = [models.Index(fields=['OrganisationName'])]
        verbose_name = 'Hospital Trust'
        verbose_name_plural = 'Hospital Trusts'
        ordering = ('OrganisationName',)

    def __str__(self) -> str:
        return self.OrganisationName
