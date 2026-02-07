from datetime import date

import pytest

from dateutil.relativedelta import relativedelta
from django.urls import reverse

from ...constants import AUDIT_CENTRE_CLINICIAN, RCPCH_AUDIT_TEAM, KPI_SCORE
from ...common_view_functions.calculate_kpis import calculate_kpis
from ...tests.view_tests.permissions_tests.perm_tests_utils import twofactor_signin
from ...models import (
    Epilepsy12User,
    KPI,
    Organisation,
    CountryKPIAggregation,
)


def check_school_individual_healthcare_kpi_aggs(
    client,
    org,
    cohort,
    expected_passed,
    expected_total_eligible
):
    url = reverse("selected_trust_kpis", kwargs={
        "organisation_id": org.id,
        "access": "private"
    })

    url = f"{url}?cohort={cohort}"

    response = client.get(url)
    assert response.status_code == 200

    aggregate_kpis = response.context["all_data"]

    org_agg_kpis = aggregate_kpis["ORGANISATION_KPIS"]["aggregation_model"]
    assert org_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
    assert org_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible

    if org.trust:
        trust_agg_kpis = aggregate_kpis["TRUST_KPIS"]["aggregation_model"]
        assert trust_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
        assert trust_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible
    elif org.local_health_board:
        local_health_board_agg_kpis = aggregate_kpis["LOCAL_HEALTH_BOARD_KPIS"]["aggregation_model"]
        assert local_health_board_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
        assert local_health_board_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible

    if org.integrated_care_board:
        icb_agg_kpis = aggregate_kpis["ICB_KPIS"]["aggregation_model"]
        assert icb_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
        assert icb_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible

    if org.nhs_england_region:
        nhs_england_region_agg_kpis = aggregate_kpis["NHS_ENGLAND_REGION_KPIS"]["aggregation_model"]
        assert nhs_england_region_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
        assert nhs_england_region_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible

    openuk_network_agg_kpis = aggregate_kpis["OPEN_UK_KPIS"]["aggregation_model"]
    assert openuk_network_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
    assert openuk_network_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible

    country_agg_kpis = aggregate_kpis["COUNTRY_KPIS"]["aggregation_model"]
    assert country_agg_kpis.school_individual_healthcare_plan_passed == expected_passed
    assert country_agg_kpis.school_individual_healthcare_plan_total_eligible == expected_total_eligible


@pytest.mark.django_db
def test_case_appears_in_trust_kpis(
    client,
    e12_case_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    user = Epilepsy12User.objects.filter(
        employer_organisations__employer_organisation__ods_code="RP401",
        role=AUDIT_CENTRE_CLINICIAN,
    ).first()

    org = user.employer_organisations.first().employer_organisation

    client.force_login(user)
    twofactor_signin(client, test_user=user)

    passed_case = e12_case_factory(
        date_of_birth=date(2013, 1, 1),
        # Must have completed first year of care
        registration__first_paediatric_assessment_date=date(2013, 1, 1) + relativedelta(years=10),
        organisations__organisation=org,
        # pass KPI 10
        registration__management__individualised_care_plan_in_place=True,
        registration__management__individualised_care_plan_includes_ehcp=True,
    )

    calculate_kpis(passed_case.registration)

    passed_case.refresh_from_db()
    assert passed_case.registration.kpi.school_individual_healthcare_plan == KPI_SCORE["PASS"]

    failed_case = e12_case_factory(
        date_of_birth=date(2013, 1, 1),
        # Must have completed first year of care
        registration__first_paediatric_assessment_date=date(2013, 1, 1) + relativedelta(years=10),
        organisations__organisation=org,
        # fail KPI 10
        registration__management__individualised_care_plan_in_place=False,
    )

    calculate_kpis(failed_case.registration)
    failed_case.refresh_from_db()
    assert failed_case.registration.kpi.school_individual_healthcare_plan == KPI_SCORE["FAIL"]

    cohort = passed_case.registration.cohort
    assert failed_case.registration.cohort == cohort

    check_school_individual_healthcare_kpi_aggs(client, org, cohort,
        expected_passed=1,
        expected_total_eligible=2,
    )


# https://github.com/rcpch/rcpch-audit-engine/issues/1347
@pytest.mark.django_db
def test_kpi_calculations_correct_for_case_with_referral_in_different_country(
    client,
    e12_case_factory,
    seed_groups_fixture,
    seed_users_fixture,
):
    welsh_org = Organisation.objects.filter(
        country__name="Wales"
    ).first()

    english_org = Organisation.objects.filter(
        country__name="England"
    ).first()

    # We need a user that can see both orgs - use an audit team member
    user = Epilepsy12User.objects.filter(
        role=RCPCH_AUDIT_TEAM,
    ).first()

    client.force_login(user)
    twofactor_signin(client, test_user=user)

    args = {
        "date_of_birth": date(2013, 1, 1),
        # Must have completed first year of care
        "registration__first_paediatric_assessment_date": date(2013, 1, 1) + relativedelta(years=10),
        "organisations__organisation": welsh_org,
        # pass KPI 10
        "registration__management__individualised_care_plan_in_place": True,
        "registration__management__individualised_care_plan_includes_ehcp": True,
    }

    cases = e12_case_factory.create_batch(2, **args)

    cohort = cases[0].registration.cohort

    for case in cases:
        calculate_kpis(case.registration)

        case.refresh_from_db()
        assert case.registration.kpi.school_individual_healthcare_plan == KPI_SCORE["PASS"]

    welsh_case_with_referral = cases[0]

    # General paediatric centre in England
    url = reverse("general_paediatric_centre", kwargs={
        "assessment_id": welsh_case_with_referral.registration.assessment.id,
    })

    response = client.post(url, data={
        "general_paediatric_centre": english_org.id,
    })

    assert response.status_code == 200
    
    welsh_case_with_referral.refresh_from_db()
    assert welsh_case_with_referral.epilepsy12_sites.count() == 2

    # Patch back assessment complete
    audit_progress = welsh_case_with_referral.registration.audit_progress
    audit_progress.assessment_complete = True
    audit_progress.save()

    # Safety check
    welsh_case_without_referral = cases[1]
    welsh_case_without_referral.refresh_from_db()
    assert welsh_case_without_referral.epilepsy12_sites.count() == 1

    check_school_individual_healthcare_kpi_aggs(client, welsh_org, cohort,
        expected_passed=2,
        expected_total_eligible=2,
    )

    # Trigger KPI recalculation for English org
    # It could be any org but use the one we already have
    url = reverse("selected_trust_kpis", kwargs={
        "organisation_id": english_org.id,
        "access": "private"
    })

    url = f"{url}?cohort={cohort}"

    response = client.get(url)
    assert response.status_code == 200

    # Check the KPI calculations did not leak into the Welsh org.
    # We have to check the database directly - if we call selected_trust_kpis it will
    # recalculate and correct them.
    welsh_kpi_agg = CountryKPIAggregation.objects.get(
        abstraction_relation__name="Wales",
        cohort=cohort
    )

    assert welsh_kpi_agg.school_individual_healthcare_plan_passed == 2
    assert welsh_kpi_agg.school_individual_healthcare_plan_total_eligible == 2
