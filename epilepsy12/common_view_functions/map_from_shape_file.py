import plotly.express as px
import plotly.io as pio
from django.conf import settings
from ..constants import RCPCH_LIGHT_BLUE, RCPCH_PINK


def generate_plotly_map(region_tiles, properties):
    """
    Generates a Plotly map from GeoJSON data.
    """
    px.set_mapbox_access_token(settings.MAPBOX_API_KEY)

    # Create a Plotly Express map using the GeoJSON data
    fig = px.choropleth_mapbox(
        geojson=region_tiles,
        locations=[0],  # Dummy location just to trigger the map creation
        featureidkey=properties,  # Adjust this to match your GeoJSON properties key
        color=[1],  # Dummy data for color
        color_continuous_scale="Viridis",
        range_color=(0, 1),
        mapbox_style="carto-positron",
        zoom=5,
        center={"lat": 53.0, "lon": -1.5},  # Adjust to the center of your map
        opacity=0.5,
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Convert the Plotly figure to JSON
    return pio.to_json(fig)
