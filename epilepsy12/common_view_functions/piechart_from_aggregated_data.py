# import third party libraries
import plotly.graph_objects as go
import plotly.io as pio

# import RCPCH data functions
from epilepsy12.common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_age,
)

from ..constants import (
    RCPCH_MID_GREY,
    RCPCH_LIGHTEST_GREY,
    RCPCH_DARK_BLUE,
    RCPCH_STRONG_BLUE,
    RCPCH_STRONG_BLUE_LIGHT_TINT1,
    RCPCH_STRONG_BLUE_LIGHT_TINT2,
    RCPCH_STRONG_BLUE_LIGHT_TINT3,
    RCPCH_STRONG_BLUE_DARK_TINT,
    RCPCH_LIGHT_BLUE,
    RCPCH_LIGHT_BLUE_TINT1,
    RCPCH_LIGHT_BLUE_TINT2,
    RCPCH_LIGHT_BLUE_TINT3,
    RCPCH_LIGHT_BLUE_DARK_TINT,
    RCPCH_PINK,
    RCPCH_PINK_LIGHT_TINT1,
    RCPCH_PINK_LIGHT_TINT2,
    RCPCH_PINK_LIGHT_TINT3,
    RCPCH_PINK_DARK_TINT,
)


def piechart_plot_cases_by_sex(organisation):
    """
    Function to plot a pie chart of cases in a given organisation aggregated by sex
    """
    aggregated_data = cases_aggregated_by_sex(selected_organisation=organisation)

    # Extract the labels and values
    labels = [item["sex_display"] for item in aggregated_data]
    values = [item["sexes"] for item in aggregated_data]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Customize the layout
    fig.update_layout(
        font=dict(family="Montserrat-Regular, sans-serif", size=10, color="#7f7f7f"),
        margin=dict(t=10, b=20, l=10, r=10),
        legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01),
    )

    # Customize the colors
    fig.update_traces(
        marker=dict(
            colors=[
                RCPCH_MID_GREY,
                RCPCH_LIGHT_BLUE_TINT3,
                RCPCH_LIGHT_BLUE_TINT1,
            ]
        )
    )

    # update hover label
    fig.update_traces(
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=12,
            font_family="Montserrat-Regular",
        ),
    )

    return pio.to_json(fig)


def piechart_plot_cases_by_age_range(organisation):
    """
    Function to plot a pie chart of cases in a given organisation aggregated by age range
    """
    aggregated_data = cases_aggregated_by_age(selected_organisation=organisation)

    # Extract the labels and values
    labels = [item["age_category_label"] for item in aggregated_data]
    values = [item["count"] for item in aggregated_data]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Customize the layout
    fig.update_layout(
        font=dict(family="Montserrat-Regular, sans-serif", size=10, color="#7f7f7f"),
        margin=dict(t=10, b=20, l=10, r=10),
        legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01),
    )

    # Customize the colors
    fig.update_traces(
        marker=dict(
            colors=[
                RCPCH_LIGHT_BLUE,
                RCPCH_LIGHT_BLUE_TINT1,
                RCPCH_LIGHT_BLUE_TINT2,
                RCPCH_LIGHT_BLUE_TINT3,
                RCPCH_LIGHT_BLUE_DARK_TINT,
            ]
        )
    )

    # update hover label
    fig.update_traces(
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=12,
            font_family="Montserrat-Regular",
        ),
    )

    return pio.to_json(fig)


def piechart_plot_cases_by_ethnicity(organisation):
    """
    Function to plot a pie chart of cases in a given organisation aggregated by ethnicity
    """
    aggregated_data = cases_aggregated_by_ethnicity(selected_organisation=organisation)

    # Extract the labels and values
    labels = [item["ethnicity_display"] for item in aggregated_data]
    values = [item["ethnicities"] for item in aggregated_data]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Customize the layout
    fig.update_layout(
        font=dict(family="Montserrat-Regular, sans-serif", size=10, color="#7f7f7f"),
        margin=dict(t=10, b=0, l=10, r=10),
        legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01),
    )

    # Customize the colors
    fig.update_traces(
        marker=dict(
            colors=[
                RCPCH_LIGHTEST_GREY,
                RCPCH_DARK_BLUE,
                RCPCH_STRONG_BLUE,
                RCPCH_STRONG_BLUE_LIGHT_TINT1,
                RCPCH_STRONG_BLUE_LIGHT_TINT2,
                RCPCH_STRONG_BLUE_LIGHT_TINT3,
                RCPCH_STRONG_BLUE_DARK_TINT,
                RCPCH_LIGHT_BLUE,
                RCPCH_LIGHT_BLUE_TINT1,
                RCPCH_LIGHT_BLUE_TINT2,
                RCPCH_LIGHT_BLUE_TINT3,
                RCPCH_LIGHT_BLUE_DARK_TINT,
                RCPCH_PINK,
                RCPCH_PINK_LIGHT_TINT1,
                RCPCH_PINK_LIGHT_TINT2,
                RCPCH_PINK_LIGHT_TINT3,
                RCPCH_PINK_DARK_TINT,
            ]
        )
    )

    # update hover label
    fig.update_traces(
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=12,
            font_family="Montserrat-Regular",
        ),
    )

    return pio.to_json(fig)


def piechart_plot_cases_by_index_of_multiple_deprivation(organisation):
    """
    Function to plot a pie chart of cases in a given organisation aggregated by index of multiple deprivation
    """
    aggregated_data = cases_aggregated_by_deprivation_score(
        selected_organisation=organisation
    )

    # Extract the labels and values
    labels = [
        item["index_of_multiple_deprivation_quintile_display_str"]
        for item in aggregated_data
    ]
    values = [item["cases_aggregated_by_deprivation"] for item in aggregated_data]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])

    # Customize the layout
    fig.update_layout(
        font=dict(family="Montserrat-Regular, sans-serif", size=10, color="#7f7f7f"),
        margin=dict(t=10, b=0, l=10, r=10),
        legend=dict(yanchor="top", y=0.01, xanchor="left", x=0.01),
    )

    # Customize the colors
    fig.update_traces(
        marker=dict(
            colors=[
                RCPCH_LIGHT_BLUE,
                RCPCH_LIGHT_BLUE_TINT1,
                RCPCH_LIGHT_BLUE_TINT2,
                RCPCH_LIGHT_BLUE_TINT3,
                RCPCH_LIGHT_BLUE_DARK_TINT,
            ]
        )
    )

    # update hover label
    fig.update_traces(
        hoverlabel=dict(
            bgcolor=RCPCH_PINK,
            font_size=12,
            font_family="Montserrat-Regular",
        ),
    )

    return pio.to_json(fig)
