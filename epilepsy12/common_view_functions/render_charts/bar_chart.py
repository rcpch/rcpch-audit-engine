"""Renders a static Plotly bar chart, used to show % passed for metric, per abstraction level in ICB, NHS Region, OPENUK, Country.

NOTE: "No data" for bars denotes that KPIAggregation model's field is None. This will be because aggregations have not yet been performed - because there are no eligibile kids to perform aggregations on.
"""
# Python imports

# 3rd Party imports
import plotly.graph_objects as go
import numpy as np

# E12 Imports
from epilepsy12.constants.colors import *
from epilepsy12.constants import EnumAbstractionLevel
from .helpers import format_icb, format_pct_text, format_subunit_name_ticktext


ABSTRACTION_GRAPH_COLOR_MAP = {
    EnumAbstractionLevel.ICB: RCPCH_LIGHT_BLUE,
    EnumAbstractionLevel.OPEN_UK: RCPCH_AQUA_GREEN,
    EnumAbstractionLevel.NHS_REGION: RCPCH_STRONG_BLUE,
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
    n_passed = []
    n_total_eligible = []
    n_ineligible = []
    n_incomplete = []
    # COLORS
    PCT_TEXT_COLOR = []
    BG_BAR_COLOR = []
    PCT_BAR_COLOR = []
    NAMES_TEXT_COLOR = []
    bar_widths = [1 for _ in names]

    # Gather colors for each of the bar charts
    ABSTRACTION_COLOR = ABSTRACTION_GRAPH_COLOR_MAP[abstraction_level]

    # Gather text for hoverlabel NOTE: <extra></extra> removes the "trace1" trace label
    hovertemplate_pct_passed = (
        f"""<b>%{{x}}%</b> of cases passed this metric.<extra></extra>"""
    )

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

        # hover template for absolute counts
        kpi_passed_count = getattr(aggregation_model, f"{kpi_name}_passed")
        kpi_total_eligible_count = getattr(aggregation_model, f"{kpi_name}_passed")
        kpi_passed_text = f"({kpi_passed_count} / {kpi_total_eligible_count})"
        kpi_ineglible_count = getattr(aggregation_model, f"{kpi_name}_ineligible")
        kpi_incomplete_count = getattr(aggregation_model, f"{kpi_name}_incomplete")

        n_passed.append(kpi_passed_text)
        n_incomplete.append(kpi_ineglible_count)
        n_ineligible.append(kpi_incomplete_count)

        # Colors
        if pct_passed_item is None:
            BG_BAR_COLOR.append(RCPCH_WHITE)
            PCT_BAR_COLOR.append(RCPCH_LIGHTEST_GREY)
            PCT_TEXT_COLOR.append(RCPCH_CHARCOAL)
            NAMES_TEXT_COLOR.append(
                format_subunit_name_ticktext(color=RCPCH_LIGHTEST_GREY, text=name)
            )
        else:
            BG_BAR_COLOR.append(RCPCH_LIGHT_GREY)
            PCT_BAR_COLOR.append(ABSTRACTION_COLOR)
            PCT_TEXT_COLOR.append(RCPCH_BLACK)
            NAMES_TEXT_COLOR.append(
                format_subunit_name_ticktext(color=RCPCH_WHITE, text=name)
            )

    # Generate the hover bar for those passed / incomplete / inelgible. Access attributes via index order set in customdata_bg_bar
    customdata_bg_bar = np.stack(
        (
            n_passed,
            n_incomplete,
            n_ineligible,
        ),
        axis=-1,
    )
    hovertemplate_bg_bar = "<b>%{y}</b><br>passed: %{customdata.0}<br>incomplete: %{customdata.1}<br>ineligible: %{customdata.2}<extra></extra>"

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
            customdata=customdata_bg_bar,
            hovertemplate=hovertemplate_bg_bar,
        ),
        layout=go.Layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"),
    )

    # Fg Bars with pct passed
    fig.add_trace(
        go.Bar(
            x=pct_passed,
            y=names,
            orientation="h",
            marker_color=PCT_BAR_COLOR,
            width=bar_widths,
            hovertemplate=hovertemplate_pct_passed,
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
        hovermode="closest",
        hoverlabel=dict(
            bgcolor=ABSTRACTION_COLOR,
            font_size=10,
            font_family="Montserrat-Regular",
            bordercolor=ABSTRACTION_COLOR,
            font={"color": "white"},
            align="left",
        ),
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

    # Calculate average
    pct_pass_exc_none = [num for num in pct_passed if num is not None]
    average_for_eligible = int(
        round(sum(pct_pass_exc_none) / len(pct_pass_exc_none), 0)
    )

    # Add avg line
    fig.add_vline(
        x=average_for_eligible,
        annotation_text=f"Average for those eligible: {average_for_eligible}%",
        annotation_position="top",
        line_color=RCPCH_PINK,
        opacity=0.69,
    )

    fig.update_xaxes(
        range=[0, 104.5],  # the "No data" labels require space past the end of the axes
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
