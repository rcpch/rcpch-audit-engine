from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import *


class NHSRegionEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    NHS_Region = models.CharField()
    NHS_Region_Code = models.CharField(unique=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "NHS Region Name"
        verbose_name_plural = "NHS Region Names"
        ordering = ("NHS_Region",)

    def __str__(self) -> str:
        return self.NHS_Region
