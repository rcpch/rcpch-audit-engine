"""
Seeds E12 Users in the test db.

Idempotent: each user is fetched-or-created by its deterministic ``first_name``
(a stable natural key per role + organisation), so the fixture is safe to run
repeatedly - including concurrently across pytest-xdist workers against a
fresh test database, where the previous sentinel-then-create pattern could
race and produce duplicate users with the same first_name (causing
``MultipleObjectsReturned`` in tests that look users up by first_name).

Note on scope: this fixture is ``scope="function"`` (not session) because
tests mutate seeded users (``set_organisation_employer``, ``is_staff`` flips,
``force_login`` session state, etc.). Function scope runs the seed inside
each test's own ``@pytest.mark.django_db`` transaction, so those mutations
are rolled back and the committed seed data stays clean for the next test.
Under xdist, session-scoped committed rows are not reliably visible to a
worker's in-flight test transaction, so function scope is also required for
correctness across workers.
"""

# Standard imports
import pytest

# 3rd Party imports
from django.contrib.auth.models import Group

# E12 Imports
from epilepsy12.tests.UserDataClasses import (
    test_user_audit_centre_administrator_data,
    test_user_audit_centre_clinician_data,
    test_user_audit_centre_lead_clinician_data,
    test_user_rcpch_audit_team_data,
    test_user_clinicial_audit_team_data,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    OrganisationEmployer,
)
from epilepsy12.constants.user_types import (
    RCPCH_AUDIT_TEAM,
)


@pytest.fixture(scope="function")
def seed_users_fixture(django_db_setup, django_db_blocker):
    users = [
        test_user_audit_centre_administrator_data,
        test_user_audit_centre_clinician_data,
        test_user_audit_centre_lead_clinician_data,
        test_user_rcpch_audit_team_data,
        test_user_clinicial_audit_team_data,
    ]

    with django_db_blocker.unblock():
        GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
        KINGS = Organisation.objects.get(ods_code="RJZ01", trust__ods_code="RJZ")
        NOAHS_ARK = Organisation.objects.get(
            ods_code="7A4H1", local_health_board__ods_code="7A4"
        )
        JERSEY = Organisation.objects.get(ods_code="RGT1W", trust__ods_code="RGT1W")

        for org in [GOSH, KINGS, NOAHS_ARK, JERSEY]:
            is_active = True
            is_staff = False
            is_rcpch_audit_team_member = False
            is_rcpch_staff = False

            # seed a user of each type
            for user in users:
                # HACK: a lot of tests assume there is only one organisation and so look up the user
                # user by name. To avoid changing all the tests, for GOSH only) set this as it was before
                # we added multiple organisations in test
                first_name = (
                    user.role_str if org == GOSH else f"{org.name}_{user.role_str}"
                )

                # set RCPCH AUDIT TEAM MEMBER ATTRIBUTE
                if user.role == RCPCH_AUDIT_TEAM:
                    is_rcpch_audit_team_member = True
                    is_rcpch_staff = True

                if user.is_clinical_audit_team:
                    is_rcpch_audit_team_member = True
                    first_name = (
                        "CLINICAL_AUDIT_TEAM"
                        if org == GOSH
                        else f"{org.name}_CLINICAL_AUDIT_TEAM"
                    )

                # Idempotent create: first_name is a stable natural key per
                # (role, organisation). Deterministic email avoids Faker
                # generating different values across racing workers, which
                # would otherwise let two workers each create a row with the
                # same first_name but different emails.
                e12_user, created = Epilepsy12User.objects.get_or_create(
                    first_name=first_name,
                    defaults={
                        "email": f"{first_name}@nhs.net",
                        "role": user.role,
                        "is_active": is_active,
                        "is_staff": is_staff,
                        "is_rcpch_audit_team_member": is_rcpch_audit_team_member,
                        "is_rcpch_staff": is_rcpch_staff,
                        "email_confirmed": True,
                    },
                )

                if created:
                    # Set a deterministic password so tests that log in via
                    # force_login() (which checks the session auth hash
                    # against the stored hash) work reliably.
                    e12_user.set_password("pw")
                    e12_user.save()

                    # Attach employer via get_or_create on the natural key
                    # (user, organisation) so concurrent workers don't create
                    # duplicate OrganisationEmployer rows.
                    OrganisationEmployer.objects.get_or_create(
                        epilepsy12_user=e12_user,
                        employer_organisation=org,
                        defaults={
                            "is_primary": True,
                            "is_active": True,
                            "created_by": e12_user,
                        },
                    )

                    # Attach group. groups is an M2M; .add() is idempotent in
                    # Django (no-op if the relation already exists), but we
                    # only run it for newly-created users to avoid touching
                    # shared rows on subsequent (no-op) fixture invocations.
                    group = Group.objects.get(name=user.group_name)
                    e12_user.groups.add(group)
