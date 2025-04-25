from datetime import datetime, date, timedelta

import pytest

from django.utils import timezone

from epilepsy12.filtersets import CaseFilter, CaseFilterMethods
from epilepsy12.tests.factories import E12CaseFactory
from ..common_view_functions_tests.aggregate_by_tests.helpers import (
    _clean_cases_from_test_db,
    _register_cases_in_organisation,
    _register_kpi_scored_cases,
)
from epilepsy12.models import (
    Case,
    KPI,
    FirstPaediatricAssessment,
    MultiaxialDiagnosis,
    Management,
    AuditProgress,
    Site,
)


@pytest.mark.django_db
def test_get_ethnicity_counts(e12_case_factory):

    _clean_cases_from_test_db()
    _register_cases_in_organisation(
        ["RGT01", "RGN90", "7A6AV"],
        e12_case_factory,
        n_cases=10,
    )
    org1_cases = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGT01"
    ).update(ethnicity="A")
    org2_cases = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGN90"
    ).update(ethnicity="B")
    org3_cases = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="7A6AV"
    ).update(ethnicity="C")

    org1_cases_count = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGT01"
    ).count()
    org2_cases_count = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGN90"
    ).count()
    org3_cases_count = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="7A6AV"
    ).count()

    ethnicity_counts = CaseFilterMethods.get_ethnicity_counts(
        queryset=Case.objects.all()
    )
    assert (
        ethnicity_counts["A"] == org1_cases_count
    ), f"Expected {org1_cases_count} for Ethnicity A"
    assert (
        ethnicity_counts["B"] == org2_cases_count
    ), f"Expected {org2_cases_count} for Ethnicity B"
    assert (
        ethnicity_counts["C"] == org3_cases_count
    ), f"Expected {org3_cases_count} for Ethnicity C"


@pytest.mark.django_db
def test_get_sex_counts(e12_case_factory):
    _clean_cases_from_test_db()
    _register_cases_in_organisation(  # create 10 cases, 5 in each org
        ["RGT01", "RGN90"],
        e12_case_factory,
        n_cases=5,
    )
    # Set sex for cases in each org
    Case.objects.filter(epilepsy12_sites__organisation__ods_code="RGT01").update(sex=1)
    Case.objects.filter(epilepsy12_sites__organisation__ods_code="RGN90").update(sex=2)

    org1_count = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGT01"
    ).count()
    org2_count = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGN90"
    ).count()

    sex_counts = CaseFilterMethods.get_sex_counts(Case.objects.all())

    assert sex_counts[1] == org1_count
    assert sex_counts[2] == org2_count


@pytest.mark.django_db
def test_get_age_counts(e12_case_factory):
    _clean_cases_from_test_db()
    _register_cases_in_organisation(["RGT01"], e12_case_factory, n_cases=2)
    # Set one case under 12, one over 12
    cases = list(Case.objects.all())
    cases[0].date_of_birth = cases[0].date_of_birth.replace(
        year=cases[0].date_of_birth.year + 13
    )
    cases[0].save()
    age_counts = CaseFilterMethods.get_age_counts(Case.objects.all())
    assert age_counts["under_12"] + age_counts["12_and_over"] == 2


@pytest.mark.django_db
def test_get_index_of_multiple_deprivation_quintile_counts(e12_case_factory):
    _clean_cases_from_test_db()
    _register_cases_in_organisation(["RGT01"], e12_case_factory, n_cases=3)
    Case.objects.all().update(index_of_multiple_deprivation_quintile=2)
    counts = CaseFilterMethods.get_index_of_multiple_deprivation_quintile_counts(
        Case.objects.all()
    )
    assert counts[2] == 3


@pytest.mark.django_db
def test_get_registration_status_counts(e12_case_factory):
    _clean_cases_from_test_db()
    _register_cases_in_organisation(["RGT01"], e12_case_factory, n_cases=2)
    # Assume all are registered by default
    registered = CaseFilterMethods.get_registration_status_counts(
        Case.objects.all(), "registered"
    )
    unregistered = CaseFilterMethods.get_registration_status_counts(
        Case.objects.all(), "unregistered"
    )
    assert registered + unregistered == 2


