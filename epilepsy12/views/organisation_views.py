# Python imports
from datetime import date

# third party libraries
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse

from django_htmx.http import HttpResponseClientRedirect
import pandas as pd

# E12 imports
from ..decorator import user_may_view_this_organisation, login_and_otp_required
from epilepsy12.constants import INDIVIDUAL_KPI_MEASURES, EnumAbstractionLevel
from epilepsy12.models import Organisation, KPI, OrganisationKPIAggregation
from ..common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_age,
    all_registered_cases_for_cohort_and_abstraction_level,
    get_all_kpi_aggregation_data_for_view,
    logged_in_user_may_access_this_organisation,
    filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction,
    generate_dataframe_and_aggregated_distance_data_from_cases,
    generate_distance_from_organisation_scatterplot_figure,
    generate_case_count_choropleth_map,
    piechart_plot_cases_by_ethnicity,
    piechart_plot_cases_by_index_of_multiple_deprivation,
    piechart_plot_cases_by_sex,
    piechart_plot_cases_by_age_range,
)
from epilepsy12.common_view_functions.render_charts import update_all_data_with_charts
from ..general_functions import (
    value_from_key,
    cohorts_and_dates,
)
from ..kpi import download_kpi_summary_as_csv
from epilepsy12.common_view_functions.aggregate_by import (
    update_all_kpi_agg_models,
)


def selected_organisation_summary_select(request):
    """
    callback from organisation select in selected_organisation_summary
    redirects to new organisation url
    """

    selected_organisation = Organisation.objects.get(
        pk=request.POST.get("selected_organisation_summary_select")
    )

    response = reverse(
        "selected_organisation_summary",
        kwargs={"organisation_id": selected_organisation.pk},
    )
    return HttpResponseClientRedirect(response)


