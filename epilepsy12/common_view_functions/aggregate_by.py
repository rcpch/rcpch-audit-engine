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
from epilepsy12.constants import ETHNICITIES, SEX_TYPE, EnumAbstractionLevel

from epilepsy12.common_view_functions import (
    calculate_kpis,
)
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


def _get_queryobjects_from_sublevel(
    abstraction_level: Literal[
        "organisation", "trust", "icb", "nhs_region", "open_uk", "country", "national"
    ],
    sublevel,
) -> Q:
    """Returns a sublevel Q object for a given abstraction level"""

    if abstraction_level == "organisation":
        sublevel_Q = Q(site__organisation__ODSCode=sublevel.ODSCode)

    if abstraction_level == "trust":
        sublevel_Q = Q(
            site__organisation__ParentOrganisation_ODSCode=sublevel.ParentOrganisation_ODSCode
        )

    if abstraction_level == "icb":
        sublevel_Q = Q(
            site__organisation__integrated_care_board__ODS_ICB_Code=sublevel.ODS_ICB_Code
        )

    if abstraction_level == "nhs_region":
        sublevel_Q = Q(
            site__organisation__nhs_region__NHS_Region_Code=sublevel.NHS_Region_Code
        )

    if abstraction_level == "open_uk":
        sublevel_Q = Q(
            site__organisation__openuk_network__OPEN_UK_Network_Code=sublevel.OPEN_UK_Network_Code
        )

    if abstraction_level == "country":
        sublevel_Q = Q(
            site__organisation__ons_region__ons_country__Country_ONS_Code=sublevel.Country_ONS_Code
        )

    return sublevel_Q


def _get_abstraction_sublevels_from_level(abstraction_level: str) -> list:
    """Returns a list of (label, subunitEntity)"""

    Organisation = apps.get_model("epilepsy12", "Organisation")
    if abstraction_level == "organisation":
        sublevels = Organisation.objects.order_by(
            "OrganisationName", "ODSCode"
        ).distinct()
        labels = [entity.ODSCode for entity in sublevels]
    elif abstraction_level == "trust":
        sublevels = Organisation.objects.order_by(
            "ParentOrganisation_OrganisationName", "ParentOrganisation_ODSCode"
        ).distinct()
        labels = [entity.ParentOrganisation_ODSCode for entity in sublevels]
    elif abstraction_level == "icb":
        sublevels = get_all_icbs()
        labels = [entity.ICB_Name for entity in sublevels]
    elif abstraction_level == "nhs_region":
        sublevels = get_all_nhs_regions()
        labels = [entity.NHS_Region for entity in sublevels]
    elif abstraction_level == "open_uk":
        sublevels = get_all_open_uk_regions()
        labels = [entity.OPEN_UK_Network_Name for entity in sublevels]
    elif abstraction_level == "country":
        sublevels = get_all_countries()
        labels = [entity.Country_ONS_Name for entity in sublevels]

    return [(label, sublevel) for label, sublevel in zip(labels, sublevels)]


def get_filtered_cases_by_abstraction(
    abstraction_level: Literal[
        "organisation", "trust", "icb", "nhs_region", "open_uk", "country", "national"
    ],
    cohort: int,
) -> list[dict]:
    """Returns a list of dicts of {label,filtered cases} for abstraction, labelled per each sub-unit of that abstraction."""

    Case = apps.get_model("epilepsy12", "Case")
    filtered_cases_per_subunit = []

    # Get list of label, subunit entity for this abstraction
    subunits = _get_abstraction_sublevels_from_level(abstraction_level)

    for unit in subunits:
        label, entity = unit

        q_obj = _get_queryobjects_from_sublevel(abstraction_level, sublevel=entity)

        filtered_cases = Case.objects.filter(
            Q(site__site_is_actively_involved_in_epilepsy_care=True)
            & Q(site__site_is_primary_centre_of_epilepsy_care=True)
            & q_obj
            & Q(registration__cohort=cohort)
        )

        filtered_cases_per_subunit.append(
            {"region": label, "filtered_cases": filtered_cases}
        )

    return filtered_cases_per_subunit


