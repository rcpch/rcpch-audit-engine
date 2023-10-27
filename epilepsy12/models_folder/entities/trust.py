from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import TimeStampAbstractBaseClass


class Trust(TimeStampAbstractBaseClass):
    ods_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    address_line_1 = models.CharField(
        max_length=100, null=True, blank=True, default=None
    )
    address_line_2 = models.CharField(max_length=100, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True, default=None)
    postcode = models.CharField(max_length=10, null=True, blank=True, default=None)
    country = models.CharField(max_length=50, null=True, blank=True, default=None)
    telephone = models.CharField(max_length=100, null=True, blank=True, default=None)
    website = models.CharField(max_length=100, null=True, blank=True, default=None)
    active = models.BooleanField(
        default=True
    )  # a boolean representing if this Trust is still operational
    published_at = models.DateField(
        null=True, blank=True, default=None
    )  # date this Trust was last amended according to the ORD

    class Meta:
        indexes = [models.Index(fields=["ods_code"])]
        verbose_name = "Trust"
        verbose_name_plural = "Trusts"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
