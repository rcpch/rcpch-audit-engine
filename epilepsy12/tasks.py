# Python Imports
from typing import Literal, Union

# Django Imports

# E12 Imports
from .general_functions import get_current_cohort_data
from epilepsy12.constants import EnumAbstractionLevel
from epilepsy12.common_view_functions.aggregate_by import update_all_kpi_agg_models


def scheduled_aggregate_kpis_update_models_for(
    cohort: int = None,
    abstractions: Union[Literal["all"], list[EnumAbstractionLevel]] = "all",
):
    # If no cohort supplied, automatically get cohort from current datetime
    if cohort is None:
        cohort = get_current_cohort_data()["cohort"]

    # By default, this will update all KPIAggregation models for all levels of abstraction
    update_all_kpi_agg_models(cohort=cohort, abstractions=abstractions)
