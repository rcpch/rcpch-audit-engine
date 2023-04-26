# django
from django.contrib.gis.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
# 3rd party
from simple_history.models import HistoricalRecords


class Keyword(models.Model):

    keyword = models.CharField(
        help_text="A validated keyword for describing the semiology of a seizure",
        max_length=100
    )
    category = models.CharField(
        help_text="The semiology category each keyword belongs to.",
        max_length=100
    )

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    class Meta:
        verbose_name = _("Keyword")
        verbose_name_plural = _("Keywords")

    def __str__(self):
        return self.keyword

    def get_absolute_url(self):
        return reverse("_detail", kwargs={"pk": self.pk})
