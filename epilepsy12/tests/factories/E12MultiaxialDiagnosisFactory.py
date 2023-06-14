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

    class Meta:
        model = MultiaxialDiagnosis

    # Once Registration instance made, it will attach to this instance
    registration = None

    # Reverse dependency
    # comorbidity = factory.RelatedFactory(
    #     E12ComorbidityFactory,
    #     factory_related_name="multiaxial_diagnosis",
    # )
    
    # Reverse dependency
    syndrome_entity = factory.RelatedFactory(
        E12SyndromeFactory,
        factory_related_name="multiaxial_diagnosis",
    )

    # Reverse dependency
    episode = factory.RelatedFactory(
        E12EpisodeFactory,
        factory_related_name="multiaxial_diagnosis",
    )
    
    class Params:
        ineligible_mri = factory.Trait(
            syndrome_present=True,
        )
    