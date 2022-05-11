from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models.deletion import CASCADE
from django.forms import CharField

from epilepsy12.models.registration import Registration
from ..constants import *
from .time_and_user_abstract_base_classes import *


class DESSCRIBE(models.Model):
    # Summarises a child or young person's epilepsy in a multiaxial way.
    # It is a standard tool for clinicians when describing or discussing a person's epilepsy and is taught nationally
    # There is one record per case.

    description = models.CharField(
        help_text="What is the episode(s) like and is the description adequate?",
        max_length=500,
        default=None
    )
    description_keywords = ArrayField(
        models.CharField(
            help_text="add a key word",
            max_length=100
        ),
        blank=True,
        null=True
    )
    epilepsy_status = models.CharField(
        "Is the episode(s) epileptic? Is this epilepsy?",
        max_length=1,
        choices=(
            (0, "epilepsy"),
            (1, "nonepilepsy"),
            (2, "unknown")
        )
    )
    seizure_type = models.CharField(
        "If epileptic, what is the seizure type (s)?",
        max_length=50
    )
    syndrome = models.CharField(
        "Is there an identifiable epilepsy syndrome?",
        max_length=50
    )
    cause = models.CharField(
        "What is the cause of this epilepsy and what further investigations may be needed to explore this?",
        max_length=50
    )

    registration = models.OneToOneField(
        Registration,
        on_delete=models.CASCADE,
        related_name='registration'
    )

    class Meta:
        verbose_name = "DESSCRIBE assessment"
        verbose_name_plural = "DESSCRIBE assessments"

    def __str__(self) -> str:
        return self.epilepsy_status
