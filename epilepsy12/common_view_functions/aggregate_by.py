from typing import Literal

# Django imports
from django.apps import apps
from django.contrib.gis.db.models import (
    Q,
    F,
    Count,
    Sum,
    Avg,
    When,
    Value,
    CharField,
    PositiveSmallIntegerField,
    Case as DJANGO_CASE,
)

# E12 imports
from epilepsy12.constants import ETHNICITIES, SEX_TYPE

# from ..models import Case
from .report_queries import (
    get_all_organisations,
    get_all_trusts,
    get_all_icbs,
    get_all_nhs_regions,
    get_all_open_uk_regions,
    get_all_countries,
)

"""
Reporting
"""


def cases_aggregated_by_sex(selected_organisation):
    # aggregate queries on trust level cases

    Case = apps.get_model("epilepsy12", "Case")

    sex_long_list = [When(sex=k, then=Value(v)) for k, v in SEX_TYPE]

    cases_aggregated_by_sex = (
        Case.objects.filter(organisations=selected_organisation)
        .values("sex")
        .annotate(sex_display=DJANGO_CASE(*sex_long_list, output_field=CharField()))
        .values("sex_display")
        .annotate(sexes=Count("sex"))
        .order_by("sexes")
    )

    return cases_aggregated_by_sex


def cases_aggregated_by_deprivation_score(selected_organisation):
    # aggregate queries on trust level cases
    Case = apps.get_model("epilepsy12", "Case")

    cases_in_selected_organisation = Case.objects.filter(
        organisations__OrganisationName__contains=selected_organisation
    )

    cases_aggregated_by_deprivation = (
        # Filter just Cases in selected org
        cases_in_selected_organisation
        # Get list of IMD quintiles
        .values("index_of_multiple_deprivation_quintile")
        # Converting 'None' to 6 in a new index_of_multiple_deprivation_quintile_display "column"
        .annotate(
            index_of_multiple_deprivation_quintile_display=DJANGO_CASE(
                When(index_of_multiple_deprivation_quintile=None, then=Value(6)),
                default="index_of_multiple_deprivation_quintile",
                output_field=PositiveSmallIntegerField(),
            )
        )
        # Keeps only the new column
        .values("index_of_multiple_deprivation_quintile_display")
        # Value count the new column
        .annotate(
            cases_aggregated_by_deprivation=Count(
                "index_of_multiple_deprivation_quintile_display"
            ),
        ).order_by("index_of_multiple_deprivation_quintile_display")
    )

    deprivation_quintile_str_map = {
        1: "1st quintile",
        2: "2nd quintile",
        3: "3rd quintile",
        4: "4th quintile",
        5: "5th quintile",
        6: "Not known",
    }

    for aggregate in cases_aggregated_by_deprivation:
        quintile = aggregate["index_of_multiple_deprivation_quintile_display"]

        str_map = deprivation_quintile_str_map.get(quintile)

        aggregate.update(
            {"index_of_multiple_deprivation_quintile_display_str": str_map}
        )

    return cases_aggregated_by_deprivation


def cases_aggregated_by_ethnicity(selected_organisation):
    # aggregate queries on trust level cases

    Case = apps.get_model("epilepsy12", "Case")

    ethnicity_long_list = [When(ethnicity=k, then=Value(v)) for k, v in ETHNICITIES]

    cases_aggregated_by_ethnicity = (
        Case.objects.filter(
            organisations__OrganisationName__contains=selected_organisation
        )
        .values("ethnicity")
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values("ethnicity_display")
        .annotate(ethnicities=Count("ethnicity"))
        .order_by("ethnicities")
    )

    return cases_aggregated_by_ethnicity


