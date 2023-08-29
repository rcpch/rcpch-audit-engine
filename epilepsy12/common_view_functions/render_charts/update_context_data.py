# Python imports

# third party libraries
from django.db.models import F, When, Case as DjangoCase, FloatField, Value

# E12 imports
from epilepsy12.common_view_functions.render_charts import (
    render_bar_pct_passed_for_kpi_agg,
    render_pie_pct_passed_for_kpi_agg,
    ChartHTML,
)

def update_all_data_with_charts(all_data:dict, kpi_name:str, kpi_name_title_case:str, cohort:int)->dict:
    """
    Takes in KPI aggregation `all_data` and for the appropriate abstraction, adds in appropriate chart HTML data to be displayed in template, and returns the updated `all_data` dict.
    """
    # Add chart HTMLs to all_data
    for abstraction, kpi_data in all_data.items():
        # Skip loop if aggregation model None (when there are no data to aggregate on so no AggregationModel made)
        if kpi_data["aggregation_model"] is None:
            continue

        # Initialise dict
        kpi_data["charts"] = {}

        # Add individual kpi passed pie chart
        pie_html_raw = render_pie_pct_passed_for_kpi_agg(
            kpi_data["aggregation_model"],
            kpi_name,
        )
        pie_html = ChartHTML(
            chart_html=pie_html_raw, name=f"{abstraction}_pct_pass_pie_{kpi_name}"
        )
        kpi_data["charts"]["passed_pie"] = pie_html

        # Skip loop if Organisation / Trust / National level
        if abstraction not in [
            "ICB_KPIS",
            "OPEN_UK_KPIS",
            "NHS_REGION_KPIS",
            "COUNTRY_KPIS",
        ]:
            continue
        
        # Gather data for selected abstraction's sub-unit barchart
        bar_data = (
            kpi_data["aggregation_model"]
            ._meta.model.objects.filter(cohort=cohort)
            .annotate(
                pct_passed=DjangoCase(
                    When(
                        **{f"{kpi_name}_total_eligible": 0},
                        then=Value(0), # Handles any division by zero errors by skipping
                    ),
                    default=(
                        100
                        * F(f"{kpi_name}_passed")
                        / F(f"{kpi_name}_total_eligible")
                    ),
                    output_field=FloatField(),
                ),
            )
            .values(
                "abstraction_name",
                "pct_passed",
                f"{kpi_name}_total_eligible",
                f"{kpi_name}_passed",
                f"{kpi_name}_ineligible",
                f"{kpi_name}_incomplete",
            )
        )

        bar_html_raw = render_bar_pct_passed_for_kpi_agg(
            aggregation_model=kpi_data["aggregation_model"],
            data=bar_data,
            kpi_name=kpi_name,
            kpi_name_title=kpi_name_title_case,
        )

        bar_html = ChartHTML(
            chart_html=bar_html_raw, name=f"{abstraction}_pct_pass_bar_{kpi_name}"
        )
        kpi_data["charts"]["passed_bar"] = bar_html