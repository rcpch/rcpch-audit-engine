from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User
from ..constants import *

class TimeAndUserStampMixin(models.Model): #TODO #12 Mixin breaks build currently
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=CASCADE)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=CASCADE)

    class Meta:
        abstract = True