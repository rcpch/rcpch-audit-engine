# Python imports
import math

# third party libraries
from django.conf import settings
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Q

from django_htmx.http import HttpResponseClientRedirect
import pandas as pd

from epilepsy12.models_folder.entities.local_health_board import LocalHealthBoard

# E12 imports
from ..decorator import user_may_view_this_organisation, login_and_otp_required
from epilepsy12.constants import INDIVIDUAL_KPI_MEASURES
from epilepsy12.models import (
    AuditPeriod,
    Organisation,
    KPI,
    OrganisationKPIAggregation,
    OrganisationalAuditSubmissionPeriod,
    Trust,
)
from ..common_view_functions import (
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    cases_aggregated_by_age,
    all_registered_cases_for_cohort_and_abstraction_level,
    get_all_kpi_aggregation_data_for_view,
    filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction,
    generate_dataframe_and_aggregated_distance_data_from_cases,
    piechart_plot_cases_by_ethnicity,
    piechart_plot_cases_by_index_of_multiple_deprivation,
    piechart_plot_cases_by_sex,
    piechart_plot_cases_by_age_range,
)
from epilepsy12.common_view_functions.render_charts import update_all_data_with_charts
from epilepsy12.common_view_functions.sanction_user_access import (
    organisation_white_list_for_user,
    merged_parent_list_for_user,
)
from ..general_functions import (
    value_from_key,
)
from ..kpi import download_kpi_summary_as_csv
from epilepsy12.common_view_functions.aggregate_by import (
    update_all_kpi_agg_models,
)


