from django.contrib.gis.db import models
from .london_borough_boundaries import LondonBoroughBoundaries


class LondonBorough(LondonBoroughBoundaries):
    class Meta:
        indexes = [models.Index(fields=["gss_code"])]
        verbose_name = "London Borough"
        verbose_name_plural = "London Boroughs"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_gss_code(self) -> str:
        return self.gss_code
