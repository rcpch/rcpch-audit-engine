"""
Tests that role changes email the admins (CHANGE_NOTIFICATION_EMAILS).

Role decides a user's permissions, including national access for the RCPCH
Audit Team, so every role change is a permission change worth notifying.
"""

import pytest
from django.core import mail
from django.test import override_settings

from epilepsy12.constants.user_types import (
    AUDIT_CENTRE_CLINICIAN,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    RCPCH_AUDIT_TEAM,
)


@pytest.mark.django_db
@override_settings(CHANGE_NOTIFICATION_EMAILS=["audit-team@rcpch.ac.uk"])
@pytest.mark.parametrize(
    "old_role, new_role",
    [
        # promotion to national access
        (AUDIT_CENTRE_LEAD_CLINICIAN, RCPCH_AUDIT_TEAM),
        # change between two audit centre roles
        (AUDIT_CENTRE_CLINICIAN, AUDIT_CENTRE_LEAD_CLINICIAN),
    ],
)
def test_role_change_emails_admins(e12_user_factory, old_role, new_role):
    user = e12_user_factory(role=old_role)
    # The factory-created user triggers a user creation notification email
    mail.outbox = []

    user.role = new_role
    user.save()

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.to == ["audit-team@rcpch.ac.uk"]
    assert "Permission Changes" in email.subject
    assert f"role: '{old_role}' → '{new_role}'" in email.body


@pytest.mark.django_db
@override_settings(CHANGE_NOTIFICATION_EMAILS=["audit-team@rcpch.ac.uk"])
def test_saving_without_a_role_change_does_not_email_admins(e12_user_factory):
    user = e12_user_factory(role=AUDIT_CENTRE_CLINICIAN)
    mail.outbox = []

    user.surname = "Changed"
    user.save()

    assert len(mail.outbox) == 0
