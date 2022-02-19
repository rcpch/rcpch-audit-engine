from django.db import models
from django.db.models.deletion import CASCADE
from django.forms import CharField
from ..constants import *
from .time_and_user_abstract_base_classes import *

class DESSCRIBE(TimeStampAbstractBaseClass, UserStampAbstractBaseClass):
    # Summarises a child or young person's epilepsy in a multiaxial way.
    # It is a standard tool for clinicians when describing or discussing a person's epilepsy and is taught nationally
    # There is one record per case.

    description=models.CharField(
        "What is the episode(s) like and is the description adequate?",
        max_length=500,
        default=None
    )
    epilepsy_status=models.CharField(
        "Is the episode(s) epileptic? Is this epilepsy?",
        choices=(
            (0, "epilepsy"),
            (1, "nonepilepsy"),
            (2, "unknown")
        )
    )
    seizure_type=models.CharField(
        "If epileptic, what is the seizure type (s)?",
        max_length=50
    )
    syndrome=models.CharField(
        "Is there an identifiable epilepsy syndrome?",
        max_length=50
    )
    cause=models.CharField(
        "What is the cause of this epilepsy and what further investigations may be needed to explore this?",
        max_length=50
    )



class Impairment(models.base):
    impairment_type=models.CharField(
        max_length=20,
        choices=(
            (0, "emotional"),
            (1, "behavioural"),
            (2, "educational"),
        )
    )
    impairment=models.CharField(
        max_length=50
    )
    dessribe=models.ForeignKey(
        DESSCRIBE,
        verbose_name="Are there any relevant associated impairments - behavioural, educational or emotional problems?",
        primary_key=True
    )