def get_kpi_value_counts(filtered_cases, kpi_measures: list[str] = None) -> dict:
    """Takes in a QuerySet[Cases] and list of selected kpi measure names, calculates an aggregate value count, and returns a dict of value counts, which can be used to update the KPIAggregation model.

    Args:
        filtered_cases (QuerySet[Case]): QuerySet of filtered Cases on which to perform aggregation queries.
        kpi_measures (list): list of KPI measures for which to aggregate. If not supplied, default will use all KPI Measures.
    """

    final_aggregation_dict = {}

    # Get models
    KPI = apps.get_model("epilepsy12", "KPI")

    # To get the filtered KPI objects, we use the following defined model relations:
    # Case <~1-2-1~> Registration <~1-2-1~> KPI
    filtered_registration_ids = filtered_cases.values_list("registration__id")
    filtered_kpis = KPI.objects.filter(registration__id__in=filtered_registration_ids)

    if kpi_measures is None:
        kpi_measures = [
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

    for kpi_name in kpi_measures:
        # Creates value counts of each value, per kpi measure, including Nulls (using "*")
        value_counts = filtered_kpis.values(
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

        # For each value count for this kpi, update the final aggregation dict with appropriate values depending on pass, incomplete, ineligible, and finally, total eligible
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


def update_kpi_aggregation_model_using_value_counts(
    value_counts: dict, organisation
) -> None:
    """Updates the KPI Aggregation model using value_counts_dict and chosen Organisation.

    Args
        value_counts (dict) - value_counts dict from `get_kpi_value_counts`
        organisation (Organisation) - instance of Organisation to attach to KPIAggregation model
    """

    KPIAggregation = apps.get_model("epilepsy12", "KPIAggregation")

    KPIAggregation.objects.update_or_create(**value_counts, organisation=organisation)


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


def get_abstraction_key_from(organisation, abstraction_level: EnumAbstractionLevel):
    """For the given abstraction level, will call getattr until the final object's value is returned.

    If attribute can't be found, default return is None. E.g. Welsh hospitals will not have an ICB Code.
    """
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        raise ValueError('EnumAbstractionLevel.NATIONAL should not be used with this function.')
    
    return_object = organisation
    for attribute in abstraction_level.value.split("__"):
        return_object = getattr(return_object, attribute, None)
    return return_object


def get_filtered_cases_queryset_for(
    abstraction_level: EnumAbstractionLevel,
    organisation,
    cohort: int,
):
    """Returns queryset of current audit filtered cases within the same abstraction level.

    Ensures the Case is filtered for an active, primary Site, and in the correct cohort.
    """

    cases_filter_key = f"organisations__{abstraction_level.value}"

    Case = apps.get_model("epilepsy12", "Case")

    # This should just be all cases so no filtering
    if abstraction_level is EnumAbstractionLevel.NATIONAL:
        abstraction_filter = {}
    else:
        abstraction_key = get_abstraction_key_from(
            organisation, abstraction_level=abstraction_level
        )
        abstraction_filter = {cases_filter_key: abstraction_key}

    return Case.objects.filter(
        **abstraction_filter,
        site__site_is_actively_involved_in_epilepsy_care=True,
        site__site_is_primary_centre_of_epilepsy_care=True,
        registration__cohort=cohort,
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
                    DJANGO_CASE(When(**{f"{kpi_name}": 1}, then=1))
                ),
                f"{kpi_name}_total_eligible": Count(
                    DJANGO_CASE(
                        When(Q(**{f"{kpi_name}": 1}) | Q(**{f"{kpi_name}": 0}), then=1)
                    )
                ),
                f"{kpi_name}_ineligible": Count(
                    DJANGO_CASE(When(**{f"{kpi_name}": 2}, then=1))
                ),
                f"{kpi_name}_incomplete": Count(
                    DJANGO_CASE(When(**{f"{kpi_name}": None}, then=1))
                ),
            }
        )

    # Perform aggregation
    kpi_value_counts = (
        KPI.objects.filter(
            registration__id__in=filtered_cases.values_list("registration")
        )  # filter for KPIs associated with filtered cases
        .values(f"organisation__{abstraction_level.value}")  # GROUPBY abstraction level
        .annotate(**aggregate_queries)  # AGGREGATE on each abstraction
        .order_by(
            f"organisation__{abstraction_level.value}"
        )  # To ensure order is always as expected
    )

    return kpi_value_counts


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
            "abstraction_entity_model": "Organisation",
        },
        EnumAbstractionLevel.ICB: {
            "kpi_aggregation_model": "ICBKPIAggregation",
            "abstraction_entity_model": "IntegratedCareBoardEntity",
        },
        EnumAbstractionLevel.NHS_REGION: {
            "kpi_aggregation_model": "NHSRegionKPIAggregation",
            "abstraction_entity_model": "NHSRegionEntity",
        },
        EnumAbstractionLevel.OPEN_UK: {
            "kpi_aggregation_model": "OpenUKKPIAggregation",
            "abstraction_entity_model": "OPENUKNetworkEntity",
        },
        EnumAbstractionLevel.COUNTRY: {
            "kpi_aggregation_model": "CountryKPIAggregation",
            "abstraction_entity_model": "ONSCountryEntity",
        },
    }
    return abstraction_model_map[enum_abstraction_level]


def update_kpi_aggregation_model(
    abstraction_level: EnumAbstractionLevel,
    kpi_value_counts,
    cohort: int,
) -> None:
    """Updates the relevant KPI Aggregation model, chosen via the `abstraction_level`. Takes output of `calculate_kpi_value_counts_queryset` to update model.

    Args:
        abstraction_level (EnumAbstractionLevel): chosen abstraction level
        kpi_value_counts (ValuesQuerySet[Model, Dict[str, Any]]): value counts of KPI scorings, grouped by abstraction
        cohort (int): cohort of aggregation
    """

    abstraction_level_models = get_abstraction_model_from_level(abstraction_level)

    # Get KPIAggregation model for the given abstraction level
    AbstractionKPIAggregationModel = apps.get_model(
        "epilepsy12", abstraction_level_models["kpi_aggregation_model"]
    )

    for value_count in kpi_value_counts:
        ABSTRACTION_CODE = value_count.pop(f"organisation__{abstraction_level.value}")

        # Get the model field name for the given abstraction model. As the enum values are all with respect to Organisation, this split and grab last gets just that related model's related field.
        related_key_field = abstraction_level.value.split("__")[-1]

        # Get related entity model
        abstraction_entity_model = apps.get_model(
            "epilepsy12", abstraction_level_models["abstraction_entity_model"]
        )

        # Get instance of the related entity model to link with Aggregation model
        # NOTE Trust is only abstraction level whose abstraction_relation field is Charfield, not foreign key
        if abstraction_level is EnumAbstractionLevel.TRUST:
            abstraction_relation_instance = ABSTRACTION_CODE
        else:
            abstraction_relation_instance = abstraction_entity_model.objects.filter(
                **{f"{related_key_field}": ABSTRACTION_CODE}
            ).first()

        new_obj, created = AbstractionKPIAggregationModel.objects.update_or_create(
            defaults={
                "abstraction_relation": abstraction_relation_instance,
                "cohort": cohort,
                **value_count,
            },
            abstraction_relation=abstraction_relation_instance,
            cohort=cohort,
        )

        if created:
            print(f"created {new_obj}")
