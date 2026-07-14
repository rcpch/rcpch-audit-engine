"""Function-based tests for the case list view.

These tests assert filtering and sorting behaviour. Tests avoid asserting
absolute totals (which may be affected by shared seeded data when using
--reuse-db) and instead assert that the cases we create are present or
in the expected order in the response.
"""

import pytest
from datetime import date
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth.models import Group

from epilepsy12.models import Organisation
from epilepsy12.tests.factories import E12CaseFactory, E12UserFactory
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)


@pytest.mark.django_db
def test_cohort_filter_includes_unregistered_and_all_children(
    client, seed_groups_fixture, seed_users_fixture
):
    """All-children should include unregistered cases; all-cohorts should not."""

    # Use a clear, unique prefix for our test cases so we can find them
    # without relying on absolute counts in the shared test DB.
    prefix = "TF_COHORT_"

    gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    group = Group.objects.get(name="trust_audit_team_edit_access")

    user = E12UserFactory(
        first_name="CohortTest",
        surname="User",
        email="cohort_test@test.com",
        role=1,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        view_preference=0,
        groups=[group],
    )
    user.set_organisation_employer(organisation_employer=gosh, is_primary=True)

    # Create one registered case and one unregistered case
    reg = E12CaseFactory(
        first_name=prefix + "Reg",
        surname="A",
        organisations__organisation=gosh,
    )
    reg.registration.cohort = 5
    reg.registration.first_paediatric_assessment_date = date(2023, 6, 1)
    reg.registration.save()

    unreg = E12CaseFactory(
        first_name=prefix + "Unreg",
        surname="B",
        organisations__organisation=gosh,
        registration=None,
    )

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})

    # all_children should include both registered and unregistered
    resp_all_children = client.get(url, {"cohort": "all_children"})
    assert resp_all_children.status_code == HTTPStatus.OK
    case_ids = {c.id for c in resp_all_children.context["case_list"]}
    assert reg.id in case_ids
    assert unreg.id in case_ids

    # all_cohorts should only include registered cases
    resp_all_cohorts = client.get(url, {"cohort": "all_cohorts"})
    assert resp_all_cohorts.status_code == HTTPStatus.OK
    case_ids2 = {c.id for c in resp_all_cohorts.context["case_list"]}
    assert reg.id in case_ids2
    assert unreg.id not in case_ids2


@pytest.mark.django_db
def test_search_filters_name_id_nhs(client, seed_groups_fixture, seed_users_fixture):
    """Search should find cases by first name, case id and NHS number."""

    prefix = "TF_SEARCH_"
    gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    group = Group.objects.get(name="trust_audit_team_edit_access")

    user = E12UserFactory(
        first_name="SearchTest",
        surname="User",
        email="search_test@test.com",
        role=1,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        view_preference=0,
        groups=[group],
    )
    user.set_organisation_employer(organisation_employer=gosh, is_primary=True)

    alice = E12CaseFactory(
        first_name=prefix + "Alice",
        surname="Alpha",
        nhs_number="9000000000",
        organisations__organisation=gosh,
    )

    bob = E12CaseFactory(
        first_name=prefix + "Bob",
        surname="Beta",
        nhs_number="8000000000",
        organisations__organisation=gosh,
    )

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})

    # search by first name
    r1 = client.get(url, {"filtered_case_list": "Alice"})
    assert r1.status_code == HTTPStatus.OK
    ids = {c.id for c in r1.context["case_list"]}
    assert alice.id in ids

    # search by NHS number
    r2 = client.get(url, {"filtered_case_list": "8000000000"})
    assert r2.status_code == HTTPStatus.OK
    ids2 = {c.id for c in r2.context["case_list"]}
    assert bob.id in ids2

    # search by case ID
    r3 = client.get(url, {"filtered_case_list": str(alice.id)})
    assert r3.status_code == HTTPStatus.OK
    ids3 = {c.id for c in r3.context["case_list"]}
    assert alice.id in ids3


