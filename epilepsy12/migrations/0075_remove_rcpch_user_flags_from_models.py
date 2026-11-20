"""
Stop using the retired is_rcpch_audit_team_member / is_rcpch_staff fields
without dropping their database columns (the "expand" half of an
expand/contract change).

Deploys start the new revision, and run migrate, while the previous revision
is still serving. The previous revision's model still has both fields, so the
columns must stay until it is gone. This migration:

1. gives both columns a database default of False, so inserts from code that
   no longer knows about the fields (this release onwards) still succeed;
2. removes the fields from Django's model state only. The columns stay, and the
   previous revision can keep reading and writing them while it drains.

A later migration archives the flag history (HistoricalEpilepsy12User) and
then drops the columns, once no running revision uses them. See
documentation/docs/development/rcpch-flags-retirement-plan.md.
"""

from django.db import migrations, models

FLAG_FIELDS = ("is_rcpch_audit_team_member", "is_rcpch_staff")
MODELS = ("epilepsy12user", "historicalepilepsy12user")


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0074_rcpch_audit_team_permissions"),
    ]

    operations = [
        # 1. Database default, so inserts that omit the columns still work
        *[
            migrations.AlterField(
                model_name=model_name,
                name=field_name,
                field=models.BooleanField(default=False, db_default=False),
            )
            for model_name in MODELS
            for field_name in FLAG_FIELDS
        ],
        # 2. Remove from the model only; the columns stay in the database
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(model_name=model_name, name=field_name)
                for model_name in MODELS
                for field_name in FLAG_FIELDS
            ],
            database_operations=[],
        ),
    ]
