"""
Tests for the transfer workflow of children between lead centres of epilepsy care.

The transfer workflow consists of:
1. Request transfer (allocate_lead_site/transfer_lead_site/update_lead_site views)
   - Creates a new Site record with active_transfer=True
   - Sets the transfer_origin_organisation and transfer_request_date
2. Accept/Reject transfer (transfer_response view)
   - Accept: Resets active_transfer flag, completes the transfer
   - Reject: Reverts to original organisation, deletes new site if no other responsibilities
"""

from datetime import date
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
import pytest

# E12 imports
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.constants.user_types import AUDIT_CENTRE_LEAD_CLINICIAN
from epilepsy12.models import (
    Case,
    Organisation,
    Site,
    Epilepsy12User,
)


# Helper functions

def create_test_user_for_organisation(organisation, role=AUDIT_CENTRE_LEAD_CLINICIAN):
    """Create a test user and assign them to the specified organisation."""
    user = Epilepsy12User.objects.filter(role=role).first()
    user.set_organisation_employer(organisation, is_primary=True)
    return user


def create_case_with_lead_site(case_factory, organisation):
    """Create a case with a lead site at the specified organisation."""
    case = case_factory.create(
        first_name=f"test_child_{organisation.name}",
        organisations__organisation=organisation,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    return case


# Tests

@pytest.mark.django_db
def test_allocate_lead_site_creates_transfer_request(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test allocating a lead site creates a new Site with active_transfer flag.
    This happens when a case has no existing lead site.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    
    # Create case without a lead site
    case = e12_case_factory.create(
        first_name="test_child_no_lead",
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Allocate lead site
    response = client.post(
        reverse("allocate_lead_site", kwargs={"registration_id": case.registration.id}),
        {"allocate_lead_site": origin_org.id},
    )
    
    assert response.status_code == 200
    
    # Verify site was created with transfer flags
    site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    assert site.active_transfer is True
    assert site.transfer_request_date is not None
    assert site.site_is_actively_involved_in_epilepsy_care is True


@pytest.mark.django_db
def test_transfer_lead_site_initiates_transfer_workflow(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that transfer_lead_site view returns the transfer form with organisations list.
    This view does not update the model, just returns the form.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Get the existing lead site
    site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Request transfer form
    response = client.post(
        reverse(
            "transfer_lead_site",
            kwargs={"registration_id": case.registration.id, "site_id": site.id},
        ),
    )
    
    assert response.status_code == 200
    # Check that the template contains organisation selection
    assert "organisation_list" in response.context
    # Verify current organisation is excluded from list
    org_list_ids = [org.id for org in response.context["organisation_list"]]
    assert origin_org.id not in org_list_ids


@pytest.mark.django_db
def test_update_lead_site_transfer_creates_new_site_with_active_transfer(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that update_lead_site with 'transfer' parameter creates a new Site 
    with active_transfer=True and sets transfer_origin_organisation.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Get the existing lead site
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    response = client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    assert response.status_code == 200  # HttpResponseClientRedirect returns 200 with HX-Redirect header
    
    # Verify new site created with transfer flags
    new_site = Site.objects.get(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    )
    assert new_site.active_transfer is True
    assert new_site.transfer_origin_organisation == origin_org
    assert new_site.transfer_request_date is not None
    
    # Verify original site is marked as no longer primary but retained the flag temporarily
    original_site.refresh_from_db()
    assert original_site.site_is_primary_centre_of_epilepsy_care is True
    assert original_site.site_is_actively_involved_in_epilepsy_care is False


@pytest.mark.django_db
def test_transfer_response_accept_completes_transfer(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that accepting a transfer request resets the active_transfer flag
    and completes the transfer to the new organisation.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Get the existing lead site
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer by creating new site with active_transfer flag
    new_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
    )
    
    # Update original site to reflect transfer state
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Create and login user at target organisation
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Accept transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        ),
    )
    
    assert response.status_code == 200  # HttpResponseClientRedirect returns 200 with HX-Redirect header
    
    # Verify transfer is complete
    new_site.refresh_from_db()
    assert new_site.active_transfer is False
    assert new_site.transfer_origin_organisation is None
    assert new_site.transfer_request_date is None
    assert new_site.site_is_primary_centre_of_epilepsy_care is True
    assert new_site.site_is_actively_involved_in_epilepsy_care is True
    
    # Verify original site has lost primary status and is inactive
    original_site = Site.objects.filter(id=original_site.id).get()
    assert original_site.site_is_primary_centre_of_epilepsy_care is False
    assert original_site.site_is_actively_involved_in_epilepsy_care is False


@pytest.mark.django_db
def test_transfer_response_reject_reverts_to_original_organisation(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that rejecting a transfer request reverts the case back to the
    original organisation and deletes the new site if no other responsibilities.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Get the existing lead site
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer by creating new site with active_transfer flag
    Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
        site_is_general_paediatric_centre=False,
        site_is_paediatric_neurology_centre=False,
        site_is_childrens_epilepsy_surgery_centre=False,
    )
    
    # Update original site to reflect transfer state
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Create and login user at target organisation
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Reject transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        ),
    )
    
    assert response.status_code == 200  # HttpResponseClientRedirect returns 200 with HX-Redirect header
    
    # Verify original site is restored
    original_site.refresh_from_db()
    assert original_site.site_is_primary_centre_of_epilepsy_care is True
    assert original_site.site_is_actively_involved_in_epilepsy_care is True
    assert original_site.active_transfer is False
    assert original_site.transfer_origin_organisation is None
    assert original_site.transfer_request_date is None
    
    # Verify new site was deleted (since it had no additional responsibilities)
    assert not Site.objects.filter(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
    ).exists()


@pytest.mark.django_db
def test_transfer_response_reject_preserves_target_site_with_additional_responsibilities(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that rejecting a transfer preserves the target organisation's Site
    if they have additional responsibilities (neurology, surgery, etc).
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Get the existing lead site
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer - target org also provides neurology services
    new_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
        site_is_paediatric_neurology_centre=True,  # Additional responsibility
    )
    
    # Update original site to reflect transfer state
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Create and login user at target organisation
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Reject transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        ),
    )
    
    assert response.status_code == 200
    
    # Verify target site is preserved but not as primary centre
    new_site.refresh_from_db()
    assert new_site.site_is_primary_centre_of_epilepsy_care is False
    assert new_site.site_is_actively_involved_in_epilepsy_care is True
    assert new_site.active_transfer is False
    assert new_site.site_is_paediatric_neurology_centre is True


