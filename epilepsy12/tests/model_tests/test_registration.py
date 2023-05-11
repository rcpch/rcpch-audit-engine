import datetime

import pytest 

from epilepsy12.models import (
    Registration,
    Case,
    AuditProgress,
    KPI,
    Site,
    )
"""
@pytest.fixture()
def example_audit_progress():
    return AuditProgress.objects.create(
            registration_complete=False,
            first_paediatric_assessment_complete=False,
            assessment_complete=False,
            epilepsy_context_complete=False,
            multiaxial_diagnosis_complete=False,
            management_complete=False,
            investigations_complete=False,
            registration_total_expected_fields=3,
            registration_total_completed_fields=0,
            first_paediatric_assessment_total_expected_fields=0,
            first_paediatric_assessment_total_completed_fields=0,
            assessment_total_expected_fields=0,
            assessment_total_completed_fields=0,
            epilepsy_context_total_expected_fields=0,
            epilepsy_context_total_completed_fields=0,
            multiaxial_diagnosis_total_expected_fields=0,
            multiaxial_diagnosis_total_completed_fields=0,
            investigations_total_expected_fields=0,
            investigations_total_completed_fields=0,
            management_total_expected_fields=0,
            management_total_completed_fields=0,
        )

@pytest.fixture()
def example_case():
    return Case.objects.first()

@pytest.fixture()
def example_lead_organisation(example_case):
    return Site.objects.create(
            case=example_case,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
        )

@pytest.fixture()
def example_kpi():
    return KPI.objects.create(
 
            organisation=lead_organisation.organisation,
            parent_trust=lead_organisation.organisation.ParentOrganisation_OrganisationName,
            paediatrician_with_expertise_in_epilepsies=0,
            epilepsy_specialist_nurse=0,
            tertiary_input=0,
            epilepsy_surgery_referral=0,
            ecg=0,
            mri=0,
            assessment_of_mental_health_issues=0,
            mental_health_support=0,
            sodium_valproate=0,
            comprehensive_care_planning_agreement=0,
            patient_held_individualised_epilepsy_document=0,
            patient_carer_parent_agreement_to_the_care_planning=0,
            care_planning_has_been_updated_when_necessary=0,
            comprehensive_care_planning_content=0,
            parental_prolonged_seizures_care_plan=0,
            water_safety=0,
            first_aid=0,
            general_participation_and_risk=0,
            service_contact_details=0,
            sudep=0,
            school_individual_healthcare_plan=0,
        )
"""  
@pytest.mark.django_db
def test_registration(e12Case):
    """
    Tests for the registration model.
    
    """
    
    
    print(f"{e12Case = }")
    
    
    