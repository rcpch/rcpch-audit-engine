from django.contrib.gis.db import models
from .nhs_england_region_boundaries import NHSEnglandRegionBoundaries


class NHSEnglandRegion(NHSEnglandRegionBoundaries):
    NHS_Region_Code = models.CharField(unique=True, blank=True, null=True)

    class Meta:
        verbose_name = "NHS England Region"
        verbose_name_plural = "NHS England Regions"
        ordering = ("nhser22nm",)

    def __str__(self) -> str:
        return self.nhser22nm
