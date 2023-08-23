# Python/Django imports

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse

# third party libraries
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import Sum

# E12 imports
from django.apps import apps
from ..decorator import user_may_view_this_organisation
from epilepsy12.constants import (
    INDIVIDUAL_KPI_MEASURES,
    EnumAbstractionLevel,
)
from epilepsy12.models import (
    Organisation,
    Case,
    KPI,
    OrganisationKPIAggregation,
    TrustKPIAggregation,
    NHSRegionKPIAggregation,
    CountryKPIAggregation,
    NationalKPIAggregation,
)
from ..common_view_functions import (
    sanction_user,
    trigger_client_event,
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    all_registered_cases_for_cohort_and_abstraction_level,
    return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel,
    return_tile_for_region,
    get_filtered_cases_queryset_for,
    calculate_kpi_value_counts_queryset,
    update_kpi_aggregation_model,
    get_abstraction_model_from_level,
    get_all_kpi_aggregation_data_for_view,
    aggregate_kpis_update_models_for_all_abstractions,
)
from epilepsy12.common_view_functions.render_charts import (
    viz,
)
from ..general_functions import (
    get_current_cohort_data,
    value_from_key,
    calculate_kpi_average,
)
from ..constants import colors

from ..tasks import (
    aggregate_kpis_for_each_level_of_abstraction_by_organisation_asynchronously,
)


@login_required
@user_may_view_this_organisation()
def selected_organisation_summary(request, organisation_id):
    """
    This function presents the organisation view - comprising the organisation contact details,
    a demographic summary of the hospital trust and a table summary of the key performance indicators
    for that organisation, its parent trust, as well as comparisons at different levels of abstraction
    (eg nhs region, ICB, OPENUK region and so on)
    If a POST request from selected_organisation_summary.html on organisation select, it returns epilepsy12/partials/selected_organisation_summary.html
    Otherwise it returns the organisation.html template
    """

    nhsregion_tiles = return_tile_for_region("nhs_region")
    icb_tiles = return_tile_for_region("icb")
    country_tiles = return_tile_for_region("country")

    if request.POST.get("selected_organisation_summary") is not None:
        selected_organisation = Organisation.objects.get(
            pk=request.POST.get("selected_organisation_summary")
        )
        template_name = "epilepsy12/partials/selected_organisation_summary.html"
    else:
        # selected_organisation = return_selected_organisation(user=request.user)
        selected_organisation = Organisation.objects.get(pk=organisation_id)
        template_name = "epilepsy12/organisation.html"

    lhb_tiles = None

    if selected_organisation.ons_region.ons_country.Country_ONS_Name == "Wales":
        lhb_tiles = return_tile_for_region("lhb")

    cohort_data = get_current_cohort_data()

    # query to return all completed E12 cases in the current cohort in this organisation
    count_of_current_cohort_registered_completed_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="organisation",
        ).count()
    )

    # query to return all completed E12 cases in the current cohort in this organisation trust
    count_of_current_cohort_registered_completed_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=True,
            abstraction_level="trust",
        ).count()
    )
    # query to return all cases (including incomplete) registered in the current cohort at this organisation
    count_of_all_current_cohort_registered_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="organisation",
        ).count()
    )
    # query to return all cases (including incomplete) registered in the current cohort at this organisation trust
    count_of_all_current_cohort_registered_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="trust",
        ).count()
    )

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_organisation = int(
            (
                count_of_current_cohort_registered_completed_cases_in_this_organisation
                / (count_of_all_current_cohort_registered_cases_in_this_organisation)
            )
            * 100
        )

    else:
        total_percent_organisation = 0

    if count_of_current_cohort_registered_completed_cases_in_this_trust > 0:
        total_percent_trust = int(
            (
                count_of_current_cohort_registered_completed_cases_in_this_trust
                / (count_of_all_current_cohort_registered_cases_in_this_trust)
                * 100
            )
        )
    else:
        total_percent_trust = 0

    context = {
        "user": request.user,
        "selected_organisation": selected_organisation,
        "organisation_list": Organisation.objects.order_by("OrganisationName").all(),
        "cases_aggregated_by_ethnicity": cases_aggregated_by_ethnicity(
            selected_organisation=selected_organisation
        ),
        "cases_aggregated_by_sex": cases_aggregated_by_sex(
            selected_organisation=selected_organisation
        ),
        "cases_aggregated_by_deprivation": cases_aggregated_by_deprivation_score(
            selected_organisation=selected_organisation
        ),
        "percent_completed_organisation": total_percent_organisation,
        "percent_completed_trust": total_percent_trust,
        "count_of_all_current_cohort_registered_cases_in_this_organisation": count_of_all_current_cohort_registered_cases_in_this_organisation,
        "count_of_current_cohort_registered_completed_cases_in_this_organisation": count_of_current_cohort_registered_completed_cases_in_this_organisation,
        "count_of_all_current_cohort_registered_cases_in_this_trust": count_of_all_current_cohort_registered_cases_in_this_trust,
        "count_of_current_cohort_registered_completed_cases_in_this_trust": count_of_current_cohort_registered_completed_cases_in_this_trust,
        "cohort_data": cohort_data,
        "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
        "nhsregion_tiles": nhsregion_tiles,
        "icb_tiles": icb_tiles,
        "country_tiles": country_tiles,
        "lhb_tiles": lhb_tiles,
    }

    return render(
        request=request,
        template_name=template_name,
        context=context,
    )


