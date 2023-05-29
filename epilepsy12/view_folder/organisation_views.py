# Python/Django imports

import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.core.serializers import serialize
from django.http import HttpResponse

# third party libraries
from django_htmx.http import HttpResponseClientRedirect

# E12 imports
from ..decorator import user_may_view_this_organisation
from epilepsy12.constants import INDIVIDUAL_KPI_MEASURES
from epilepsy12.models import (
    Organisation,
    KPI,
    NHSEnglandRegionBoundaries,
    IntegratedCareBoardBoundaries,
    CountryBoundaries,
    LocalHealthBoardBoundaries,
)
from ..common_view_functions import (
    return_selected_organisation,
    sanction_user,
    trigger_client_event,
    cases_aggregated_by_sex,
    cases_aggregated_by_ethnicity,
    cases_aggregated_by_deprivation_score,
    all_registered_cases_for_cohort_and_abstraction_level,
    aggregate_all_eligible_kpi_fields,
    return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel,
)
from ..general_functions import (
    get_current_cohort_data,
    value_from_key,
    calculate_kpi_average,
)
from ..constants import colors


@login_required
def organisation_reports(request):
    """
    This function presents the organisation view - comprising the organisation contact details,
    a demographic summary of the hospital trust and a table summary of the key performance indicators
    for that organisation, its parent trust, as well as comparisons at different levels of abstraction
    (eg nhs region, ICB, OPENUK region and so on)
    It returns the organisation.html template
    It does not accept a parameter as it is the next page on from index.html, where users are not yet
    logged in. It has the login_required decorator. Once the logged in user gains access, they are
    presented with their own organisation's details, unless they are an RCPCH staff member not affiliated
    with an organisation. If they somehow gain access, have no organisation affiliation but are not an RCPCH
    member or a superuser, access is denied
    """
    nhsregion_tiles = serialize(
        "geojson",
        NHSEnglandRegionBoundaries.objects.all(),
    )
    newnhsregion_tiles = json.loads(nhsregion_tiles)
    newnhsregion_tiles.pop("crs", None)
    newnhsregion_tiles = json.dumps(newnhsregion_tiles)
    icb_tiles = serialize("geojson", IntegratedCareBoardBoundaries.objects.all())
    newicb_tiles = json.loads(icb_tiles)
    newicb_tiles.pop("crs", None)
    newicb_tiles = json.dumps(newicb_tiles)
    country_tiles = serialize("geojson", CountryBoundaries.objects.all())
    newcountry_tiles = json.loads(country_tiles)
    newcountry_tiles.pop("crs", None)
    newcountry_tiles = json.dumps(newcountry_tiles)

    newlhb_tiles = None

    # this function returns the users organisation or the first in list depending on affilation
    # or raises a permission error
    selected_organisation = return_selected_organisation(user=request.user)

    if selected_organisation.ons_region.ons_country.Country_ONS_Name == "Wales":
        lhb_tiles = serialize("geojson", LocalHealthBoardBoundaries.objects.all())
        newlhb_tiles = json.loads(lhb_tiles)
        newlhb_tiles.pop("crs", None)
        newlhb_tiles = json.dumps(newlhb_tiles)

    template_name = "epilepsy12/organisation.html"

    # selects the current cohort number and dates
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
    # query to return all cases registered in the current cohort at this organisation
    count_of_current_cohort_registered_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="organisation",
        ).count()
    )
    # query to return all cases registered in the current cohort at this organisation trust
    count_of_current_cohort_registered_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="trust",
        ).count()
    )

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_organisation = round(
            (
                count_of_current_cohort_registered_completed_cases_in_this_organisation
                / count_of_current_cohort_registered_cases_in_this_organisation
            )
        )
    else:
        total_percent_organisation = 0

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_trust = round(
            (
                count_of_current_cohort_registered_completed_cases_in_this_trust
                / count_of_current_cohort_registered_cases_in_this_trust
            )
        )
    else:
        total_percent_trust = 0

    return render(
        request=request,
        template_name=template_name,
        context={
            "user": request.user,
            "selected_organisation": selected_organisation,
            "organisation_list": Organisation.objects.order_by(
                "OrganisationName"
            ).all(),
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
            "count_of_current_cohort_registered_cases_in_this_organisation": count_of_current_cohort_registered_cases_in_this_organisation,
            "count_of_current_cohort_registered_completed_cases_in_this_organisation": count_of_current_cohort_registered_completed_cases_in_this_trust,
            "count_of_current_cohort_registered_cases_in_this_trust": count_of_current_cohort_registered_cases_in_this_trust,
            "count_of_current_cohort_registered_completed_cases_in_this_trust": count_of_current_cohort_registered_completed_cases_in_this_trust,
            "cohort_data": cohort_data,
            # 'all_models': all_models,
            "model_list": (
                "allregisteredcases",
                "registration",
                "firstpaediatricassessment",
                "epilepsycontext",
                "multiaxialdiagnosis",
                "assessment",
                "investigations",
                "management",
                "site",
                "case",
                "epilepsy12user",
                "organisation",
                "comorbidity",
                "episode",
                "syndrome",
                "keyword",
            ),
            "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
            "nhsregion_tiles": newnhsregion_tiles,
            "icb_tiles": newicb_tiles,
            "country_tiles": newcountry_tiles,
            "lhb_tiles": newlhb_tiles,
        },
    )

    return render(request=request, template_name=template_name, context=context)


