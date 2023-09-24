from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import TimeStampAbstractBaseClass


class Trust(TimeStampAbstractBaseClass):
    ods_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=100)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100)
    town = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=50)

    class Meta:
        indexes = [models.Index(fields=["ods_code"])]
        verbose_name = "Trust"
        verbose_name_plural = "Trusts"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
