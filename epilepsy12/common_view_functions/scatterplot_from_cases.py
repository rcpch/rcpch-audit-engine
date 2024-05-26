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

    fig = go.Figure(
        go.Scattermapbox(
            lat=geo_df["latitude"] if not geo_df.empty else [],
            lon=geo_df["longitude"] if not geo_df.empty else [],
            hovertext=geo_df["site__organisation__name"] if not geo_df.empty else None,
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=9,
                color=RCPCH_PINK,
            ),
            customdata=geo_df[["pk", "distance_mi", "distance_km"]],
        )
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=10,
        mapbox_center=dict(lat=organisation.latitude, lon=organisation.longitude),
        height=600,
        mapbox_accesstoken=settings.MAPBOX_API_KEY,
        showlegend=False,
    )

    # Update the hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Epilepsy12 ID: %{customdata[0]}<br>Distance to Lead Centre: %{customdata[1]:.2f} mi (%{customdata[2]:.2f} km)<extra></extra>"
    )

    # Add a scatterplot point for the organization
    fig.add_trace(
        go.Scattermapbox(
            lat=[organisation.latitude],
            lon=[organisation.longitude],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=12,
                color=RCPCH_DARK_BLUE,  # Set the color of the point
            ),
            text=[organisation.name],  # Set the hover text for the point
            hovertemplate="%{text}<extra></extra>",  # Custom hovertemplate just for the lead organisation
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