@login_required
def selected_organisation_summary(request):
    """
    POST request from selected_organisation_summary.html on organisation select
    """

    nhsregion_tiles = serialize(
        "geojson",
        NHSEnglandRegionBoundaries.objects.all(),
    )
    newnhsregion_tiles = json.loads(nhsregion_tiles)
    newnhsregion_tiles.pop("crs", None)
    newnhsregion_tiles = json.dumps(newnhsregion_tiles)
    icb_tiles = serialize("geojson", IntegratedCareBoardBoundaries.objects.all())
    newicb_tiles = json.loads(icb_tiles)
    newicb_tiles.pop("crs", None)
    newicb_tiles = json.dumps(newicb_tiles)
    country_tiles = serialize("geojson", CountryBoundaries.objects.all())
    newcountry_tiles = json.loads(country_tiles)
    newcountry_tiles.pop("crs", None)
    newcountry_tiles = json.dumps(newcountry_tiles)

    selected_organisation = Organisation.objects.get(
        pk=request.POST.get("selected_organisation_summary")
    )

    newlhb_tiles = None

    if selected_organisation.ons_region.ons_country.Country_ONS_Name == "Wales":
        lhb_tiles = serialize("geojson", LocalHealthBoardBoundaries.objects.all())
        newlhb_tiles = json.loads(lhb_tiles)
        newlhb_tiles.pop("crs", None)
        newlhb_tiles = json.dumps(newlhb_tiles)

    # if logged in user is from different trust and not a superuser or rcpch member, deny access
    sanction_user(user=request.user)

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

    print(
        f"{count_of_current_cohort_registered_completed_cases_in_this_organisation} in this organisation"
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
    # query to return all cases registered in the current cohort at this organisation
    count_of_current_cohort_registered_cases_in_this_organisation = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="organisation",
        ).count()
    )
    # query to return all cases registered in the current cohort at this organisation trust
    count_of_current_cohort_registered_cases_in_this_trust = (
        all_registered_cases_for_cohort_and_abstraction_level(
            organisation_instance=selected_organisation,
            cohort=cohort_data["cohort"],
            case_complete=False,
            abstraction_level="trust",
        ).count()
    )

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_organisation = (
            round(
                (
                    count_of_current_cohort_registered_completed_cases_in_this_organisation
                    / count_of_current_cohort_registered_cases_in_this_organisation
                )
            )
            * 10
        )
    else:
        total_percent_organisation = 0

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_trust = (
            round(
                (
                    count_of_current_cohort_registered_completed_cases_in_this_organisation
                    / count_of_current_cohort_registered_cases_in_this_organisation
                )
            )
            * 10
        )
    else:
        total_percent_trust = 0

    context={
            "user": request.user,
            "selected_organisation": selected_organisation,
            "organisation_list": Organisation.objects.order_by(
                "OrganisationName"
            ).all(),
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
            "count_of_current_cohort_registered_cases_in_this_organisation": count_of_current_cohort_registered_cases_in_this_organisation,
            "count_of_current_cohort_registered_completed_cases_in_this_organisation": count_of_current_cohort_registered_completed_cases_in_this_organisation,
            "count_of_current_cohort_registered_cases_in_this_trust": count_of_current_cohort_registered_cases_in_this_trust,
            "count_of_current_cohort_registered_completed_cases_in_this_trust": count_of_current_cohort_registered_completed_cases_in_this_trust,
            "cohort_data": cohort_data,
            "individual_kpi_choices": INDIVIDUAL_KPI_MEASURES,
            "nhsregion_tiles": newnhsregion_tiles,
            "icb_tiles": newicb_tiles,
            "country_tiles": newcountry_tiles,
            "lhb_tiles": newlhb_tiles,
        }

    return render(
        request=request,
        template_name="epilepsy12/partials/selected_organisation_summary.html",
        context=context,
    )


