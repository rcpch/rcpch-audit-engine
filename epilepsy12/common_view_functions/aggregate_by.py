from typing import Literal, Union
from datetime import date
import logging

# Django imports
from django.apps import apps
from django.contrib.gis.db.models import (
    Q,
    F,
    Count,
    When,
    Value,
    CharField,
    PositiveSmallIntegerField,
    Case as DJANGO_CASE,
    ExpressionWrapper,
    IntegerField,
)
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractDay

# E12 imports
from epilepsy12.constants import (
    ETHNICITIES,
    SEX_TYPE,
    EnumAbstractionLevel,
)
from epilepsy12.general_functions import cohorts_and_dates
from epilepsy12.common_view_functions import calculate_kpis

# Logging setup
logger = logging.getLogger(__name__)

# Third party imports

import pandas as pd

"""
Reporting
"""

"""
Aggregations for pie charts
"""


def cases_aggregated_by_sex(selected_organisation):
    # aggregate queries on trust level cases

    Case = apps.get_model("epilepsy12", "Case")

    sex_long_list = [When(sex=k, then=Value(v)) for k, v in SEX_TYPE]

    cases_aggregated_by_sex = (
        Case.objects.filter(
            site__organisation=selected_organisation,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
        )
        .values("sex")
        .annotate(sex_display=DJANGO_CASE(*sex_long_list, output_field=CharField()))
        .values("sex_display")
        .annotate(sexes=Count("sex"))
        .order_by("sexes")
    )

    return cases_aggregated_by_sex


def cases_aggregated_by_age(selected_organisation):
    """
    Aggregates cases by age in days in the selected organisation by age ranges
    - under a year
    - 1 to 5 years
    - 5 to 11 years
    - 11 to 18 years
    """

    Case = apps.get_model("epilepsy12", "Case")

    # Define age ranges in days
    under_a_year = 365
    one_to_five_years = 5 * 365
    five_to_eleven_years = 11 * 365
    eleven_to_eighteen_years = 18 * 365

    # Current date
    today = date.today()

    # Annotate each case with its age in days
    cases_with_age = Case.objects.filter(
        site__organisation=selected_organisation,
        site__site_is_primary_centre_of_epilepsy_care=True,
        site__site_is_actively_involved_in_epilepsy_care=True,
    ).annotate(
        age_in_days=ExpressionWrapper(
            (ExtractYear(today) - ExtractYear(F("date_of_birth"))) * 365
            + (ExtractMonth(today) - ExtractMonth(F("date_of_birth"))) * 30
            + (ExtractDay(today) - ExtractDay(F("date_of_birth"))),
            output_field=IntegerField(),
        )
    )

    # Aggregate cases by age range
    cases_aggregated_by_age_ranges = (
        cases_with_age.annotate(
            age_range=DJANGO_CASE(
                When(
                    age_in_days__isnull=False,
                    age_in_days__lt=under_a_year,
                    then=Value("under_a_year"),
                ),
                When(
                    age_in_days__isnull=False,
                    age_in_days__gte=under_a_year,
                    age_in_days__lt=one_to_five_years,
                    then=Value("one_to_five_years"),
                ),
                When(
                    age_in_days__isnull=False,
                    age_in_days__gte=one_to_five_years,
                    age_in_days__lt=five_to_eleven_years,
                    then=Value("five_to_eleven_years"),
                ),
                When(
                    age_in_days__isnull=False,
                    age_in_days__gte=five_to_eleven_years,
                    age_in_days__lt=eleven_to_eighteen_years,
                    then=Value("eleven_to_eighteen_years"),
                ),
                When(
                    age_in_days__isnull=False,
                    age_in_days__gte=eleven_to_eighteen_years,
                    then=Value("over_eighteen_years"),
                ),
                default=Value("unknown"),
                output_field=CharField(),
            )
        )
        .values("age_range")
        .annotate(count=Count("id"))
        .order_by("age_range")
    )

    # add the display name for each age range
    age_categories = {
        "under_a_year": "Under a year",
        "one_to_five_years": "1 to 5 years",
        "five_to_eleven_years": "5 to 11 years",
        "eleven_to_eighteen_years": "11 to 18 years",
        "over_eighteen_years": "Over 18 years",
    }

    for aggregate in cases_aggregated_by_age_ranges:
        age_range = aggregate["age_range"]

        str_map = age_categories.get(age_range, "Unknown")

        aggregate.update({"age_category_label": str_map})

    return cases_aggregated_by_age_ranges


