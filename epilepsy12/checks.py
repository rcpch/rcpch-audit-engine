"""
System checks for the epilepsy12 app.

Registered in ``Epilepsy12Config.ready()``.
"""

from django.core.checks import Error, Tags, register
from django.db import DatabaseError

from epilepsy12.constants.user_types import (
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_TEAM_REQUIRED_PERMISSIONS,
)


@register(Tags.database)
def check_rcpch_audit_team_permissions(app_configs, databases=None, **kwargs):
    """
    Error if the RCPCH audit team group is missing a permission its access
    depends on, i.e. the groups seeder has not been run since the permission
    was added. Without it the audit team silently loses national access.

    Database checks run on ``migrate`` and ``manage.py check --database
    default``. Skipped when:

    - the group does not exist yet (a fresh database, before seeding);
    - a permission row does not exist yet. ``migrate`` runs this check before
      applying migrations, so a permission added by a pending migration would
      otherwise block the deploy that adds it.
    """
    if not databases:
        return []

    from django.contrib.auth.models import Group, Permission

    try:
        group = Group.objects.filter(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS).first()
        if group is None:
            return []

        existing = {
            f"{app_label}.{codename}"
            for app_label, codename in Permission.objects.values_list(
                "content_type__app_label", "codename"
            )
        }
        held = {
            f"{app_label}.{codename}"
            for app_label, codename in group.permissions.values_list(
                "content_type__app_label", "codename"
            )
        }
    except DatabaseError:
        # Tables not created yet (first migrate on an empty database).
        return []

    missing = sorted(
        permission
        for permission in RCPCH_AUDIT_TEAM_REQUIRED_PERMISSIONS
        if permission in existing and permission not in held
    )
    if not missing:
        return []

    return [
        Error(
            f"The {EPILEPSY12_AUDIT_TEAM_FULL_ACCESS} group is missing "
            f"{', '.join(missing)}. RCPCH audit team members will lose the access "
            "these permissions grant.",
            hint="Run: python manage.py seed --mode=seed_groups_and_permissions",
            id="epilepsy12.E001",
        )
    ]