@pytest.mark.django_db
def test_get_developmental_learning_or_schooling_problems_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__first_paediatric_assessment__developmental_learning_or_schooling_problems=True
    )
    case_2 = e12_case_factory(
        registration__first_paediatric_assessment__developmental_learning_or_schooling_problems=False
    )

    count = CaseFilterMethods.get_developmental_learning_or_schooling_problems_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_behavioural_or_emotional_problems_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__first_paediatric_assessment__behavioural_or_emotional_problems=True
    )
    case_2 = e12_case_factory(
        registration__first_paediatric_assessment__behavioural_or_emotional_problems=False
    )

    count = CaseFilterMethods.get_behavioural_or_emotional_problems_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_syndrome_present_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(registration__multiaxial_diagnosis__syndrome_present=True)
    case_2 = e12_case_factory(
        registration__multiaxial_diagnosis__syndrome_present=False
    )

    count = CaseFilterMethods.get_syndrome_present_counts(Case.objects.all())
    assert count == 1


@pytest.mark.django_db
def test_get_epilepsy_cause_known_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__multiaxial_diagnosis__epilepsy_cause_known=True
    )
    case_2 = e12_case_factory(
        registration__multiaxial_diagnosis__epilepsy_cause_known=False
    )

    count = CaseFilterMethods.get_epilepsy_cause_known_counts(Case.objects.all())
    assert count == 1


@pytest.mark.django_db
def test_get_global_developmental_delay_or_learning_difficulties_counts(
    e12_case_factory,
):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=True
    )
    case_2 = e12_case_factory(
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=False
    )

    count = CaseFilterMethods.get_global_developmental_delay_or_learning_difficulties_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_autistic_spectrum_disorder_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__multiaxial_diagnosis__autistic_spectrum_disorder=True
    )
    case_2 = e12_case_factory(
        registration__multiaxial_diagnosis__autistic_spectrum_disorder=False
    )

    count = CaseFilterMethods.get_autistic_spectrum_disorder_counts(Case.objects.all())
    assert count == 1


