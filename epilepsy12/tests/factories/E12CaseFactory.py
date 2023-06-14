"""Factory fn to create new E12 Cases"""
# standard imports
import datetime

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Case
from .E12SiteFactory import E12SiteFactory
from .E12RegistrationFactory import E12RegistrationFactory
from epilepsy12.constants import VALID_NHS_NUMS


class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory for making E12 Cases, with all associated models (with answers as model-defined defaults, usually None)
    
    Using FactoryBoy factories, Traits can be set on related factories, directly on creation of this e12_user_factory. To use the useful flags defined below, set the value of the flag to True, to get the required result.
    
    Example use:
    
        case = e12_case_factory.create(
            registration__assessment__fail_paediatrician_with_expertise_in_epilepsies=True,
            
            registration__assessment__pass_epilepsy_specialist_nurse=True,
        )
    
    NOTE: ONLY 1 FLAG SHOULD BE SET TRUE PER KPI (i.e. don't set KPI 1 to pass AND fail).
    

    
    Useful flags:
        - KPI 1
            - PASS: `pass_paediatrician_with_expertise_in_epilepsies`
            - FAIL: `fail_paediatrician_with_expertise_in_epilepsies`
        - KPI 2
            - PASS: `pass_epilepsy_specialist_nurse`
            - FAIL: `fail_epilepsy_specialist_nurse`
    """
    class Meta:
        model = Case

    # TODO - once Case.nhs_number has appropriate validation + cleaning, won't need to strip spaces here
    # Iterates through available valid NHS nums. Will reset from beginning once end of list is reached.
    nhs_number = factory.Iterator(VALID_NHS_NUMS, getter=lambda nhs_num: nhs_num.replace(' ',''))
    first_name = "Thomas"
    surname = "Anderson"
    sex = 1
    date_of_birth = datetime.date(2021, 9, 2)
    ethnicity = "A"
    locked = False

    # once case created, create a Site, which acts as a link table between the Case and Organisation
    organisations = factory.RelatedFactory(E12SiteFactory, factory_related_name="case")

    # reverse dependency
    registration = factory.RelatedFactory(
        E12RegistrationFactory,
        factory_related_name="case",
    )