@login_and_otp_required()
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
    selected_organisation = Organisation.objects.get(pk=organisation_id)

    template_name = "epilepsy12/organisation.html"

    # Dates for the closed, data collection ongoing and actively recruiting cohorts
    cohort_data = cohorts_and_dates(first_paediatric_assessment_date=date.today())

    # Where dashboard data is filtered by cohort, which cohort?
    # Users still want to see dashboard data even when data collection is complete.
    requested_cohort_number = request.GET.get("cohort")

    if requested_cohort_number:
        cohort_number = int(requested_cohort_number)
    else:
        cohort_number = (
            cohort_data["grace_cohort"]["cohort"]
            if cohort_data["within_grace_period"]
            else cohort_data["submitting_cohort"]
        )

    # thes are all registered cases for the current cohort at the selected organisation to be plotted in the map
    cases_to_plot = filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction(
        organisation=selected_organisation, cohort=cohort_number
    )

    # aggregated distances (mean, median, max, min) that cases have travelled to the selected organisation
    aggregated_distances, case_distances_dataframe = (
        generate_dataframe_and_aggregated_distance_data_from_cases(
            filtered_cases=cases_to_plot
        )
    )

    # generate scatterplot of cases by distance from the selected organisation

    scatterplot_of_cases_for_selected_organisation = (
        generate_distance_from_organisation_scatterplot_figure(
            geo_df=case_distances_dataframe, organisation=selected_organisation
        )
    )

    # differentiate between England and Wales
    if selected_organisation.country.boundary_identifier == "W92000004":  # Wales
        abstraction_level = "local_health_board"
        # generate choropleth map of case counts for each level of abstraction
        lhb_heatmap = generate_case_count_choropleth_map(
            properties="ods_code",
            abstraction_level=EnumAbstractionLevel.LOCAL_HEALTH_BOARD,
            organisation=selected_organisation,
            cohort=cohort_number,
        )
    else:
        # generate choropleth map of case counts for each level of abstraction
        if selected_organisation.ods_code == "RGT1W":
            # Jersey is a special case and although is mapped to England, is in the Channel Islands and has no ICB, NHS Region or LHB
            abstraction_level = "trust"
        else:
            abstraction_level = "trust"
            icb_heatmap = generate_case_count_choropleth_map(
                properties="ods_code",
                abstraction_level=EnumAbstractionLevel.ICB,
                organisation=selected_organisation,
                cohort=cohort_number,
            )
            nhsregion_heatmap = generate_case_count_choropleth_map(
                properties="region_code",
                abstraction_level=EnumAbstractionLevel.NHS_ENGLAND_REGION,
                organisation=selected_organisation,
                cohort=cohort_number,
            )

    country_heatmap = generate_case_count_choropleth_map(
        properties="boundary_identifier",
        abstraction_level=EnumAbstractionLevel.COUNTRY,
        organisation=selected_organisation,
        cohort=cohort_number,
    )

    # query to return all completed E12 cases in the current cohort in this organisation
    count_of_current_cohort_registered_completed_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_number,
            case_complete=True,
            abstraction_level="organisation",
        ).count()
    )
    # query to return all cases (including incomplete) registered in the current cohort at this organisation
    count_of_all_current_cohort_registered_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_number,
            case_complete=False,
            abstraction_level="organisation",
        ).count()
    )

    # query to return all completed E12 cases in the current cohort in this organisation trust
    count_of_current_cohort_registered_completed_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_number,
            case_complete=True,
            abstraction_level=abstraction_level,
        ).count()
    )
    # query to return all cases (including incomplete) registered in the current cohort at this organisation trust
    count_of_all_current_cohort_registered_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_number,
            case_complete=False,
            abstraction_level=abstraction_level,
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

    # organisation list scoped to permissions of user
    if (
        request.user.is_rcpch_audit_team_member
        or request.user.is_superuser
        or request.user.is_rcpch_staff
    ):
        # select any organisations except currently selected organisation
        organisation_list = Organisation.objects.filter(active=True).order_by("name")
    else:
        if selected_organisation.country.boundary_identifier == "W92000004":  # Wales
            organisation_list = Organisation.objects.filter(
                local_health_board=selected_organisation.local_health_board,
                active=True,
            )
        else:
            organisation_list = Organisation.objects.filter(
                trust=selected_organisation.trust,
                active=True,
            )

    context = {
        "user": request.user,
        "cohort_number": cohort_number,  # the number of the cohort that should be highlighted as imminently submitting
        "cohort_data": cohort_data,  # the cohort data object for the cohort_card
        "selected_organisation": selected_organisation,
        "organisation_list": organisation_list,
        "cases_aggregated_by_ethnicity": cases_aggregated_by_ethnicity(
            selected_organisation=selected_organisation
        ),
        "cases_aggregated_by_sex": cases_aggregated_by_sex(
            selected_organisation=selected_organisation
        ),
        "cases_aggregated_by_deprivation": cases_aggregated_by_deprivation_score(
            selected_organisation=selected_organisation
        ),
        "cases_aggregated_by_age_range": cases_aggregated_by_age(
            selected_organisation=selected_organisation
        ),
        "index_of_multiple_deprivation_score_piechart": piechart_plot_cases_by_index_of_multiple_deprivation(
            organisation=selected_organisation
        ),
        "ethnicity_piechart": piechart_plot_cases_by_ethnicity(
            organisation=selected_organisation
        ),
        "sex_piechart": piechart_plot_cases_by_sex(organisation=selected_organisation),
        "age_range_piechart": piechart_plot_cases_by_age_range(
            organisation=selected_organisation
        ),
        "percent_completed_organisation": total_percent_organisation,
        "percent_completed_trust": total_percent_trust,
        "count_of_all_current_cohort_registered_cases_in_this_organisation": count_of_all_current_cohort_registered_cases_in_this_organisation,
        "count_of_current_cohort_registered_completed_cases_in_this_organisation": count_of_current_cohort_registered_completed_cases_in_this_organisation,
        "count_of_all_current_cohort_registered_cases_in_this_trust": count_of_all_current_cohort_registered_cases_in_this_trust,
        "count_of_current_cohort_registered_completed_cases_in_this_trust": count_of_current_cohort_registered_completed_cases_in_this_trust,
        "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
        "organisation_cases_map": scatterplot_of_cases_for_selected_organisation,
        "aggregated_distances": aggregated_distances,
        "country_heatmap": country_heatmap,
    }
    if selected_organisation.country.boundary_identifier == "W92000004":
        context["lhb_heatmap"] = lhb_heatmap
        context["trust_heatmap"] = None
        context["icb_heatmap"] = None
        context["nhsregion_heatmap"] = None
    else:
        if selected_organisation.ods_code == "RGT1W":
            # Jersey is a special case as it is in the Channel Islands and has no ICB, NHS Region or LHB
            context["trust_heatmap"] = None
            context["icb_heatmap"] = None
            context["nhsregion_heatmap"] = None
        else:
            context["lhb_heatmap"] = None
            context["icb_heatmap"] = icb_heatmap
            context["nhsregion_heatmap"] = nhsregion_heatmap

    return render(
        request=request,
        template_name=template_name,
        context=context,
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@permission_required("epilepsy12.can_publish_epilepsy12_data", raise_exception=True)
def publish_kpis(request, organisation_id):
    """
    call back from selected_organisation_summary page on click of publish button
    Publishes all data held for current cohort publicly
    Returns the publish button partial + success message
    """

    # get submitting_cohort number - in future will be selectable
    cohort_data = cohorts_and_dates(first_paediatric_assessment_date=date.today())

    cohort_number = (
        cohort_data["grace_cohort"]["cohort"]
        if cohort_data["within_grace_period"]
        else cohort_data["submitting_cohort"]
    )

    # perform aggregations and update all the KPIAggregation models only for clinicians
    update_all_kpi_agg_models(cohort=cohort_number, open_access=True)

    return render(
        request=request,
        template_name="epilepsy12/partials/organisation/publish_button.html",
        context={
            "selected_organisation": Organisation.objects.get(pk=organisation_id),
            "publish_success": True,
        },
    )


def selected_trust_kpis(request, organisation_id, access):
    """
    HTMX get request returning kpis.html 'Real-time Key Performance Indicator (KPI) Metrics' table.

    This aggregates all KPI measures synchronously at different levels of abstraction related to the selected organisation
    Organisation level, Trust level, ICB level, NHS Region, OPEN UK level, country level and national level.

    It then presents each abstraction level's KPIAggregation model.

    It is called by htmx get request from the kpi table, either on page load, or on click of the
    refresh button in the header.

    Params:
    organisation_id: the primary key for the organisation viewed
    access: string, one of ['open', 'private'] - ensure if refresh is called from public view, even if by someone logged in, only
    public view data is seen

    This endpoint can be called from the public dashboard so protection happens within the view
    """

    # Get all relevant data for submission cohort
    requested_cohort_number = request.GET.get("cohort")

    cohort_data = cohorts_and_dates(first_paediatric_assessment_date=date.today())
    submitting_cohort_number = (
        cohort_data["grace_cohort"]["cohort"]
        if cohort_data["within_grace_period"]
        else cohort_data["submitting_cohort"]
    )

    if requested_cohort_number:
        cohort_number = int(requested_cohort_number)
    else:
        cohort_number = submitting_cohort_number

    organisation = Organisation.objects.get(pk=organisation_id)

    if logged_in_user_may_access_this_organisation(request.user, organisation):
        # user is logged in and allowed to access this organisation

        if access == "private":
            # perform aggregations and update all the KPIAggregation models only for clinicians
            update_all_kpi_agg_models(cohort=cohort_number, open_access=False)

        # Gather relevant data specific for this view - still show only published data if this is public view
        all_data = get_all_kpi_aggregation_data_for_view(
            organisation=organisation,
            cohort=cohort_number,
            open_access=access == "open",
        )

    else:
        # User is not logged in and not eligible to run aggregations
        # Gather relevant open access data specific for this view
        all_data = get_all_kpi_aggregation_data_for_view(
            organisation=organisation,
            cohort=cohort_number,
            open_access=True,
        )

    # Instance of KPI to access field name help text attributes for KPI "Indicator" row values in table
    kpi_instance = KPI(organisation=organisation)
    kpi_names_list = list(kpi_instance.get_kpis().keys())

    # Last publication date
    last_published_kpi_aggregation = (
        OrganisationKPIAggregation.objects.filter(
            abstraction_relation=organisation, open_access=True
        )
        .order_by("-last_updated")
        .first()
    )
    if last_published_kpi_aggregation:
        last_published_date = last_published_kpi_aggregation.last_updated
    else:
        last_published_date = None

    context = {
        "organisation": organisation,
        "all_data": all_data,
        "kpis": kpi_instance,
        "kpi_names_list": kpi_names_list,
        "open": access == "open",
        "organisation_list": Organisation.objects.filter(active=True).order_by(
            "name"
        ),  # for public view dropdown
        "last_published_date": last_published_date,
        "publish_success": False,
        "cohort_number": cohort_number,
        "submitting_cohort_number": submitting_cohort_number,
    }

    return render(
        request=request,
        template_name="epilepsy12/partials/kpis/kpis.html",
        context=context,
    )


def selected_trust_open_select(request, organisation_id):
    """
    POST callback on change of RCPCH organisations dropdown in open access view
    Selects new hospital and redirects to open_access endpoint returning table with new organisation
    """
    url = reverse(
        "open_access",
        kwargs={"organisation_id": request.POST.get("selected_trust_open_select")},
    )
    return HttpResponseClientRedirect(url)


def selected_trust_select_kpi(request, organisation_id):
    """
    POST request from dropdown in selected_organisation_summary.html returning the individual kpis data and visualisations.

    It takes the kpi_name parameter in the HTMX request which contains the value of the selected KPI measure from
    the select field. This is then aggregated across the levels of abstraction.

    Aggregations should already be performed.

    all_data is of the format:
    {
    "ORGANISATION_KPIS":{
        'aggregation_model': <OrganisationKPIAggregation: OrganisationKPIAggregation (ods_code=RGT01) KPIAggregations>,
        'total_cases_registered': 10,
        'charts': {
            'passed_pie': <ORGANISATION_KPIS_pct_pass_pie_paediatrician_with_expertise_in_epilepsies ChartHTML object>
            }
    },
    "TRUST_KPIS":{
        ...
    },
    "LOCAL_HEALTH_BOARD":{
        ...
    },
    "ICB_KPIS":{
        ...
    },
    "NHS_ENGLAND_REGION_KPIS":{
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

    requested_cohort_number = request.POST.get("cohort")

    if requested_cohort_number:
        cohort_number = int(requested_cohort_number)
    else:
        cohort_data = cohorts_and_dates(first_paediatric_assessment_date=date.today())
        cohort_number = (
            cohort_data["grace_cohort"]["cohort"]
            if cohort_data["within_grace_period"]
            else cohort_data["submitting_cohort"]
        )

    all_data = get_all_kpi_aggregation_data_for_view(
        organisation=organisation, cohort=cohort_number, open_access=False
    )

    all_data = update_all_data_with_charts(
        all_data=all_data,
        kpi_name=kpi_name,
        kpi_name_title_case=kpi_name_title_case,
        cohort=cohort_number,
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


@login_and_otp_required()
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


@login_and_otp_required()
@user_may_view_this_organisation()
def view_preference(request, organisation_id, template_name):
    """
    POST request from Toggle in has rcpch_view_preference.html template
    Users can toggle between national, trust and organisation views.
    Only RCPCH staff can request a National level.
    """
    organisation = Organisation.objects.get(pk=organisation_id)

    request.user.view_preference = request.htmx.trigger_name
    request.user.save(update_fields=["view_preference"])

    return HttpResponseClientRedirect(
        reverse(template_name, kwargs={"organisation_id": organisation.pk})
    )


@login_and_otp_required()
@permission_required("epilepsy12.can_publish_epilepsy12_data")
def kpi_download(request, organisation_id):
    """
    GET: Loads the page necessary for downloading KPIs
    """

    context = {"organisation_id": organisation_id}

    template_name = "epilepsy12/partials/kpis/kpi_download.html"

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@permission_required("epilepsy12.can_publish_epilepsy12_data")
def kpi_download_file(request):

    (
        country_df,
        trust_hb_df,
        icb_df,
        region_df,
        network_df,
        national_df,
        reference_df,
        trust_totals_df,
        local_health_board_totals_df,
        icb_totals_df,
        nhs_england_region_totals_df,
        openuk_network_totals_df,
        country_totals_df,
    ) = download_kpi_summary_as_csv(cohort=6)

    with pd.ExcelWriter("kpi_export.xlsx") as writer:
        country_df.to_excel(writer, sheet_name="Country_level", index=False)
        trust_hb_df.to_excel(writer, sheet_name="HBT_level", index=False)
        icb_df.to_excel(writer, sheet_name="ICB_level", index=False)
        region_df.to_excel(writer, sheet_name="NHSregion_level", index=False)
        network_df.to_excel(writer, sheet_name="Network_level", index=False)
        national_df.to_excel(writer, sheet_name="National_level", index=False)
        reference_df.to_excel(writer, sheet_name="Reference", index=False)
        trust_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - Trust", index=False
        )
        local_health_board_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - LHB", index=False
        )
        icb_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - ICB", index=False
        )
        nhs_england_region_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - NHSregion", index=False
        )
        openuk_network_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - Network", index=False
        )
        country_totals_df.to_excel(
            writer, sheet_name="Registered vs Total - Country", index=False
        )

    with open("kpi_export.xlsx", "rb") as file:
        excel_data = file.read()

    response = HttpResponse(
        excel_data,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=kpi_export.xlsx"
    return response