def cases_aggregated_by_deprivation_score(selected_organisation):
    # aggregate queries on trust level cases
    Case = apps.get_model("epilepsy12", "Case")

    cases_in_selected_organisation = Case.objects.filter(
        site__organisation=selected_organisation,
        site__site_is_primary_centre_of_epilepsy_care=True,
        site__site_is_actively_involved_in_epilepsy_care=True,
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
            site__organisation=selected_organisation,
            site__site_is_primary_centre_of_epilepsy_care=True,
            site__site_is_actively_involved_in_epilepsy_care=True,
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


"""
Filter cases, run aggregations and store results in KPIAggregation models - there is one for each cohort and one for each level of abstraction
"""


def update_all_kpi_agg_models(
    cohort: int,
    abstractions: Union[Literal["all"], list[EnumAbstractionLevel]] = "all",
    open_access=False,
) -> None:
    """
    Using all cases in a given cohort,
        for all abstraction levels | specified `abstractions`,
            aggregate kpi scores and update that abstraction's KPIAggregation model

    Args:
        `cohort` - cohort filter for Cases
        `abstraction` (optional, default='all') - specify abstraction level(s) to update. Provide list of EnumAbstractionLevel values if required.
    """

    if (abstractions != "all") and not isinstance(abstractions, list):
        raise ValueError(
            'Can only be string literal "all" or list of EnumAbstraction values'
        )

    if isinstance(abstractions, list):
        if not all(isinstance(item, EnumAbstractionLevel) for item in abstractions):
            raise ValueError(
                "If providing list, all items must be EnumAbstraction values"
            )

    abstraction_levels = EnumAbstractionLevel if abstractions == "all" else abstractions

    for ABSTRACTION_LEVEL in abstraction_levels:
        """
        Loop through each level of abstraction

        For each level of of abstraction:

        filter all Cases for all sites where
        # site is actively involved in care
        # site is lead centre
        # matched for cohort
        # have completed a full year of epilepsy care
        """

        all_cases = filter_completed_cases_at_one_year_by_abstraction_level(
            abstraction_level=ABSTRACTION_LEVEL, cohort=cohort
        )

        """
        calculate the totals for each KPI
        """

        kpi_value_counts = calculate_kpi_value_counts_queryset(
            filtered_cases=all_cases,
            abstraction_level=ABSTRACTION_LEVEL,
            kpis="all",
        )

        # Update all KPIAggregation models for abstraction
        update_kpi_aggregation_model(
            abstraction_level=ABSTRACTION_LEVEL,
            kpi_value_counts=kpi_value_counts,
            cohort=cohort,
            open_access=open_access,
        )


def calculate_kpi_value_counts_queryset(
    filtered_cases,
    abstraction_level: EnumAbstractionLevel,
    kpis: "list[str] | Literal['all']" = "all",
):
    """For the given filtered_cases queryset, for all KPIs, calculates the value counts, per abstraction level.

    Assumes the filtered_cases already have kpi scores calculated.

    Args
        `filtered_cases` (QuerySet[Case]) - filtered Cases, for which KPI model has already been updated

        `abstraction_level` (EnumAbstractionLevel) - specifies the abstraction level on which to return value counts. E.g. if EnumAbstractionLevel.ORGANISATION, each queryset in the return object will have 'organisation__ODSCode'.

        `kpis` (list[str] or Literal['all']) - Default 'all'. List of KPI model fields to perform aggregation on. If 'all', then all available fields on the KPI model, found using KPI.get_kpis() method, will be used.

    Returns `ValuesQuerySet[KPI, dict[str, any]]`.
    """

    # Get models
    KPI = apps.get_model("epilepsy12", "KPI")

    # Dict of kpi names
    kpi_names = KPI().get_kpis() if kpis == "all" else kpis

    # Initialise aggregation queries dict
    aggregate_queries = {}

    # for each kpi name, eg. 'ecg',
    # create aggregation query to calculate total passed, total eligible, total ineligble, incompelete
    for kpi_name in kpi_names:
        aggregate_queries.update(
            {
                f"{kpi_name}_passed": Count(
                    DJANGO_CASE(
                        When(**{f"{kpi_name}": 1}, then=1),
                    ),
                ),
                f"{kpi_name}_total_eligible": Count(
                    DJANGO_CASE(
                        When(Q(**{f"{kpi_name}": 1}) | Q(**{f"{kpi_name}": 0}), then=1),
                    )
                ),
                f"{kpi_name}_ineligible": Count(
                    DJANGO_CASE(
                        When(**{f"{kpi_name}": 2}, then=1),
                    ),
                ),
                f"{kpi_name}_incomplete": Count(
                    DJANGO_CASE(
                        When(**{f"{kpi_name}": None}, then=1),
                    ),
                ),
            }
        )

    # Perform aggregation
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        # NO NEED TO GROUPBY IF NATIONAL
        kpi_value_counts = KPI.objects.filter(
            registration__id__in=filtered_cases.values_list("registration"),
        ).aggregate(**aggregate_queries)
    else:
        kpi_value_counts = (
            KPI.objects.filter(
                registration__id__in=filtered_cases.values_list("registration")
            )  # filter for KPIs associated with filtered cases
            .values(
                f"organisation__{abstraction_level.value}"
            )  # GROUPBY abstraction level
            .annotate(**aggregate_queries)  # AGGREGATE on each abstraction
            .order_by(
                f"organisation__{abstraction_level.value}"
            )  # To ensure order is always as expected
        )

    return kpi_value_counts


def update_kpi_aggregation_model(
    abstraction_level: EnumAbstractionLevel,
    kpi_value_counts,
    cohort: int,
    open_access=False,
) -> None:
    """Updates the relevant KPI Aggregation model, chosen via the `abstraction_level`. Takes output of `calculate_kpi_value_counts_queryset` to update model.

    Args:
        abstraction_level (EnumAbstractionLevel): chosen abstraction level
        kpi_value_counts (ValuesQuerySet[Model, Dict[str, Any]]): value counts of KPI scorings, grouped by abstraction
        cohort (int): cohort of aggregation
        open_access: boolean - whether publicly viewable or not. Defaults to False

        If open_access is true, a new KPI aggregation record is created, to store historical publications.
        If open_access is false, the existing KPI aggregation is updated
    """

    abstraction_level_models = get_abstraction_model_from_level(abstraction_level)

    # Get KPIAggregation model for the given abstraction level
    AbstractionKPIAggregationModel = apps.get_model(
        "epilepsy12", abstraction_level_models["kpi_aggregation_model"]
    )

    list_of_updated_abstraction_level_instance = []

    # Separate logic for national as no groupby key in aggregation value counts
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")
        if open_access:
            # create a new record
            new_obj = NationalKPIAggregation.objects.create(
                **kpi_value_counts,
                **{
                    "cohort": cohort,
                    "open_access": open_access,
                },
            )
            logger.debug(f"created {new_obj}")
            return

        else:
            try:
                new_obj, created = NationalKPIAggregation.objects.update_or_create(
                    defaults={
                        "cohort": cohort,
                        "open_access": open_access,
                        **kpi_value_counts,
                    },
                    cohort=cohort,
                    open_access=open_access,
                )
                if created:
                    logger.debug(f"created {new_obj}")
                else:
                    logger.debug(f"updated {new_obj}")
            except Exception as error:
                logger.exception(f"Unable to save National KPIAggregation: {error}")

        return

    # update models where numbers have changed.
    for value_count in kpi_value_counts:
        ABSTRACTION_CODE = value_count.pop(f"organisation__{abstraction_level.value}")
        if ABSTRACTION_CODE is None:
            # we don't have any values for this abstraction level (eg local health board only applies in Wales not England)
            return

        # Get the model field name for the given abstraction model. As the enum values are all with respect to Organisation, this split and grab last gets just that related model's related field.
        related_key_field = abstraction_level.value.split("__")[-1]

        # Get related entity model
        abstraction_entity_model = apps.get_model(
            "epilepsy12", abstraction_level_models["abstraction_entity_model"]
        )

        # Get instance of the related entity model to link with Aggregation model
        abstraction_relation_instance = abstraction_entity_model.objects.filter(
            **{f"{related_key_field}": ABSTRACTION_CODE}
        ).first()

        # store this instance in a temporary list - this is used to identify remaining unscored abstraction level records
        list_of_updated_abstraction_level_instance.append(abstraction_relation_instance)

        if open_access:
            # for public view: create a new record

            value_count["abstraction_relation"] = abstraction_relation_instance
            value_count["cohort"] = cohort
            value_count["open_access"] = open_access

            try:
                new_obj = AbstractionKPIAggregationModel.objects.create(**value_count)
                logger.debug(f"created {new_obj}")
            except Exception as error:
                logger.exception(
                    f"Can't save new KPIAggregations for {abstraction_level} for {abstraction_relation_instance}: {error}"
                )
                return

        else:
            # not for public view - create or update existing
            try:
                (
                    new_obj,
                    created,
                ) = AbstractionKPIAggregationModel.objects.update_or_create(
                    defaults={
                        "abstraction_relation": abstraction_relation_instance,
                        "cohort": cohort,
                        "open_access": False,
                        **value_count,
                    },
                    abstraction_relation=abstraction_relation_instance,
                    cohort=cohort,
                    open_access=open_access,
                )
                logger.debug(f"updating/saving: {abstraction_relation_instance}")
            except Exception as error:
                logger.exception(
                    f"CLOSED VIEW: Can't update/save KPIAggregations for {abstraction_level} for {abstraction_relation_instance}: {error}"
                )
                return

            if created:
                logger.debug(f"created {new_obj}")
            else:
                logger.debug(f"updated {new_obj}")

    logger.debug(
        f"{len(list_of_updated_abstraction_level_instance)} scored {abstraction_level.name} instances updated with aggregated scores of a total {AbstractionKPIAggregationModel.objects.filter(cohort=cohort).count()} {abstraction_level.name}s"
    )

    not_updated = AbstractionKPIAggregationModel.objects.exclude(
        abstraction_relation__in=list_of_updated_abstraction_level_instance
    ).filter(cohort=cohort)

    if not_updated.count() > 0:
        logger.debug(
            f"Not updated: {list(not_updated.values_list('abstraction_name'))})"
        )


def filter_completed_cases_at_one_year_by_abstraction_level(
    abstraction_level: EnumAbstractionLevel, cohort: int
):
    """
    Filters all cases for a given abstraction level and cohort
    Cases returned are for all children registered at lead sites actively involve in care, a full year has been completed and all cases have been fully scored.

    NOTE: this step is used as a filter query prior to performing aggregations and persisting results in the KPIAggregations tables
    """
    Case = apps.get_model("epilepsy12", "Case")
    if abstraction_level == EnumAbstractionLevel.NATIONAL:
        # no filters required for National level data
        abstraction_filter = None
    else:
        abstraction_filter = {
            f"site__organisation__{abstraction_level.value}__isnull": False
        }

    all_cases = Case.objects.filter(
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
        registration__id__isnull=False,
        registration__cohort=cohort,
        registration__completed_first_year_of_care_date__lte=date.today(),
        registration__audit_progress__registration_complete=True,
        registration__audit_progress__first_paediatric_assessment_complete=True,
        registration__audit_progress__assessment_complete=True,
        registration__audit_progress__epilepsy_context_complete=True,
        registration__audit_progress__multiaxial_diagnosis_complete=True,
        registration__audit_progress__investigations_complete=True,
        registration__audit_progress__management_complete=True,
    )

    if abstraction_filter:
        return all_cases.filter(**abstraction_filter)
    return all_cases


"""
Get KPIAggregation data from tables
"""


def get_filtered_cases_queryset_for(
    abstraction_level: EnumAbstractionLevel, organisation, cohort: int
):
    """Returns queryset of current audit filtered cases within the same abstraction level.

    Ensures the Case is filtered for an active, primary Site, and in the correct cohort, and all cases are completely scored and have completed a full year of care
    NOTE as this is confusing. It is NOT used in any aggregation calculation steps prior to updating KPIAggregation models. It is only used to pull existing data from KPIAggregation tables
    It is also used in the test suite.
    """

    cases_filter_key = f"organisations__{abstraction_level.value}"

    Case = apps.get_model("epilepsy12", "Case")

    # This should just be all cases so no filtering based on code
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        abstraction_filter = {}
    else:
        abstraction_key = get_abstraction_value_from(
            organisation, abstraction_level=abstraction_level
        )

        # Some organisations have null values for abstraction e.g. Welsh Orgs don't have ICBs; English orgs don't have  LHBs. Therefore, should return no Cases
        if abstraction_key is None:
            return Case.objects.none()

        abstraction_filter = {cases_filter_key: abstraction_key}

    cases = Case.objects.filter(
        **abstraction_filter,
        # site__organisation__country__boundary_identifier="E92000001",
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
        registration__cohort=cohort,
        registration__completed_first_year_of_care_date__lte=date.today(),
        registration__audit_progress__registration_complete=True,
        registration__audit_progress__first_paediatric_assessment_complete=True,
        registration__audit_progress__assessment_complete=True,
        registration__audit_progress__epilepsy_context_complete=True,
        registration__audit_progress__multiaxial_diagnosis_complete=True,
        registration__audit_progress__investigations_complete=True,
        registration__audit_progress__management_complete=True,
    )

    return cases


def get_all_kpi_aggregation_data_for_view(
    organisation,
    cohort: int,
    kpis: "list[str] | Literal['all']" = "all",
    open_access=False,
) -> dict:
    """
    Pulls KPI data stored in the KPIAggregation tables, for each level of EnumAbstractionLevel abstraction,
    updates the relevant AbstractionModel and returns the KPI model as a dict.

    """

    ALL_DATA = {}
    for enum_abstraction_level in EnumAbstractionLevel:
        # For the given abstraction, get the {ABSTRACTION}KPIAggregation model
        abstraction_kpi_agg_model_name = get_abstraction_model_from_level(
            enum_abstraction_level
        )["kpi_aggregation_model"]
        abstraction_kpi_agg_model = apps.get_model(
            "epilepsy12", abstraction_kpi_agg_model_name
        )

        # Get THIS organisation instance's abstraction relation entity. All the enum values are with respect to Organisation, thus the first element of .split('__') is the related field.
        abstraction_relation_field_name = enum_abstraction_level.value.split("__")[0]

        if enum_abstraction_level is EnumAbstractionLevel.ORGANISATION:
            abstraction_relation = organisation
        else:
            abstraction_relation = getattr(
                organisation, f"{abstraction_relation_field_name}"
            )

        # NationalKPIAggregation model does not have abstraction relation field, so handle differently to the rest and skip rest of loop
        NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")
        if abstraction_kpi_agg_model == NationalKPIAggregation:
            if (
                abstraction_kpi_agg_model.objects.filter(
                    cohort=cohort, open_access=open_access
                )
                .order_by("-last_updated")
                .first()
                is None
            ):
                total_registered = 0
            else:
                total_registered = (
                    abstraction_kpi_agg_model.objects.filter(
                        cohort=cohort, open_access=open_access
                    )
                    .order_by("-last_updated")
                    .first()
                    .get_total_cases_included_in_aggregation()
                )

            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": abstraction_kpi_agg_model.objects.filter(
                    cohort=cohort, open_access=open_access
                )
                .order_by("-last_updated")
                .first(),
                "total_cases_registered": total_registered,
            }
            continue

        # Check if KPIAggregation model exists. If Organisation does not have any cases where that Organisation is primary care Site, then the KPIAgg will not exist.
        if abstraction_kpi_agg_model.objects.filter(
            abstraction_relation=abstraction_relation,
            cohort=cohort,
            open_access=open_access,
        ).exists():
            aggregation_model_instance = (
                abstraction_kpi_agg_model.objects.filter(
                    abstraction_relation=abstraction_relation,
                    cohort=cohort,
                    open_access=open_access,
                )
                .order_by("-last_updated")
                .first()
            )
            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": aggregation_model_instance,
                "total_cases_registered": aggregation_model_instance.get_total_cases_included_in_aggregation(),
            }
        else:
            filtered_cases = get_filtered_cases_queryset_for(
                organisation=organisation,
                abstraction_level=enum_abstraction_level,
                cohort=cohort,
            )

            ALL_DATA[f"{enum_abstraction_level.name}_KPIS"] = {
                "aggregation_model": None,
                "total_cases_registered": filtered_cases.count(),
            }

    return ALL_DATA