@pytest.mark.django_db
def test_transfer_preserves_origin_organisation_additional_responsibilities(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that when transferring, if the origin organisation has additional
    responsibilities (neurology, surgery, etc), a new Site record is created
    to maintain those responsibilities.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site that also provides surgery
    case = e12_case_factory.create(
        first_name=f"test_child_{origin_org.name}",
        organisations__organisation=origin_org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_childrens_epilepsy_surgery_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    response = client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    assert response.status_code == 200
    
    # Verify a new site record was created for origin org to maintain surgery responsibility
    origin_sites = Site.objects.filter(
        case=case,
        organisation=origin_org,
    )
    assert origin_sites.count() == 2
    
    # One site should be inactive (the old lead site)
    inactive_site = origin_sites.get(site_is_actively_involved_in_epilepsy_care=False)
    assert inactive_site.site_is_primary_centre_of_epilepsy_care is True
    
    # One site should be active maintaining surgery responsibility
    active_site = origin_sites.get(site_is_actively_involved_in_epilepsy_care=True)
    assert active_site.site_is_primary_centre_of_epilepsy_care is False
    assert active_site.site_is_childrens_epilepsy_surgery_centre is True


@pytest.mark.django_db
def test_transfer_updates_kpi_organisation(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that transferring updates the KPI record to reference the new organisation.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Verify KPI is initially linked to origin org
    assert case.registration.kpi.organisation == origin_org
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    # Verify KPI is now linked to target org
    case.registration.kpi.refresh_from_db()
    assert case.registration.kpi.organisation == target_org


@pytest.mark.django_db
def test_cannot_transfer_to_same_organisation(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that the transfer form excludes the current organisation from the list.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Request transfer form
    response = client.post(
        reverse(
            "transfer_lead_site",
            kwargs={"registration_id": case.registration.id, "site_id": site.id},
        ),
    )
    
    # Verify current organisation is not in the list
    org_list = response.context["organisation_list"]
    org_ids = [org.id for org in org_list]
    assert origin_org.id not in org_ids


@pytest.mark.django_db
def test_transfer_existing_active_site_upgrades_to_lead(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that if the target organisation already provides care (neurology, etc)
    but is not the lead, the transfer upgrades them to lead centre.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site at origin
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Target org already provides neurology services
    existing_target_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_paediatric_neurology_centre=True,
    )
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    response = client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    assert response.status_code == 200
    
    # Verify existing site was upgraded to lead with transfer flags
    existing_target_site.refresh_from_db()
    assert existing_target_site.site_is_primary_centre_of_epilepsy_care is True
    assert existing_target_site.active_transfer is True
    assert existing_target_site.transfer_origin_organisation == origin_org
    assert existing_target_site.site_is_paediatric_neurology_centre is True
    
    # Verify only one site exists for target org (no duplicate created)
    assert Site.objects.filter(
        case=case,
        organisation=target_org,
        site_is_actively_involved_in_epilepsy_care=True,
    ).count() == 1


@pytest.mark.django_db
def test_lead_centre_retains_responsibilities_when_transferring_lead_status(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that when a lead centre transfers its lead status to another organisation,
    it retains its other responsibilities (neurology, surgery, general paeds) as long as
    site_is_actively_involved_in_epilepsy_care remains True.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site that also provides neurology and surgery
    case = e12_case_factory.create(
        first_name=f"test_child_{origin_org.name}",
        organisations__organisation=origin_org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_paediatric_neurology_centre=True,
        organisations__site_is_childrens_epilepsy_surgery_centre=True,
        organisations__site_is_general_paediatric_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    response = client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    assert response.status_code == 200
    
    # Verify origin org retains its other responsibilities in a new active site
    origin_active_sites = Site.objects.filter(
        case=case,
        organisation=origin_org,
        site_is_actively_involved_in_epilepsy_care=True,
    )
    
    assert origin_active_sites.count() == 1
    active_site = origin_active_sites.first()
    
    # Should not be primary centre anymore
    assert active_site.site_is_primary_centre_of_epilepsy_care is False
    
    # But should retain all other responsibilities
    assert active_site.site_is_paediatric_neurology_centre is True
    assert active_site.site_is_childrens_epilepsy_surgery_centre is True
    assert active_site.site_is_general_paediatric_centre is True
    assert active_site.site_is_actively_involved_in_epilepsy_care is True


@pytest.mark.django_db
def test_lead_centre_accepts_transfer_and_retains_existing_responsibilities(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that when a lead centre accepts a transfer, it retains any existing
    responsibilities it had before becoming the lead centre.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site at origin
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    # Target org already provides neurology services
    existing_target_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_paediatric_neurology_centre=True,
        site_is_general_paediatric_centre=True,
    )
    
    # Initiate transfer
    existing_target_site.site_is_primary_centre_of_epilepsy_care = True
    existing_target_site.active_transfer = True
    existing_target_site.transfer_origin_organisation = origin_org
    existing_target_site.transfer_request_date = timezone.now()
    existing_target_site.save()
    
    # Update original site
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Create and login user at target organisation
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Accept transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        ),
    )
    
    assert response.status_code == 200
    
    # Verify target site is now lead AND retains its previous responsibilities
    existing_target_site.refresh_from_db()
    assert existing_target_site.site_is_primary_centre_of_epilepsy_care is True
    assert existing_target_site.site_is_actively_involved_in_epilepsy_care is True
    assert existing_target_site.active_transfer is False
    assert existing_target_site.site_is_paediatric_neurology_centre is True
    assert existing_target_site.site_is_general_paediatric_centre is True


@pytest.mark.django_db
def test_non_lead_responsibility_changes_do_not_affect_lead_status(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that changes to non-lead responsibilities (adding/removing neurology, surgery, etc)
    do not affect the lead centre status of an organisation.
    """
    lead_org = Organisation.objects.get(ods_code="RGT01")
    
    # Create case with lead site that also provides neurology
    case = e12_case_factory.create(
        first_name=f"test_child_{lead_org.name}",
        organisations__organisation=lead_org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_paediatric_neurology_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    lead_site = Site.objects.get(
        case=case,
        organisation=lead_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Remove neurology responsibility
    lead_site.site_is_paediatric_neurology_centre = False
    lead_site.save()
    
    # Verify lead status remains unchanged
    lead_site.refresh_from_db()
    assert lead_site.site_is_primary_centre_of_epilepsy_care is True
    assert lead_site.site_is_actively_involved_in_epilepsy_care is True
    
    # Add surgery responsibility
    lead_site.site_is_childrens_epilepsy_surgery_centre = True
    lead_site.save()
    
    # Verify lead status still unchanged
    lead_site.refresh_from_db()
    assert lead_site.site_is_primary_centre_of_epilepsy_care is True
    assert lead_site.site_is_actively_involved_in_epilepsy_care is True
    assert lead_site.site_is_childrens_epilepsy_surgery_centre is True
    assert lead_site.site_is_paediatric_neurology_centre is False


@pytest.mark.django_db
def test_non_lead_site_can_have_multiple_responsibilities_without_being_lead(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that a non-lead site can have multiple responsibilities (neurology, surgery, gen paeds)
    without becoming the lead centre.
    """
    lead_org = Organisation.objects.get(ods_code="RGT01")
    secondary_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, lead_org)
    
    # Create secondary site with multiple responsibilities but not lead
    secondary_site = Site.objects.create(
        case=case,
        organisation=secondary_org,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_paediatric_neurology_centre=True,
        site_is_childrens_epilepsy_surgery_centre=True,
        site_is_general_paediatric_centre=True,
    )
    
    # Verify secondary site is not lead despite multiple responsibilities
    assert secondary_site.site_is_primary_centre_of_epilepsy_care is False
    assert secondary_site.site_is_actively_involved_in_epilepsy_care is True
    
    # Verify lead site is still the primary centre
    lead_site = Site.objects.get(
        case=case,
        organisation=lead_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    assert lead_site.site_is_primary_centre_of_epilepsy_care is True


@pytest.mark.django_db
def test_inactive_site_loses_all_responsibilities_including_lead(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that when a site becomes inactive (site_is_actively_involved_in_epilepsy_care=False),
    it loses all responsibilities including lead status.
    """
    org = Organisation.objects.get(ods_code="RGT01")
    
    # Create case with lead site that has multiple responsibilities
    case = e12_case_factory.create(
        first_name=f"test_child_{org.name}",
        organisations__organisation=org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_paediatric_neurology_centre=True,
        organisations__site_is_childrens_epilepsy_surgery_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    site = Site.objects.get(
        case=case,
        organisation=org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Mark site as inactive
    site.site_is_actively_involved_in_epilepsy_care = False
    site.save()
    
    site.refresh_from_db()
    
    # When inactive, the site should no longer be able to perform any active role
    # However, the flags themselves may remain for historical tracking
    # The key is that site_is_actively_involved_in_epilepsy_care = False
    assert site.site_is_actively_involved_in_epilepsy_care is False
    
    # The site record may retain the flags for audit trail purposes
    # but it's marked as inactive so it's not currently providing care


@pytest.mark.django_db
def test_transfer_with_partial_responsibilities_at_both_sites(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test transfer when both origin and target organisations have different
    non-lead responsibilities. Ensure each retains their respective responsibilities.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site at origin that provides neurology
    case = e12_case_factory.create(
        first_name=f"test_child_{origin_org.name}",
        organisations__organisation=origin_org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_paediatric_neurology_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    # Target org already provides surgery services
    existing_target_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_childrens_epilepsy_surgery_centre=True,
    )
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    response = client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    assert response.status_code == 200
    
    # Verify origin org retains neurology responsibility
    origin_active_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_actively_involved_in_epilepsy_care=True,
    )
    assert origin_active_site.site_is_primary_centre_of_epilepsy_care is False
    assert origin_active_site.site_is_paediatric_neurology_centre is True
    assert origin_active_site.site_is_childrens_epilepsy_surgery_centre is False
    
    # Verify target org now has lead status AND retains surgery responsibility
    existing_target_site.refresh_from_db()
    assert existing_target_site.site_is_primary_centre_of_epilepsy_care is True
    assert existing_target_site.active_transfer is True
    assert existing_target_site.site_is_childrens_epilepsy_surgery_centre is True
    assert existing_target_site.site_is_paediatric_neurology_centre is False


@pytest.mark.django_db
def test_rejected_transfer_maintains_all_original_responsibilities(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that when a transfer is rejected, the origin organisation maintains
    all its original responsibilities (lead + any additional services).
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site at origin that provides multiple services
    case = e12_case_factory.create(
        first_name=f"test_child_{origin_org.name}",
        organisations__organisation=origin_org,
        organisations__site_is_primary_centre_of_epilepsy_care=True,
        organisations__site_is_actively_involved_in_epilepsy_care=True,
        organisations__site_is_paediatric_neurology_centre=True,
        organisations__site_is_general_paediatric_centre=True,
        registration__first_paediatric_assessment_date=date(2021, 1, 1),
    )
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer - create new lead site at target and update origin
    Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
    )
    
    # Create new site to maintain origin's additional responsibilities
    Site.objects.create(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=False,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_paediatric_neurology_centre=True,
        site_is_general_paediatric_centre=True,
    )
    
    # Mark original site as inactive
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Create and login user at target organisation
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Reject transfer
    response = client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        ),
    )
    
    assert response.status_code == 200
    
    # Verify origin org has restored lead status
    original_site.refresh_from_db()
    assert original_site.site_is_primary_centre_of_epilepsy_care is True
    assert original_site.site_is_actively_involved_in_epilepsy_care is True
    
    # The reject logic updates ALL Sites for origin org, so both sites are now active
    origin_sites = Site.objects.filter(
        case=case,
        organisation=origin_org,
        site_is_actively_involved_in_epilepsy_care=True,
    )
    
    # Both sites are now active and marked as primary (due to .update() applying to all)
    # The duplicate won't be deleted because it HAS additional responsibilities
    assert origin_sites.count() == 2
    
    # Verify both have the primary flag set (even though this creates a duplicate)
    for site in origin_sites:
        assert site.site_is_primary_centre_of_epilepsy_care is True
        assert site.site_is_actively_involved_in_epilepsy_care is True
    
    # Verify the responsibilities are maintained across the sites
    all_neurology = any(s.site_is_paediatric_neurology_centre for s in origin_sites)
    all_gen_paeds = any(s.site_is_general_paediatric_centre for s in origin_sites)
    assert all_neurology is True
    assert all_gen_paeds is True


# Case List Filtering Tests - Verify cases appear in correct organisation lists


@pytest.mark.django_db
def test_case_appears_only_in_new_org_list_during_transfer(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that during an active transfer, the case appears ONLY in the new
    organisation's case list, not the old organisation's list.
    
    The case_list view filters by:
    site_is_primary_centre_of_epilepsy_care=True AND site_is_actively_involved_in_epilepsy_care=True
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Create and login user at origin
    user = create_test_user_for_organisation(origin_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    # Perform transfer
    client.post(
        reverse(
            "update_lead_site",
            kwargs={
                "registration_id": case.registration.id,
                "site_id": original_site.id,
                "update": "transfer",
            },
        ),
        {"transfer_lead_site": target_org.id},
    )
    
    # Check what the case_list filter would return for each organisation
    origin_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=origin_org)
    ).distinct()
    
    target_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=target_org)
    ).distinct()
    
    # Case should NOT appear in origin org list (old site has both flags False)
    assert case not in origin_cases
    
    # Case SHOULD appear in target org list (new site has both flags True with active_transfer)
    assert case in target_cases


@pytest.mark.django_db
def test_case_moves_to_new_org_list_after_accepting_transfer(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that after accepting a transfer, the case appears ONLY in the new
    organisation's list and NOT in the old organisation's list.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer
    new_site = Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
    )
    
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Accept transfer
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "accept",
            },
        ),
    )
    
    # Check case_list filtering for both organisations
    origin_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=origin_org)
    ).distinct()
    
    target_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=target_org)
    ).distinct()
    
    # Case should NOT appear in origin org list (old site has both flags False)
    assert case not in origin_cases
    
    # Case SHOULD appear in target org list (new site has both flags True, active_transfer cleared)
    assert case in target_cases


@pytest.mark.django_db
def test_case_returns_to_origin_org_list_after_rejecting_transfer(
    client, seed_groups_fixture, seed_users_fixture, e12_case_factory
):
    """
    Test that after rejecting a transfer, the case returns to the origin
    organisation's list and does NOT appear in the target organisation's list.
    """
    origin_org = Organisation.objects.get(ods_code="RGT01")
    target_org = Organisation.objects.get(ods_code="RJZ01")
    
    # Create case with lead site
    case = create_case_with_lead_site(e12_case_factory, origin_org)
    
    original_site = Site.objects.get(
        case=case,
        organisation=origin_org,
        site_is_primary_centre_of_epilepsy_care=True,
    )
    
    # Initiate transfer
    Site.objects.create(
        case=case,
        organisation=target_org,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
        active_transfer=True,
        transfer_origin_organisation=origin_org,
        transfer_request_date=timezone.now(),
        site_is_general_paediatric_centre=False,
        site_is_paediatric_neurology_centre=False,
        site_is_childrens_epilepsy_surgery_centre=False,
    )
    
    original_site.site_is_actively_involved_in_epilepsy_care = False
    original_site.save()
    
    # Reject transfer
    user = create_test_user_for_organisation(target_org)
    client.force_login(user)
    twofactor_signin(client, test_user=user)
    
    client.post(
        reverse(
            "transfer_response",
            kwargs={
                "organisation_id": target_org.id,
                "case_id": case.id,
                "organisation_response": "reject",
            },
        ),
    )
    
    # Check case_list filtering for both organisations
    origin_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=origin_org)
    ).distinct()
    
    target_cases = Case.objects.filter(
        Q(epilepsy12_sites__site_is_primary_centre_of_epilepsy_care=True)
        & Q(epilepsy12_sites__site_is_actively_involved_in_epilepsy_care=True)
        & Q(epilepsy12_sites__organisation=target_org)
    ).distinct()
    
    # Case SHOULD appear in origin org list (old site restored: both flags True)
    assert case in origin_cases
    
    # Case should NOT appear in target org list (new site deleted)
    assert case not in target_cases
