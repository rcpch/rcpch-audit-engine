"""

## Custom Permissions Tests
TODO #511

Opt out
    [x] Assert an Audit Centre Administrator CANNOT let a child opt out of Epilepsy12
    [x] Assert an audit centre clinician CANNOT let a child opt out of Epilepsy12
    [x] Assert an Audit Centre Lead Clinician CANNOT let a child outside their own Trust opt out of Epilepsy12

    [] Assert an Audit Centre Lead Clinician can let a child within their own Trust opt out of Epilepsy12
    [] Assert RCPCH Audit Team can let a child opt out of Epilepsy12
    [] Assert Clinical Audit Team can let a child opt out of Epilepsy12

Locking
[] Assert an Audit Centre Administrator CANNOT lock a child from being edited
[] Assert an audit centre clinician CANNOT unlock a child for editing
[] Assert an Audit Centre Clinician CAN lock a child from being edited
[] Assert an Audit Centre Lead Clinician CAN lock a child from being edited
[] Assert an Audit Centre Lead Clinician CANNOT unlock a child for editing
[] Assert RCPCH Audit Team can lock a child from being edited
[] Assert RCPCH Audit Team can unlock a child from being edited

can_consent_to_audit_participation
[] Assert an Audit Centre Administrator CANNOT consent for a child to be included in Epilepsy12
[] Assert an audit centre clinician CANNOT consent for a child to be included in Epilepsy12
[] Assert an Audit Centre Lead Clinician CANNOT consent for a child to be included in Epilepsy12
[] Assert RCPCH Audit Team CANNOT consent for a child to be included in Epilepsy12
[] Assert a Child, Young Person or family can member consent for a child to be included in Epilepsy12

can_register_child_in_epilepsy12
[] Assert an Audit Centre Administrator CANNOT register a child in Epilepsy12
[] Assert an audit centre clinician CAN register a child within their own Trust in Epilepsy12
[] Assert an audit centre clinician CANNOT register a child outside their own Trust in Epilepsy12
[] Assert an Audit Centre Lead Clinician CAN register a child within their own Trust in Epilepsy12
[] Assert an Audit Centre Lead Clinician CANNOT register a child outside their own Trust in Epilepsy12
[] Assert RCPCH Audit Team CAN register a child within any Trust in Epilepsy12

can_delete_epilepsy12_lead_centre
[] Assert an Audit Centre Administrator CANNOT 'delete_lead_site'
[] Assert an audit centre clinician CANNOT delete_lead_site
[] Assert an Audit Centre Lead Clinician CANNOT delete_lead_site
[] Assert RCPCH Audit Team CAN delete_lead_site

"""
# python imports
import pytest

# django imports
from django.urls import reverse

# E12 imports
# E12 imports
from epilepsy12.models import Epilepsy12User, Organisation, Case


@pytest.mark.skip(reason="Unfinished test. Awaiting E12 advice re custom permissions.")
@pytest.mark.django_db
def test_users_opt_out_forbidden(
    client,
    seed_groups_fixture,
    seed_users_fixture,
    seed_cases_fixture,
):
    """
    Simulating different E12 Users attempting to opt children out of Epilepsy12

    Assert these users cannot opt child out of Epilepsy12
    """

    # set up constants

    # GOSH
    TEST_USER_ORGANISATION = Organisation.objects.get(
        ODSCode="RP401",
        ParentOrganisation_ODSCode="RP4",
    )

    # ADDENBROOKE'S
    DIFF_TRUST_DIFF_ORGANISATION = Organisation.objects.get(
        ODSCode="RGT01",
        ParentOrganisation_ODSCode="RGT",
    )

    CASE_FROM_SAME_ORG = Case.objects.get(
        first_name=f"child_{TEST_USER_ORGANISATION.OrganisationName}"
    )

    users = Epilepsy12User.objects.all().exclude(
        first_name__in=["RCPCH_AUDIT_TEAM", "CLINICAL_AUDIT_TEAM"]
    )

    for test_user in users:
        # Log in Test User
        client.force_login(test_user)

        response = client.get(
            reverse(
                "opt_out",
                kwargs={
                    "organisation_id": DIFF_TRUST_DIFF_ORGANISATION.id,
                    "case_id": CASE_FROM_SAME_ORG.id,
                },
            )
        )

        assert (
            response.status_code == 403
        ), f"{test_user.first_name} (from {test_user.organisation_employer}) requested opt out for {CASE_FROM_SAME_ORG} in {TEST_USER_ORGANISATION}. Has groups: {test_user.groups.all()} Expected 403 response status code, received {response.status_code}"