@login_required
@user_may_view_this_organisation()
def selected_trust_kpis(request, organisation_id):
    """
    HTMX get request returning kpis.html 'Real-time Key Performance Indicator (KPI) Metrics' table.

    This aggregates all KPI measures at different levels of abstraction related to the selected organisation
    Organisation level, Trust level, ICB level, NHS Region, OPEN UK level, country level and national level.

    It then presents each abstraction level's KPIAggregation model.
    """

    # Get all relevant data for this cohort
    cohort = get_current_cohort_data()["cohort"]
    organisation = Organisation.objects.get(pk=organisation_id)

    # perform aggregations and update all the KPIAggregation models
    aggregate_kpis_update_models_for_all_abstractions(
        organisation=organisation, cohort=cohort
    )

    # Gather relevant data specific for this view
    all_data = get_all_kpi_aggregation_data_for_view(
        organisation=organisation, cohort=cohort
    )

    # Instance of KPI to access field name help text attributes for KPI "Indicator" row values in table
    kpi_instance = KPI(organisation=organisation, parent_trust="TEMP")
    kpi_names_list = list(kpi_instance.get_kpis().keys())

    context = {
        "organisation": organisation,
        "all_data": all_data,
        "kpis": kpi_instance,
        "kpi_names_list": kpi_names_list,
        "open_access": False,
    }

    return render(
        request=request,
        template_name="epilepsy12/partials/kpis/kpis.html",
        context=context,
    )
    # TODO: 17/8/2023 -> check with @eatyourpeas re this trigger client code
    # response = render(request=request, template_name=template_name, context=context)

    # # trigger a GET request from the steps template
    # trigger_client_event(
    #     response=response, name="registration_active", params={}
    # )  # reloads the form to show the active steps


def selected_trust_kpis_open(request, organisation_id):
    """
    Open access endpoint for KPIs table
    """

    organisation = Organisation.objects.get(pk=organisation_id)

    # run the aggregations TODO This will need ultimately throttling to run only periodically

    # get aggregated KPIs for level of abstraction from KPIAggregation

    # create an empty instance of KPI model to access the labels - this is a bit of a hack but works and
    # and has very little overhead
    kpis = KPI.objects.create(
        organisation=organisation,
        parent_trust=organisation.ParentOrganisation_OrganisationName,
    )

    template_name = "epilepsy12/partials/kpis/kpis.html"
    context = {
        "organisation": organisation,
        # "organisation_kpis": organisation_kpis,
        # "trust_kpis": trust_kpis,
        # "icb_kpis": icb_kpis,
        # "nhs_kpis": nhs_kpis,
        # "open_uk_kpis": open_uk_kpis,
        # "country_kpis": country_kpis,
        # "national_kpis": national_kpis,
        "kpis": kpis,
        "organisation_list": Organisation.objects.all().order_by("OrganisationName"),
        "open_access": True,
    }

    # remove the temporary instance as otherwise would contribute to totals
    kpis.delete()

    response = render(request=request, template_name=template_name, context=context)

    return response


@login_required
@user_may_view_this_organisation()
def child_organisation_select(request, organisation_id, template_name):
    """
    POST call back from organisation_select to allow user to toggle between organisations in selected trust
    """

    selected_organisation_id = request.POST.get("child_organisation_select")

    # get currently selected organisation
    organisation = Organisation.objects.get(pk=selected_organisation_id)

    # trigger page reload with new organisation
    return HttpResponseClientRedirect(
        reverse(template_name, kwargs={"organisation_id": organisation.pk})
    )


@login_required
@user_may_view_this_organisation()
def view_preference(request, organisation_id, template_name):
    """
    POST request from Toggle in has rcpch_view_preference.html template
    Users can toggle between national, trust and organisation views.
    Only RCPCH staff can request a National level.
    """
    organisation = Organisation.objects.get(pk=organisation_id)

    request.user.view_preference = request.htmx.trigger_name
    request.user.save()

    return HttpResponseClientRedirect(
        reverse(template_name, kwargs={"organisation_id": organisation.pk})
    )


