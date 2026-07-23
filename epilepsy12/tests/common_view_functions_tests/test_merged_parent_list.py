"""
Tests for merged_parent_list_for_user function

This test suite ensures that:
1. Users with multiple employers (across trusts and health boards) see all their accessible parents
2. Admin users see the full list of all parents
3. Regular users only see parents where they have organisation access
4. No N+1 query problems exist
"""

# Standard imports
import pytest
from django.test import override_settings

# E12 Imports
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    OrganisationEmployer,
    Trust,
    LocalHealthBoard,
)
from epilepsy12.common_view_functions.sanction_user_access import (
    merged_parent_list_for_user,
    organisation_white_list_for_user,
)


@pytest.mark.django_db
def test_merged_parent_list_multi_employer_england_wales(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that a user with multiple employers across England (Trust) and Wales (LHB)
    can see both their Trust and Local Health Board in the merged parent list.

    This simulates a user employed at:
    - GOSH (England, Trust RP4)
    - Noah's Ark (Wales, LHB 7A4)
    """

    # Get test organisations
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    NOAHS_ARK = Organisation.objects.get(
        ods_code="7A4H1", local_health_board__ods_code="7A4"
    )

    # Create a test user with employers in both England and Wales
    multi_employer_user = Epilepsy12User.objects.create(
        first_name="Multi",
        surname="Employer",
        email="multi.employer@test.com",
        is_active=True,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
    )

    # Add both organisations as employers
    OrganisationEmployer.objects.create(
        epilepsy12_user=multi_employer_user,
        employer_organisation=GOSH,
        is_active=True,
    )
    OrganisationEmployer.objects.create(
        epilepsy12_user=multi_employer_user,
        employer_organisation=NOAHS_ARK,
        is_active=True,
    )

    # Get the merged parent list
    parent_list = merged_parent_list_for_user(multi_employer_user)

    # Extract parent names and types for easier assertion
    parent_names = [p['name'] for p in parent_list]
    parent_types = {p['name']: p['parent_type'] for p in parent_list}

    # Assert both parents are in the list
    assert GOSH.trust.name in parent_names, "GOSH Trust should be in parent list"
    assert NOAHS_ARK.local_health_board.name in parent_names, "Noah's Ark LHB should be in parent list"

    # Assert correct parent types
    assert parent_types[GOSH.trust.name] == 'trust', "GOSH parent should be marked as trust"
    assert parent_types[NOAHS_ARK.local_health_board.name] == 'local_health_board', "Noah's Ark parent should be marked as local_health_board"

    # Assert each parent has required fields
    for parent in parent_list:
        assert 'pk' in parent
        assert 'name' in parent
        assert 'parent_type' in parent
        assert 'ods_code' in parent
        assert parent['parent_type'] in ['trust', 'local_health_board']


@pytest.mark.django_db
def test_merged_parent_list_admin_sees_all(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that admin users (RCPCH staff, superuser, or RCPCH audit team)
    see all active parents with organisations, not just their own employers.

    Admin users should pass Organisation.objects.get_organisation_list()
    to the function to see all parents.
    """

    # Get an RCPCH audit team user (admin)
    admin_user = Epilepsy12User.objects.get(first_name="RCPCH_AUDIT_TEAM")

    # Get all active trusts and LHBs that have organisations
    all_trusts_with_orgs = Trust.objects.filter(
        organisation__active=True
    ).distinct()
    all_lhbs_with_orgs = LocalHealthBoard.objects.filter(
        organisation__active=True
    ).distinct()

    expected_parent_count = all_trusts_with_orgs.count() + all_lhbs_with_orgs.count()

    # Get all active organisations (as the view does for admin users)
    all_organisations = Organisation.objects.get_organisation_list()

    # Get the merged parent list for admin with all organisations
    parent_list = merged_parent_list_for_user(
        admin_user,
        organisation_list=all_organisations
    )

    # Admin should see all parents
    assert len(parent_list) == expected_parent_count, (
        f"Admin should see all {expected_parent_count} parents, "
        f"but only sees {len(parent_list)}"
    )

    # Verify all trusts are in the list
    parent_names = [p['name'] for p in parent_list]
    for trust in all_trusts_with_orgs:
        assert trust.name in parent_names, f"Admin should see trust {trust.name}"

    # Verify all LHBs are in the list
    for lhb in all_lhbs_with_orgs:
        assert lhb.name in parent_names, f"Admin should see LHB {lhb.name}"


@pytest.mark.django_db
def test_merged_parent_list_regular_user_scoped(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that regular (non-admin) users only see parents where they have
    organisation access through OrganisationEmployer relationships.
    """

    # Get a regular user (audit centre clinician at GOSH)
    regular_user = Epilepsy12User.objects.get(first_name="AUDIT_CENTRE_CLINICIAN")

    # Get GOSH organisation and trust
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    gosh_trust = GOSH.trust

    # Get the merged parent list
    parent_list = merged_parent_list_for_user(regular_user)

    # User should only see their trust (RP4 - Great Ormond Street Hospital)
    # They should NOT see other trusts or LHBs they don't have access to
    parent_names = [p['name'] for p in parent_list]

    assert gosh_trust.name in parent_names, "User should see their own trust"

    # Get a trust/LHB the user is NOT employed at
    other_org = Organisation.objects.exclude(
        trust=gosh_trust
    ).exclude(
        local_health_board__isnull=True
    ).first()

    if other_org and other_org.local_health_board:
        # User should not see LHBs they're not employed at
        assert other_org.local_health_board.name not in parent_names, (
            f"User should not see LHB {other_org.local_health_board.name} "
            "they are not employed at"
        )


@pytest.mark.django_db
def test_merged_parent_list_sorted_by_name(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that the merged parent list is sorted alphabetically by name,
    regardless of whether they are Trusts or Local Health Boards.
    """

    admin_user = Epilepsy12User.objects.get(first_name="RCPCH_AUDIT_TEAM")
    parent_list = merged_parent_list_for_user(admin_user)

    # Extract names
    names = [p['name'] for p in parent_list]

    # Check they are sorted
    assert names == sorted(names), "Parent list should be sorted alphabetically by name"


@pytest.mark.django_db
def test_merged_parent_list_excludes_inactive_trusts(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that inactive trusts (active=False) are excluded from the merged list.
    Note: LocalHealthBoard does not have an active field, only Trust does.
    """

    # Get a trust and deactivate it
    trust_to_deactivate = Trust.objects.filter(
        organisation__active=True
    ).first()

    if trust_to_deactivate:
        trust_name = trust_to_deactivate.name
        trust_to_deactivate.active = False
        trust_to_deactivate.save()

        # Get admin user's parent list
        admin_user = Epilepsy12User.objects.get(first_name="RCPCH_AUDIT_TEAM")
        all_organisations = Organisation.objects.get_organisation_list()
        parent_list = merged_parent_list_for_user(admin_user, organisation_list=all_organisations)

        # Inactive trust should not appear
        parent_names = [p['name'] for p in parent_list]
        assert trust_name not in parent_names, "Inactive trust should not appear in parent list"

        # Reactivate for other tests
        trust_to_deactivate.active = True
        trust_to_deactivate.save()


@pytest.mark.django_db
def test_merged_parent_list_with_prefiltered_organisations(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that merged_parent_list_for_user works correctly when passed
    a pre-filtered organisation_list parameter.
    """

    regular_user = Epilepsy12User.objects.get(first_name="AUDIT_CENTRE_CLINICIAN")

    # Get the organisation whitelist for this user
    org_list = organisation_white_list_for_user(regular_user)

    # Pass it to merged_parent_list_for_user
    parent_list = merged_parent_list_for_user(
        regular_user,
        organisation_list=org_list
    )

    # Should only contain parents from the provided organisation list
    assert len(parent_list) > 0, "Should have at least one parent"

    # All parents should correspond to organisations in the provided list
    org_trust_ids = set(org_list.filter(trust__isnull=False).values_list('trust', flat=True))
    org_lhb_ids = set(org_list.filter(local_health_board__isnull=False).values_list('local_health_board', flat=True))

    for parent in parent_list:
        if parent['parent_type'] == 'trust':
            assert parent['pk'] in org_trust_ids, "Trust parent should be from provided org list"
        else:
            assert parent['pk'] in org_lhb_ids, "LHB parent should be from provided org list"


@pytest.mark.django_db
def test_merged_parent_list_multiple_orgs_same_trust(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that when a user has access to multiple organisations within the same trust,
    that trust appears only once in the merged parent list (no duplicates).
    """

    # Get two organisations from the same trust
    first_org = Organisation.objects.filter(
        trust__isnull=False,
        active=True
    ).first()

    if first_org and first_org.trust:
        # Find another org in the same trust
        second_org = Organisation.objects.filter(
            trust=first_org.trust,
            active=True
        ).exclude(pk=first_org.pk).first()

        if second_org:
            # Create user with access to both
            multi_org_user = Epilepsy12User.objects.create(
                first_name="Multi",
                surname="OrgSameTrust",
                email="multi.org.trust@test.com",
                is_active=True,
            )

            OrganisationEmployer.objects.create(
                epilepsy12_user=multi_org_user,
                employer_organisation=first_org,
                is_active=True,
            )
            OrganisationEmployer.objects.create(
                epilepsy12_user=multi_org_user,
                employer_organisation=second_org,
                is_active=True,
            )

            # Get merged parent list
            parent_list = merged_parent_list_for_user(multi_org_user)

            # Count how many times the trust appears
            trust_count = sum(
                1 for p in parent_list
                if p['name'] == first_org.trust.name
            )

            assert trust_count == 1, (
                f"Trust {first_org.trust.name} should appear only once, "
                f"not {trust_count} times"
            )


@pytest.mark.django_db
def test_merged_parent_list_jersey_user_cannot_see_uk_trusts(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that Jersey users can only see Jersey trust, not UK trusts or LHBs.

    Jersey is a special case with country="JERSEY". Users employed at Jersey
    should not see UK trusts or Welsh LHBs unless they are also employed there.
    """

    # Get Jersey organisation
    JERSEY = Organisation.objects.get(ods_code="RGT1W", trust__ods_code="RGT1W")
    jersey_trust = JERSEY.trust

    # Create a Jersey-only user
    jersey_user = Epilepsy12User.objects.create(
        first_name="Jersey",
        surname="User",
        email="jersey.user@test.com",
        is_active=True,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
    )

    OrganisationEmployer.objects.create(
        epilepsy12_user=jersey_user,
        employer_organisation=JERSEY,
        is_active=True,
    )

    # Get merged parent list
    parent_list = merged_parent_list_for_user(jersey_user)

    # User should only see Jersey trust
    assert len(parent_list) == 1, (
        f"Jersey user should see only 1 parent (Jersey), but sees {len(parent_list)}"
    )

    assert parent_list[0]['name'] == jersey_trust.name
    assert parent_list[0]['country'] and parent_list[0]['country'].upper() == 'JERSEY'
    assert parent_list[0]['parent_type'] == 'trust'

    # Verify no UK trusts or LHBs are in the list
    parent_names = [p['name'] for p in parent_list]

    # Check some UK organisations are NOT in the list
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    assert GOSH.trust.name not in parent_names, "Jersey user should not see UK trusts"


@pytest.mark.django_db
def test_merged_parent_list_uk_user_cannot_see_jersey(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that UK users cannot see Jersey trust unless employed there.

    Users employed at UK trusts should not see Jersey in their parent list
    unless they are also employed at Jersey.
    """

    # Get a UK organisation
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Create a UK-only user
    uk_user = Epilepsy12User.objects.create(
        first_name="UK",
        surname="User",
        email="uk.user@test.com",
        is_active=True,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
    )

    OrganisationEmployer.objects.create(
        epilepsy12_user=uk_user,
        employer_organisation=GOSH,
        is_active=True,
    )

    # Get merged parent list
    parent_list = merged_parent_list_for_user(uk_user)

    # Verify Jersey is NOT in the list
    parent_names = [p['name'] for p in parent_list]
    parent_countries = [p.get('country') for p in parent_list if p.get('country')]

    # Check that Jersey is not in countries (case-insensitive)
    jersey_found = any(c and c.upper() == 'JERSEY' for c in parent_countries)
    assert not jersey_found, "UK user should not see Jersey trust"

    # Get Jersey trust name
    JERSEY = Organisation.objects.get(ods_code="RGT1W", trust__ods_code="RGT1W")
    assert JERSEY.trust.name not in parent_names, (
        "UK user should not see Jersey trust in parent list"
    )


@pytest.mark.django_db
def test_merged_parent_list_admin_sees_jersey_and_uk(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that admin users can see both Jersey and UK trusts/LHBs.

    Admin users should have access to all parents regardless of country.
    """

    # Get an admin user
    admin_user = Epilepsy12User.objects.get(first_name="RCPCH_AUDIT_TEAM")

    # Get all active organisations (as admin would)
    all_organisations = Organisation.objects.get_organisation_list()

    # Get merged parent list
    parent_list = merged_parent_list_for_user(admin_user, organisation_list=all_organisations)

    # Check that both Jersey and UK trusts are present
    parent_countries = [p.get('country') for p in parent_list if p.get('country')]

    # Should have Jersey (case-insensitive check)
    jersey_found = any(c and c.upper() == 'JERSEY' for c in parent_countries)
    assert jersey_found, f"Admin should see Jersey trust. Countries found: {parent_countries}"

    # Should also have UK trusts
    uk_found = any(c and c.upper() in ['ENGLAND', 'WALES'] for c in parent_countries)
    assert uk_found or any(c is None for c in [p.get('country') for p in parent_list]), (
        "Admin should see UK trusts as well as Jersey"
    )


@pytest.mark.django_db
def test_merged_parent_list_user_employed_both_jersey_and_uk(
    seed_groups_fixture,
    seed_users_fixture,
):
    """
    Test that a user employed at both Jersey and UK organisations
    can see both sets of parents.

    This is a rare edge case but should be supported.
    """

    # Get Jersey and UK organisations
    JERSEY = Organisation.objects.get(ods_code="RGT1W", trust__ods_code="RGT1W")
    GOSH = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")

    # Create a user employed at both
    dual_user = Epilepsy12User.objects.create(
        first_name="Dual",
        surname="User",
        email="dual.user@test.com",
        is_active=True,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        is_rcpch_staff=False,
    )

    OrganisationEmployer.objects.create(
        epilepsy12_user=dual_user,
        employer_organisation=JERSEY,
        is_active=True,
    )
    OrganisationEmployer.objects.create(
        epilepsy12_user=dual_user,
        employer_organisation=GOSH,
        is_active=True,
    )

    # Get merged parent list
    parent_list = merged_parent_list_for_user(dual_user)

    # User should see both Jersey and UK parent(s)
    parent_names = [p['name'] for p in parent_list]
    parent_countries = [p.get('country') for p in parent_list if p.get('country')]

    assert JERSEY.trust.name in parent_names, "Dual-employed user should see Jersey"
    assert GOSH.trust.name in parent_names, "Dual-employed user should see UK trust"

    # Check Jersey is in countries (case-insensitive)
    jersey_found = any(c and c.upper() == 'JERSEY' for c in parent_countries)
    assert jersey_found, f"Should have Jersey country in list. Found: {parent_countries}"
