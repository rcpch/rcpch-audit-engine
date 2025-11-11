"""
Integration tests for the case_list view filtering, sorting, and totals functionality.

Tests cover:
- Filtering by cohort (all_children, all_cohorts, specific cohort)
- Filtering by search terms (first name, surname, NHS number, case ID)
- Sorting by all available parameters
- Correct totals before and after filtering
- View preferences (organisation, trust, national level)
- Pagination
- HTMX requests
"""

# python imports
import pytest
from datetime import date
from http import HTTPStatus

# django imports
from django.urls import reverse
from django.contrib.auth.models import Group

# E12 imports
from epilepsy12.models import (
    Organisation,
    Case,
    Registration,
)
from epilepsy12.tests.factories import (
    E12CaseFactory,
    E12UserFactory,
)
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.constants import GROUPS


# ===== COHORT FILTERING TESTS =====


@pytest.mark.django_db
def test_filter_by_all_children(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by 'all_children' shows all cases"""

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

    # Create 3 cases for cohort 5
    for i in range(3):
        case = E12CaseFactory(
            first_name=f"Cohort5Child{i}",
            surname=f"Cohort5{i}",
            organisations__organisation=gosh,
        )
        case.registration.cohort = 5
        case.registration.first_paediatric_assessment_date = date(2023, 1, 1)
        case.registration.save()

    # Create 2 cases for cohort 6
    for i in range(2):
        case = E12CaseFactory(
            first_name=f"Cohort6Child{i}",
            surname=f"Cohort6{i}",
            organisations__organisation=gosh,
        )
        case.registration.cohort = 6
        case.registration.first_paediatric_assessment_date = date(2024, 1, 1)
        case.registration.save()

    # Create 1 case for cohort 7
    case = E12CaseFactory(
        first_name="Cohort7Child0",
        surname="Cohort70",
        organisations__organisation=gosh,
    )
    case.registration.cohort = 7
    case.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    case.registration.save()

    # Create 2 unregistered cases
    for i in range(2):
        E12CaseFactory(
            first_name=f"UnregisteredChild{i}",
            surname=f"Unregistered{i}",
            organisations__organisation=gosh,
            registration=None,
        )

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})
    response = client.get(url, {"cohort": "all_children"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["selected_cohort"] == "all_children"
    # Should return all 8 cases (3+2+1 registered + 2 unregistered)
    total_cases = response.context["case_list"].paginator.count
    assert total_cases == 8, f"Expected 8 cases, got {total_cases}"


@pytest.mark.django_db
def test_filter_by_all_cohorts(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by 'all_cohorts' shows only registered cases"""

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

    # Create 3 cases for cohort 5
    for i in range(3):
        case = E12CaseFactory(
            first_name=f"Cohort5Child{i}",
            surname=f"Cohort5{i}",
            organisations__organisation=gosh,
        )
        case.registration.cohort = 5
        case.registration.first_paediatric_assessment_date = date(2023, 1, 1)
        case.registration.save()

    # Create 2 cases for cohort 6
    for i in range(2):
        case = E12CaseFactory(
            first_name=f"Cohort6Child{i}",
            surname=f"Cohort6{i}",
            organisations__organisation=gosh,
        )
        case.registration.cohort = 6
        case.registration.first_paediatric_assessment_date = date(2024, 1, 1)
        case.registration.save()

    # Create 1 case for cohort 7
    case = E12CaseFactory(
        first_name="Cohort7Child0",
        surname="Cohort70",
        organisations__organisation=gosh,
    )
    case.registration.cohort = 7
    case.registration.first_paediatric_assessment_date = date(2025, 1, 1)
    case.registration.save()

    # Create 2 unregistered cases
    for i in range(2):
        E12CaseFactory(
            first_name=f"UnregisteredChild{i}",
            surname=f"Unregistered{i}",
            organisations__organisation=gosh,
            registration=None,
        )

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})
    response = client.get(url, {"cohort": "all_cohorts"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["selected_cohort"] == "all_cohorts"
    # Should return only registered cases with cohort set (3+2+1 = 6)
    total_cases = response.context["case_list"].paginator.count
    assert (
        total_cases == 6
    ), f"Expected 6 registered cases with cohort, got {total_cases}"


@pytest.mark.django_db
def test_filter_by_cohort_5(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by cohort 5"""
    # Clean only test cases, not session fixture data
    Case.objects.filter(first_name__startswith="Cohort").delete()

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

    # Create 3 cases for cohort 5
    for i in range(3):
        case = E12CaseFactory(
            first_name=f"Cohort5Child{i}",
            surname=f"Cohort5{i}",
            organisations__organisation=gosh,
        )
        # Cohort 5: 1 December 2021 - 30 November 2022
        case.registration.first_paediatric_assessment_date = date(2022, 1, 15)
        case.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})
    response = client.get(url, {"cohort": "5"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["selected_cohort"] == "5"
    # Should return 3 cases in cohort 5
    total_cases = response.context["case_list"].paginator.count
    assert total_cases == 3, f"Expected 3 cases in cohort 5, got {total_cases}"


@pytest.mark.django_db
def test_filter_by_cohort_6(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by cohort 6"""
    # Clean only test cases, not session fixture data
    Case.objects.filter(first_name__startswith="Cohort").delete()

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

    # Create 2 cases for cohort 6
    for i in range(2):
        case = E12CaseFactory(
            first_name=f"Cohort6Child{i}",
            surname=f"Cohort6{i}",
            organisations__organisation=gosh,
        )
        # Cohort 6: 1 December 2022 - 30 November 2023
        case.registration.first_paediatric_assessment_date = date(2023, 1, 15)
        case.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})
    response = client.get(url, {"cohort": "6"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["selected_cohort"] == "6"
    # Should return 2 cases in cohort 6
    total_cases = response.context["case_list"].paginator.count
    assert total_cases == 2, f"Expected 2 cases in cohort 6, got {total_cases}"


@pytest.mark.django_db
def test_filter_by_cohort_7(client, seed_groups_fixture, seed_users_fixture):
    """Test filtering by cohort 7"""
    # Clean only test cases, not session fixture data
    Case.objects.filter(first_name__startswith="Cohort").delete()

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

    # Create 1 case for cohort 7
    case = E12CaseFactory(
        first_name="Cohort7Child0",
        surname="Cohort70",
        organisations__organisation=gosh,
    )
    # Cohort 7: 1 December 2023 - 30 November 2024
    case.registration.first_paediatric_assessment_date = date(2024, 1, 15)
    case.registration.save()

    client.force_login(user)
    twofactor_signin(client, user)

    url = reverse("cases", kwargs={"organisation_id": gosh.pk})
    response = client.get(url, {"cohort": "7"})

    assert response.status_code == HTTPStatus.OK
    assert response.context["selected_cohort"] == "7"
    # Should return 1 case in cohort 7
    total_cases = response.context["case_list"].paginator.count
    assert total_cases == 1, f"Expected 1 case in cohort 7, got {total_cases}"


# ===== SEARCH FILTERING TESTS =====


@pytest.mark.django_db
class TestCaseListSearchFiltering:
    """Tests for search filtering in case_list view"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_all_test_cases():
            """Helper to clean up all test cases and their related objects"""
            test_cases = Case.objects.all()

            for case in test_cases:
                # Delete related objects first to avoid ProtectedError
                if hasattr(case, "registration") and case.registration:
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                Site.objects.filter(case=case).delete()
                case.delete()

        yield
        clean_all_test_cases()

    @pytest.fixture(scope="function")
    def setup_search_test_data(self, seed_groups_fixture, seed_users_fixture):
        """Create test data for search testing"""
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

        # Create cases with specific searchable attributes
        case_alice = E12CaseFactory(
            first_name="Alice",
            surname="Smith",
            nhs_number="1234567890",
            organisations__organisation=gosh,
        )

        case_bob = E12CaseFactory(
            first_name="Bob",
            surname="Jones",
            nhs_number="9876543210",
            organisations__organisation=gosh,
        )

        case_charlie = E12CaseFactory(
            first_name="Charlie",
            surname="Smith",
            nhs_number="5555555555",
            organisations__organisation=gosh,
        )

        return {
            "gosh": gosh,
            "user": user,
            "case_alice": case_alice,
            "case_bob": case_bob,
            "case_charlie": case_charlie,
        }

    def test_search_by_first_name(self, client, setup_search_test_data):
        """Test search filtering by first name"""
        data = setup_search_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"filtered_case_list": "Alice"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["filtered_case_list"] == "Alice"
        assert response.context["case_list"].paginator.count == 1

    def test_search_by_surname(self, client, setup_search_test_data):
        """Test search filtering by surname"""
        data = setup_search_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"filtered_case_list": "Smith"})

        assert response.status_code == HTTPStatus.OK
        # Should match Alice Smith and Charlie Smith
        assert response.context["case_list"].paginator.count == 2

    def test_search_by_nhs_number(self, client, setup_search_test_data):
        """Test search filtering by NHS number"""
        data = setup_search_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"filtered_case_list": "1234567890"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["case_list"].paginator.count == 1

    def test_search_by_case_id(self, client, setup_search_test_data):
        """Test search filtering by case ID"""
        data = setup_search_test_data
        case_id = data["case_alice"].id
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"filtered_case_list": str(case_id)})

        assert response.status_code == HTTPStatus.OK
        assert response.context["case_list"].paginator.count == 1

    def test_search_partial_match(self, client, setup_search_test_data):
        """Test search with partial matching"""
        data = setup_search_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"filtered_case_list": "Smi"})

        assert response.status_code == HTTPStatus.OK
        # Should match both Smith surnames
        assert response.context["case_list"].paginator.count == 2


@pytest.mark.django_db
class TestCaseListSorting:
    """Tests for sorting functionality in case_list view"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_all_test_cases():
            """Helper to clean up all test cases and their related objects"""
            test_cases = Case.objects.all()

            for case in test_cases:
                # Delete related objects first to avoid ProtectedError
                if hasattr(case, "registration") and case.registration:
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                Site.objects.filter(case=case).delete()
                case.delete()

        yield
        clean_all_test_cases()

    @pytest.fixture(scope="function")
    def setup_sorting_test_data(self, seed_groups_fixture, seed_users_fixture):
        """Create test data for sorting tests"""
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

        # Create cases with varied data for sorting
        case_a = E12CaseFactory(
            first_name="Adam",
            surname="Zebra",
            nhs_number="1111111111",
            sex=1,
            ethnicity="A",
            organisations__organisation=gosh,
        )
        case_a.registration.cohort = 5
        case_a.registration.first_paediatric_assessment_date = date(2023, 1, 1)
        case_a.registration.audit_submission_date = date(2024, 1, 1)
        case_a.registration.save()

        case_b = E12CaseFactory(
            first_name="Brenda",
            surname="Young",
            nhs_number="3333333333",
            sex=2,
            ethnicity="B",
            organisations__organisation=gosh,
        )
        case_b.registration.cohort = 6
        case_b.registration.first_paediatric_assessment_date = date(2024, 1, 1)
        case_b.registration.audit_submission_date = date(2025, 6, 1)
        case_b.registration.save()

        case_c = E12CaseFactory(
            first_name="Charlie",
            surname="Xavier",
            nhs_number="5555555555",
            sex=1,
            ethnicity="C",
            organisations__organisation=gosh,
        )
        case_c.registration.cohort = 7
        case_c.registration.first_paediatric_assessment_date = date(2025, 1, 1)
        case_c.registration.audit_submission_date = date(2026, 12, 31)
        case_c.registration.save()

        return {
            "gosh": gosh,
            "user": user,
            "case_a": case_a,
            "case_b": case_b,
            "case_c": case_c,
        }

    def test_sort_by_name_up(self, client, setup_sorting_test_data):
        """Test sorting by name ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_name_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_name_up"
        cases = list(response.context["case_list"])
        # Should be Xavier, Young, Zebra
        assert cases[0].surname == "Xavier"
        assert cases[-1].surname == "Zebra"

    def test_sort_by_name_down(self, client, setup_sorting_test_data):
        """Test sorting by name descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_name_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_name_down"
        cases = list(response.context["case_list"])
        # Should be Zebra, Young, Xavier
        assert cases[0].surname == "Zebra"
        assert cases[-1].surname == "Xavier"

    def test_sort_by_nhs_number_up(self, client, setup_sorting_test_data):
        """Test sorting by NHS number ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_nhs_number_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_nhs_number_up"
        cases = list(response.context["case_list"])
        assert cases[0].nhs_number == "1111111111"
        assert cases[-1].nhs_number == "5555555555"

    def test_sort_by_nhs_number_down(self, client, setup_sorting_test_data):
        """Test sorting by NHS number descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_nhs_number_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_nhs_number_down"
        cases = list(response.context["case_list"])
        assert cases[0].nhs_number == "5555555555"
        assert cases[-1].nhs_number == "1111111111"

    def test_sort_by_id_up(self, client, setup_sorting_test_data):
        """Test sorting by ID ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_id_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_id_up"

    def test_sort_by_id_down(self, client, setup_sorting_test_data):
        """Test sorting by ID descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_id_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_id_down"

    def test_sort_by_cohort_up(self, client, setup_sorting_test_data):
        """Test sorting by cohort ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_cohort_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_cohort_up"

    def test_sort_by_cohort_down(self, client, setup_sorting_test_data):
        """Test sorting by cohort descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_cohort_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_cohort_down"

    def test_sort_by_deadline_up(self, client, setup_sorting_test_data):
        """Test sorting by deadline ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_deadline_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_deadline_up"

    def test_sort_by_deadline_down(self, client, setup_sorting_test_data):
        """Test sorting by deadline descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_deadline_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_deadline_down"

    def test_sort_by_ethnicity_up(self, client, setup_sorting_test_data):
        """Test sorting by ethnicity ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_ethnicity_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_ethnicity_up"

    def test_sort_by_ethnicity_down(self, client, setup_sorting_test_data):
        """Test sorting by ethnicity descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_ethnicity_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_ethnicity_down"

    def test_sort_by_sex_up(self, client, setup_sorting_test_data):
        """Test sorting by sex ascending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_sex_up"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_sex_up"

    def test_sort_by_sex_down(self, client, setup_sorting_test_data):
        """Test sorting by sex descending"""
        data = setup_sorting_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"sort_flag": "sort_by_sex_down"})

        assert response.status_code == HTTPStatus.OK
        assert response.context["sort_flag"] == "sort_by_sex_down"


@pytest.mark.django_db
class TestCaseListTotals:
    """Tests for totals calculation before and after filtering"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up test cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_test_cases():
            """Helper to clean up test cases and their related objects"""
            # Get all test cases
            test_cases = (
                Case.objects.filter(first_name__startswith="Finished")
                | Case.objects.filter(first_name__startswith="Incomplete")
                | Case.objects.filter(first_name__startswith="Unregistered")
            )

            # Delete related objects first to avoid ProtectedError
            for case in test_cases:
                # Delete registration and its related objects if they exist
                if hasattr(case, "registration") and case.registration:
                    # Delete audit progress if it exists
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    # Delete KPIs if they exist
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                # Delete sites
                Site.objects.filter(case=case).delete()

                # Now delete the case itself
                case.delete()

        # Clean before test
        clean_test_cases()

        yield

        # Clean after test
        clean_test_cases()

    @pytest.fixture(scope="function")
    def setup_totals_test_data(self, seed_groups_fixture, seed_users_fixture):
        """Create test data for totals calculation testing"""
        gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="TotalsTest",
            surname="User",
            email="totals_test@test.com",
            role=1,
            is_staff=True,
            is_rcpch_audit_team_member=False,
            view_preference=0,
            groups=[group],
        )

        # Create registered cases with complete/incomplete status
        complete_cases = []
        for i in range(3):
            case = E12CaseFactory(
                first_name=f"FinishedChild{i}",
                surname=f"Finished{i}",
                organisations__organisation=gosh,
            )
            # Cohort 5: 1 December 2021 - 30 November 2022
            case.registration.first_paediatric_assessment_date = date(2022, 1, 15)
            case.registration.save()

            # Mark as complete
            case.registration.audit_progress.registration_complete = True
            case.registration.audit_progress.first_paediatric_assessment_complete = True
            case.registration.audit_progress.epilepsy_context_complete = True
            case.registration.audit_progress.assessment_complete = True
            case.registration.audit_progress.multiaxial_diagnosis_complete = True
            case.registration.audit_progress.investigations_complete = True
            case.registration.audit_progress.management_complete = True
            case.registration.audit_progress.save()
            complete_cases.append(case)

        # Create incomplete registered cases
        incomplete_cases = []
        for i in range(2):
            case = E12CaseFactory(
                first_name=f"IncompleteChild{i}",
                surname=f"Incomplete{i}",
                organisations__organisation=gosh,
            )
            # Cohort 6: 1 December 2022 - 30 November 2023
            case.registration.first_paediatric_assessment_date = date(2023, 1, 15)
            case.registration.save()
            # Explicitly mark as incomplete
            case.registration.audit_progress.registration_complete = False
            case.registration.audit_progress.first_paediatric_assessment_complete = (
                False
            )
            case.registration.audit_progress.epilepsy_context_complete = False
            case.registration.audit_progress.assessment_complete = False
            case.registration.audit_progress.multiaxial_diagnosis_complete = False
            case.registration.audit_progress.investigations_complete = False
            case.registration.audit_progress.management_complete = False
            case.registration.audit_progress.save()
            incomplete_cases.append(case)

        # Create unregistered cases
        unregistered_cases = []
        for i in range(2):
            case = E12CaseFactory(
                first_name=f"UnregisteredChild{i}",
                surname=f"Unregistered{i}",
                organisations__organisation=gosh,
                registration=None,  # No registration
            )
            unregistered_cases.append(case)

        return {
            "gosh": gosh,
            "user": user,
            "complete_cases": complete_cases,
            "incomplete_cases": incomplete_cases,
            "unregistered_cases": unregistered_cases,
        }

    def test_unfiltered_totals(self, client, setup_totals_test_data):
        """Test that unfiltered totals show correct counts"""
        data = setup_totals_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        # Total should be 3 complete + 2 incomplete + 2 unregistered = 7
        assert response.context["all_unfiltered_counts"] == 7
        # Registered should be 3 complete + 2 incomplete = 5
        assert response.context["total_registered"] == 5
        # Unregistered should be 2
        assert response.context["total_unregistered"] == 2

    def test_filtered_totals_by_cohort_5(self, client, setup_totals_test_data):
        """Test that filtered totals update when filtering by cohort 5"""
        data = setup_totals_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"cohort": "5"})

        assert response.status_code == HTTPStatus.OK
        # Filtered should show only cohort 5 (3 complete cases)
        assert response.context["total_filtered_registered"] == 3
        assert response.context["total_filtered_complete"] == 3
        assert response.context["total_filtered_incomplete"] == 0
        # Unfiltered totals should remain the same
        assert response.context["all_unfiltered_counts"] == 7

    def test_filtered_totals_by_cohort_6(self, client, setup_totals_test_data):
        """Test that filtered totals update when filtering by cohort 6"""
        data = setup_totals_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"cohort": "6"})

        assert response.status_code == HTTPStatus.OK
        # Filtered should show only cohort 6 (2 incomplete cases)
        assert response.context["total_filtered_registered"] == 2
        assert response.context["total_filtered_complete"] == 0
        assert response.context["total_filtered_incomplete"] == 2
        # Unfiltered totals should remain the same
        assert response.context["all_unfiltered_counts"] == 7

    def test_filtered_totals_by_search(self, client, setup_totals_test_data):
        """Test that filtered totals update when searching"""
        data = setup_totals_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        # Search for "Finished" to match only finished/complete cases
        response = client.get(url, {"filtered_case_list": "Finished"})

        assert response.status_code == HTTPStatus.OK
        # Should find only 3 finished cases
        assert response.context["case_list"].paginator.count == 3
        # Unfiltered totals should remain the same
        assert response.context["all_unfiltered_counts"] == 7

    def test_complete_incomplete_totals(self, client, setup_totals_test_data):
        """Test complete and incomplete totals"""
        data = setup_totals_test_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        # Should have 3 complete and 2 incomplete
        assert response.context["total_filtered_complete"] == 3
        assert response.context["total_filtered_incomplete"] == 2


