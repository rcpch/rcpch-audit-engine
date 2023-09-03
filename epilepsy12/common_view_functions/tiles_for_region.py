from typing import Literal
import json

# django
from django.core.serializers import serialize
from django.apps import apps

# third party
#


def return_tile_for_region(
    abstraction_level: Literal["icb", "nhs_region", "lhb", "country"]
):
    """
    Returns geojson data for a given region.
    """
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    CountryBoundaries = apps.get_model("epilepsy12", "Country")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")

    model = IntegratedCareBoard

    if abstraction_level == "nhs_region":
        model = NHSEnglandRegion
    elif abstraction_level == "country":
        model = CountryBoundaries
    elif abstraction_level == "lhb":
        model = LocalHealthBoard

    unedited_tile = serialize("geojson", model.objects.all())
    edited_tile = json.loads(unedited_tile)
    edited_tile.pop("crs", None)
    tile = json.dumps(edited_tile)

    return tile
