"""Factory fn to create new E12 Comorbidity, related to a created Registration.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Comorbidity,
)


class E12ComorbidityFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12MaDFactory.
    
    This Factory is generated AFTER a E12MaDFactory generated.

    """
    class Meta:
        model = Comorbidity
    
    # Once MultiaxialDiagnosis instance made, it will attach to this instance
    multiaxial_diagnosis = None
    
    
    
    