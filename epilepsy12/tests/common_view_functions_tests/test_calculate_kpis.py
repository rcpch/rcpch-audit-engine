"""
Tests for the calculate_kpi function.

Tests
- [x] return None if child not registered in audit (registration.registration_date is None, or registration_eligibility_criteria_met is None or False, Site.site_is_primary_centre_of_epilepsy_care is None)


Measure 8
- [ ] Measure 8 passed (registration.kpi.sodium_valproate == 1) if sex == 2 and on valproate and age >= 12 (line 378) and has_a_valproate_annual_risk_acknowledgement_form_been_completed
- [ ] Measure 8 failed (registration.kpi.sodium_valproate == 1) if sex == 2 and on valproate and age >= 12 (line 378) and not has_a_valproate_annual_risk_acknowledgement_form_been_completed
- [ ] Measure 8 ineligible (registration.kpi.sodium_valproate == 2) if sex == 2 and on valproate and age >= 12 (line 378)

Measure 9A
- [ ] Measure 9A passed (registration.kpi.comprehensive_care_planning_agreement) if registration_instance.management.individualised_care_plan_in_place
- [ ] Measure 9A failed (registration.kpi.comprehensive_care_planning_agreement) if not registration_instance.management.individualised_care_plan_in_place

Measure 9i
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 1) if (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if not (registration_instance.management.individualised_care_plan_in_place) and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 0) if registration_instance.management.individualised_care_plan_in_place) and not registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9i (registration.kpi.patient_held_individualised_epilepsy_document == 2) if not (registration_instance.management.individualised_care_plan_in_place)

Measure 9ii
- [ ] Measure 9ii passed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 1) if (registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement)
- [ ] Measure 9ii failed (registration.kpi.patient_carer_parent_agreement_to_the_care_planning == 0) if (Not registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement)

Measure 9iii
- [ ] Measure 9iii passed (registration.kpi.care_planning_has_been_updated_when_necessary == 1) if (registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)
- [ ] Measure 9iii failed (registration.kpi.care_planning_has_been_updated_when_necessary == 0) if (Not registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year)

Measure 9B
- [ ] Measure 9B passed (registration.kpi.comprehensive_care_planning_content == 1) if (
            registration_instance.management.has_rescue_medication_been_prescribed
            and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_include_first_aid
            and registration_instance.management.individualised_care_plan_addresses_water_safety
            and registration_instance.management.individualised_care_plan_includes_service_contact_details
            and registration_instance.management.individualised_care_plan_includes_general_participation_risk
            and registration_instance.management.individualised_care_plan_addresses_sudep
        )
- [ ] Measure 9B failed (registration.kpi.comprehensive_care_planning_content == 0) if (
            registration_instance.management.has_rescue_medication_been_prescribed
            and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_include_first_aid
            and registration_instance.management.individualised_care_plan_addresses_water_safety
            and registration_instance.management.individualised_care_plan_includes_service_contact_details
            and registration_instance.management.individualised_care_plan_includes_general_participation_risk
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ) == False

Measure 9B i
- [ ] Measure 9B i passed (registration.kpi.parental_prolonged_seizures_care_plan == 1) if (
                registration_instance.management.has_rescue_medication_been_prescribed
                and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            ) is True
- [ ] Measure 9B i failed (registration.kpi.parental_prolonged_seizures_care_plan == 0) if (
                registration_instance.management.has_rescue_medication_been_prescribed
                and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            ) is False

Measure 9B ii
- [ ] Measure 9B ii passed (registration.kpi.water_safety == 1) if (registration_instance.management.individualised_care_plan_addresses_water_safety)
- [ ] Measure 9B ii failed (registration.kpi.water_safety == 0) if not (registration_instance.management.individualised_care_plan_addresses_water_safety)

Measure 9B iii
- [ ] Measure 9B iii passed (registration.kpi.first_aid == 1) if (if registration_instance.management.individualised_care_plan_include_first_aid)
- [ ] Measure 9B iii failed (registration.kpi.first_aid == 0) if not (if registration_instance.management.individualised_care_plan_include_first_aid)

Measure 9B iv
- [ ] Measure 9B iv passed (registration.kpi.general_participation_and_risk == 1) if (registration_instance.management.individualised_care_plan_includes_general_participation_risk)
- [ ] Measure 9B iv failed (registration.kpi.general_participation_and_risk == 0) if not (registration_instance.management.individualised_care_plan_includes_general_participation_risk)

Measure 9B v
- [ ] Measure 9B v passed (registration.kpi.service_contact_details == 1) if (registration_instance.management.individualised_care_plan_includes_service_contact_details)
- [ ] Measure 9B v failed (registration.kpi.service_contact_details == 0) if not (registration_instance.management.individualised_care_plan_includes_service_contact_details)

Measure 9B vi
- [ ] Measure 9B vi passed (registration.kpi.sudep == 1) if (
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_addresses_sudep
        )
- [ ] Measure 9B vi failed (registration.kpi.sudep == 0) if not(
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ):

Measure 10
- [ ] Measure 10 passed (registration.kpi.school_individual_healthcare_plan == 1) if (age_at_first_paediatric_assessment >= 5) and (
                registration_instance.management.individualised_care_plan_includes_ehcp
            ):
- [ ] Measure 10 failed (registration.kpi.school_individual_healthcare_plan == 0) if not (age_at_first_paediatric_assessment >= 5) and (
                registration_instance.management.individualised_care_plan_includes_ehcp
            ):
- [ ] Measure 10 ineligible (registration.kpi.school_individual_healthcare_plan == 2) if not age_at_first_paediatric_assessment < 5
            ):


"""

# Standard imports
import pytest
from datetime import date
from dateutil.relativedelta import relativedelta

# Third party imports

# RCPCH imports
from epilepsy12.common_view_functions import calculate_kpis
from epilepsy12.models import (
    Registration,
    KPI,
)


@pytest.mark.django_db
def test_child_not_registered_in_audit_returns_none(e12_case_factory):
    """
    Test that calculate_kpis() returns None if child is not registered in the audit.
    """

    # creates an case with all audit values filled with default values
    case = e12_case_factory()

    # overwrite registration_date and eligibility criteria
    case.registration.registration_date = None
    case.registration.eligibility_criteria_met = None
    case.save()

    registration = Registration.objects.get(case=case)

    assert calculate_kpis(registration) is None

    # repeat with eligibility_criteria_met = False
    case.registration.registration_date = None
    case.registration.eligibility_criteria_met = False
    case.save()

    # get registration for the saved case model
    registration = Registration.objects.get(case=case)

    assert calculate_kpis(registration) is None





