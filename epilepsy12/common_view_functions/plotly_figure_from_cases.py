from django.apps import apps
import pandas as pd
import plotly.express as px
import plotly.io as pio
from django.conf import settings
from ..constants import RCPCH_LIGHT_BLUE, RCPCH_PINK, EnumAbstractionLevel
from .aggregate_by import get_abstraction_model_from_level


def generate_ploty_figure(geo_df: pd.DataFrame, organisation=None):
    """
    Returns a plottable map with Cases overlayed as dots with tooltips on hover
    """

    px.set_mapbox_access_token(settings.MAPBOX_API_KEY)
    fig = px.scatter_mapbox(
        data_frame=geo_df,
        lat="latitude" if not geo_df.empty else [],
        lon="longitude" if not geo_df.empty else [],
        hover_name="site__organisation__name" if not geo_df.empty else None,
        zoom=10,
        height=600,
        color_discrete_sequence=[RCPCH_PINK],
        custom_data=["pk", "distance_mi", "distance_km"],
    )

    # Update the map layout
    fig.update_layout(
        mapbox_style="mapbox://styles/mapbox/light-v11",
        mapbox_accesstoken=settings.MAPBOX_API_KEY,
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        font=dict(family="Montserrat", color="#FFFFFF"),
        hoverlabel=dict(
            bgcolor=RCPCH_LIGHT_BLUE,
            font_size=12,
            font=dict(color="white"),
            bordercolor=RCPCH_LIGHT_BLUE,
        ),
    )
    # Update the hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Epilepsy12 ID: %{customdata[0]}<br>Distance to Lead Centre: %{customdata[1]:.2f} mi (%{customdata[2]:.2f} km)<extra></extra>"
    )

    if organisation:
        # centre the map on the lead organisation
        fig.update_geos(
            center=dict(lat=organisation.latitude, lon=organisation.longitude)
        )

    # Convert the Plotly figure to JSON
    return pio.to_json(fig)


def generate_dataframe_and_aggregated_distance_data_from_cases(filtered_cases):
    """
    Returns a dataframe of all Cases, location data and distances with aggregated results
    """
    geo_df = pd.DataFrame(list(filtered_cases))
    # Ensure location is a tuple of (easting, northing)

    if not geo_df.empty:
        if "location_wgs84" in geo_df.columns:
            geo_df["longitude"] = geo_df["location_wgs84"].apply(lambda loc: loc.x)
            geo_df["latitude"] = geo_df["location_wgs84"].apply(lambda loc: loc.y)
            geo_df["distance_km"] = geo_df["distance_from_lead_organisation"].apply(
                lambda d: d.km
            )
            geo_df["distance_mi"] = geo_df["distance_from_lead_organisation"].apply(
                lambda d: d.mi
            )

            max_distance_travelled_km = geo_df["distance_km"].min()
            mean_distance_travelled_km = geo_df["distance_km"].mean()
            median_distance_travelled_km = geo_df["distance_km"].median()
            std_distance_travelled_km = geo_df["distance_km"].std()

            max_distance_travelled_mi = geo_df["distance_mi"].min()
            mean_distance_travelled_mi = geo_df["distance_mi"].mean()
            median_distance_travelled_mi = geo_df["distance_mi"].median()
            std_distance_travelled_mi = geo_df["distance_mi"].std()

            return {
                "max_distance_travelled_km": f"{max_distance_travelled_km:.2f}",
                "mean_distance_travelled_km": f"{mean_distance_travelled_km:.2f}",
                "median_distance_travelled_km": f"{median_distance_travelled_km:.2f}",
                "std_distance_travelled_km": f"{std_distance_travelled_km:.2f}",
                "max_distance_travelled_mi": f"{max_distance_travelled_mi:.2f}",
                "mean_distance_travelled_mi": f"{mean_distance_travelled_mi:.2f}",
                "median_distance_travelled_mi": f"{median_distance_travelled_mi:.2f}",
                "std_distance_travelled_mi": f"{std_distance_travelled_mi:.2f}",
            }, geo_df


def generate_case_counts_for_each_region_in_each_abstraction_level(
    abstraction_level: EnumAbstractionLevel, cohort: int, organisation
):
    """
    Returns a dataframe of all case counts, for a given cohort, in all members of a given abstraction_level.
    The member of the level of abstraction where the organisation is a child is flagged in the result
    """

    # get lists of all members of each level of abstraction
    Trust = apps.get_model("epilepsy12", "Trust")
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    Country = apps.get_model("epilepsy12", "Country")
    National = apps.get_model("epilepsy12", "National")

    level_abstraction_members = None
    if abstraction_level == EnumAbstractionLevel.Trust:
        level_abstraction_members = (
            Trust.objects.filter(active=True).order_by("name").values("ods_code", "name")
        )
    elif abstraction_level == EnumAbstractionLevel.ICB:
        level_abstraction_members = (
            IntegratedCareBoard.objects.all()
            .order_by("name")
            .values("boundary_identifier", "name", "ods_code")
        )
    elif abstraction_level == EnumAbstractionLevel.LOCAL_HEALTH_BOARD:
        level_abstraction_members = (
            LocalHealthBoard.objects.all()
            .order_by("name")
            .values("boundary_identifier", "name", "ods_code")
        )
    elif abstraction_level == EnumAbstractionLevel.NHS_ENGLAND_REGION
        level_abstraction_members = (
            NHSEnglandRegion.objects.all()
            .order_by("name")
            .values("boundary_identifier", "name", "region_code")
        )
    elif abstraction_level == EnumAbstractionLevel.COUNTRY:
        level_abstraction_members = (
            Country.objects.all()
            .order_by("name")
            .values(
                "boundary_identifier",
                "name",
            )
    )
        
    for member in level_abstraction_members:
        


