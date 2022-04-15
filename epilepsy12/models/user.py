from django.contrib.auth.models import AbstractUser
from django.db import models

from epilepsy12.constants.user_types import ROLES


class User(AbstractUser):
    role = models.PositiveSmallIntegerField(
        choices=ROLES,
        blank=True,
        null=True
    )
    hospital_trust = ()
