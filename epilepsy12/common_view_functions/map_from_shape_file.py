# python imports
from datetime import date
import json
import logging

# django imports
from django.apps import apps
from django.conf import settings

# third party imports
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go

# RCPCH imports
from ..constants import (
    RCPCH_LIGHT_BLUE,
    RCPCH_PINK,
    RCPCH_LIGHT_BLUE_TINT1,
    RCPCH_LIGHT_BLUE_TINT2,
    RCPCH_LIGHT_BLUE_TINT3,
    RCPCH_LIGHT_BLUE_DARK_TINT,
    EnumAbstractionLevel,
)
from .tiles_for_region import return_tile_for_region

logger = logging.getLogger(__name__)


def generate_case_count_choropleth_map(
    properties, organisation, abstraction_level, cohort
):
    """
    Generates a Plotly Choropleth map from GeoJSON data.
    Accepts the geojson data as a string, the properties key to use as the identifier, and the cohort.
    """
    px.set_mapbox_access_token(settings.MAPBOX_API_KEY)

    region_tile = region_tile_for_abstraction_level(
        abstraction_level=abstraction_level, organisation=organisation
    )

    geojson_data = json.loads(region_tile)
    features = geojson_data["features"]
    abstraction_level_ids = [feature["properties"][properties] for feature in features]
    abstraction_level_names = [feature["properties"]["name"] for feature in features]
    custom_colorscale = [
        [0, RCPCH_LIGHT_BLUE_TINT3],  # Very light blue
        [0.25, RCPCH_LIGHT_BLUE_TINT2],  # Light blue
        [0.5, RCPCH_LIGHT_BLUE_TINT1],  # Medium light blue
        [0.75, RCPCH_LIGHT_BLUE],  # blue
        [1, RCPCH_LIGHT_BLUE_DARK_TINT],  # Dark blue
    ]

    dataframe = generate_case_counts_for_each_region_in_each_abstraction_level(
        abstraction_level=abstraction_level, cohort=cohort, organisation=organisation
    )

    # Create a Plotly map using the GeoJSON data, data, and color data
    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=geojson_data,
            locations=abstraction_level_ids,
            featureidkey=f"properties.{properties}",
            z=dataframe["cases"],
            colorscale=custom_colorscale,
            marker_line_width=1,  # Set the width of the boundaries
            marker_line_color=RCPCH_LIGHT_BLUE,  # Set the color of the boundaries
            customdata=abstraction_level_names,
            hovertemplate="<b>%{customdata}</b><br>cases: %{z}<extra></extra>",  # Custom hovertemplate
        )
    )

    # centre the map on the lead organisation
    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_center={
            "lat": organisation.latitude,
            "lon": organisation.longitude,
        },
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=16,
            font_family="Montserrat-Regular",
        ),
        font=dict(family="Montserrat-Regular", size=12, color="black"),
    )

    # Make hover label pink and montserrat
    fig.update_traces(
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=16,
            font_family="Montserrat-Regular",
        )
    )

    # Add a layer for the region to highlight
    if abstraction_level == EnumAbstractionLevel.NHS_ENGLAND_REGION:
        identifier = "nhs_england_region"
        custom_zoom = 6
    elif abstraction_level == EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        identifier = "local_health_board"
        custom_zoom = 7
    elif abstraction_level == EnumAbstractionLevel.ICB:
        identifier = "integrated_care_board"
        custom_zoom = 7
    elif abstraction_level == EnumAbstractionLevel.COUNTRY:
        identifier = "country"
        custom_zoom = 5
    elif abstraction_level == EnumAbstractionLevel.TRUST:
        identifier = "trust"
        custom_zoom = 8
    else:
        identifier = None

    # Highlight the region of the organisation by colouring the region boundary in a pink colour
    organisation_region = getattr(organisation, identifier)
    organisation_region_identifier = getattr(organisation_region, properties)

    highlighted_region = dataframe[
        dataframe["identifier"] == organisation_region_identifier
    ]

    fig.add_trace(
        go.Choroplethmapbox(
            geojson=geojson_data,
            locations=highlighted_region["identifier"],
            marker_line_color=RCPCH_PINK,  # Set the outline color
            marker_line_width=3,  # Set the outline width
        )
    )

    # Add a scatterplot point for the organization
    fig.add_trace(
        go.Scattermapbox(
            lat=[organisation.latitude],
            lon=[organisation.longitude],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=12,
                color=RCPCH_PINK,  # Set the color of the point
            ),
            text=[organisation.name],  # Set the hover text for the point
            hovertemplate="%{text}<extra></extra>",  # Custom hovertemplate
        )
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, mapbox_zoom=custom_zoom)

    # Convert the Plotly figure to JSON
    return pio.to_json(fig)


