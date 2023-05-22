"""Factory fn to create new E12 Multiaxial diagnoses, related to a created Case.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    Comorbidity,
    ComorbidityEntity,
)
from epilepsy12.general_functions import (
    fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set,
)

class E12ComorbidityFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12MaDFactory.
    
    This Factory is generated AFTER a E12MaDFactory generated.

    """
    class Meta:
        model = Comorbidity
    
    # Once MultiaxialDiagnosis instance made, it will attach to this instance
    multiaxial_diagnosis = None
    
    # comorbidity diagnosis date is 365 days before registration
    @factory.lazy_attribute
    def comorbidity_diagnosis_date(self): 
        return self.multiaxial_diagnosis.registration.registration_date - timedelta(days=365)
    
    @factory.lazy_attribute
    def comorbidityentity(self):
        comorbidity_choices = (fetch_paediatric_neurodisability_outpatient_diagnosis_simple_reference_set())
        return ComorbidityEntity.objects.filter(conceptId=comorbidity_choices[0]["conceptId"]).first()
    
    
    