"""
Helper functions
"""


def get_abstraction_value_from(organisation, abstraction_level: EnumAbstractionLevel):
    """For the given abstraction level, will call getattr until the final object's value is returned.

    If attribute can't be found, default return is None. E.g. Welsh hospitals will not have an ICB Code.
    """
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        raise ValueError(
            "EnumAbstractionLevel.NATIONAL should not be used with this function."
        )

    return_object = organisation
    for attribute in abstraction_level.value.split("__"):
        return_object = getattr(return_object, attribute, None)
    return return_object


def get_abstraction_model_from_level(
    enum_abstraction_level: EnumAbstractionLevel,
) -> dict:
    """Returns dict, for abstraction, of structure:

    {
        "kpi_aggregation_model": abstractionKPIAggregation model name (str),
        "abstraction_entity_model": that KPIAggregation's abstraction_relation entity model's name (str)
    }
    """
    abstraction_model_map = {
        EnumAbstractionLevel.ORGANISATION: {
            "kpi_aggregation_model": "OrganisationKPIAggregation",
            "abstraction_entity_model": "Organisation",
        },
        EnumAbstractionLevel.TRUST: {
            "kpi_aggregation_model": "TrustKPIAggregation",
            "abstraction_entity_model": "Trust",
        },
        EnumAbstractionLevel.LOCAL_HEALTH_BOARD: {
            "kpi_aggregation_model": "LocalHealthBoardKPIAggregation",
            "abstraction_entity_model": "LocalHealthBoard",
        },
        EnumAbstractionLevel.ICB: {
            "kpi_aggregation_model": "ICBKPIAggregation",
            "abstraction_entity_model": "IntegratedCareBoard",
        },
        EnumAbstractionLevel.NHS_ENGLAND_REGION: {
            "kpi_aggregation_model": "NHSEnglandRegionKPIAggregation",
            "abstraction_entity_model": "NHSEnglandRegion",
        },
        EnumAbstractionLevel.OPEN_UK: {
            "kpi_aggregation_model": "OpenUKKPIAggregation",
            "abstraction_entity_model": "OPENUKNetwork",
        },
        EnumAbstractionLevel.COUNTRY: {
            "kpi_aggregation_model": "CountryKPIAggregation",
            "abstraction_entity_model": "Country",
        },
        EnumAbstractionLevel.NATIONAL: {
            "kpi_aggregation_model": "NationalKPIAggregation",
            "abstraction_entity_model": "Country",
        },
    }
    return abstraction_model_map[enum_abstraction_level]


