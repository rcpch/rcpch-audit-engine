"""Factory fn to create new E12 Multiaxial diagnoses, related to a created Case.
"""
# standard imports


# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    MultiaxialDiagnosis
)

class E12MultiaxialDiagnosisFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = MultiaxialDiagnosis
    
    