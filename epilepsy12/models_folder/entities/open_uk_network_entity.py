from django.db import models
from ..time_and_user_abstract_base_classes import *


class OPENUKNetworkEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    ods_trust_code = models.CharField()
    OPEN_UK_Network_Name = models.CharField()
    OPEN_UK_Network_Code = models.CharField()
    country = models.CharField()

    class Meta:
        verbose_name = 'OPENUK Network'
        verbose_name_plural = 'OPENUK Networks'
        ordering = ('OPEN_UK_Network_Name',)

    def __str__(self) -> str:
        return self.OPEN_UK_Network_Name
