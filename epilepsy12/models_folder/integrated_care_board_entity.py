from django.db import models
from .time_and_user_abstract_base_classes import *


class IntegratedCareBoardEntity(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    NHS_England_Region = models.CharField()
    NHS_England_Region_Code = models.CharField()
    ODS_ICB_Code = models.CharField()
    ONS_ICB_Boundary_Code = models.CharField()
    ICB_Name = models.CharField()
    Sub_ICB_Locations = models.CharField(
        "Sub ICB Locations (Formerly CCGs)"
    )
    ODS_Sub_ICB_Code = models.CharField()
    Local_Authority = models.CharField()
    ODS_LA_Code = models.CharField()
    NHS_Trusts = models.CharField()
    ODS_Trust_Code = models.CharField()
