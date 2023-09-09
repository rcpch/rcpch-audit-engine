from django.contrib.gis.db import models
from ..time_and_user_abstract_base_classes import *


class OPENUKNetwork(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    name = models.CharField()
    boundary_identifier = models.CharField(unique=True)
    country = models.CharField()

    class Meta:
        verbose_name = "OPENUK Network"
        verbose_name_plural = "OPENUK Networks"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name
