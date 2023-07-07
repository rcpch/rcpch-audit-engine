"""Factory fn to create new E12 Cases"""
# standard imports
from datetime import date

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Case
from .E12SiteFactory import E12SiteFactory
from .E12RegistrationFactory import E12RegistrationFactory
from epilepsy12.constants import VALID_NHS_NUMS, SEX_TYPE
from epilepsy12.general_functions import generate_nhs_number


class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory for making E12 Cases, with all associated models (with answers as model-defined defaults, usually None). As default values should be none, KPIs should be 'NOT_SCORED' if no specific flags are passed.

    Using FactoryBoy factories, Traits can be set on related factories, directly on creation of this e12_user_factory.

    Using the KPIMetric class, we take advantage of traits to generate completed audits which pass | fail specified KPIs. Please see CreateKPIMetrics module for full details.
    """

    class Meta:
        model = Case

    class Params:
        # helper eligibility flags to set age
        eligible_kpi_3_5_ineligible_6_8_10 = factory.Trait(
            date_of_birth=date(2022, 1, 1)  # age = 1y
        )

        eligible_kpi_6_8_10_ineligible_3_5 = factory.Trait(
            date_of_birth=date(2011, 1, 1)  # age = 12y
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
    # nhs_number = factory.Iterator(
    #     VALID_NHS_NUMS, getter=lambda nhs_num: nhs_num.replace(" ", "")
    # )
    nhs_number = generate_nhs_number()
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
