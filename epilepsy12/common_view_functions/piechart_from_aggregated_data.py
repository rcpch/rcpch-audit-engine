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

    return pio.to_json(fig)