def _calculate_all_kpis():
    """
    Loops through all registered cases for all cohorts and reruns the KPI calculation for each one
    """
    Case = apps.get_model("epilepsy12", "Case")
    all_cases = Case.objects.filter(registration__isnull=False)
    index = 0
    for case in all_cases:
        try:
            calculate_kpis(case.registration)
            logger.debug(f"KPIs recalculated for {case}")
            index += 1
        except Exception as error:
            logger.error(
                f"It was not possible to calculate and update KPI record for {case}: {error}"
            )
            continue
    logger.info(f"{index} cases updated from a total of {all_cases.count()}")


"""
Sets up the KPIAggregation models - one for each cohort and each level of abstraction
Function also to delete them
"""


def _seed_all_aggregation_models(cohort=None) -> None:
    """
    Seeds all KPIAggregation models for each level of abstraction, for requested cohort
    If no cohort supplied, defaults to currently recruiting cohort
    """

    Organisation = apps.get_model("epilepsy12", "Organisation")
    OrganisationKPIAggregation = apps.get_model(
        "epilepsy12", "OrganisationKPIAggregation"
    )

    Trust = apps.get_model("epilepsy12", "Trust")
    TrustKPIAggregation = apps.get_model("epilepsy12", "TrustKPIAggregation")

    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    LocalHealthBoardKPIAggregation = apps.get_model(
        "epilepsy12", "LocalHealthBoardKPIAggregation"
    )

    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    ICBKPIAggregation = apps.get_model("epilepsy12", "ICBKPIAggregation")

    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    NHSEnglandRegionKPIAggregation = apps.get_model(
        "epilepsy12", "NHSEnglandRegionKPIAggregation"
    )

    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    OpenUKKPIAggregation = apps.get_model("epilepsy12", "OpenUKKPIAggregation")

    Country = apps.get_model("epilepsy12", "Country")
    CountryKPIAggregation = apps.get_model("epilepsy12", "CountryKPIAggregation")

    NationalKPIAggregation = apps.get_model("epilepsy12", "NationalKPIAggregation")

    if cohort:
        requested_cohort = cohort
    else:
        cohort = cohorts_and_dates(
            first_paediatric_assessment_date=date.today()
        )  # gets current recruiting and submitting cohorts
        requested_cohort = cohort["currently_recruiting_cohort"]

    all_orgs = Organisation.objects.all().distinct()
    all_trusts = Trust.objects.all().distinct()
    all_local_health_boards = LocalHealthBoard.objects.all()
    all_icbs = IntegratedCareBoard.objects.all().distinct()
    all_nhs_regions = NHSEnglandRegion.objects.all().distinct()
    all_open_uks = OPENUKNetwork.objects.all().distinct()
    all_countries = Country.objects.all().distinct()

    all_entities = [
        all_orgs,
        all_trusts,
        all_local_health_boards,
        all_icbs,
        all_nhs_regions,
        all_open_uks,
        all_countries,
    ]
    all_agg_models = [
        OrganisationKPIAggregation,
        TrustKPIAggregation,
        LocalHealthBoardKPIAggregation,
        ICBKPIAggregation,
        NHSEnglandRegionKPIAggregation,
        OpenUKKPIAggregation,
        CountryKPIAggregation,
        NationalKPIAggregation,
    ]

    if len(all_entities) + 1 != len(all_agg_models):
        logger.error(
            f"Incorrect lengths for entities. KPIAggregations not seeded. {len(all_entities)+1=}{len(all_agg_models)=}"
        )
        return

    for entities, AggregationModel in zip(all_entities, all_agg_models):
        logger.info(f"Creating aggregations for {AggregationModel}")
        for entity in entities:
            if AggregationModel.objects.filter(
                abstraction_relation=entity,
                cohort=requested_cohort,
            ).exists():
                logger.info(
                    f"AggregationModel for {entity} already exists. Skipping..."
                )
                continue

            new_agg_model = AggregationModel.objects.create(
                abstraction_relation=entity,
                cohort=requested_cohort,
            )

            logger.info(f"Created {new_agg_model}")

    # National handled separately as it has no abstraction relation field
    if NationalKPIAggregation.objects.filter(
        cohort=requested_cohort,
    ).exists():
        logger.info(f"NationalKPIAggregation for {entity} already exists. Skipping...")
    else:
        new_agg_model = NationalKPIAggregation.objects.create(
            cohort=requested_cohort,
        )
        logger.info(f"Created {new_agg_model} (Cohort {requested_cohort})")


