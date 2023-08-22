# Python imports

# 3rd Party imports
import plotly.express as px
import plotly.graph_objects as go

# E12 Imports
from epilepsy12.constants.colors import *

PLOTLY_CONFIG_OPTIONS = {
    "displayModeBar": False,
}


def render_pie_pct_passed_for_kpi_agg(aggregation_model, kpi_name: str) -> str:
    """
    For a given KPIAggregation model, returns Plotly HTML pie chart.
    """

    passed = getattr(aggregation_model, f"{kpi_name}_passed")
    total = getattr(aggregation_model, f"{kpi_name}_total_eligible")
    failed = total - passed

    # Pie chart args
    labels = [
        "pass",
        "failed",
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
            hole=0.9,
            textinfo="none",
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
        autosize=False,
        height=110,
        width=110,
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        font={"family": "Montserrat-Regular"},
    )

    # convert to html
    fig_as_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        div_id=f"pie_passed_{aggregation_model.get_abstraction_level()}_{kpi_name}",
        config=PLOTLY_CONFIG_OPTIONS,
    )

    return fig_as_html
