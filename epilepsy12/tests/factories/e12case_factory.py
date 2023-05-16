import datetime

import pytest
import factory
from pytest_factoryboy import register

from epilepsy12.models import Case, Organisation, Site

class E12SiteFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Sites"""

    class Meta:
        model = Site
    
    # define many to many relationship
    organisation=factory.LazyFunction(lambda: Organisation.objects.filter(ODSCode="RP401").first())
    
    site_is_actively_involved_in_epilepsy_care=True
    site_is_primary_centre_of_epilepsy_care=True


class E12CaseFactory(factory.django.DjangoModelFactory):
    """Factory fn to create new E12 Cases"""

    class Meta:
        model = Case

    nhs_number = "4799637827"
    first_name = "Thomas"
    surname = factory.Sequence(lambda n: f"Anderson-{n}") # Anderson-1, Anderson-2, ...
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