def ___delete_and_recreate_all_kpi_aggregation_models():
    """WARNING: DESTRUCTIVE FUNCTION, only for use in local dev environments.

    This 'wipes clean' the KPIAggregation models - it first deletes all models, then it creates new, empty ones where values are none.

    Its purpose is for internal testing.
    """

    ALL_AGGREGATION_MODEL_NAMES = [
        "OrganisationKPIAggregation",
        "TrustKPIAggregation",
        "LocalHealthBoardKPIAggregation",
        "ICBKPIAggregation",
        "NHSEnglandRegionKPIAggregation",
        "OpenUKKPIAggregation",
        "CountryKPIAggregation",
        "NationalKPIAggregation",
    ]

    for aggregation_model_name in ALL_AGGREGATION_MODEL_NAMES:
        aggregation_model = apps.get_model("epilepsy12", aggregation_model_name)

        aggregation_model.objects.all().delete()

    _seed_all_aggregation_models()


"""
Functions to create Excel reports
"""


def create_kpi_report_row(key, kpi_field, aggregation_row, level):
    kpi = kpi_field.name
    measure = kpi_field.help_text["label"]

    ret = {
        level: key,
        "Measure": measure,
    }

    if aggregation_row:
        numerator = aggregation_row[f"{kpi}_passed"]
        denominator = aggregation_row[f"{kpi}_total_eligible"]

        if numerator is not None and denominator is not None:
            # Make sure we don't divide by zero
            ret["Percentage"] = 0 if denominator == 0 else (numerator / denominator)
            ret["Numerator"] = numerator
            ret["Denominator"] = denominator

        if numerator is None:
            logger.info(f"Missing numerator for {key} {measure} {kpi}")

        if denominator is None:
            logger.info(f"Missing denominator for {key} {measure} {kpi}")

    return ret


