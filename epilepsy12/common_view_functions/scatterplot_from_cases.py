# python imports
from datetime import date

# django imports
from django.conf import settings

# third party imports
import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go

# RCPCH imports
from ..constants import RCPCH_LIGHT_BLUE, RCPCH_PINK, RCPCH_DARK_BLUE


def generate_distance_from_organisation_scatterplot_figure(
    geo_df: pd.DataFrame, organisation
):
    """
    Returns a plottable map with Cases overlayed as dots with tooltips on hover
    """

    # Ensure numeric and drop rows without coordinates
    geo_df = geo_df.copy()
    geo_df["latitude"] = pd.to_numeric(geo_df["latitude"], errors="coerce")
    geo_df["longitude"] = pd.to_numeric(geo_df["longitude"], errors="coerce")
    geo_df = geo_df.dropna(subset=["latitude", "longitude"])

    # Use plain lists/ndarrays for safety
    lats = geo_df["latitude"].astype(float).tolist()
    lons = geo_df["longitude"].astype(float).tolist()
    has_custom = {"pk", "distance_mi", "distance_km"}.issubset(geo_df.columns)
    custom = (
        list(
            zip(
                geo_df["pk"].astype(str).tolist(),
                geo_df["distance_mi"].astype(float).tolist(),
                geo_df["distance_km"].astype(float).tolist(),
            )
        )
        if has_custom
        else None
    )
    hovertext = (
        geo_df["epilepsy12_sites__organisation__name"].astype(str).tolist()
        if "epilepsy12_sites__organisation__name" in geo_df.columns
        else None
    )

    # Compute a sensible center (fall back to organisation if available)
    center_lat = (
        float(geo_df["latitude"].mean())
        if not geo_df.empty
        else getattr(organisation, "latitude", None)
    )
    center_lon = (
        float(geo_df["longitude"].mean())
        if not geo_df.empty
        else getattr(organisation, "longitude", None)
    )

    # plot the cases
    fig = go.Figure(
        go.Scattermapbox(
            lat=lats,
            lon=lons,
            hovertext=hovertext,
            mode="markers",
            marker=go.scattermapbox.Marker(size=12, color=RCPCH_PINK, opacity=0.95),
            customdata=custom,
        )
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=8,
        mapbox_center=dict(lat=center_lat, lon=center_lon),
        height=590,
        mapbox_accesstoken=settings.MAPBOX_API_KEY,
        showlegend=False,
    )

    # Update the hover template (only if customdata present)
    if set(["pk", "distance_mi", "distance_km"]).issubset(geo_df.columns):
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><br>Epilepsy12 ID: %{customdata[0]}<br>Distance to Lead Centre: %{customdata[1]:.2f} mi (%{customdata[2]:.2f} km)<extra></extra>"
        )

    # Add a scatterplot point for the organization if it has valid coords
    if (
        getattr(organisation, "latitude", None) is not None
        and getattr(organisation, "longitude", None) is not None
    ):
        fig.add_trace(
            go.Scattermapbox(
                lat=[organisation.latitude],
                lon=[organisation.longitude],
                mode="markers",
                marker=go.scattermapbox.Marker(size=12, color=RCPCH_DARK_BLUE),
                text=[organisation.name],
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        font=dict(family="Montserrat-Regular", color="#FFFFFF"),
        hoverlabel=dict(
            bgcolor=RCPCH_LIGHT_BLUE,
            font_size=12,
            font=dict(color="white", family="Montserrat-Regular"),
            bordercolor=RCPCH_LIGHT_BLUE,
        ),
    )

    return pio.to_json(fig)


def generate_dataframe_and_aggregated_distance_data_from_cases(filtered_cases):
    """
    Returns a dataframe of all Cases, location data and distances with aggregated results
    """
    geo_df = pd.DataFrame(list(filtered_cases))
    # Ensure location is a tuple of (easting, northing)

    if not geo_df.empty:
        if "location_wgs84" in geo_df.columns:
            # Filter out rows where location_wgs84 is None - this should have been filtered out in the query in any case
            geo_df = geo_df[geo_df["location_wgs84"].notnull()]

            geo_df["longitude"] = geo_df["location_wgs84"].apply(lambda loc: loc.x)
            geo_df["latitude"] = geo_df["location_wgs84"].apply(lambda loc: loc.y)
            geo_df["distance_km"] = geo_df["distance_from_lead_organisation"].apply(
                lambda d: d.km
            )
            geo_df["distance_mi"] = geo_df["distance_from_lead_organisation"].apply(
                lambda d: d.mi
            )

            max_distance_travelled_km = geo_df["distance_km"].max()
            mean_distance_travelled_km = geo_df["distance_km"].mean()
            median_distance_travelled_km = geo_df["distance_km"].median()
            std_distance_travelled_km = geo_df["distance_km"].std()

            max_distance_travelled_mi = geo_df["distance_mi"].max()
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
    else:
        geo_df["pk"] = None
        geo_df["longitude"] = None
        geo_df["latitude"] = None
        geo_df["distance_km"] = 0
        geo_df["distance_mi"] = 0
        return {
            "max_distance_travelled_km": f"~",
            "mean_distance_travelled_km": f"~",
            "median_distance_travelled_km": f"~",
            "std_distance_travelled_km": f"~",
            "max_distance_travelled_mi": f"~",
            "mean_distance_travelled_mi": f"~",
            "median_distance_travelled_mi": f"~",
            "std_distance_travelled_mi": f"~",
        }, geo_df
