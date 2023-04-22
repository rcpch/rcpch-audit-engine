from django.db import models
from ..time_and_user_abstract_base_classes import *


class CountryONSRegionEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    Country_ONS_Code = models.CharField()
    Country_ONS_Name = models.CharField()
    Region_ONS_Code = models.CharField()
    Region_ONS_Name = models.CharField()

    class Meta:
        verbose_name = 'Country ONS Name'
        verbose_name_plural = 'Country ONS Names'
        ordering = ('Country_ONS_Name',)

    def __str__(self) -> str:
        return self.Country_ONS_Name