def get_kpi_aggregation_rows(
    model_aggregation,
    cohort,
    abstraction_key_field=None,
):
    query = model_aggregation.objects.filter(cohort=cohort, open_access=False)

    if abstraction_key_field:
        query = query.annotate(
            key_field=F(f"abstraction_relation__{abstraction_key_field}")
        )

    # Eagerly evaluate the query as we use some result sets twice in kpi.py
    # Otherwise we'd have to re-run the query to avoid getting empty results
    # the second time we try and use it.
    return list(query.values())


def create_KPI_aggregation_dataframe(
    aggregation_rows,
    measures,
    title,
):
    final_list = []

    for measure in measures:
        for aggregation_row in aggregation_rows:
            report_row = create_kpi_report_row(
                aggregation_row["key_field"], measure, aggregation_row, title
            )

            final_list.append(report_row)

    return pd.DataFrame.from_dict(final_list)


def create_reference_dataframe(trusts, health_boards, networks, icbs, totals=False):
    """
    INPUTS:
    - trusts: TRUSTS should be passed in. Contains a list of trust objects
    - health_boards: LOCAL_HEALTH_BOARDS should be passed in. Contains a list of local health board objects
    - networks: OPEN_UK_NETWORK_TRUSTS should be passed in. Contains a list of trusts and their ods codes
    - icbs: INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES should be passed in. Contains a list of ICBs, with their trusts and ods codes

    BODY - Create Reference sheet containing all trusts and health boards with their respective networks, ods codes, countries, NHS regions and ICBs

    OUTPUT - Dataframe containing list of trusts and health boards and their organisational relationships; columns specified as HBT, HBT_name, Network, Country, UK, NHSregion and ICB
    """

    final_list = []

    # For Welsh health boards - create row with HBT, HBT_name, Network, Country, UK, NHSregion and ICB as the column names
    for health_board in health_boards:
        ods_code = health_board["ods_code"]
        health_board_name = health_board["health_board"]
        network_name = ""

        for network in networks:
            if ods_code == network["ods trust code"]:
                network_name = network["OPEN UK Network Code"]

        item = {
            "HBT": ods_code,
            "HBT_name": health_board_name,
            "Network": network_name,
            "Country": "Wales",
            "UK": "England and Wales",
            "NHSregion": "",
            "ICB": "",
        }

        final_list.append(item)

    # For the English Trusts - create row with HBT, HBT_name, Network, Country, UK, NHSregion and ICB as the column names
    for trust in trusts:
        ods_code = trust["ods_code"]
        trust_name = trust["name"]
        network_name = ""
        region = ""
        icb = ""

        for network in networks:
            if ods_code == network["ods trust code"]:
                network_name = network["OPEN UK Network Code"]

        for board in icbs:
            if ods_code == board["ODS Trust Code"]:
                icb = board["ICB Name"]
                region = board["NHS England Region"]
                if region == "Midlands (Y60)":
                    region = "Midlands"

        item = {
            "HBT": ods_code,
            "HBT_name": trust_name,
            "Network": network_name,
            "Country": "England",
            "UK": "England and Wales",
            "NHSregion": region,
            "ICB": icb,
        }

        final_list.append(item)

    return pd.DataFrame.from_dict(final_list)


