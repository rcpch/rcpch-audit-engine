"""Factory fn to create new E12 Multiaxial diagnoses, related to a created Case.
"""
# standard imports

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    MultiaxialDiagnosis,
    SyndromeEntity,
)
from .E12EpisodeFactory import E12EpisodeFactory
from epilepsy12.constants import SYNDROMES

class E12MultiaxialDiagnosisFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = MultiaxialDiagnosis
    
    # Once Registration instance made, it will attach to this instance
    registration = None
    
    syndrome_present = False
    epilepsy_cause_known = False
    relevant_impairments_behavioural_educational = False
    mental_health_screen = False
    mental_health_issue_identified = False
    
    # Reverse dependencies, see docstrings for available flags to change default values
    episode = factory.RelatedFactory(
        E12EpisodeFactory,
        factory_related_name = 'multiaxial_diagnosis',
    )
    