from django.db import models
from ..constants import *
from .time_and_user_abstract_base_classes import *


class ElectroClinicalSyndrome(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information on electroclinical syndromes.
    It references the episode class, since one episode can have features of a single electroclinical syndrome.
    """

    electroclinical_syndrome = models.IntegerField(
        choices=ELECTROCLINICAL_SYNDROMES)
    electroclinical_syndrome_other = models.CharField(
        default=None,
        max_length=250
    )

    class Meta:
        verbose_name = 'electroclinical syndrome'
        verbose_name_plural = 'electroclinical syndromes'

    def __str__(self) -> str:
        return self.electroclinical_syndrome
