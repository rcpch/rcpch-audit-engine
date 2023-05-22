"""
Factories for creating test data for epilepsy12 app
"""
# standard imports
import datetime

# third-party imports
import pytest
import factory
from django.contrib.auth import get_user_model

# rcpch imports
from epilepsy12.models import (
    Case,
    Organisation,
    Site,
    Registration,
    AuditProgress,
    KPI,
)
from epilepsy12.constants import user_types, VALID_NHS_NUMS


class E12AuditProgressFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 AuditProgress"""

    class Meta:
        model = AuditProgress

    registration_complete = False
    first_paediatric_assessment_complete = False
    assessment_complete = False
    epilepsy_context_complete = False
    multiaxial_diagnosis_complete = False
    management_complete = False
    investigations_complete = False
    registration_total_expected_fields = 3
    registration_total_completed_fields = 0
    first_paediatric_assessment_total_expected_fields = 0
    first_paediatric_assessment_total_completed_fields = 0
    assessment_total_expected_fields = 0
    assessment_total_completed_fields = 0
    epilepsy_context_total_expected_fields = 0
    epilepsy_context_total_completed_fields = 0
    multiaxial_diagnosis_total_expected_fields = 0
    multiaxial_diagnosis_total_completed_fields = 0
    investigations_total_expected_fields = 0
    investigations_total_completed_fields = 0
    management_total_expected_fields = 0
    management_total_completed_fields = 0


class E12SiteFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Sites

    A new site is create automatically once `E12CaseFactory.create()` is called.
    """

    class Meta:
        model = Site

    # define many to many relationship
    organisation = factory.LazyFunction(
        lambda: Organisation.objects.filter(ODSCode="RP401").first()
    )

    site_is_actively_involved_in_epilepsy_care = True
    site_is_primary_centre_of_epilepsy_care = True
        

class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Cases"""

    class Meta:
        model = Case

    # TODO - once Case.nhs_number has appropriate validation + cleaning, won't need to strip spaces here
    nhs_number = factory.Sequence(lambda n: VALID_NHS_NUMS[n].replace(' ','')) 
    first_name = "Thomas"
    surname = factory.Sequence(lambda n: f"Anderson-{n}")  # Anderson-1, Anderson-2, ...
    sex = 1
    date_of_birth = datetime.date(1964, 9, 2)
    ethnicity = "A"
    locked = False

    @factory.post_generation
    def organisations(self, create, extracted, **kwargs):
        if not create:
            # factory NOT called with .create() method
            return

        E12SiteFactory.create(case=self)


class E12RegistrationFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Registrations"""

    class Meta:
        model = Registration

    # Sets the minimal 'required' fields for a registration to be valid
    registration_date = datetime.date(2023, 1, 1)
    eligibility_criteria_met = True
    case = factory.SubFactory(E12CaseFactory)
    audit_progress = factory.SubFactory(E12AuditProgressFactory)
    
    # Getting the KPI organisation requires a more complex operation so we use the .lazy_attribute decorator. Once a Registration is .create()'d, filter Sites using the related Case to find the lead organisation - which is used to generate the kpi model. 
    @factory.lazy_attribute
    def kpi(self):
        lead_organisation = Site.objects.filter(
            case=self.case,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
        ).get()
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

class E12UserFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Users"""

    class Meta:
        model = get_user_model() # returns the Epilepsy12User object

    email = factory.Sequence(lambda n: f"e12_test_user_{n}@rcpch.com")
    password = "password"
    first_name = "Mandel"
    surname = "Brot"
    is_active = True
    is_staff = True
    is_rcpch_audit_team_member = True
    is_superuser = False
    role = user_types.AUDIT_CENTRE_LEAD_CLINICIAN
    email_confirmed = True
    organisation_employer = factory.LazyFunction(
        lambda: Organisation.objects.filter(ODSCode="RP401").first()
    ) 