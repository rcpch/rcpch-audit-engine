"""Factory fn to create new E12 Cases"""

# standard imports
from datetime import date

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Case
from .E12SiteFactory import E12SiteFactory
from .E12RegistrationFactory import E12RegistrationFactory
from epilepsy12.constants import SEX_TYPE, DEPRIVATION_QUINTILES
import nhs_number as nhs_number_package


def nhs_number_not_yet_in_db():
    not_found_unique_nhs_num = True

    while not_found_unique_nhs_num:
        candidate_num = nhs_number_package.generate()[0]

        if not Case.objects.filter(nhs_number=candidate_num).exists():
            not_found_unique_nhs_num = False

    return candidate_num

def unique_urn_not_yet_in_db():
    num = Case.objects.count() + 1
    return f"JERSEY-{num}"


class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory for making E12 Cases, with all associated models (with answers as model-defined defaults, usually None). As default values should be none, KPIs should be 'NOT_SCORED' if no specific flags are passed.

    Using FactoryBoy factories, Traits can be set on related factories, directly on creation of this e12_user_factory.

    Using the KPIMetric class, we take advantage of traits to generate completed audits which pass | fail specified KPIs. Please see CreateKPIMetrics module for full details.
    """

    class Meta:
        model = Case
        skip_postgeneration_save = True

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
        seed_male = factory.Trait(
            first_name="Agent",
            surname=factory.Sequence(lambda n: f"Smith-{n}"),
            registration=None,
        )
        seed_female = factory.Trait(
            first_name="Dolly",
            surname=factory.Sequence(lambda n: f"Shepard-{n}"),
            registration=None,
        )

        is_jersey = factory.Trait(
            nhs_number=None,
            unique_reference_number=factory.LazyFunction(unique_urn_not_yet_in_db),
        )

    @factory.lazy_attribute
    def nhs_number(self):
        return nhs_number_not_yet_in_db()

    first_name = "Thomas"
    surname = "Anderson"
    sex = 1

    # default date of birth (with no Params flags set) will be 2022,1,1
    date_of_birth = date(2022, 1, 1)

    ethnicity = "A"
    index_of_multiple_deprivation_quintile = DEPRIVATION_QUINTILES.first
    locked = False

    # once case created, create a Site, which acts as a link table between the Case and Organisation
    organisations = factory.RelatedFactory(E12SiteFactory, factory_related_name="case")

    # reverse dependency
    registration = factory.RelatedFactory(
        E12RegistrationFactory,
        factory_related_name="case",
    )
