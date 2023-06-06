"""Factory fn to create new E12 FPAs

NOTE: calling this factory will cause dependencies to be created automatically e.g. Registration, Case related to an Organisation.
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    FirstPaediatricAssessment
)

class E12FirstPaediatricAssessmentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = FirstPaediatricAssessment
    
    # when a registration instance created, it will attach to this instance
    registration = None
    
    first_paediatric_assessment_in_acute_or_nonacute_setting=True
    has_number_of_episodes_since_the_first_been_documented=True
    general_examination_performed=True
    neurological_examination_performed=True
    developmental_learning_or_schooling_problems=True
    behavioural_or_emotional_problems=True