def create_totals_dataframe(cohort, abstraction_level):
    """
    create a dataframe for all organisations with totals of all registered cases vs cases included in aggregation
    """

    from ..common_view_functions import (
        all_registered_cases_for_cohort_and_abstraction_level,
    )

    Organisation = apps.get_model("epilepsy12", "Organisation")
    Trust = apps.get_model("epilepsy12", "Trust")
    LocalHealthBoard = apps.get_model("epilepsy12", "LocalHealthBoard")
    IntegratedCareBoard = apps.get_model("epilepsy12", "IntegratedCareBoard")
    NHSEnglandRegion = apps.get_model("epilepsy12", "NHSEnglandRegion")
    OPENUKNetwork = apps.get_model("epilepsy12", "OPENUKNetwork")
    Country = apps.get_model("epilepsy12", "Country")

    abs_level = []

    if abstraction_level == "trust":
        query_set = Trust.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)
    elif abstraction_level == "local_health_board":
        query_set = LocalHealthBoard.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)
    elif abstraction_level == "icb":
        query_set = IntegratedCareBoard.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)
    elif abstraction_level == "nhs_england_region":
        query_set = NHSEnglandRegion.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)
    elif abstraction_level == "open_uk":
        query_set = OPENUKNetwork.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)
    elif abstraction_level == "country":
        query_set = Country.objects.annotate(
            organisation_count=Count("organisation")
        ).filter(organisation_count__gt=0)

    for abstraction_item in query_set:
        if abstraction_level == "trust":
            organisation_instance = Organisation.objects.filter(
                trust=abstraction_item, active=True
            ).first()
        elif abstraction_level == "local_health_board":
            organisation_instance = Organisation.objects.filter(
                local_health_board=abstraction_item, active=True
            ).first()
        elif abstraction_level == "icb":
            organisation_instance = Organisation.objects.filter(
                integrated_care_board=abstraction_item, active=True
            ).first()
        elif abstraction_level == "nhs_england_region":
            organisation_instance = Organisation.objects.filter(
                nhs_england_region=abstraction_item, active=True
            ).first()
        elif abstraction_level == "open_uk":
            organisation_instance = Organisation.objects.filter(
                openuk_network=abstraction_item, active=True
            ).first()
        elif abstraction_level == "country":
            organisation_instance = Organisation.objects.filter(
                country=abstraction_item, active=True
            ).first()

        all_cases = all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation_instance,
            cohort=cohort,
            case_complete=False,
            abstraction_level=abstraction_level,
        ).count()
        all_registered_cases = all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=organisation_instance,
            cohort=cohort,
            case_complete=True,
            abstraction_level=abstraction_level,
        ).count()

        abs_level.append(
            {
                "Name": abstraction_item.name,
                "All Registered Cases": all_registered_cases,
                "All Cases": all_cases,
                "Percentage": (
                    round((all_registered_cases / all_cases) * 100, 1)
                    if all_cases > 0
                    else 0
                ),
            }
        )

    return pd.DataFrame.from_dict(abs_level)
