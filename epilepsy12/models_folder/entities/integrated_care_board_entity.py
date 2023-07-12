from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import *


class IntegratedCareBoardEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    ODS_ICB_Code = models.CharField()
    ONS_ICB_Boundary_Code = models.CharField()
    ICB_Name = models.CharField()

    class Meta:
        verbose_name = "ICB Name"
        verbose_name_plural = "ICB Names"
        ordering = ("ICB_Name",)

    def __str__(self) -> str:
        return self.ICB_Name