def generate_case_counts_for_each_region_in_each_abstraction_level(
    abstraction_level: EnumAbstractionLevel, cohort: int, organisation
):
    """
    Returns a dataframe of all case counts, for a given cohort, in all members of a given abstraction_level.
    The member of the level of abstraction where the organisation is a child is flagged in the result
    """

    Case = apps.get_model("epilepsy12", "Case")
    Organisation = apps.get_model("epilepsy12", "Organisation")

    # Create a new DataFrame to store the results
    df = pd.DataFrame(columns=["identifier", "name", "cases"])

    level_abstraction_members, identifier = all_level_of_abstraction_members(
        abstraction_level=abstraction_level
    )

    for member in level_abstraction_members:
        list_of_organisations_within_member = (
            all_organisations_within_a_level_of_abstraction(
                abstraction_level=abstraction_level, abstraction_level_member=member
            )
        )
        # Get all cases for the organisation
        all_registered_completed_cases = Case.objects.filter(
            site__organisation__in=list_of_organisations_within_member,
            site__site_is_actively_involved_in_epilepsy_care=True,
            site__site_is_primary_centre_of_epilepsy_care=True,
            registration__cohort=cohort,
            registration__completed_first_year_of_care_date__lte=date.today(),
            registration__audit_progress__registration_complete=True,
            registration__audit_progress__first_paediatric_assessment_complete=True,
            registration__audit_progress__assessment_complete=True,
            registration__audit_progress__epilepsy_context_complete=True,
            registration__audit_progress__multiaxial_diagnosis_complete=True,
            registration__audit_progress__investigations_complete=True,
            registration__audit_progress__management_complete=True,
        ).count()

        # Append a new row to the DataFrame
        df = pd.concat(
            [
                df,
                pd.DataFrame(
                    [
                        {
                            "identifier": getattr(member, identifier),
                            "name": getattr(member, "name"),
                            "cases": all_registered_completed_cases,
                        }
                    ]
                ),
            ],
            ignore_index=True,
        )

    return df


# Helper functions
def all_level_of_abstraction_members(abstraction_level: EnumAbstractionLevel):
    """
    Returns all members of a given level of abstraction and the identifier for the level
    """
    # get lists of all members of each level of abstraction
    Trust = apps.get_model("epilepsy12", "Trust")
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    Country = apps.get_model("epilepsy12", "Country")

    if abstraction_level == EnumAbstractionLevel.TRUST:
        level_abstraction_members = Trust.objects.filter(active=True).order_by("name")
        identifier = "ods_code"
    elif abstraction_level == EnumAbstractionLevel.ICB:
        level_abstraction_members = IntegratedCareBoard.objects.all().order_by("name")
        identifier = "ods_code"
    elif abstraction_level == EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        level_abstraction_members = LocalHealthBoard.objects.all().order_by("name")
        identifier = "ods_code"
    elif abstraction_level == EnumAbstractionLevel.NHS_ENGLAND_REGION:
        level_abstraction_members = NHSEnglandRegion.objects.all().order_by("name")
        identifier = "region_code"
    elif abstraction_level == EnumAbstractionLevel.COUNTRY:
        level_abstraction_members = Country.objects.all().order_by("name")
        identifier = "boundary_identifier"
    else:  # pragma: no cover
        raise ValueError("Invalid abstraction level")

    return level_abstraction_members, identifier


def all_organisations_within_a_level_of_abstraction(
    abstraction_level: EnumAbstractionLevel,
    abstraction_level_member,
):
    """
    Returns all organisation members of a given level of abstraction, along with the identifier for the level
    """
    Organisation = apps.get_model("epilepsy12", "Organisation")

    level_abstraction_organisations = None
    if abstraction_level == EnumAbstractionLevel.TRUST:
        level_abstraction_organisations = Organisation.objects.filter(
            trust=abstraction_level_member, active=True
        )
    elif abstraction_level == EnumAbstractionLevel.ICB:
        level_abstraction_organisations = Organisation.objects.filter(
            integrated_care_board=abstraction_level_member, active=True
        )
    elif abstraction_level == EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        level_abstraction_organisations = Organisation.objects.filter(
            local_health_board=abstraction_level_member, active=True
        )
    elif abstraction_level == EnumAbstractionLevel.NHS_ENGLAND_REGION:
        level_abstraction_organisations = Organisation.objects.filter(
            nhs_england_region=abstraction_level_member, active=True
        )
    elif abstraction_level == EnumAbstractionLevel.COUNTRY:
        level_abstraction_organisations = Organisation.objects.filter(
            country=abstraction_level_member, active=True
        )
    else:  # pragma: no cover
        raise ValueError("Invalid abstraction level")

    return level_abstraction_organisations


def region_tile_for_abstraction_level(
    abstraction_level: EnumAbstractionLevel, organisation
):
    """
    Returns the geojson tile for a given level of abstraction
    """

    if abstraction_level == EnumAbstractionLevel.TRUST:
        region_tile = return_tile_for_region("trust")
    elif abstraction_level == EnumAbstractionLevel.ICB:
        region_tile = return_tile_for_region("icb")
    elif abstraction_level == EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        region_tile = lhb_tiles = return_tile_for_region("lhb")
    elif abstraction_level == EnumAbstractionLevel.NHS_ENGLAND_REGION:
        region_tile = return_tile_for_region("nhs_england_region")
    elif abstraction_level == EnumAbstractionLevel.COUNTRY:
        region_tile = return_tile_for_region("country", organisation)
    else:  # pragma: no cover
        raise ValueError("Invalid abstraction level")

    return region_tile
