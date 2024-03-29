"""Renders a static Plotly hole-pie chart, used to show % passed for metric, per abstraction level.

PLOTLY_CONFIG_OPTIONS turns off the interactivity.
"""

# Python imports

# 3rd Party imports
import plotly.graph_objects as go
from django.utils.safestring import mark_safe

# E12 Imports
from epilepsy12.constants.colors import *
from epilepsy12.templatetags.epilepsy12_template_tags import _plural

PLOTLY_CONFIG_OPTIONS = {
    "displayModeBar": False,
}


def render_pie_pct_passed_for_kpi_agg(aggregation_model, kpi_name: str) -> str:
    """
    For a given KPIAggregation model, returns Plotly pie chart as HTML string.

    If no aggregation model, raises ValueError.

    If kpi_total is None, returns `"Aggregation not yet performed"`.

    If kpi_total is 0, returns
    """

    if aggregation_model is None:
        raise ValueError("aggregation_model cannot be None")

    total = getattr(aggregation_model, f"{kpi_name}_total_eligible")

    if total is None:
        return "Aggregation not yet performed"

    if total == 0:
        n_ineligible = getattr(aggregation_model, f"{kpi_name}_ineligible")
        n_incomplete = getattr(aggregation_model, f"{kpi_name}_incomplete")
        return mark_safe(
            f"""No eligible Cases to score.<br>
        <b>{n_ineligible}</b> case{_plural(n_ineligible)} ineligible.<br>
        <b>{n_incomplete}</b> case{_plural(n_incomplete)} incomplete."""
        )

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
        autosize=True, 
        height=300,
        width=300,
        font={"family": "Montserrat-Regular"},
    )

    # convert to html
    fig_as_html = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        div_id=f"pie_passed_{aggregation_model.get_abstraction_level()}_{kpi_name}",
            # default_width="50%",
            # default_height="100%",
        config=PLOTLY_CONFIG_OPTIONS,
    )

    return fig_as_html
