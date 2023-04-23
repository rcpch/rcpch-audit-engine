from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import *


class ONSCountryEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    Country_ONS_Code = models.CharField()
    Country_ONS_Name = models.CharField()
    year = models.IntegerField()

    class Meta:
        verbose_name = 'ONS Country'
        verbose_name_plural = 'ONS Countries'
        ordering = ('Country_ONS_Name',)

    def __str__(self) -> str:
        return self.Country_ONS_Name
