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
