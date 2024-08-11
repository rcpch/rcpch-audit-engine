## Step 1

1. a new table needs to be created: `EmployerOrganisation` that sits between `Epilepsy12User` and `Organisation`. This table will have fields for `is_active` and `is_primary_employer` to define the relationships. It will have foreign keys from each of `Epilepsy12User` and `Organisation`. To should store dates that users began and ended their relationships with that organisation.
2. Current records in the `Epilepsy12User` table need to have their foreign key stored in the new `EmployerOrganisation` table, associated with the foreign key of their current affiliate organisation. The `Meta` class should set the `unique_together` attribute to `Epilepsy12User` and `Organisation`. A new field should be placed in the `Epilepsy12User` table called `organisations` as a `ManyToManyField` field to `epilepsy12.organisation`, through `epilepsy12.employerorganisation`, with the `through_fields` set to `epilepsy12user` and `organisation` (assuming those are the field names holding the foreign keys for those two models).

```python
# models/employer_organisation.py - DON'T FORGET TO ADD AN IMPORT FOR THIS FILE IN THE FOLDER __init__.py

# django
from django.utils import timezone
from django.contrib.gis.db import models

# 3rd party
from simple_history.models import HistoricalRecords

# rcpch
from .time_and_user_abstract_base_classes import *
from .help_text_mixin import HelpTextMixin

class OrganisationEmployer(
    TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin
):
    """
    This class represents the middle table in a ManyToMany relationship between the Organisation and Epilepsy12User classes.
    It also records aspects of the relationship between the organisation and the user.
    """

    is_primary_employer = models.BooleanField(
        help_text={
            "label": "Is this the primary employer?",
            "reference": "Is this the primary employer?",
        },
        default=True,
    )

    is_active = models.BooleanField(
        help_text={
            "label": "Is this employer active?",
            "reference": "Is this employer active?",
        },
        default=True,
    )

    organisation = models.ForeignKey(
        "epilepsy12.Organisation",
        on_delete=models.CASCADE,
        help_text={
            "label": "Organisation",
            "reference": "Organisation",
        },
    )

    epilepsy12user = models.ForeignKey(
        "epilepsy12.Epilepsy12User",
        on_delete=models.CASCADE,
        help_text={
            "label": "Epilepsy12 User",
            "reference": "Epilepsy12 User",
        },
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        help_text={
            "label": "Date left employing organisation.",
            "reference": "Date left employing organisation.",
        }
    )

    date_deactivated = models.DateField(
        help_text={
            "label": "Date left employing organisation.",
            "reference": "Date left employing organisation.",
        },
        blank=True,
        null=True,
        default=None,
    )

    class Meta:
        unique_together = ("organisation", "epilepsy12user")
        verbose_name = "Organisation Employer"
        verbose_name_plural = "Organisation Employers"
```

3. We then need to run `python manage.py makemigrations` and `python manage.py makemigrations migrate` to cement these changes in the database.
