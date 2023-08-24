# Python imports
import re

# 3rd Party imports
import plotly.express as px
import plotly.graph_objects as go

# E12 Imports
from epilepsy12.constants.colors import *
from epilepsy12.constants import EnumAbstractionLevel

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
        raise ValueError("aggregation_model cannot be None")

    total = getattr(aggregation_model, f"{kpi_name}_total_eligible")
    if total is None:
        return "Aggregation not yet performed"

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
        default_width="100%",
        default_height="100%",
        config=PLOTLY_CONFIG_OPTIONS,
    )

    return fig_as_html


def format_icb(label):
    if label is None:
        return "Unclassified"
    else:
        nhs_icb_string = re.search(r"(NHS\s)(.+)(\sINTEGRATED CARE BOARD)", label)
        if nhs_icb_string:
            # \u002D fixes hyphen render for 'Stoke-on-trent'
            return nhs_icb_string.group(2).replace(r"\u002D", "-").title()
        return label


def format_pct_text(label):
    if label is None:
        return "No data"

    return f"{label} %"


def format_subunit_name_ticktext(color, text):
    return f"<span style='color:{str(color)}'> {str(text)} </span>"

ABSTRACTION_GRAPH_COLOR_MAP = {
    EnumAbstractionLevel.ICB: RCPCH_STRONG_BLUE,
    EnumAbstractionLevel.NHS_REGION: RCPCH_LIGHT_BLUE,
    EnumAbstractionLevel.OPEN_UK: RCPCH_AQUA_GREEN,
    EnumAbstractionLevel.COUNTRY: RCPCH_DARK_BLUE,
}

def render_bar_pct_passed_for_kpi_agg(
    aggregation_model,
    data,
    kpi_name: str,
    kpi_name_title: str,
) -> str:
    # Constants
    abstraction_level = aggregation_model.get_abstraction_level()
    region = ""
    if abstraction_level is EnumAbstractionLevel.ICB:
        region = "Integrated Care Board"
    title = f"% Passed {kpi_name_title} per {region}"

    # Gather data
    names = []
    pct_passed = []
    pct_passed_text = []
    # COLORS
    PCT_TEXT_COLOR = []
    BG_BAR_COLOR = []
    PCT_BAR_COLOR = []
    NAMES_TEXT_COLOR = []

    ABSTRACTION_COLOR = ABSTRACTION_GRAPH_COLOR_MAP[abstraction_level]

    for item in data:
        name = item["abstraction_name"]
        if abstraction_level is EnumAbstractionLevel.ICB:
            name = format_icb(name)
        names.append(name)

        # Pct values
        pct_passed_item = item["pct_passed"]
        pct_passed.append(pct_passed_item)

        # pct labels
        pct_passed_text.append(format_pct_text(pct_passed_item))

        # Colors
        if pct_passed_item is None:
            BG_BAR_COLOR.append(RCPCH_LIGHTEST_GREY)
            PCT_BAR_COLOR.append(RCPCH_LIGHTEST_GREY)
            PCT_TEXT_COLOR.append(RCPCH_CHARCOAL)
            NAMES_TEXT_COLOR.append(
                format_subunit_name_ticktext(color=RCPCH_CHARCOAL, text=name)
            )
        else:
            BG_BAR_COLOR.append(RCPCH_LIGHT_GREY)
            PCT_BAR_COLOR.append(ABSTRACTION_COLOR)
            PCT_TEXT_COLOR.append(RCPCH_BLACK)
            NAMES_TEXT_COLOR.append(
                format_subunit_name_ticktext(color=RCPCH_WHITE, text=name)
            )

    # Bg Bars
    fig = go.Figure(
        go.Bar(
            x=[100] * len(names),
            y=names,
            text=pct_passed_text,
            textposition="outside",
            textfont=dict(color=PCT_TEXT_COLOR),
            orientation="h",
            marker_color=BG_BAR_COLOR,
        )
    )

    # Fg Bars with pct passed
    fig.add_trace(
        go.Bar(
            x=pct_passed,
            y=names,
            orientation="h",
            marker_color=PCT_BAR_COLOR,
        )
    )

    # Overlay bars, add title, set minimal theme
    fig.update_layout(
        title=title,
        barmode="overlay",
        showlegend=False,
        template="none",
        # Set size
        autosize=True,
        # height=950,
        # width=1200,
        margin=dict(l=0, r=0, b=10, t=75, pad=0),
        font={"family": "Montserrat-Regular"},
    )

    # Move name ticks inside bars
    fig.update_yaxes(
        tickmode="array",
        # categoryorder="total ascending",
        tickvals=names,
        ticktext=NAMES_TEXT_COLOR,
        ticklabelposition="inside",
        automargin=True,
    )

    fig.update_xaxes(
        range=[0, 108],
        visible=False,
        automargin=True,
    )

    # convert to html
    fig_as_html = fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id=f"bar_passed_{aggregation_model.get_abstraction_level().name}",
        default_width="100%",
        default_height="100vh",
        # config=PLOTLY_CONFIG_OPTIONS,
    )

    return fig_as_html
