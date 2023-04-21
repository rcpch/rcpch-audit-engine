from django.db import models
from .time_and_user_abstract_base_classes import *


class OPENUKNetworkEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    ods_trust_code = models.CharField()
    OPEN_UK_Network_Name = models.CharField()
    OPEN_UK_Network_Code = models.CharField()
    country = models.CharField()
