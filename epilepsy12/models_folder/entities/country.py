from django.contrib.gis.db import models
from .country_boundaries import CountryBoundaries


class Country(CountryBoundaries):
    class Meta:
        indexes = [models.Index(fields=["ctry22cd"])]
        verbose_name = "Country"
        verbose_name_plural = "Countries"
        ordering = ("ctry22nm",)

    def __str__(self) -> str:
        return self.ctry22nm

    def get_country_code(self) -> str:
        return self.ctry22cd