@pytest.mark.django_db
def test_sorting_name_sex_nhs_deadline(client, seed_groups_fixture, seed_users_fixture):
    """Sorting: name (surname), sex, NHS number and deadline (first paediatric assessment).

    We assert ordering of our created cases rather than absolute positions.
    """

    prefix = "TF_SORT_"
    gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    group = Group.objects.get(name="trust_audit_team_edit_access")

    user = E12UserFactory(
        first_name="SortTest",
        surname="User",
        email="sort_test@test.com",
        role=1,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        view_preference=0,
        groups=[group],
    )
    user.set_organisation_employer(organisation_employer=gosh, is_primary=True)

    # Create three cases with different surnames, sexes, nhs numbers and deadlines
    c1 = E12CaseFactory(
        first_name=prefix + "One",
        surname="Alpha",
        nhs_number="1000000001",
        sex=1,
        organisations__organisation=gosh,
    )
    c1.registration.first_paediatric_assessment_date = date(2023, 1, 1)
    c1.registration.save()

    c2 = E12CaseFactory(
        first_name=prefix + "Two",
        surname="Beta",
        nhs_number="1000000002",
        sex=2,
        organisations__organisation=gosh,
    )
    c2.registration.first_paediatric_assessment_date = date(2024, 1, 1)
    c2.registration.save()

    c3 = E12CaseFactory(
        first_name=prefix + "Three",
        surname="Gamma",
        nhs_number="1000000003",
        sex=1,
        organisations__organisation=gosh,
    )
    c3.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    c3.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})

    # sort by name ascending (surname alphabetical)
    r_name_up = client.get(url, {"sort_flag": "sort_by_name_up"})
    assert r_name_up.status_code == HTTPStatus.OK
    surnames = [
        c.surname
        for c in r_name_up.context["case_list"]
        if c.first_name.startswith(prefix)
    ]
    # our three surnames should be in alphabetical order
    assert surnames[:3] == sorted(["Alpha", "Beta", "Gamma"])

    # sort by sex ascending (expect sex=1 before sex=2)
    r_sex_up = client.get(url, {"sort_flag": "sort_by_sex_up"})
    assert r_sex_up.status_code == HTTPStatus.OK
    sexes = [
        c.sex for c in r_sex_up.context["case_list"] if c.first_name.startswith(prefix)
    ]
    # sexes should start with 1 (male)
    assert sexes[0] == 1

    # sort by NHS number descending
    r_nhs_down = client.get(url, {"sort_flag": "sort_by_nhs_number_down"})
    assert r_nhs_down.status_code == HTTPStatus.OK
    nhs_list = [
        c.nhs_number
        for c in r_nhs_down.context["case_list"]
        if c.first_name.startswith(prefix)
    ]
    assert nhs_list[:3] == sorted(
        [c3.nhs_number, c2.nhs_number, c1.nhs_number], reverse=True
    )

    # sort by deadline ascending (earliest first)
    r_deadline_up = client.get(url, {"sort_flag": "sort_by_deadline_up"})
    assert r_deadline_up.status_code == HTTPStatus.OK
    deadlines = [
        c.registration.first_paediatric_assessment_date
        for c in r_deadline_up.context["case_list"]
        if c.first_name.startswith(prefix)
    ]
    assert deadlines[:3] == sorted(
        [
            c1.registration.first_paediatric_assessment_date,
            c2.registration.first_paediatric_assessment_date,
            c3.registration.first_paediatric_assessment_date,
        ]
    )


