from django.db import migrations
from django.apps import apps as django_apps

import os
from django.contrib.gis.utils import LayerMapping

"""
Levels of abstraction relate to the regions within which a trust sits.
This migration seeds those levels of abstraction for which a boundary file exists for mapping.
These include:
Health regions:
 - ICB (if in England)
 - Local Health Board (if in Wales)
 - NHS England region (if in England)
Administrative regions
 - London borough (if in London)
 - Country
"""

integratedcareboardboundaries_mapping = {
    "boundary_identifier": "ICB23CD",
    "name": "ICB23NM",
    "bng_e": "BNG_E",
    "bng_n": "BNG_N",
    "long": "LONG",
    "lat": "LAT",
    "globalid": "GlobalID",
    "geom": "MULTIPOLYGON",
}

localhealthboardboundaries_mapping = {
    "boundary_identifier": "LHB22CD",
    "name": "LHB22NM",
    "lhb22nmw": "LHB22NMW",
    "bng_e": "BNG_E",
    "bng_n": "BNG_N",
    "long": "LONG",
    "lat": "LAT",
    "globalid": "GlobalID",
    "geom": "MULTIPOLYGON",
}

nhsenglandregionboundaries_mapping = {
    "boundary_identifier": "NHSER22CD",
    "name": "NHSER22NM",
    "bng_e": "BNG_E",
    "bng_n": "BNG_N",
    "long": "LONG",
    "lat": "LAT",
    "globalid": "GlobalID",
    "geom": "MULTIPOLYGON",
}

londonborough_mapping = {
    "name": "NAME",
    "gss_code": "GSS_CODE",
    "hectares": "HECTARES",
    "nonld_area": "NONLD_AREA",
    "ons_inner": "ONS_INNER",
    "sub_2009": "SUB_2009",
    "sub_2006": "SUB_2006",
    "geom": "MULTIPOLYGON",
}

countryboundaries_mapping = {
    "boundary_identifier": "CTRY22CD",
    "name": "CTRY22NM",
    "ctry22nmw": "CTRY22NMW",
    "bng_e": "BNG_E",
    "bng_n": "BNG_N",
    "long": "LONG",
    "lat": "LAT",
    "globalid": "GlobalID",
    "geom": "MULTIPOLYGON",
}


# Boundary files

app_config = django_apps.get_app_config("epilepsy12")
app_path = app_config.path

Countries_December_2022_UK_BUC = os.path.join(
    app_path,
    "shape_files",
    "Countries_December_2022_UK_BUC",
    "CTRY_DEC_2022_UK_BUC.shp",
)

Integrated_Care_Boards_April_2023_EN_BSC = os.path.join(
    app_path,
    "shape_files",
    "Integrated_Care_Boards_April_2023_EN_BSC",
    "ICB_APR_2023_EN_BSC.shp",
)

Local_Health_Boards_April_2022_WA_BUC_2022 = os.path.join(
    app_path,
    "shape_files",
    "Local_Health_Boards_April_2022_WA_BUC_2022",
    "LHB_APR_2022_WA_BUC.shp",
)

London_Borough_Boundary_File = os.path.join(
    app_path, "shape_files", "London_Boroughs", "London_Borough_Excluding_MHW.shp"
)

NHS_England_Regions_July_2022_EN_BUC_2022 = os.path.join(
    app_path,
    "shape_files",
    "NHS_England_Regions_July_2022_EN_BUC_2022",
    "NHSER_JUL_2022_EN_BUC.shp",
)


def load(apps, schema_editor, verbose=True):
    LondonBorough = apps.get_model("epilepsy12", "LondonBorough")
    lm = LayerMapping(
        LondonBorough,
        London_Borough_Boundary_File,
        londonborough_mapping,
        transform=False,
        encoding="utf-8",
    )
    lm.save(strict=True, verbose=verbose)

    Country = apps.get_model("epilepsy12", "Country")
    lm = LayerMapping(
        Country,
        Countries_December_2022_UK_BUC,
        countryboundaries_mapping,
        transform=False,
        encoding="utf-8",
    )
    lm.save(strict=True, verbose=verbose)

    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    lm = LayerMapping(
        IntegratedCareBoard,
        Integrated_Care_Boards_April_2023_EN_BSC,
        integratedcareboardboundaries_mapping,
        transform=False,
        encoding="utf-8",
    )
    lm.save(strict=True, verbose=verbose)

    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    lm = LayerMapping(
        LocalHealthBoard,
        Local_Health_Boards_April_2022_WA_BUC_2022,
        localhealthboardboundaries_mapping,
        transform=False,
        encoding="utf-8",
    )
    lm.save(strict=True, verbose=verbose)

    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    lm = LayerMapping(
        NHSEnglandRegion,
        NHS_England_Regions_July_2022_EN_BUC_2022,
        nhsenglandregionboundaries_mapping,
        transform=False,
        encoding="utf-8",
    )
    lm.save(strict=True, verbose=verbose)


class Migration(migrations.Migration):
    dependencies = [
        ("epilepsy12", "0001_initial"),
    ]

    operations = [migrations.RunPython(load)]
