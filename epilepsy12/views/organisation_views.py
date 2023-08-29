# Python imports

# third party libraries
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import F, When, Case as DjangoCase, FloatField, Value

# E12 imports
from ..decorator import user_may_view_this_organisation
from epilepsy12.constants import (
    INDIVIDUAL_KPI_MEASURES,
)
from epilepsy12.models import (
    Organisation,
    KPI,
)
from ..common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    all_registered_cases_for_cohort_and_abstraction_level,
    return_tile_for_region,
    get_all_kpi_aggregation_data_for_view,
    aggregate_kpis_update_models_for_all_abstractions,
)
from epilepsy12.common_view_functions.render_charts import update_all_data_with_charts
from ..general_functions import (
    get_current_cohort_data,
    value_from_key,
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


@login_required
@user_may_view_this_organisation()
def selected_trust_select_kpi(request, organisation_id):
    """
    POST request from dropdown in selected_organisation_summary.html returning the individual kpis data and visualisations.

    It takes the kpi_name parameter in the HTMX request which contains the value of the selected KPI measure from
    the select field. This is then aggregated across the levels of abstraction.

    Aggregations should already be performed.

    all_data is of the format:
    {
    "ORGANISATION_KPIS":{
        'aggregation_model': <OrganisationKPIAggregation: OrganisationKPIAggregation (ODSCode=RGT01) KPIAggregations>,
        'total_cases_registered': 10,
        'charts': {
            'passed_pie': <ORGANISATION_KPIS_pct_pass_pie_paediatrician_with_expertise_in_epilepsies ChartHTML object>
            }
    },
    "TRUST_KPIS":{
        ...
    },
    "ICB_KPIS":{
        ...
    },
    "NHS_REGION_KPIS":{
        ...
    },
    "OPEN_UK_KPIS":{
        ...
    },
    "COUNTRY_KPIS":{
        'aggregation_model': <CountryKPIAggregation: CountryKPIAggregations (ONSCountryEntity=England)>,
        'total_cases_registered': 200,
        'charts': {
            'passed_pie': <COUNTRY_KPIS_pct_pass_pie_paediatrician_with_expertise_in_epilepsies ChartHTML object>,
            'passed_bar': <COUNTRY_KPIS_pct_pass_bar_paediatrician_with_expertise_in_epilepsies ChartHTML object>
            }
    },
    "NATIONAL_KPIS":{
        ...
    },
    }
    """
    # Gather data for use later
    organisation = Organisation.objects.get(pk=organisation_id)
    kpi_name = request.POST.get("kpi_name")
    if kpi_name is None:
        # on page load there may be no kpi_name - default to paediatrician_with_experise_in_epilepsy
        kpi_name = INDIVIDUAL_KPI_MEASURES[0][0]
    kpi_name_title_case = value_from_key(key=kpi_name, choices=INDIVIDUAL_KPI_MEASURES)
    cohort = get_current_cohort_data()["cohort"]

    all_data = get_all_kpi_aggregation_data_for_view(
        organisation=organisation,
        cohort=cohort,
    )

    all_data = update_all_data_with_charts(
        all_data=all_data,
        kpi_name=kpi_name,
        kpi_name_title_case=kpi_name_title_case,
        cohort=cohort,
    )

    context = {
        "kpi_name": kpi_name,
        "kpi_name_title_case": kpi_name_title_case,
        "selected_organisation": organisation,
        "all_data": all_data,
        "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
    }

    template_name = "epilepsy12/partials/organisation/metric.html"

    return render(request=request, template_name=template_name, context=context)


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