@login_and_otp_required()
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
def filter_organisations_by_parent(request, parent_id, parent_type):
    """
    HTMX callback when parent dropdown changes.
    Since the entire dashboard is tied to the selected organisation,
    we redirect to the first organisation in the selected parent.

    Params:
    parent_id: primary key of selected parent trust or local health board
    parent_type: string, one of ['trust', 'local_health_board']
    """

    # If HTMX posts the selected parent in the body, extract both id and type
    # Format: "parent_id:parent_type" (e.g., "5:trust" or "12:local_health_board")
    posted_parent = request.POST.get("selected_parent_summary_select")
    if posted_parent and ":" in posted_parent:
        try:
            parent_id_str, parent_type = posted_parent.split(":", 1)
            parent_id = int(parent_id_str)
        except (ValueError, TypeError):
            # Ignore and use URL parameters
            pass

    # Filter organisations by parent type
    if parent_type == "trust":
        organisations = Organisation.objects.filter(trust__id=parent_id, active=True)
    else:  # local_health_board
        organisations = Organisation.objects.filter(
            local_health_board__id=parent_id, active=True
        )

    # Apply user access restrictions if not admin
    if not (request.user.is_rcpch_staff or request.user.is_superuser):
        allowed_orgs = organisation_white_list_for_user(request.user)
        organisations = organisations.filter(
            id__in=allowed_orgs.values_list("id", flat=True)
        )

    # Get the first organisation in the filtered list and redirect to it
    # This triggers a full page reload with all the organisation-specific data
    selected_organisation = organisations.order_by("name").first()

    if selected_organisation:
        response = reverse(
            "selected_organisation_summary",
            kwargs={"organisation_id": selected_organisation.pk},
        )
        return HttpResponseClientRedirect(response)
    else:
        # No organisations found for this parent
        # This should not happen if parent_list is properly filtered
        from django.http import HttpResponse

        return HttpResponse(
            f"No organisations found for the selected {'trust' if parent_type == 'trust' else 'local health board'}. "
            "Please contact support if this issue persists.",
            status=404,
        )


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
    if selected_organisation.trust:
        selected_parent = selected_organisation.trust
    else:
        selected_parent = selected_organisation.local_health_board

    template_name = "epilepsy12/organisation.html"

    # Dates for the closed, data collection ongoing and actively recruiting cohorts
    cohort_data = AuditPeriod.objects.cohort_summary()

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

    # these are all registered cases for the current cohort at the selected organisation to be plotted in the map
    cases_to_plot = filter_all_registered_cases_by_active_lead_site_and_cohort_and_level_of_abstraction(
        organisation=selected_organisation, cohort=cohort_number
    )

    # aggregated distances (mean, median, max, min) that cases have travelled to the selected organisation
    aggregated_distances, case_distances_dataframe = (
        generate_dataframe_and_aggregated_distance_data_from_cases(
            filtered_cases=cases_to_plot
        )
    )

    # IMD tile era selection:
    # - England: cohort < 8 -> 2011 boundaries (2019 IMD), cohort >= 8 -> 2021 boundaries (2025 IMD)
    # - Wales: all cohorts -> 2011 boundaries (2019 WIMD)
    # - Other nations: default to 2011 boundaries
    is_england = selected_organisation.country.boundary_identifier == "E92000001"
    imd_tile_era = "2021" if (is_england and cohort_number >= 8) else "2011"
    nation_by_boundary_identifier = {
        "E92000001": "england",
        "W92000004": "wales",
        "S92000003": "scotland",
        "N92000002": "northern_ireland",
        "JEY": "channel_islands",
    }
    imd_initial_nation = nation_by_boundary_identifier.get(
        selected_organisation.country.boundary_identifier, "all"
    )

    # Build patient list for the IMD map
    imd_map_patients = []
    if not case_distances_dataframe.empty:
        _required = {"latitude", "longitude"}
        if _required.issubset(case_distances_dataframe.columns):
            for _, _row in case_distances_dataframe.dropna(
                subset=["latitude", "longitude"]
            ).iterrows():
                patient_lat = float(_row["latitude"])
                patient_lon = float(_row["longitude"])
                patient_id = (
                    _row["pk"] if "pk" in case_distances_dataframe.columns else None
                )
                if patient_id is None or (
                    isinstance(patient_id, float) and math.isnan(patient_id)
                ):
                    patient_id = f"case-{len(imd_map_patients) + 1}"

                imd_map_patient = {
                    "id": str(patient_id),
                    "lat": patient_lat,
                    "lon": patient_lon,
                }
                if "distance_mi" in case_distances_dataframe.columns:
                    distance_mi = _row["distance_mi"]
                    if not (isinstance(distance_mi, float) and math.isnan(distance_mi)):
                        imd_map_patient["distance_mi"] = float(distance_mi)
                if "distance_km" in case_distances_dataframe.columns:
                    distance_km = _row["distance_km"]
                    if not (isinstance(distance_km, float) and math.isnan(distance_km)):
                        imd_map_patient["distance_km"] = float(distance_km)
                imd_map_patients.append(imd_map_patient)
    imd_map_lead_centre = None
    if (
        selected_organisation.latitude is not None
        and selected_organisation.longitude is not None
    ):
        imd_map_lead_centre = {
            "lat": float(selected_organisation.latitude),
            "lon": float(selected_organisation.longitude),
            "label": selected_organisation.name,
        }

    organisation_cases_imd_payload = {
        "initialNation": imd_initial_nation,
        "initialEra": imd_tile_era,
        "patients": imd_map_patients,
        "leadCentre": imd_map_lead_centre,
    }

    # Use centre geography to choose trust/LHB denominator for completion summary cards.
    if selected_organisation.country.boundary_identifier == "W92000004":  # Wales
        abstraction_level = "local_health_board"
    else:
        abstraction_level = "trust"

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
        # Admin users: select any organisations except currently selected organisation
        organisation_list = Organisation.objects.get_organisation_list()
        # Get merged parent list for all active organisations
        parent_list = merged_parent_list_for_user(
            epilepsy12_user=request.user, organisation_list=organisation_list
        )
    else:
        # Regular users: organisation list is scoped to the organisations in the user's organisation_employer list and their siblings
        organisation_list = organisation_white_list_for_user(
            epilepsy12_user=request.user
        )
        # Get merged parent list only for organisations the user has access to
        parent_list = merged_parent_list_for_user(
            epilepsy12_user=request.user, organisation_list=organisation_list
        )

    # Filter organisation_list to only show organisations within the selected parent
    # This makes the organisation dropdown dependent on the parent dropdown
    if selected_organisation.trust:
        organisation_list = organisation_list.filter(trust=selected_parent)
        parent_type = "trust"
    elif selected_organisation.local_health_board:
        organisation_list = organisation_list.filter(local_health_board=selected_parent)
        parent_type = "local_health_board"
    else:
        # Organisation has no parent (shouldn't happen in practice)
        parent_type = None

    organisational_audit_submission_period = (
        OrganisationalAuditSubmissionPeriod.objects.order_by("-year").first()
    )

    context = {
        "user": request.user,
        "cohort_number": cohort_number,  # the number of the cohort that should be highlighted as imminently submitting
        "cohort_data": cohort_data,  # the cohort data object for the cohort_card
        "selected_organisation": selected_organisation,
        "organisation_list": organisation_list,
        "selected_parent": selected_parent,
        "parent_list": parent_list,
        "parent_type": parent_type,  # Set above based on selected_organisation's parent
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
        "deprivation_tiles_url": settings.RCPCH_DEPRIVATION_TILES_URL,
        "deprivation_tiles_api_key": settings.RCPCH_DEPRIVATION_TILES_API_KEY,
        "deprivation_tiles_api_key_param": settings.RCPCH_DEPRIVATION_TILES_API_KEY_PARAM,
        "organisation_cases_imd_payload": organisation_cases_imd_payload,
        "aggregated_distances": aggregated_distances,
        "organisational_audit_submission_period": organisational_audit_submission_period,
    }

    return render(
        request=request,
        template_name=template_name,
        context=context,
    )


