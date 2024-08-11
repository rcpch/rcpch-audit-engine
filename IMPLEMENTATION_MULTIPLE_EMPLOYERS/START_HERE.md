# Issue Multiple Employers (issue #879)

This is a temporary folder and contains the step to migrate users in live from having single accounts associated with one Organisation, to being affiliated with multiple organisation affiliations. 

Superusers and RCPCH Audit Team Members, currently have a short cut here to see all organisations and their patients as a single highly policed flag in the Epilepsy12User model.

Regular users (clinicians especially) can currently only be affiliated with one organisation. Because of relational integrity, no records in the `Epilepsy12User` can be deleted, since they will be associated with patients and their data.They can be set to inactive if they need removing from lists of active users. However there is now a requirement for:

1. users to move between organisations - this means one use must have affiliation to multiple organisations
2. the nature of the relationship needs defining - some organisations might represent the primary affiliation, some relationships might be historical (nolonger active). In time, there may be a need to define other types of relationship between the user and their organisation.

In order to allow this, four things needs to happen that can only happen in steps. I have broken each one into their own files also but they are here in sequence for readability.

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

## Step 2

1. At this point, each `Epilepsy12User` record will still be associated with an organisation through the `organisation_employer` field. We therefore need to copy the relationship from that field to the new table. This is done with a new custom migration.
    `python manage.py makemigrations --emply epilepsy12 migrate_users_to_organisation_employer`
2. This creates an empty file in the migrations folder

   ```python
    from django.db import migrations

    def migrate_existing_data(apps, schema_editor):
        Epilepsy12User = apps.get_model("epilepsy12", "Epilepsy12User")
        OrganisationEmployer = apps.get_model("epilepsy12", "OrganisationEmployer")

        for user in Epilepsy12User.objects.all():
            if user.organisation_employer:
                OrganisationEmployer.objects.create(
                    epilepsy12user=user,
                    organisation=user.organisation_employer,
                    is_primary=True,
                    is_active=True,
                    join_date=user.date_joined,
                    deactivation_date=None
                )


    class Migration(migrations.Migration):

        dependencies = [
            (
                "epilepsy12",
                "0032_remove_epilepsy12user_organisation_employer_and_more",
            ),  # Replace with the actual previous migration name
        ]

        operations = [
            migrations.RunPython(migrate_existing_data),
        ]
   ```

3. This file needs pushing to live which will trigger `python manage.py makemigrations` and `python manage.py makemigrations migrate`
4. We must then check in the admin that users have the same organisation affiliation in the `Epilepsy12User` model in the `organisation_employer` field and  in the related `EmployerOrganisation`. **NOTE**:*The admin class will not work without small changes to view records.* This will include adding a `HorizontalFilter` to the `fieldsets` element referencing the new table.
5. It is possibly worth running a custom test, either to call from the command line through `manage.py` or `pytest` to ensure that all users have two matching fields and values as above. **This needs writing**.

## Step 3

1. The `organisation_employer` field (currently a foreign key for `Organisation`) now needs deprecating by removing from `Epilepsy12User`
   
   ```python
   # remove these lines
   organisation_employer = models.ForeignKey(
        "epilepsy12.Organisation", on_delete=models.CASCADE, blank=True, null=True
    )
   ```

2. Once again, make a commit and then push to live. This will trigger `python manage.py makemigrations` and `python manage.py makemigrations migrate`

## Step 4

1. Refactor the codebase to use the new table. This will include updating the tests.

## Suggested methodology

Each of these 4 steps should have the relevant changes in a string of 4 chained branches. Each one can be merged into live consecutively, with the different checks and tests running at each merge.
