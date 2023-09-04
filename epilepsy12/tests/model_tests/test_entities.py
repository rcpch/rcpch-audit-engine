"""
Tests for the entities.

These should all be seeded during test db migrations.
"""

# Standard imports
import pytest


# Third party imports

# RCPCH imports
from epilepsy12.models import (
    ComorbidityList,
    EpilepsyCause,
    SyndromeList,
    Keyword,
    Medicine,
    Organisation,
    Trust,
    IntegratedCareBoard,
    NHSEnglandRegion,
    OPENUKNetwork,
    Country,
)


@pytest.mark.parametrize(
    "entity",
    [
        ComorbidityList,
        EpilepsyCause,
        SyndromeList,
        Keyword,
        Medicine,
        Organisation,
        Trust,
        IntegratedCareBoard,
        NHSEnglandRegion,
        OPENUKNetwork,
        Country,
    ],
)
@pytest.mark.django_db
def test_entity_exists(entity):
    assert entity.objects.exists(), f"{entity} not found in database"
