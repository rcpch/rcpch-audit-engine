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
                registration__assessment__pass_paediatrician_with_expertise_in_epilepsies=True
            - FAIL:
                registration__assessment__fail_paediatrician_with_expertise_in_epilepsies=True

        - KPI 2
            - PASS:
                registration__assessment__pass_epilepsy_specialist_nurse=True
            - FAIL:
                registration__assessment__fail_epilepsy_specialist_nurse=True

        - KPI 3 + 5 ELIGIBILITY FLAG
        > NOTE: Due to eligibility reasons, KPI3+5 eligible only when age is 1y (<2y), KPI 6+8+10 only eligible when age is 12y(>=12y).
            eligible_kpi_3_5_ineligible_6_8_10=True,
        
        - KPI 3 & 3b > NOTE: IF either PASS/FAIL flags set here, eligible_kpi_3_5_ineligible_6_8_10 must be used!
            - PASS:
                registration__assessment__pass_tertiary_input_AND_epilepsy_surgery_referral=True,
            - FAIL:
                registration__assessment__fail_tertiary_input_AND_epilepsy_surgery_referral=True,

        - KPI 4
            - PASS:
                registration__epilepsy_context__pass_ecg=True,
                registration__investigations__pass_ecg=True,
            - FAIL:
                registration__epilepsy_context__fail_ecg=True,
                registration__investigations__fail_ecg=True,
            - INELIGIBLE:
                registration__epilepsy_context__ineligible_ecg=True,

        - KPI 5 > NOTE: IF either PASS/FAIL flags set here, eligible_kpi_3_5_ineligible_6_8_10 must be used!
            - PASS:
                registration__investigations__pass_mri=True,
            - FAIL:
                registration__investigations__fail_mri=True,

        - KPI 6
            > NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
            - PASS:
                pass_assessment_of_mental_health_issues=True,
                registration__pass_assessment_of_mental_health_issues=True,
                registration__multiaxial_diagnosis__pass_assessment_of_mental_health_issues=True,
            - FAIL:
                fail_assessment_of_mental_health_issues=True,
                registration__fail_assessment_of_mental_health_issues=True,
                registration__multiaxial_diagnosis__fail_assessment_of_mental_health_issues=True,

        - KPI 7
            - PASS:
                registration__multiaxial_diagnosis__pass_mental_health_support=True,
                registration__management__pass_mental_health_support=True,
            - FAIL:
                registration__multiaxial_diagnosis__fail_mental_health_support=True,
                registration__management__fail_mental_health_support=True,
            - INELIGIBLE:
                registration__multiaxial_diagnosis__ineligible_mental_health_support=True,
        
        - KPI 8 
            > NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
            - PASS:
                pass_sodium_valproate = True,
                registration__management__sodium_valproate = 'pass',
            - FAIL:
                fail_sodium_valproate = True,
                registration__management__sodium_valproate = 'fail',
                
        - KPI 9
        > NOTE: as these sub-measures are all related, and flags are applied sequentially, we can only set ALL to pass or ALL to fail.
            - PASS
                registration__management__pass_kpi_9=True,
            - FAIL
            > NOTE: if fail flag set, parental_prolonged_seizures_care_plan is set to ineligible (due to is_rescue_medicine_prescribed=False)
                registration__management__fail_kpi_9=True,
        
        - KPI 10
        > NOTE: NOTE: If either PASS/FAIL flags set here, must use flag eligible_kpi_6_8_10_ineligible_3_5.
            - PASS
                pass_school_individual_healthcare_plan = True,
                registration__management__pass_school_individual_healthcare_plan=True,
            - FAIL
                fail_school_individual_healthcare_plan = True,
                registration__management__fail_school_individual_healthcare_plan=True,

    """

    class Meta:
        model = Case

    class Params:
        
        # helper eligibility flags to set age
        eligible_kpi_3_5_ineligible_6_8_10 = factory.Trait(
            date_of_birth = date(2021, 1, 1) # age = 1y
        )
        
        eligible_kpi_6_8_10_ineligible_3_5= factory.Trait(
            date_of_birth=date(2011, 1, 1)# age = 12y
            )

        pass_assessment_of_mental_health_issues = factory.Trait(
            eligible_kpi_6_8_10_ineligible_3_5=True,
            )
        fail_assessment_of_mental_health_issues = factory.Trait(
            pass_assessment_of_mental_health_issues=True
        )

        pass_sodium_valproate = factory.Trait(
            eligible_kpi_6_8_10_ineligible_3_5=True,
            sex=SEX_TYPE[2][0],
        )
        fail_sodium_valproate = factory.Trait(
           pass_sodium_valproate=True,
        )
        
        pass_school_individual_healthcare_plan = factory.Trait(
            eligible_kpi_6_8_10_ineligible_3_5=True,
        )
        fail_school_individual_healthcare_plan = factory.Trait(
            pass_school_individual_healthcare_plan=True,
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