def refactored_aggregate_all_eligible_kpi_fields(
    filtered_cases, kpi_measures: list[str]
) -> dict:
    """Takes in a QuerySet[Cases] and list of selected kpi measure names, calculates an aggregate value count, and returns a dict of value counts, which can be used to update the KPIAggregation model.

    **WIP Fn, to refactor aggregate_all_elibible_kpi_fields without affecting application.**

    Args:
        filtered_cases (QuerySet[Case]): QuerySet of filtered Cases on which to perform aggregation queries.
        kpi_measures (list): list of KPI measures for which to aggregate
    """
    final_aggregation_dict = {}
    KPI = apps.get_model("epilepsy12", "KPI")

    for kpi_name in kpi_measures:
        # Creates value counts of each value, per kpi measure, including Nulls (using "*")
        value_counts = KPI.objects.values(
            **{f"{kpi_name}_score": F(kpi_name)}
        ).annotate(count=Count("*"))

        # Initialise with all keys
        initial_object = {
            f"{kpi_name}_passed": 0,
            f"{kpi_name}_total_eligible": 0,
            f"{kpi_name}_ineligible": 0,
            f"{kpi_name}_incomplete": 0,
        }
        total_eligible = 0

        for value_count in value_counts:
            score = value_count[f"{kpi_name}_score"]
            count = value_count["count"]

            if score is None:
                initial_object[f"{kpi_name}_incomplete"] = count
            elif score == 0:
                total_eligible += count

            elif score == 1:
                total_eligible += count

                initial_object[f"{kpi_name}_passed"] = count

            elif score == 2:
                initial_object[f"{kpi_name}_ineligible"] = count

        initial_object[f"{kpi_name}_total_eligible"] = total_eligible
        final_aggregation_dict.update(initial_object)

    return final_aggregation_dict


def aggregate_all_eligible_kpi_fields(filtered_cases, kpi_measure=None):
    """
    Returns a dictionary of all KPI fields with aggregation for each measure ready to persist in KPIAggregations.
    It accepts a list of cases filtered by a given level of abstraction (all cases in an organisation, trust, icb etc)
    If an individual measure is passed in, only that measure will be aggregated.
    Returned fields include sum of all eligible KPI measures (identified as having an individual score of 1 or 0)
    for that registration as well as average score of the same and total number KPIs.
    A KPI score of 2 is excluded as not eligible for that measure.
    """

    all_kpi_measures = [
        "paediatrician_with_expertise_in_epilepsies",
        "epilepsy_specialist_nurse",
        "tertiary_input",
        "epilepsy_surgery_referral",
        "ecg",
        "mri",
        "assessment_of_mental_health_issues",
        "mental_health_support",
        "sodium_valproate",
        "comprehensive_care_planning_agreement",
        "patient_held_individualised_epilepsy_document",
        "patient_carer_parent_agreement_to_the_care_planning",
        "care_planning_has_been_updated_when_necessary",
        "comprehensive_care_planning_content",
        "parental_prolonged_seizures_care_plan",
        "water_safety",
        "first_aid",
        "general_participation_and_risk",
        "service_contact_details",
        "sudep",
        "school_individual_healthcare_plan",
    ]

    aggregation_fields = {}

    if kpi_measure:
        # a single measure selected for aggregation

        q_objects = Q(**{f"registration__kpi__{kpi_measure}__lt": 2}) & Q(
            **{f"registration__kpi__{kpi_measure}__isnull": False}
        )
        f_objects = F(f"registration__kpi__{kpi_measure}")

        # sum this measure
        aggregation_fields[f"{kpi_measure}"] = Sum(
            DJANGO_CASE(When(q_objects, then=f_objects), default=None)
        )
        # average of the sum of this measure
        aggregation_fields[f"{kpi_measure}_average"] = Avg(
            DJANGO_CASE(When(q_objects, then=f_objects), default=None)
        )

        # total cases scored for this measure
        aggregation_fields["total_number_of_cases"] = Count(
            DJANGO_CASE(When(q_objects, then=f_objects), default=None)
        )
    else:
        # aggregate all measures

        for measure in all_kpi_measures:
            # filter cases for all kpi with a score < 2
            q_objects = Q(**{f"registration__kpi__{measure}__lt": 2}) & Q(
                **{f"registration__kpi__{measure}__isnull": False}
            )  # & Q(**{f'registration__kpi__{measure}__isnull': False})
            f_objects = F(f"registration__kpi__{measure}")

            # sum this measure
            aggregation_fields[f"{measure}"] = Sum(
                DJANGO_CASE(When(q_objects, then=f_objects), default=0)
            )
            # average of the sum of this measure
            aggregation_fields[f"{measure}_average"] = Avg(
                DJANGO_CASE(When(q_objects, then=f_objects), default=None)
            )
            # total cases scored for this measure
            aggregation_fields[f"{measure}_total"] = Count(
                DJANGO_CASE(When(q_objects, then=f_objects), default=None)
            )
        # total_cases scored for all measures
        aggregation_fields["total_number_of_cases"] = Count(
            "registration__pk", default=None
        )

    return filtered_cases.aggregate(**aggregation_fields)


