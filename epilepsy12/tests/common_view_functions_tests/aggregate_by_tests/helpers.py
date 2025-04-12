# python imports
import pytest
import random
from datetime import date
from dateutil.relativedelta import relativedelta

# 3rd party imports


# E12 imports
from epilepsy12.common_view_functions import (
    calculate_kpis,
)
from epilepsy12.models import (
    Organisation,
    Registration,
    Case,
)
from epilepsy12.tests.common_view_functions_tests.CreateKPIMetrics import KPIMetric


def _register_cases_in_organisation(
    ods_codes: list[str], e12_case_factory, n_cases: int = 10
) -> list:
    for code in ods_codes:
        # Community Paediatrics Org returning with the actual org so need to do filter.first()
        org = Organisation.objects.filter(ods_code=code, active=True).first()

        e12_case_factory.create_batch(
            n_cases,
            organisations__organisation=org,
            first_name=f"temp_{org.name}",
        )


def _register_kpi_scored_cases(
    e12_case_factory, ods_codes: "list[str]", num_cases: int = 10
):
    """Helper function to return a queryset of num_cases kids with scored, known KPI scores.

    Let metric = kpis 4 + 7:
        For each ods_code, num_cases will PASS metric, num_cases will FAIL metric, num_cases will be INELIGBLE for metric, num_cases will be INCOMPLETE
    """
    ORGANISATIONS = Organisation.objects.filter(
        ods_code__in=ods_codes,
    )

    # create answersets for cases to achieve the stated expected output
    answer_object = KPIMetric(eligible_kpi_6_8_10=True)
    pass_answers = answer_object.generate_metrics(
        kpi_1="PASS",
        kpi_2="PASS",
        kpi_4="PASS",
        kpi_6="PASS",
        kpi_7="PASS",
        kpi_8="PASS",
        kpi_9="PASS",
        kpi_10="PASS",
    )
    fail_answers = answer_object.generate_metrics(
        kpi_1="FAIL",
        kpi_2="FAIL",
        kpi_4="FAIL",
        kpi_6="FAIL",
        kpi_7="FAIL",
        kpi_8="FAIL",
        kpi_9="FAIL",
        kpi_10="FAIL",
    )
    ineligible_answers = answer_object.generate_metrics(
        kpi_1="FAIL",
        kpi_2="FAIL",
        kpi_4="INELIGIBLE",
        kpi_6="FAIL",
        kpi_7="INELIGIBLE",
        kpi_8="FAIL",
        kpi_9="FAIL",
        kpi_10="FAIL",
    )
    # NOTE: here we specify date of birth for 'empty answer set', as the default age would otherwise be 1yo, making them ineligible for kpis 6,8,10
    incomplete_answers = {"date_of_birth": date(2011, 1, 1)}

    filled_case_objects = []
    # iterate through answersets (pass, fail, ineligble, incomplete) for kpi, create 10 Cases per answerset
    for organisation in ORGANISATIONS:
        for answer_set in [
            pass_answers,
            fail_answers,
            ineligible_answers,
            incomplete_answers,
        ]:
            test_cases = e12_case_factory.create_batch(
                num_cases,
                organisations__organisation=organisation,
                first_name=f"temp_{organisation.name}",
                **answer_set,
            )
            filled_case_objects += test_cases

    for test_case in filled_case_objects:
        test_case.registration.completed_first_year_of_care_date = (
            test_case.registration.first_paediatric_assessment_date
            + relativedelta(years=1)
        )
        test_case.registration.audit_progress.registration_complete = True
        test_case.registration.audit_progress.first_paediatric_assessment_complete = (
            True
        )
        test_case.registration.audit_progress.assessment_complete = True
        test_case.registration.audit_progress.epilepsy_context_complete = True
        test_case.registration.audit_progress.multiaxial_diagnosis_complete = True
        test_case.registration.audit_progress.investigations_complete = True
        test_case.registration.audit_progress.management_complete = True

        calculate_kpis(registration_instance=test_case.registration)


def _clean_cases_from_test_db() -> None:
    Registration.objects.all().delete()
    Case.objects.all().delete()