@pytest.mark.django_db
def test_individual_cohort_filtering(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by individual cohorts (5, 6, 7)."""

    prefix = "TF_IND_COHORT_"
    gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    group = Group.objects.get(name="trust_audit_team_edit_access")

    user = E12UserFactory(
        first_name="IndividualCohortTest",
        surname="User",
        email="ind_cohort_test@test.com",
        role=1,
        is_staff=True,
        is_rcpch_audit_team_member=False,
        view_preference=0,
        groups=[group],
    )
    user.set_organisation_employer(organisation_employer=gosh, is_primary=True)

    # Create cases in different cohorts
    # Cohort 5 case
    c5 = E12CaseFactory(
        first_name=prefix + "Cohort5",
        surname="A",
        organisations__organisation=gosh,
    )
    c5.registration.cohort = 5
    c5.registration.first_paediatric_assessment_date = date(2022, 1, 15)
    c5.registration.save()

    # Cohort 6 case
    c6 = E12CaseFactory(
        first_name=prefix + "Cohort6",
        surname="B",
        organisations__organisation=gosh,
    )
    c6.registration.cohort = 6
    c6.registration.first_paediatric_assessment_date = date(2023, 1, 15)
    c6.registration.save()

    # Cohort 7 case
    c7 = E12CaseFactory(
        first_name=prefix + "Cohort7",
        surname="C",
        organisations__organisation=gosh,
    )
    c7.registration.cohort = 7
    c7.registration.first_paediatric_assessment_date = date(2024, 1, 15)
    c7.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})

    # Filter by cohort 5
    r_c5 = client.get(url, {"cohort": "5"})
    assert r_c5.status_code == HTTPStatus.OK
    ids_c5 = {c.id for c in r_c5.context["case_list"]}
    assert c5.id in ids_c5
    assert c6.id not in ids_c5
    assert c7.id not in ids_c5

    # Filter by cohort 6
    r_c6 = client.get(url, {"cohort": "6"})
    assert r_c6.status_code == HTTPStatus.OK
    ids_c6 = {c.id for c in r_c6.context["case_list"]}
    assert c5.id not in ids_c6
    assert c6.id in ids_c6
    assert c7.id not in ids_c6

    # Filter by cohort 7
    r_c7 = client.get(url, {"cohort": "7"})
    assert r_c7.status_code == HTTPStatus.OK
    ids_c7 = {c.id for c in r_c7.context["case_list"]}
    assert c5.id not in ids_c7
    assert c6.id not in ids_c7
    assert c7.id in ids_c7


@pytest.mark.django_db
def test_national_view_preference_restricted_to_rcpch_audit_team(client, seed_groups_fixture, seed_users_fixture):
    """Only RCPCH audit team members should be able to set national view preference."""

    gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    addenbrookes = Organisation.objects.get(ods_code="RGT01", trust__ods_code="RGT")

    group = Group.objects.get(name="trust_audit_team_edit_access")

    # Create a non-RCPCH audit team user
    user = E12UserFactory(
        first_name="NationalViewTest",
        surname="User",
        email="national_view_test_user@test.com",
        role=1,
        is_staff=False,
        is_rcpch_audit_team_member=False,
        view_preference=0,
        groups=[group],
    )
    user.set_organisation_employer(organisation_employer=gosh, is_primary=True)

    gosh_case = E12CaseFactory(
        first_name="gosh",
        surname="A",
        organisations__organisation=gosh,
    )
    gosh_case.registration.cohort = 6
    gosh_case.registration.first_paediatric_assessment_date = date(2023, 1, 15)
    gosh_case.registration.save()

    addenbrookes_case = E12CaseFactory(
        first_name="Addenbrookes",
        surname="B",
        organisations__organisation=addenbrookes,
    )
    addenbrookes_case.registration.cohort = 6
    addenbrookes_case.registration.first_paediatric_assessment_date = date(2023, 1, 15)
    addenbrookes_case.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    def assert_can_only_see_gosh_case():
        url = reverse("cases", kwargs={"organisation_id": gosh.pk})
        response = client.get(url, {"cohort": "6"})
        assert response.status_code == HTTPStatus.OK

        case_ids = {c.id for c in response.context["case_list"]}
        assert gosh_case.id in case_ids
        assert addenbrookes_case.id not in case_ids


    assert_can_only_see_gosh_case()

    url = reverse("view_preference", kwargs={"organisation_id": gosh.pk, "template_name": "cases"})
    response = client.post(
        url,
        headers={
            "Hx-Trigger-Name": 2, # national view, should be disallowed
            "Hx-Request": "true"
        },
    )
    assert response.status_code == HTTPStatus.OK # TODO MRB: change to forbidden?

    assert_can_only_see_gosh_case()
