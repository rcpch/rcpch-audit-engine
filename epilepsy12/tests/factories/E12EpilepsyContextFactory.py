"""Factory fn to create new E12 EpilepsyContext
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    EpilepsyContext
)

class E12EpilepsyContextFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = EpilepsyContext
    
    # when a registration instance created, it will attach to this instance
    registration = None

    class Params:
        pass_ecg = factory.Trait(
            were_any_of_the_epileptic_seizures_convulsive = True,
        )
        fail_ecg = factory.Trait(
            pass_ecg = True,
        )
        ineligible_ecg = factory.Trait(
            were_any_of_the_epileptic_seizures_convulsive = False,
        )