@login_and_otp_required()
@user_may_view_this_organisation()
def individual_metrics(request, organisation_id):
    """
    HTMX get request returning individual_metrics.html  real-time Key Performance Indicator (KPI) Metrics table.
    """

    context = {
        "selected_organisation": Organisation.objects.get(pk=organisation_id),
        "cohort_number": request.GET.get("cohort"),
        "cohort_data": AuditPeriod.objects.cohort_summary(),
        "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
    }
    template = "epilepsy12/partials/organisation/individual_metrics.html"
    return render(request=request, template_name=template, context=context)


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
    cohort_data = AuditPeriod.objects.cohort_summary()

    cohort_number = (
        cohort_data["grace_cohort"]["cohort"]
        if cohort_data["within_grace_period"]
        else cohort_data["submitting_cohort"]
    )

    organisation = Organisation.objects.get(pk=organisation_id)

    # perform aggregations and update all the KPIAggregation models only for clinicians
    update_all_kpi_agg_models(
        organisation=organisation, cohort=cohort_number, open_access=True
    )

    return render(
        request=request,
        template_name="epilepsy12/partials/organisation/publish_button.html",
        context={
            "selected_organisation": Organisation.objects.get(pk=organisation_id),
            "publish_success": True,
        },
    )


@login_and_otp_required()
@user_may_view_this_organisation()
def selected_trust_kpis(request, organisation_id):
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

    cohort_data = AuditPeriod.objects.cohort_summary()
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

    # Perform aggregations and update all the KPIAggregation models
    update_all_kpi_agg_models(
        organisation=organisation, cohort=cohort_number, open_access=False
    )

    all_data = get_all_kpi_aggregation_data_for_view(
        organisation=organisation,
        cohort=cohort_number,
        open_access=False
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
        "open": False,
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


@login_and_otp_required()
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
        cohort_data = AuditPeriod.objects.cohort_summary()
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

    view_preference = int(request.htmx.trigger_name)

    if view_preference == 2 and not (
        request.user.is_rcpch_audit_team_member or request.user.is_superuser
    ):
        return HttpResponseForbidden(
            "Only RCPCH audit team members or superusers can select the National view preference."
        )

    request.user.view_preference = view_preference
    request.user.save(update_fields=["view_preference"])

    return HttpResponseClientRedirect(
        reverse(template_name, kwargs={"organisation_id": organisation.pk})
    )


@login_and_otp_required()
@permission_required("epilepsy12.can_publish_epilepsy12_data")
def kpi_download(request, organisation_id, cohort):
    """
    GET: Loads the page necessary for downloading KPIs
    """

    context = {"organisation_id": organisation_id, "cohort": cohort}

    template_name = "epilepsy12/partials/kpis/kpi_download.html"

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@permission_required("epilepsy12.can_publish_epilepsy12_data")
def kpi_download_file(request, cohort):

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
    ) = download_kpi_summary_as_csv(cohort)

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
    # cohort should be validated by Django as an integer
    response["Content-Disposition"] = (
        f"attachment; filename=kpi_export_cohort_{cohort}.xlsx"
    )
    return response
