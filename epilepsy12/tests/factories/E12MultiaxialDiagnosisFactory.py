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