@pytest.mark.django_db
class TestCaseListViewPreferences:
    """Tests for different view preference levels"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_all_test_cases():
            """Helper to clean up all test cases and their related objects"""
            test_cases = Case.objects.all()

            for case in test_cases:
                # Delete related objects first to avoid ProtectedError
                if hasattr(case, "registration") and case.registration:
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                Site.objects.filter(case=case).delete()
                case.delete()

        yield
        clean_all_test_cases()

    @pytest.fixture(scope="function")
    def setup_view_preference_data(self, seed_groups_fixture, seed_users_fixture):
        """Create cases across multiple organisations"""
        gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
        # Get another org in same trust as GOSH
        gosh_trust = gosh.trust
        other_org_same_trust = (
            Organisation.objects.filter(trust=gosh_trust, active=True)
            .exclude(pk=gosh.pk)
            .first()
        )

        # Get org in different trust (Addenbrooke's)
        addenbrookes = Organisation.objects.get(ods_code="RGT01", trust__ods_code="RGT")

        # Create case at GOSH
        gosh_case = E12CaseFactory(
            first_name="GOSHChild",
            surname="TestGOSH",
            organisations__organisation=gosh,
        )

        # Create case at other org in same trust (if exists)
        trust_case = None
        if other_org_same_trust:
            trust_case = E12CaseFactory(
                first_name="TrustChild",
                surname="TestTrust",
                organisations__organisation=other_org_same_trust,
            )

        # Create case at Addenbrooke's
        addenbrookes_case = E12CaseFactory(
            first_name="AddenbrookesChild",
            surname="TestAddenbrookes",
            organisations__organisation=addenbrookes,
        )

        return {
            "gosh": gosh,
            "other_org_same_trust": other_org_same_trust,
            "addenbrookes": addenbrookes,
            "gosh_case": gosh_case,
            "trust_case": trust_case,
            "addenbrookes_case": addenbrookes_case,
        }

    def test_organisation_level_view(self, client, setup_view_preference_data):
        """Test organisation level view shows only org cases"""
        data = setup_view_preference_data
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="OrgLevel",
            surname="User",
            email="org_level@test.com",
            role=1,
            is_staff=True,
            is_rcpch_audit_team_member=False,
            view_preference=0,  # Organisation level
            groups=[group],
        )

        client.force_login(user)
        twofactor_signin(client, user)

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        # Should see only GOSH case
        assert response.context["case_list"].paginator.count == 1

    def test_trust_level_view(self, client, setup_view_preference_data):
        """Test trust level view shows all trust cases"""
        data = setup_view_preference_data
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="TrustLevel",
            surname="User",
            email="trust_level@test.com",
            role=1,
            is_staff=True,
            is_rcpch_audit_team_member=False,
            view_preference=1,  # Trust level
            groups=[group],
        )

        client.force_login(user)
        twofactor_signin(client, user)

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        # Should see GOSH case and trust case if it exists
        expected_count = 2 if data["trust_case"] else 1
        assert response.context["case_list"].paginator.count == expected_count

    def test_national_level_view(self, client, setup_view_preference_data):
        """Test national level view shows all cases"""
        data = setup_view_preference_data
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="NationalLevel",
            surname="User",
            email="national_level@test.com",
            role=4,  # RCPCH Audit Team
            is_staff=True,
            is_rcpch_audit_team_member=True,
            view_preference=2,  # National level
            groups=[group],
        )

        client.force_login(user)
        twofactor_signin(client, user)

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        # Should see all cases across all trusts
        expected_count = 3 if data["trust_case"] else 2
        assert response.context["case_list"].paginator.count == expected_count


@pytest.mark.django_db
class TestCaseListPagination:
    """Tests for pagination functionality"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_all_test_cases():
            """Helper to clean up all test cases and their related objects"""
            test_cases = Case.objects.all()

            for case in test_cases:
                # Delete related objects first to avoid ProtectedError
                if hasattr(case, "registration") and case.registration:
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                Site.objects.filter(case=case).delete()
                case.delete()

        yield
        clean_all_test_cases()

    @pytest.fixture(scope="function")
    def setup_pagination_data(self, seed_groups_fixture, seed_users_fixture):
        """Create more than 50 cases to test pagination"""
        gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="PaginationTest",
            surname="User",
            email="pagination_test@test.com",
            role=1,
            is_staff=True,
            is_rcpch_audit_team_member=False,
            view_preference=0,
            groups=[group],
        )

        # Create 75 cases to test pagination (page size = 50)
        cases = []
        for i in range(75):
            case = E12CaseFactory(
                first_name=f"PageChild{i}",
                surname=f"Page{i}",
                organisations__organisation=gosh,
            )
            cases.append(case)

        return {
            "gosh": gosh,
            "user": user,
            "cases": cases,
        }

    def test_first_page_has_50_items(self, client, setup_pagination_data):
        """Test first page shows 50 items"""
        data = setup_pagination_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK
        assert len(response.context["case_list"]) == 50
        assert response.context["case_list"].paginator.num_pages == 2

    def test_second_page_has_remaining_items(self, client, setup_pagination_data):
        """Test second page shows remaining items"""
        data = setup_pagination_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(url, {"page": "2"})

        assert response.status_code == HTTPStatus.OK
        assert len(response.context["case_list"]) == 25