def uk_shapes(request, abstraction_level):
    """
    return region shapes request from maps.html depending on abstraction_level
    ['icb', 'nhs_region', 'country', 'lhb']
    """
    if abstraction_level == "nhs_region":
        object_to_return = NHSEnglandRegionBoundaries
    elif abstraction_level == "icb":
        object_to_return = IntegratedCareBoardBoundaries
    elif abstraction_level == "country":
        object_to_return = CountryBoundaries
    else:
        raise ValueError(f"Cannot return region shape {abstraction_level}")

    # serialize data to geojson
    tiles = serialize(
        "geojson",
        object_to_return.objects.all(),
    )
    # strip the crs element
    deserialized_tiles = json.loads(tiles)
    deserialized_tiles.pop("crs", None)
    # reserialize
    serialized_tiles = json.dumps(deserialized_tiles)
    return HttpResponse(serialized_tiles, content_type="application/json")


@login_required
@user_may_view_this_organisation()
def selected_trust_kpis(request, organisation_id):
    """
    HTMX get request returning trust_level_kpi.html partial

    This aggregates all KPI measures at different levels of abstraction related to the selected organisation
    Organisation level, Trust level, ICB level, NHS Region, OPEN UK level, country level and national level

    It uses django aggregation which is super quick
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    cohort_data = get_current_cohort_data()
    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="organisation",
    )
    trust_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="trust",
    )
    icb_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="icb",
    )
    nhs_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="nhs_region",
    )
    open_uk_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="open_uk",
    )
    country_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="country",
    )
    national_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="national",
    )

    # aggregate at each level of abstraction
    organisation_kpis = aggregate_all_eligible_kpi_fields(organisation_level)
    trust_kpis = aggregate_all_eligible_kpi_fields(trust_level)
    icb_kpis = aggregate_all_eligible_kpi_fields(icb_level)
    nhs_kpis = aggregate_all_eligible_kpi_fields(nhs_level)
    open_uk_kpis = aggregate_all_eligible_kpi_fields(open_uk_level)
    country_kpis = aggregate_all_eligible_kpi_fields(country_level)
    national_kpis = aggregate_all_eligible_kpi_fields(national_level)

    # create an empty instance of KPI model to access the labels - this is a bit of a hack but works and
    # and has very little overhead
    organisation = Organisation.objects.get(pk=organisation_id)
    kpis = KPI.objects.create(
        organisation=organisation,
        parent_trust=organisation.ParentOrganisation_OrganisationName,
    )

    template_name = "epilepsy12/partials/kpis/kpis.html"
    context = {
        "organisation": organisation,
        "organisation_kpis": organisation_kpis,
        "trust_kpis": trust_kpis,
        "icb_kpis": icb_kpis,
        "nhs_kpis": nhs_kpis,
        "open_uk_kpis": open_uk_kpis,
        "country_kpis": country_kpis,
        "national_kpis": national_kpis,
        "kpis": kpis,
        "open_access": False,
    }

    # remove the temporary instance as otherwise would contribute to totals
    kpis.delete()

    response = render(request=request, template_name=template_name, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response, name="registration_active", params={}
    )  # reloads the form to show the active steps

    return response


def selected_trust_kpis_open(request, organisation_id):
    """
    Open access endpoint for KPIs table
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    cohort_data = get_current_cohort_data()
    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="organisation",
    )
    trust_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="trust",
    )
    icb_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="icb",
    )
    nhs_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="nhs_region",
    )
    open_uk_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="open_uk",
    )
    country_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="country",
    )
    national_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="national",
    )

    # aggregate at each level of abstraction
    organisation_kpis = aggregate_all_eligible_kpi_fields(organisation_level)
    trust_kpis = aggregate_all_eligible_kpi_fields(trust_level)
    icb_kpis = aggregate_all_eligible_kpi_fields(icb_level)
    nhs_kpis = aggregate_all_eligible_kpi_fields(nhs_level)
    open_uk_kpis = aggregate_all_eligible_kpi_fields(open_uk_level)
    country_kpis = aggregate_all_eligible_kpi_fields(country_level)
    national_kpis = aggregate_all_eligible_kpi_fields(national_level)

    # create an empty instance of KPI model to access the labels - this is a bit of a hack but works and
    # and has very little overhead
    organisation = Organisation.objects.get(pk=organisation_id)
    kpis = KPI.objects.create(
        organisation=organisation,
        parent_trust=organisation.ParentOrganisation_OrganisationName,
    )

    template_name = "epilepsy12/partials/kpis/kpis.html"
    context = {
        "organisation": organisation,
        "organisation_kpis": organisation_kpis,
        "trust_kpis": trust_kpis,
        "icb_kpis": icb_kpis,
        "nhs_kpis": nhs_kpis,
        "open_uk_kpis": open_uk_kpis,
        "country_kpis": country_kpis,
        "national_kpis": national_kpis,
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
    the select field. This is then aggregated across the levels of abstraction
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    kpi_name = request.POST.get("kpi_name")
    if kpi_name is None:
        # on page load there may be no kpi_name - default to paediatrician_with_experise_in_epilepsy
        kpi_name = INDIVIDUAL_KPI_MEASURES[0][0]
    kpi_value = value_from_key(key=kpi_name, choices=INDIVIDUAL_KPI_MEASURES)

    organisation = Organisation.objects.get(pk=organisation_id)
    cohort_data = get_current_cohort_data()
    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="organisation",
    )
    trust_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="trust",
    )
    icb_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="icb",
    )
    nhs_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="nhs_region",
    )
    open_uk_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="open_uk",
    )
    country_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="country",
    )
    national_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data["cohort"],
        case_complete=True,
        abstraction_level="national",
    )

    # aggregate at each level of abstraction
    # organisation_level.aggregate(**aggregation_fields)
    organisation_kpi = aggregate_all_eligible_kpi_fields(organisation_level, kpi_name)
    # trust_level.aggregate(**aggregation_fields)
    trust_kpi = aggregate_all_eligible_kpi_fields(trust_level, kpi_name)
    # icb_level.aggregate(**aggregation_fields)
    icb_kpi = aggregate_all_eligible_kpi_fields(icb_level, kpi_name)
    # nhs_level.aggregate(**aggregation_fields)
    nhs_kpi = aggregate_all_eligible_kpi_fields(nhs_level, kpi_name)
    # open_uk_level.aggregate(**aggregation_fields)
    open_uk_kpi = aggregate_all_eligible_kpi_fields(open_uk_level, kpi_name)
    # country_level.aggregate(**aggregation_fields)
    country_kpi = aggregate_all_eligible_kpi_fields(country_level, kpi_name)
    # national_level.aggregate(**aggregation_fields)
    national_kpi = aggregate_all_eligible_kpi_fields(national_level, kpi_name)

    all_aggregated_kpis_by_open_uk_region_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data["cohort"], abstraction_level="open_uk", kpi_measure=kpi_name
    )
    open_uk_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_open_uk_region_in_current_cohort,
        kpi=kpi_name,
    )

    all_aggregated_kpis_by_nhs_region_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data["cohort"],
        abstraction_level="nhs_region",
        kpi_measure=kpi_name,
    )
    nhs_region_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_nhs_region_in_current_cohort,
        kpi=kpi_name,
    )

    all_aggregated_kpis_by_icb_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data["cohort"], abstraction_level="icb", kpi_measure=kpi_name
    )
    icb_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_icb_in_current_cohort,
        kpi=kpi_name,
    )

    all_aggregated_kpis_by_country_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data["cohort"], abstraction_level="country", kpi_measure=kpi_name
    )
    country_avg = calculate_kpi_average(
        decimal_places=1,
        kpi_data=all_aggregated_kpis_by_country_in_current_cohort,
        kpi=kpi_name,
    )

    context = {
        "kpi_name": kpi_name,
        "kpi_value": kpi_value,
        "selected_organisation": organisation,
        "organisation_kpi": organisation_kpi[kpi_name],
        "total_organisation_kpi_cases": organisation_kpi["total_number_of_cases"],
        "trust_kpi": trust_kpi[kpi_name],
        "total_trust_kpi_cases": trust_kpi["total_number_of_cases"],
        "icb_kpi": icb_kpi[kpi_name],
        "total_icb_kpi_cases": icb_kpi["total_number_of_cases"],
        "nhs_kpi": nhs_kpi[kpi_name],
        "total_nhs_kpi_cases": nhs_kpi["total_number_of_cases"],
        "open_uk_kpi": open_uk_kpi[kpi_name],
        "total_open_uk_kpi_cases": open_uk_kpi["total_number_of_cases"],
        "country_kpi": country_kpi[kpi_name],
        "total_country_kpi_cases": country_kpi["total_number_of_cases"],
        "national_kpi": national_kpi[kpi_name],
        "total_national_kpi_cases": national_kpi["total_number_of_cases"],
        "open_uk": all_aggregated_kpis_by_open_uk_region_in_current_cohort,
        "open_uk_avg": open_uk_avg,
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
    }

    template_name = "epilepsy12/partials/organisation/metric.html"

    return render(request=request, template_name=template_name, context=context)
