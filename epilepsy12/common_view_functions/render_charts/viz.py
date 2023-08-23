# Python imports

# 3rd Party imports
import plotly.express as px
import plotly.graph_objects as go

# E12 Imports
from epilepsy12.constants.colors import *

PLOTLY_CONFIG_OPTIONS = {
    "displayModeBar": False,
}


class ChartHTML:
    """Simple container class to hold chart HTML content.

    Useful to avoid lots of rendered html if trying to print a view's context.
    """

    def __init__(self, chart_html: str, name: str):
        self.chart_html = chart_html
        self.name = name

    def get_html(self) -> str:
        return self.chart_html

    def get_name(self) -> str:
        return self.name

    def __str__(self):
        return f"<{self.get_name()} ChartHTML object>"

    def __repr__(self):
        return f"<{self.get_name()} ChartHTML object>"


def render_pie_pct_passed_for_kpi_agg(aggregation_model, kpi_name: str) -> str:
    """
    For a given KPIAggregation model, returns Plotly HTML pie chart.
    """
    
    if aggregation_model is None:
        raise ValueError('aggregation_model cannot be None')

    total = getattr(aggregation_model, f"{kpi_name}_total_eligible")
    if total is None:
        return 'Aggregation not yet performed'
    
    passed = getattr(aggregation_model, f"{kpi_name}_passed")
    
    failed = total - passed

    # Pie chart args
    labels = [
        "Passed",
        "Failed",
    ]
    values = [
        passed,
        failed,
    ]
    colors = [
        RCPCH_LIGHT_BLUE,
        RCPCH_LIGHT_GREY,
    ]

    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hole=0.9,  # sets the middle hole size
            textinfo="none",
            hoverinfo="none",
        )
    )
    # Position the % pass in the center of the hole
    pct_passed = round(passed / total * 100)
    fig.add_annotation(
        text=f"{pct_passed}%",
        x=0.5,
        y=0.5,
        font=dict(
            size=30,
            color=RCPCH_LIGHT_BLUE,
        ),
        showarrow=False,
    )

    fig.update_layout(
        showlegend=False,  # remove legend
        autosize=False,  # remove any auto sizing to place nicely inside template
        height=150,
        width=150,
        margin=dict(l=0, r=0, b=20, t=0, pad=0),
        font={"family": "Montserrat-Regular"},
    )

    # convert to html
    fig_as_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        div_id=f"pie_passed_{aggregation_model.get_abstraction_level()}_{kpi_name}",
        default_width='100%',
        default_height='100%',
        config=PLOTLY_CONFIG_OPTIONS,
    )

    return fig_as_html
