"""Factory fn to create new E12 Multiaxial diagnoses, related to a created Case.
"""
# standard imports

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    MultiaxialDiagnosis,
    EpilepsyCauseEntity,
)
from .E12EpisodeFactory import E12EpisodeFactory
from .E12SyndromeFactory import E12SyndromeFactory
from .E12ComorbidityFactory import E12ComorbidityFactory
from epilepsy12.general_functions import (
    fetch_ecl,
)
from epilepsy12.constants import (
    EPILEPSY_CAUSES,
    NEUROPSYCHIATRIC,
)


class E12MultiaxialDiagnosisFactory(factory.django.DjangoModelFactory):
    """Defaults:
    syndrome_present: True
    epilepsy_cause_known: True
    epilepsy_cause_categories: ['Gen']
    relevant_impairments_behavioural_educational: True
    global_developmental_delay_or_learning_difficulties: False
    global_developmental_delay_or_learning_difficulties_severity: None
    autistic_spectrum_disorder: None
    mental_health_screen: False
    mental_health_issue_identified: True
    mental_health_issue: AxD
    
    Reverse foreign keys (created automatically on instantiation of this object):
        - comorbidity 
        - syndrome 
        - episode 
    """
    class Meta:
        model = MultiaxialDiagnosis

    # Once Registration instance made, it will attach to this instance
    registration = None

    epilepsy_cause_known = True
    epilepsy_cause_categories = [EPILEPSY_CAUSES[0][0]]  # Genetic
    
    global_developmental_delay_or_learning_difficulties = False

    @factory.lazy_attribute
    def epilepsy_cause(self):
        ecl = "<< 363235000"
        epilepsy_causes = fetch_ecl(ecl)
        return EpilepsyCauseEntity.objects.filter(
            conceptId=epilepsy_causes[0]["conceptId"]
        ).first()

    relevant_impairments_behavioural_educational = True
    # Reverse dependency
    comorbidity = factory.RelatedFactory(
        E12ComorbidityFactory,
        factory_related_name="multiaxial_diagnosis",
    )

    syndrome_present = True
    # Reverse dependency
    syndrome_entity = factory.RelatedFactory(
        E12SyndromeFactory,
        factory_related_name="multiaxial_diagnosis",
    )

    # Reverse dependency, see docstrings for available flags to change default values
    episode = factory.RelatedFactory(
        E12EpisodeFactory,
        factory_related_name="multiaxial_diagnosis",
    )

    mental_health_issue_identified = True
    mental_health_issue = NEUROPSYCHIATRIC[0][0]  # anx disorder
    mental_health_screen = False
