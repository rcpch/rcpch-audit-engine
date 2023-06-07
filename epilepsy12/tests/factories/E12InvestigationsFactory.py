"""Factory fn to create new E12 Investigations, related to a created Registration.
"""
# standard imports

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Investigations
)

class E12InvestigationsFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Investigations.
    
    This Factory is generated AFTER a Registration is created.
    
    
    """
    class Meta:
        model = Investigations
    
    # Once Registration instance made, it will attach to this instance
    registration = None
    
    class Params:
        pass_ecg = factory.Trait(
            twelve_lead_ecg_status = True,
        )
        fail_ecg = factory.Trait(
            twelve_lead_ecg_status = False,
        )