"""
Stop using the retired is_rcpch_audit_team_member / is_rcpch_staff fields
without dropping their database columns (the "expand" half of an
expand/contract change).

Deploys start the new revision, and run migrate, while the previous revision
is still serving. The previous revision's model still has both fields, so the
columns must stay until it is gone. This migration:

0. writes a VisitActivity entry recording the flags of every user who has
   either set, as an audit record of who held them at removal (users created
   with a flag set have no earlier record of it);
1. gives both columns a database default of False, so inserts from code that
   no longer knows about the fields (this release onwards) still succeed;
2. removes the fields from Django's model state only. The columns stay, and the
   previous revision can keep reading and writing them while it drains.

A later migration archives the flag history (HistoricalEpilepsy12User) and
then drops the columns, once no running revision uses them. See
documentation/docs/development/rcpch-flags-retirement-plan.md.
"""

from django.db import migrations, models
from django.db.models import Q

FLAG_FIELDS = ("is_rcpch_audit_team_member", "is_rcpch_staff")
MODELS = ("epilepsy12user", "historicalepilepsy12user")

# VisitActivity.CHANGED_ADMIN_FLAG ("Superuser or admin status changed"), the
# activity the user change log already uses for flag changes
CHANGED_ADMIN_FLAG = 13


def record_flags_at_removal(apps, schema_editor):
    """
    One VisitActivity per user with either flag set, recording both flags,
    e.g. "RCPCH flags at removal: is_rcpch_audit_team_member=True,
    is_rcpch_staff=False".
    """
    Epilepsy12User = apps.get_model("epilepsy12", "Epilepsy12User")
    VisitActivity = apps.get_model("epilepsy12", "VisitActivity")

    flagged_users = Epilepsy12User.objects.filter(
        Q(is_rcpch_audit_team_member=True) | Q(is_rcpch_staff=True)
    ).values_list("pk", *FLAG_FIELDS)

    VisitActivity.objects.bulk_create(
        [
            VisitActivity(
                activity=CHANGED_ADMIN_FLAG,
                epilepsy12user_id=pk,
                details=(
                    "RCPCH flags at removal: "
                    f"is_rcpch_audit_team_member={is_rcpch_audit_team_member}, "
                    f"is_rcpch_staff={is_rcpch_staff}"
                ),
            )
            for pk, is_rcpch_audit_team_member, is_rcpch_staff in flagged_users
        ]
    )


class Migration(migrations.Migration):

    dependencies = [
        ("epilepsy12", "0074_rcpch_audit_team_permissions"),
    ]

    operations = [
        # 0. Audit record of who held the flags. Reversing leaves the entries
        # in place: they're an audit log.
        migrations.RunPython(record_flags_at_removal, migrations.RunPython.noop),
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
