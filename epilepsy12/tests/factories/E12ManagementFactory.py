"""Factory fn to create new E12 Management, related to a created Registration.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import Management
from .E12AntiEpilepsyMedicineFactory import E12AntiEpilepsyMedicineFactory

from epilepsy12.models import (
    MedicineEntity,
)

class E12ManagementFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Management.

    This Factory is generated AFTER a Registration is created.

    Default:
        - aed will be sodium valproate, with pregnancy fields automatically filled as True if childbearing age girl
    """

    class Meta:
        model = Management

    # Once Registration instance made, it will attach to this instance
    registration = None

    class Params:
        pass_mental_health_support = factory.Trait(
            has_support_for_mental_health_support = True
        )
        fail_mental_health_support = factory.Trait(
            has_support_for_mental_health_support = False
        )
