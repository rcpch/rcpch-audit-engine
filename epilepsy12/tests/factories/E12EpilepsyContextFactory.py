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
    