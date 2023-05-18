"""Factory fn to create new E12 Sites

A new site is create automatically once `E12CaseFactory.create()` is called.
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    FirstPaediatricAssessment
)
from .E12RegistrationFactory import E12RegistrationFactory

class E12FirstPaediatricAssessmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = FirstPaediatricAssessment
    
    registration = factory.SubFactory(E12RegistrationFactory)
    first_paediatric_assessment_in_acute_or_nonacute_setting=True
    has_number_of_episodes_since_the_first_been_documented=True
    general_examination_performed=True
    neurological_examination_performed=True
    developmental_learning_or_schooling_problems=True
    behavioural_or_emotional_problems=True