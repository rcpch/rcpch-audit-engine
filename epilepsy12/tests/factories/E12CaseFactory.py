"""Factory fn to create new E12 Cases"""
# standard imports
from datetime import date
from dateutil.relativedelta import relativedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Case
from .E12SiteFactory import E12SiteFactory
from .E12RegistrationFactory import E12RegistrationFactory
from epilepsy12.constants import VALID_NHS_NUMS, SEX_TYPE


class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory for making E12 Cases, with all associated models (with answers as model-defined defaults, usually None). As default values should be none, KPIs should be 'NOT_SCORED' if no specific flags are passed.

    Using FactoryBoy factories, Traits can be set on related factories, directly on creation of this e12_user_factory. To use the useful flags defined below, set the value of the flag to True, to get the required result.

    Example use:

        case = e12_case_factory.create(
            # set KPI 1 to fail
            registration__assessment__fail_paediatrician_with_expertise_in_epilepsies=True,
            # set KPI 2 to pass
            registration__assessment__pass_epilepsy_specialist_nurse=True,
        )

        NOTE: ONLY 1 FLAG SHOULD BE SET TRUE PER KPI (i.e. don't set KPI 1 to pass AND fail).

    Useful flags:

        - KPI 1
            - PASS:
                - `registration__assessment__pass_paediatrician_with_expertise_in_epilepsies`
            - FAIL:
                - `registration__assessment__fail_paediatrician_with_expertise_in_epilepsies`

        - KPI 2
            - PASS:
                - `registration__assessment__pass_epilepsy_specialist_nurse`
            - FAIL:
                - `registration__assessment__fail_epilepsy_specialist_nurse`

        - KPI 3 & 3b
            - PASS:
                - `registration__assessment__pass_tertiary_input_AND_epilepsy_surgery_referral`
            - FAIL:
                - `registration__assessment__fail_tertiary_input_AND_epilepsy_surgery_referral`
            - INELIGIBLE:
                - `registration__assessment__ineligible_tertiary_input_AND_epilepsy_surgery_referral`

        - KPI 4
            - PASS:
                - `registration__epilepsy_context__pass_ecg`
                - `registration__investigations__pass_ecg`
            - FAIL:
                - `registration__epilepsy_context__fail_ecg`
                - `registration__investigations__fail_ecg`
            - INELIGIBLE:
                - `registration__epilepsy_context__ineligible_ecg`

        - KPI 5 NOTE: please see caveats defined in KPI 6
            - PASS:
                - `registration__investigations__pass_mri`
            - FAIL:
                - `registration__investigations__fail_mri`
            - INELIGIBLE:
                - ineligible_mri
                - registration__ineligible_mri
                - registration__multiaxial_diagnosis__ineligible_mri
                - registration__multiaxial_diagnosis__syndrome_entity__ineligible_mri

        - KPI 6
            NOTE: If either PASS/FAIL flags set, KPI5 PASS/FAIL FIELDS CAN NOT BE USED. KPI6 pass/fail fields make child 6yo (age at FPA >= 5 required to be eligible for this measure). Therefore, they automatically become ineligible for KPI 5 (eligibility requires age at FPA < 2).
            - PASS:
                pass_assessment_of_mental_health_issues=True,
                registration__pass_assessment_of_mental_health_issues=True,
                registration__multiaxial_diagnosis__pass_assessment_of_mental_health_issues=True,
            - FAIL:
                fail_assessment_of_mental_health_issues=True,
                registration__fail_assessment_of_mental_health_issues=True,
                registration__multiaxial_diagnosis__fail_assessment_of_mental_health_issues=True,
            - INELIGIBLE:
                - `ineligible_assessment_of_mental_health_issues`

        - KPI 7
            - PASS:
                - `registration__multiaxial_diagnosis__pass_mental_health_support`
                - `registration__management__pass_mental_health_support`
            - FAIL:
                - `registration__multiaxial_diagnosis__fail_mental_health_support`
                - `registration__management__fail_mental_health_support`
            - INELIGIBLE:
                - `registration__multiaxial_diagnosis__ineligible_mental_health_support`
        
        - KPI 8 
            > NOTE: IF ANY OF THESE flags set, KPI5 PASS/FAIL FIELDS CAN NOT BE USED. See KPI 6 NOTE for reason (eligibility for this KPI requires age >= 12). If ineligible, age is set to fail mri, but stay eligible for KPI 6.
            - PASS:
                pass_sodium_valproate = True,
                registration__management__sodium_valproate = 'pass',
            - FAIL:
                fail_sodium_valproate = True,
                registration__management__sodium_valproate = 'fail',
            - INELIGIBLE:
                ineligible_sodium_valproate=True,
        - KPI 9
        > NOTE: as these sub-measures are all related, and flags are applied sequentially, we can only set ALL to pass or ALL to fail.
            - PASS
                registration__management__pass_kpi_9=True,
            - FAIL
            > NOTE: if fail flag set, parental_prolonged_seizures_care_plan is set to ineligible (due to is_rescue_medicine_prescribed=False)
                registration__management__fail_kpi_9=True,
        
        - KPI 10
        > NOTE: PASS/FAIL fields set KPI5 to Ineligible. See KPI6 for details. KPI 10 eligibility requires age >= 5.
            - PASS
                pass_individualised_care_plan_includes_ehcp = True,
                registration__management__pass_individualised_care_plan_includes_ehcp=True,
            - FAIL
                fail_school_individual_healthcare_plan = True,
                registration__management__fail_school_individual_healthcare_plan=True,
            - INELIGIBLE 
            > NOTE: if ineligible, sets age to 1yo, so eligible for KPI5 but ineligible for KPI6
                ineligible_individualised_care_plan_includes_ehcp=True,
                
                
    """

    class Meta:
        model = Case

    class Params:
        ineligible_mri = factory.Trait(date_of_birth=date(2017, 1, 1))

        pass_assessment_of_mental_health_issues = factory.Trait(ineligible_mri=True)
        fail_assessment_of_mental_health_issues = factory.Trait(
            pass_assessment_of_mental_health_issues=True
        )
        ineligible_assessment_of_mental_health_issues = factory.Trait(
            ineligible_mri=False, date_of_birth=date(2022, 1, 1)
        )

        pass_sodium_valproate = factory.Trait(
            ineligible_mri=True,
            date_of_birth=date(2010, 1, 1),
            sex=SEX_TYPE[2][0],
        )
        fail_sodium_valproate = factory.Trait(
           pass_sodium_valproate=True
        )
        ineligible_sodium_valproate = factory.Trait(
            ineligible_mri=True
        )
        
        pass_school_individual_healthcare_plan = factory.Trait(
            ineligible_mri=True,
        )
        fail_school_individual_healthcare_plan = factory.Trait(
            pass_school_individual_healthcare_plan=True,
        )
        ineligible_school_individual_healthcare_plan = factory.Trait( 
            ineligible_assessment_of_mental_health_issues = True,
            date_of_birth=date(2022, 1, 1),
        )
        

    # TODO - once Case.nhs_number has appropriate validation + cleaning, won't need to strip spaces here
    # Iterates through available valid NHS nums. Will reset from beginning once end of list is reached.
    nhs_number = factory.Iterator(
        VALID_NHS_NUMS, getter=lambda nhs_num: nhs_num.replace(" ", "")
    )
    first_name = "Thomas"
    surname = "Anderson"
    sex = 1

    # default date of birth (with no Params flags set) will be 2022,1,1
    date_of_birth = date(2022, 1, 1)

    ethnicity = "A"
    locked = False

    # once case created, create a Site, which acts as a link table between the Case and Organisation
    organisations = factory.RelatedFactory(E12SiteFactory, factory_related_name="case")

    # reverse dependency
    registration = factory.RelatedFactory(
        E12RegistrationFactory,
        factory_related_name="case",
    )