@pytest.mark.django_db
class TestCaseListHTMX:
    """Tests for HTMX requests"""

    @pytest.fixture(scope="function", autouse=True)
    def cleanup_cases(self):
        """Clean up cases before and after each test"""
        from epilepsy12.models import Case, Site

        def clean_all_test_cases():
            """Helper to clean up all test cases and their related objects"""
            test_cases = Case.objects.all()

            for case in test_cases:
                # Delete related objects first to avoid ProtectedError
                if hasattr(case, "registration") and case.registration:
                    if (
                        hasattr(case.registration, "audit_progress")
                        and case.registration.audit_progress
                    ):
                        case.registration.audit_progress.delete()
                    if hasattr(case.registration, "kpi") and case.registration.kpi:
                        case.registration.kpi.delete()
                    case.registration.delete()

                Site.objects.filter(case=case).delete()
                case.delete()

        yield
        clean_all_test_cases()

    @pytest.fixture(scope="function")
    def setup_htmx_data(self, seed_groups_fixture, seed_users_fixture):
        """Create test data for HTMX tests"""
        gosh = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
        group = Group.objects.get(name="trust_audit_team_edit_access")

        user = E12UserFactory(
            first_name="HTMXTest",
            surname="User",
            email="htmx_test@test.com",
            role=1,
            is_staff=True,
            is_rcpch_audit_team_member=False,
            view_preference=0,
            groups=[group],
        )

        case = E12CaseFactory(
            first_name="HTMXChild",
            surname="TestHTMX",
            organisations__organisation=gosh,
        )

        return {
            "gosh": gosh,
            "user": user,
            "case": case,
        }

    def test_htmx_request_returns_partial_template(self, client, setup_htmx_data):
        """Test HTMX request returns partial template"""
        data = setup_htmx_data
        client.force_login(data["user"])
        twofactor_signin(client, data["user"])

        url = reverse("cases", kwargs={"organisation_id": data["gosh"].pk})
        response = client.get(
            url,
            HTTP_HX_REQUEST="true",
            HTTP_HX_TRIGGER_NAME="sort_by_name_up",
        )

        assert response.status_code == HTTPStatus.OK
        # HTMX requests should use partial template
        template_names = [t.name for t in response.templates]
        assert "epilepsy12/partials/case_table.html" in template_names
