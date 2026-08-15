from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import TimeStampAbstractBaseClass

class TrustManager(models.Manager):
    def get_trust_list(self, exclude_pk=None):
        queryset = self.filter(active=True)

        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)

        return queryset.order_by("name")

class Trust(TimeStampAbstractBaseClass):
    objects = TrustManager()
    
    ods_code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    address_line_1 = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    address_line_2 = models.CharField(max_length=255, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True, default=None)
    postcode = models.CharField(max_length=15, null=True, blank=True, default=None)
    country = models.CharField(max_length=50, null=True, blank=True, default=None)
    telephone = models.CharField(max_length=100, null=True, blank=True, default=None)
    website = models.CharField(max_length=255, null=True, blank=True, default=None)
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