@pytest.mark.django_db
def test_get_mental_health_issue_identified_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__multiaxial_diagnosis__mental_health_issue_identified=True
    )
    case_2 = e12_case_factory(
        registration__multiaxial_diagnosis__mental_health_issue_identified=False
    )

    count = CaseFilterMethods.get_mental_health_issue_identified_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_has_been_referred_for_mental_health_support_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__management__has_been_referred_for_mental_health_support=True
    )
    case_2 = e12_case_factory(
        registration__management__has_been_referred_for_mental_health_support=False
    )

    count = CaseFilterMethods.get_has_been_referred_for_mental_health_support_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_has_support_for_mental_health_support_counts(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(
        registration__management__has_support_for_mental_health_support=True
    )
    case_2 = e12_case_factory(
        registration__management__has_support_for_mental_health_support=False
    )

    count = CaseFilterMethods.get_has_support_for_mental_health_support_counts(
        Case.objects.all()
    )
    assert count == 1


@pytest.mark.django_db
def test_get_kpi_failed_counts(e12_case_factory):
    _clean_cases_from_test_db()
    _register_kpi_scored_cases(
        e12_case_factory,
        ods_codes=["RJT01", "RGN90"],
        num_cases=10,
    )

    total_failed_tuples = CaseFilterMethods.get_kpi_failed_counts(Case.objects.all())
    # Get the counts dictionary {('kpi_id', 'kpi_name'): count, ...}
    total_failed = {
        kpi_id: count for (kpi_id, kpi_name), count in total_failed_tuples.items()
    }

    assert (
        total_failed.get("1") == 20
    ), f"KPI 1 Expected 20 failed cases, got {total_failed.get('1')}"
    assert (
        total_failed.get("2") == 20
    ), f"KPI 2 Expected 20 failed cases, got {total_failed.get('2')}"
    assert (
        total_failed.get("3") == 0
    ), f"KPI 3 Expected 20 failed cases, got {total_failed.get('3')}"
    assert (
        total_failed.get("3b") == 0
    ), f"KPI 3b Expected 20 failed cases, got {total_failed.get('3b')}"
    assert (
        total_failed.get("4") == 10
    ), f"KPI 4 Expected 20 failed cases, got {total_failed.get('4')}"
    assert (
        total_failed.get("5") == 10
    ), f"KPI 5 Expected 20 failed cases, got {total_failed.get('5')}"
    assert (
        total_failed.get("6") == 20
    ), f"KPI 6 Expected 20 failed cases, got {total_failed.get('6')}"
    assert (
        total_failed.get("7") == 10
    ), f"KPI 7 Expected 20 failed cases, got {total_failed.get('7')}"
    assert (
        total_failed.get("8") == 0
    ), f"KPI 8 Expected 20 failed cases, got {total_failed.get('8')}"
    assert (
        total_failed.get("9a") == 20
    ), f"KPI 9a Expected 20 failed cases, got {total_failed.get('9a')}"
    assert (
        total_failed.get("9aa") == 20
    ), f"KPI 9aa Expected 20 failed cases, got {total_failed.get('9aa')}"
    assert (
        total_failed.get("9ab") == 20
    ), f"KPI 9ab Expected 20 failed cases, got {total_failed.get('9ab')}"
    assert (
        total_failed.get("9ac") == 20
    ), f"KPI 9ac Expected 20 failed cases, got {total_failed.get('9ac')}"
    assert (
        total_failed.get("9b") == 20
    ), f"KPI 9b Expected 20 failed cases, got {total_failed.get('9b')}"
    assert (
        total_failed.get("9ba") == 20
    ), f"KPI 9ba Expected 20 failed cases, got {total_failed.get('9ba')}"
    assert (
        total_failed.get("9bb") == 20
    ), f"KPI 9bb Expected 20 failed cases, got {total_failed.get('9bb')}"
    assert (
        total_failed.get("9bc") == 20
    ), f"KPI 9bc Expected 20 failed cases, got {total_failed.get('9bc')}"
    assert (
        total_failed.get("9bd") == 20
    ), f"KPI 9bd Expected 20 failed cases, got {total_failed.get('9bd')}"
    assert (
        total_failed.get("9be") == 20
    ), f"KPI 9be Expected 20 failed cases, got {total_failed.get('9be')}"
    assert (
        total_failed.get("9bf") == 20
    ), f"KPI 9bf Expected 20 failed cases, got {total_failed.get('9bf')}"
    assert (
        total_failed.get("10") == 20
    ), f"KPI 9 Expected 20 failed cases, got {total_failed.get('10')}"


# {
# ("1", "paediatrician_with_expertise_in_epilepsies"): 20,
# ("2", "epilepsy_specialist_nurse"): 20,
# ("3", "tertiary_input"): 0,
# ("3b", "epilepsy_surgery_referral"): 0,
# ("4", "ecg"): 10,
# ("5", "mri"): 10,
# ("6", "assessment_of_mental_health_issues"): 20,
# ("7", "mental_health_support"): 10,
# ("8", "sodium_valproate"): 0,
# ("9a", "comprehensive_care_planning_agreement"): 20,
# ("9aa", "patient_held_individualised_epilepsy_document"): 20,
# ("9ab", "patient_carer_parent_agreement_to_the_care_planning"): 20,
# ("9ac", "care_planning_has_been_updated_when_necessary"): 20,
# ("9b", "comprehensive_care_planning_content"): 20,
# ("9ba", "parental_prolonged_seizures_care_plan"): 20,
# ("9bb", "water_safety"): 20,
# ("9bc", "first_aid"): 20,
# ("9bd", "general_participation_and_risk"): 20,
# ("9be", "service_contact_details"): 20,
# ("9bf", "sudep"): 20,
# ("10", "school_individual_healthcare_plan"): 20,
# }

"""
Filter by tests
"""


@pytest.mark.django_db
def test_filter_by_developmental_learning_or_schooling_problems(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__first_paediatric_assessment__developmental_learning_or_schooling_problems=True
    )
    case_false = e12_case_factory(
        registration__first_paediatric_assessment__developmental_learning_or_schooling_problems=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_developmental_learning_or_schooling_problems(
        qs, True
    )
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_behavioural_or_emotional_problems(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__first_paediatric_assessment__behavioural_or_emotional_problems=True
    )
    case_false = e12_case_factory(
        registration__first_paediatric_assessment__behavioural_or_emotional_problems=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_behavioural_or_emotional_problems(qs, True)
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_syndrome_present(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__multiaxial_diagnosis__syndrome_present=True
    )
    case_false = e12_case_factory(
        registration__multiaxial_diagnosis__syndrome_present=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_syndrome_present(qs, True)
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_epilepsy_cause_known(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__multiaxial_diagnosis__epilepsy_cause_known=True
    )
    case_false = e12_case_factory(
        registration__multiaxial_diagnosis__epilepsy_cause_known=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_epilepsy_cause_known(qs, True)
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_global_developmental_delay_or_learning_difficulties(
    e12_case_factory,
):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=True
    )
    case_false = e12_case_factory(
        registration__multiaxial_diagnosis__global_developmental_delay_or_learning_difficulties=False
    )
    qs = Case.objects.all()
    filtered = (
        CaseFilterMethods.filter_by_global_developmental_delay_or_learning_difficulties(
            qs, True
        )
    )
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_autistic_spectrum_disorder(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__multiaxial_diagnosis__autistic_spectrum_disorder=True
    )
    case_false = e12_case_factory(
        registration__multiaxial_diagnosis__autistic_spectrum_disorder=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_autistic_spectrum_disorder(qs, True)
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_mental_health_issue_identified(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__multiaxial_diagnosis__mental_health_issue_identified=True
    )
    case_false = e12_case_factory(
        registration__multiaxial_diagnosis__mental_health_issue_identified=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_mental_health_issue_identified(qs, True)
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_has_been_referred_for_mental_health_support(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__management__has_been_referred_for_mental_health_support=True
    )
    case_false = e12_case_factory(
        registration__management__has_been_referred_for_mental_health_support=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_has_been_referred_for_mental_health_support(
        queryset=qs, value=True
    )
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_has_support_for_mental_health_support(e12_case_factory):
    _clean_cases_from_test_db()
    case_true = e12_case_factory(
        registration__management__has_support_for_mental_health_support=True
    )
    case_false = e12_case_factory(
        registration__management__has_support_for_mental_health_support=False
    )
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_has_support_for_mental_health_support(
        queryset=qs, value=True
    )
    assert case_true in filtered
    assert case_false not in filtered


@pytest.mark.django_db
def test_filter_by_kpi_failed(e12_case_factory):
    _clean_cases_from_test_db()
    _register_kpi_scored_cases(
        e12_case_factory,
        ods_codes=["RJZ01", "RGN90"],
        num_cases=10,
    )  # Generates 40 cases per organisation, only 10 should pass in each (note only for KPI 4 and 7)

    rjz01_cases = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RJZ01",
    )
    rgn90_cases = Case.objects.filter(
        epilepsy12_sites__organisation__ods_code="RGN90",
    )

    KPI.objects.filter(registration__case__in=rjz01_cases).update(
        ecg=1
    )  # Now 40 cases should pass and should be from RJZ01

    KPI.objects.filter(registration__case__in=rgn90_cases).update(
        ecg=0
    )  # Now 40 cases should fail and should be from RGN90

    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_kpi_failed(qs, ["4"])  # ecg
    assert (
        filtered.count() == 40
    ), f"Expected 40 cases failed KPI 1, got {filtered.count()}"

    # requery the cases
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_kpi_failed(
        qs, ["7"]
    )  # mental_health_support
    assert (
        filtered.count() == 20  # 10 from each org as these were not updated
    ), f"Expected 20 cases failed KPI 2, got {filtered.count()}"


@pytest.mark.django_db
def test_filter_by_index_of_multiple_deprivation_quintile(e12_case_factory):
    _clean_cases_from_test_db()
    case_1 = e12_case_factory(index_of_multiple_deprivation_quintile=1)
    case_2 = e12_case_factory(index_of_multiple_deprivation_quintile=2)
    qs = Case.objects.all()
    filtered = CaseFilterMethods.filter_by_index_of_multiple_deprivation_quintile(qs, 1)
    assert case_1 in filtered
    assert case_2 not in filtered


import pytest
from django.http import QueryDict
from epilepsy12.filtersets.case_filterset import CaseFilterMethods
from epilepsy12.models import Case


@pytest.mark.django_db
def test_apply_all_active_filters(e12_case_factory):
    # Clean up and create a case that matches all filters
    _clean_cases_from_test_db()
    matching_case = e12_case_factory(
        sex=1,
        date_of_birth="2018-01-01",  # under 12
        index_of_multiple_deprivation_quintile=2,
        registration__cohort="6",
    )
    matching_case.registration.firstpaediatricassessment.developmental_learning_or_schooling_problems = (
        True
    )
    matching_case.registration.firstpaediatricassessment.behavioural_or_emotional_problems = (
        True
    )
    matching_case.registration.firstpaediatricassessment.save()

    matching_case.registration.multiaxialdiagnosis.syndrome_present = True
    matching_case.registration.multiaxialdiagnosis.epilepsy_cause_known = True
    matching_case.registration.multiaxialdiagnosis.global_developmental_delay_or_learning_difficulties = (
        True
    )
    matching_case.registration.multiaxialdiagnosis.autistic_spectrum_disorder = True
    matching_case.registration.multiaxialdiagnosis.mental_health_issue_identified = True
    matching_case.registration.multiaxialdiagnosis.save()

    matching_case.registration.management.has_been_referred_for_mental_health_support = (
        True
    )
    matching_case.registration.management.has_support_for_mental_health_support = True
    matching_case.registration.management.save()

    matching_case.registration.audit_progress.registration_complete = True
    matching_case.registration.audit_progress.first_paediatric_assessment_complete = (
        True
    )
    matching_case.registration.audit_progress.epilepsy_context_complete = True
    matching_case.registration.audit_progress.assessment_complete = True
    matching_case.registration.audit_progress.multiaxial_diagnosis_complete = True
    matching_case.registration.audit_progress.investigations_complete = True
    matching_case.registration.audit_progress.management_complete = True
    matching_case.registration.audit_progress.save()

    matching_case.registration.kpi.paediatrician_with_expertise_in_epilepsies = 0
    matching_case.registration.kpi.epilepsy_specialist_nurse = 0
    matching_case.registration.kpi.save()

    non_matching_case = e12_case_factory(
        date_of_birth="2018-01-01",  # under 12
        index_of_multiple_deprivation_quintile=2,
        registration__cohort="7",
    )

    non_matching_case.registration.firstpaediatricassessment.developmental_learning_or_schooling_problems = (
        False
    )
    non_matching_case.registration.firstpaediatricassessment.behavioural_or_emotional_problems = (
        False
    )
    non_matching_case.registration.firstpaediatricassessment.save()

    non_matching_case.registration.multiaxialdiagnosis.syndrome_present = False
    non_matching_case.registration.multiaxialdiagnosis.epilepsy_cause_known = False
    non_matching_case.registration.multiaxialdiagnosis.global_developmental_delay_or_learning_difficulties = (
        False
    )
    non_matching_case.registration.multiaxialdiagnosis.autistic_spectrum_disorder = (
        False
    )
    non_matching_case.registration.multiaxialdiagnosis.mental_health_issue_identified = (
        False
    )
    non_matching_case.registration.multiaxialdiagnosis.save()

    non_matching_case.registration.management.has_been_referred_for_mental_health_support = (
        False
    )
    non_matching_case.registration.management.has_support_for_mental_health_support = (
        False
    )
    non_matching_case.registration.management.save()

    non_matching_case.registration.audit_progress.registration_complete = False
    non_matching_case.registration.audit_progress.first_paediatric_assessment_complete = (
        False
    )
    non_matching_case.registration.audit_progress.epilepsy_context_complete = False
    non_matching_case.registration.audit_progress.assessment_complete = False
    non_matching_case.registration.audit_progress.multiaxial_diagnosis_complete = False
    non_matching_case.registration.audit_progress.investigations_complete = False
    non_matching_case.registration.audit_progress.management_complete = False
    non_matching_case.registration.audit_progress.save()

    non_matching_case.registration.kpi.epilepsy_specialist_nurse = 1
    non_matching_case.registration.kpi.paediatrician_with_expertise_in_epilepsies = 1
    non_matching_case.registration.kpi.save()

    # Simulate a request with all filters set to match the first case
    params = {
        "developmental_learning_or_schooling_problems": "true",
        "behavioural_or_emotional_problems": "true",
        "syndrome_present": "true",
        "epilepsy_cause_known": "true",
        "global_developmental_delay_or_learning_difficulties": "true",
        "autistic_spectrum_disorder": "true",
        "mental_health_issue_identified": "true",
        "has_been_referred_for_mental_health_support": "true",
        "has_support_for_mental_health_support": "true",
        "audit_progress_complete": "true",
        "registration_cohort": "6",
        "sex": "1",
        "age_range": "under_12",
        "registration_status": "registered",
        "kpi_failed": "1,2",
        "index_of_multiple_deprivation_quintile": "2",
    }

    # Django's QueryDict is required for .getlist() to work in the filter method
    qdict = QueryDict("", mutable=True)
    qdict.update(params)

    class DummyRequest:
        GET = qdict

    special_filter_params = [
        "developmental_learning_or_schooling_problems",
        "behavioural_or_emotional_problems",
        "syndrome_present",
        "epilepsy_cause_known",
        "global_developmental_delay_or_learning_difficulties",
        "autistic_spectrum_disorder",
        "mental_health_issue_identified",
        "has_been_referred_for_mental_health_support",
        "has_support_for_mental_health_support",
        "audit_progress_complete",
        "audit_progress_incomplete",
        "registration_cohort",
    ]

    qs = Case.objects.all()
    filtered = CaseFilterMethods.apply_all_active_filters(
        qs,
        DummyRequest(),
        special_filter_params=special_filter_params,
        apply_special_filters=True,
    )
    assert filtered.count() == 1
    assert matching_case in filtered
