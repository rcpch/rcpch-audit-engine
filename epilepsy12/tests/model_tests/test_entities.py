"""
Tests for the entities.

These should all be seeded during test db migrations.
"""

# Standard imports
import pytest


# Third party imports

# RCPCH imports
from epilepsy12.models import (
    ComorbidityEntity,
    EpilepsyCauseEntity,
    IntegratedCareBoardEntity,
    Keyword,
    MedicineEntity,
    NHSRegionEntity,
    ONSCountryEntity,
    OPENUKNetworkEntity,
    Organisation,
    SyndromeEntity,
)


@pytest.mark.parametrize(
    "entity",
    [
        ComorbidityEntity,
        EpilepsyCauseEntity,
        IntegratedCareBoardEntity,
        Keyword,
        MedicineEntity,
        NHSRegionEntity,
        ONSCountryEntity,
        OPENUKNetworkEntity,
        Organisation,
        SyndromeEntity,
    ],
)
@pytest.mark.django_db
def test_entity_exists(entity):
    assert entity.objects.exists(), f"{entity} not found in database"
