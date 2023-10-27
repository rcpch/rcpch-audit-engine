# django
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# RCPCH
from ..time_and_user_abstract_base_classes import *


class ComorbidityList(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    """
    This class records information on all mental health, behavioural and developmental comorbidities
    It is a lookup table for the Comorbidity table
    """

    conceptId = models.CharField(default=None, null=True, blank=True, unique=True)
    term = models.CharField(default=None, null=True, blank=True)
    preferredTerm = models.CharField(default=None, null=True, blank=True)

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = "ComorbidityList"
        verbose_name_plural = "ComorbidityLists"

    def __str__(self) -> str:
        return f"{self.preferredTerm}"
