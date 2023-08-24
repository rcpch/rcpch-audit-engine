"""Renders a static Plotly bar chart, used to show % passed for metric, per abstraction level in ICB, NHS Region, OPENUK, Country.

NOTE: "No data" for bars denotes that KPIAggregation model's field is None. This will be because aggregations have not yet been performed - because there are no eligibile kids to perform aggregations on.
"""
# Python imports

# 3rd Party imports
import plotly.graph_objects as go

# E12 Imports
from epilepsy12.constants.colors import *
from epilepsy12.constants import EnumAbstractionLevel
from .helpers import format_icb, format_pct_text, format_subunit_name_ticktext


ABSTRACTION_GRAPH_COLOR_MAP = {
    EnumAbstractionLevel.ICB: RCPCH_STRONG_BLUE,
    EnumAbstractionLevel.OPEN_UK: RCPCH_AQUA_GREEN,
    EnumAbstractionLevel.NHS_REGION: RCPCH_LIGHT_BLUE,
    EnumAbstractionLevel.COUNTRY: RCPCH_DARK_BLUE,
}
ABSTRACTION_CHART_HEIGHT = {
    EnumAbstractionLevel.ICB: "100vh",
    EnumAbstractionLevel.OPEN_UK: "80vh",
    EnumAbstractionLevel.NHS_REGION: "70vh",
    EnumAbstractionLevel.COUNTRY: "50vh",
}
ABSTRACTION_GRAPH_TITLE_SUBUNIT = {
    EnumAbstractionLevel.ICB: "Integrated Care Board",
    EnumAbstractionLevel.OPEN_UK: "OPEN UK Region",
    EnumAbstractionLevel.NHS_REGION: "NHS Region",
    EnumAbstractionLevel.COUNTRY: "Country",
}


def render_bar_pct_passed_for_kpi_agg(
    aggregation_model,
    data,
    kpi_name: str,
    kpi_name_title: str,
) -> str:
    # Constants
    abstraction_level = aggregation_model.get_abstraction_level()

    title = f"% Passed {kpi_name_title} per {ABSTRACTION_GRAPH_TITLE_SUBUNIT[abstraction_level]}"

    # Gather data
    names = []
    pct_passed = []
    pct_passed_text = []
    # COLORS
    PCT_TEXT_COLOR = []
    BG_BAR_COLOR = []
    PCT_BAR_COLOR = []
    NAMES_TEXT_COLOR = []
    bar_widths = [1 for _ in names]

    # Gather colors for each of the bar charts
    ABSTRACTION_COLOR = ABSTRACTION_GRAPH_COLOR_MAP[abstraction_level]

    # Gather text for hoverlabel NOTE: <extra></extra> removes the "trace1" trace label
    hovertemplate = f"""<b>%{{x}}%</b> of cases passed this metric.<extra></extra>"""

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
            width=bar_widths,
            hoverinfo="none",
        )
    )

    # Fg Bars with pct passed
    fig.add_trace(
        go.Bar(
            x=pct_passed,
            y=names,
            orientation="h",
            marker_color=PCT_BAR_COLOR,
            width=bar_widths,
            hovertemplate=hovertemplate,
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
        margin=dict(l=0, r=0, b=10, t=75, pad=0),
        font={"family": "Montserrat-Regular"},  # set font
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
        default_height=ABSTRACTION_CHART_HEIGHT[abstraction_level],
        config={
            "modeBarButtonsToRemove": ["zoom", "pan"],
        },
    )

    return fig_as_html
