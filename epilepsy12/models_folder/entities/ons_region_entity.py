from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import *


class ONSRegionEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    Region_ONS_Code = models.CharField()
    Region_ONS_Name = models.CharField()

    ons_country = models.ForeignKey(
        "epilepsy12.ONSCountryEntity", on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "ONS Region"
        verbose_name_plural = "ONS Regions"
        ordering = ("Region_ONS_Name",)

    def __str__(self) -> str:
        return self.Region_ONS_Name
