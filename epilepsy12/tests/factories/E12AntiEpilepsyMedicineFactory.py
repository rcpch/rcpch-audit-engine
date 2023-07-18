"""Factory fn to create new E12 AntiEpilepsyMedicine, related to a management.
"""
# standard imports
from datetime import timedelta

# third-party imports
import factory

# rcpch imports
from epilepsy12.models import (
    AntiEpilepsyMedicine,
    MedicineEntity,
)


class E12AntiEpilepsyMedicineFactory(factory.django.DjangoModelFactory):
    """Dependency factory for creating a minimum viable E12Management.

    This Factory is generated AFTER a Management generated.
    """

    class Meta:
        model = AntiEpilepsyMedicine

    # Once Management instance made, it will attach to this instance
    management = None

    

