def calculate_kpi_average(kpi_data: list[dict], kpi: str, decimal_places: int=2) -> int:
    """
    Calculates the average percentage of passing for a given KPI across all regions in the input data.
    Only considers rows that are eligible, i.e., those that are not None or have no missing data.

    Args:
        kpi_data (list[dict]): A list of dictionaries, where each dictionary contains selected KPI data for a region.
        kpi (str): The KPI for which the average percentage of passing is to be calculated.

    Returns:
        int: The average percentage passing for the given KPI across all eligible rows.
    """
    total_pct_achieving_measure = 0
    num_eligible_rows = 0

    for region_data in kpi_data:
        region_eligible_passing = region_data['aggregated_kpis'][kpi]
        region_eligible_cases = region_data['aggregated_kpis']['total_number_of_cases']

        # Only include eligible, non-None rows in the calculation
        if (region_eligible_passing is not None) and (region_eligible_cases is not None):
            pct_achieving_measure = 100 * \
                (region_eligible_passing / region_eligible_cases)
            # print(f"Adding {pct_achieving_measure}%")
            total_pct_achieving_measure += pct_achieving_measure
            num_eligible_rows += 1

    if num_eligible_rows == 0:
        return 0
    else:
        return round(total_pct_achieving_measure / num_eligible_rows, decimal_places)
