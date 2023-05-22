"""Factory fn to create new E12 Multiaxial diagnoses, related to a created Case.
"""
# standard imports

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    MultiaxialDiagnosis,
)
from .E12EpisodeFactory import E12EpisodeFactory

class E12MultiaxialDiagnosisFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = MultiaxialDiagnosis
    
    # Once Registration instance made, it will attach to this instance
    registration = None
    
    # Reverse dependencies, see docstrings for available flags to change default values
    episode = factory.RelatedFactory(
        E12EpisodeFactory,
        factory_related_name = 'multiaxial_diagnosis',
    )
    