@login_required
@user_may_view_this_organisation()
def selected_trust_select_kpi(request, organisation_id):
    """
    POST request from dropdown in selected_organisation_summary.html

    It takes the kpi_name parameter in the HTMX request which contains the value of the selected KPI measure from
    the select field. This is then aggregated across the levels of abstraction.
    
    Aggregations should already be performed.

    all_data is of the format:
    {
    "ORGANISATION_KPIS":{
        "aggregation_model":"<OrganisationKPIAggregation":OrganisationKPIAggregation (ODSCode=RGT01) KPIAggregations>,
        "total_cases_registered":10
    },
    "TRUST_KPIS":{
        "aggregation_model":"<TrustKPIAggregation":"TrustKPIAggregation (parent_organisation_ods_code=RGT)>",
        "total_cases_registered":10
    },
    "ICB_KPIS":{
        "aggregation_model":"<ICBKPIAggregation":"ICBKPIAggregation (IntegratedCareBoardEntity=NHS CAMBRIDGESHIRE AND PETERBOROUGH INTEGRATED CARE BOARD)>",
        "total_cases_registered":10
    },
    "NHS_REGION_KPIS":{
        "aggregation_model":"<NHSRegionKPIAggregation":"KPIAggregations (NHSRegionEntity=East of England)>",
        "total_cases_registered":20
    },
    "OPEN_UK_KPIS":{
        "aggregation_model":"<OpenUKKPIAggregation":"OPENUKKPIAggregations (OPENUKNetworkEntity=Eastern Paediatric Epilepsy Network)>",
        "total_cases_registered":10
    },
    "COUNTRY_KPIS":{
        "aggregation_model":"<CountryKPIAggregation":"CountryKPIAggregations (ONSCountryEntity=England)>",
        "total_cases_registered":170
    },
    "NATIONAL_KPIS":{
        "aggregation_model":"<NationalKPIAggregation":National KPIAggregations for England and Wales (Cohort 6)>,
        "total_cases_registered":200
    },
    }
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    kpi_name = request.POST.get("kpi_name")
    if kpi_name is None:
        # on page load there may be no kpi_name - default to paediatrician_with_experise_in_epilepsy
        kpi_name = INDIVIDUAL_KPI_MEASURES[0][0]
    kpi_value = value_from_key(key=kpi_name, choices=INDIVIDUAL_KPI_MEASURES)
    cohort = get_current_cohort_data()["cohort"]

    all_data = get_all_kpi_aggregation_data_for_view(
        organisation=organisation,
        cohort=cohort,
    )

    # Add chart HTMLs to all_data
    for abstraction, kpi_data in all_data.items():
        
        # Skip loop if aggregation model None (when there are no data to aggregate on so no AggregationModel made)
        if kpi_data['aggregation_model'] is None:
            continue
        
        # Initialise dict
        kpi_data["charts"] = {}

        # Add individual kpi passed pie chart
        pie_html_raw = viz.render_pie_pct_passed_for_kpi_agg(
            kpi_data["aggregation_model"],
            kpi_name,
        )
        pie_html = viz.ChartHTML(chart_html=pie_html_raw, name=f"{abstraction}_pct_pass_pie_{kpi_name}")
        kpi_data["charts"]["passed_pie"] = pie_html
        
    print(all_data)

    all_aggregated_kpis_by_nhs_region_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort,
        abstraction_level="nhs_region",
        kpi_measure=kpi_name,
    )
    nhs_region_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_nhs_region_in_current_cohort,
        kpi=kpi_name,
    )

    all_aggregated_kpis_by_icb_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort, abstraction_level="icb", kpi_measure=kpi_name
    )
    icb_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_icb_in_current_cohort,
        kpi=kpi_name,
    )

    all_aggregated_kpis_by_country_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort, abstraction_level="country", kpi_measure=kpi_name
    )
    country_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_country_in_current_cohort,
        kpi=kpi_name,
    )

    context = {
        "kpi_name": kpi_name,
        "kpi_name_title_case": kpi_value,
        "selected_organisation": organisation,
        "all_data": all_data,
        # ALL BELOW TO BE REPLACED
        "open_uk_title": f"{kpi_value} by OPEN UK Region",
        "open_uk_id": "open_uk_id",
        "icb": all_aggregated_kpis_by_icb_in_current_cohort,
        "icb_avg": icb_avg,
        "icb_title": f"{kpi_value} by Integrated Care Board",
        "icb_id": "icb_id",
        "nhs_region": all_aggregated_kpis_by_nhs_region_in_current_cohort,
        "nhs_region_avg": nhs_region_avg,
        "nhs_region_title": f"{kpi_value} by NHS Region",
        "nhs_region_id": "nhs_region_id",
        "country": all_aggregated_kpis_by_country_in_current_cohort,
        "country_avg": country_avg,
        "country_title": f"{kpi_value} by Country",
        "country_id": "country_id",
        # ADD COLOR PER ABSTRACTION
        "icb_color": colors.RCPCH_AQUA_GREEN,
        "open_uk_color": colors.RCPCH_LIGHT_BLUE,
        "nhs_region_color": colors.RCPCH_STRONG_BLUE,
        "country_color": colors.RCPCH_DARK_BLUE,
        "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
    }

    template_name = "epilepsy12/partials/organisation/metric.html"

    return render(request=request, template_name=template_name, context=context)
