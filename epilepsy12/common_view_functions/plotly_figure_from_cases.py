import pandas as pd
import plotly.express as px
import plotly.io as pio
from pyproj import Transformer


def generate_ploty_figure_from_cases(filtered_cases):
    """
    Returns a plottable map with Cases overlayed as dots with tooltips on hover
    """
    geo_df = pd.DataFrame(list(filtered_cases))
    # Ensure location is a tuple of (easting, northing)
    if "location" in geo_df.columns:
        geo_df["easting"], geo_df["northing"] = zip(*geo_df["location"])

    # Create a transformer to convert from EPSG:27700 to EPSG:4326
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326")

    # Convert the coordinates
    latitudes, longitudes = transformer.transform(
        geo_df["easting"].values, geo_df["northing"].values
    )
    geo_df["latitude"] = latitudes
    geo_df["longitude"] = longitudes

    fig = px.scatter_mapbox(
        data_frame=geo_df,
        lat="latitude",
        lon="longitude",
        hover_name="surname",
        zoom=10,
        height=600,
    )

    # Update the map layout
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Convert the Plotly figure to JSON
    return pio.to_json(fig)
