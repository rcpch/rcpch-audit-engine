from typing import Literal
import json

# django
from django.core.serializers import serialize

# third party
from epilepsy12.models import (
    NHSEnglandRegionBoundaries,
    IntegratedCareBoardBoundaries,
    CountryBoundaries,
    LocalHealthBoardBoundaries,
)


def return_tile_for_region(
    abstraction_level: Literal["icb", "nhs_region", "lhb", "country"]
):
    """
    Returns geojson data for a given region.
    """

    model = IntegratedCareBoardBoundaries

    if abstraction_level == "nhs_region":
        model = NHSEnglandRegionBoundaries
    elif abstraction_level == "country":
        model = CountryBoundaries
    elif abstraction_level == "lhb":
        model = LocalHealthBoardBoundaries

    unedited_tile = serialize("geojson", model.objects.all())
    edited_tile = json.loads(unedited_tile)
    edited_tile.pop("crs", None)
    tile = json.dumps(edited_tile)

    return tile
