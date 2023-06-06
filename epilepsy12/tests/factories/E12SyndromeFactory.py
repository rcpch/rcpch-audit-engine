"""Factory fn to create new E12 Syndromes, related to a multiaxial diagnosis.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Syndrome,
    SyndromeEntity,
)
from epilepsy12.constants import (
    SYNDROMES
)

class E12SyndromeFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12MaDFactory.
    
    This Factory is generated AFTER a E12MaDFactory generated.

    """
    class Meta:
        model = Syndrome
    
    # Once MultiaxialDiagnosis instance made, it will attach to this instance
    multiaxial_diagnosis = None
    
    # Self-limited (familial) neonatal epilepsy
    syndrome = factory.Iterator(SyndromeEntity.objects.filter(syndrome_name=SYNDROMES[0][1]).all())
    
    # syndrome diagnosis is 365 days before registration
    @factory.lazy_attribute
    def syndrome_diagnosis_date(self): 
        return self.multiaxial_diagnosis.registration.registration_date - timedelta(days=365)
    