def return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
    cohort,
    abstraction_level: Literal[
        "organisation", "trust", "icb", "nhs_region", "open_uk", "country", "national"
    ] = "organisation",
    kpi_measure=None,
):
    """
    Returns aggregated KPIS for given cohort annotated by sublevel of abstraction (eg kpis in each NHS England region, labelled by region)
    """
    Case = apps.get_model("epilepsy12", "Case")

    if abstraction_level == "organisation":
        abstraction_sublevels = get_all_organisations()

    if abstraction_level == "trust":
        abstraction_sublevels = get_all_trusts()

    if abstraction_level == "icb":
        abstraction_sublevels = get_all_icbs()

    if abstraction_level == "nhs_region":
        abstraction_sublevels = get_all_nhs_regions()

    if abstraction_level == "open_uk":
        abstraction_sublevels = get_all_open_uk_regions()

    if abstraction_level == "country":
        abstraction_sublevels = get_all_countries()

    # if abstraction_level == 'national':
    #     abstraction_sublevels = get_all_countries()
    #     abstraction_sublevel_Q = Q(site__organisation__CountryONSCode=abstraction_sublevel[0])
    # NOT NEEDED AS COVERED BY  ALL ORGANISATIONS

    final_object = []
    for abstraction_sublevel in abstraction_sublevels:
        if abstraction_level == "organisation":
            abstraction_sublevel_Q = Q(
                site__organisation__ODSCode=abstraction_sublevel.ODSCode
            )
            label = abstraction_sublevel.ODSCode
        if abstraction_level == "trust":
            abstraction_sublevel_Q = Q(
                site__organisation__ParentOrganisation_ODSCode=abstraction_sublevel.ParentOrganisation_ODSCode
            )
            label = abstraction_sublevel.ParentOrganisation_OrganisationName
        if abstraction_level == "icb":
            abstraction_sublevel_Q = Q(
                site__organisation__integrated_care_board__ODS_ICB_Code=abstraction_sublevel.ODS_ICB_Code
            )
            label = abstraction_sublevel.ICB_Name
        if abstraction_level == "nhs_region":
            abstraction_sublevel_Q = Q(
                site__organisation__nhs_region__NHS_Region_Code=abstraction_sublevel.NHS_Region_Code
            )
            label = abstraction_sublevel.NHS_Region
        if abstraction_level == "open_uk":
            abstraction_sublevel_Q = Q(
                site__organisation__openuk_network__OPEN_UK_Network_Code=abstraction_sublevel.OPEN_UK_Network_Code
            )
            label = abstraction_sublevel.OPEN_UK_Network_Name
        if abstraction_level == "country":
            abstraction_sublevel_Q = Q(
                site__organisation__ons_region__ons_country__Country_ONS_Code=abstraction_sublevel.Country_ONS_Code
            )
            label = abstraction_sublevel.Country_ONS_Name

        filtered_cases = Case.objects.filter(
            Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            & abstraction_sublevel_Q
            & Q(registration__cohort=cohort)
        )
        aggregated_kpis = aggregate_all_eligible_kpi_fields(
            filtered_cases, kpi_measure=kpi_measure
        )
        final_object.append(
            {
                "region": label,
                "aggregated_kpis": aggregated_kpis,
                "color": "#808080"
                if aggregated_kpis[kpi_measure] is None
                else "#000000",
            }
        )

    return final_object
