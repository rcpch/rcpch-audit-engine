# Python/Django imports
from datetime import date
from dateutil.relativedelta import relativedelta
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Sum, Count, Avg
from pprint import pprint
# third party libraries
from django_htmx.http import HttpResponseClientRedirect

# E12 imports
from epilepsy12.constants import INDIVIDUAL_KPI_MEASURES
from epilepsy12.models import Case, FirstPaediatricAssessment, Assessment, FirstPaediatricAssessment, Assessment, Site, EpilepsyContext, MultiaxialDiagnosis, Syndrome, Investigations, Management, Comorbidity, Registration, Episode, Organisation, KPI
from ..common_view_functions import trigger_client_event, cases_aggregated_by_sex, cases_aggregated_by_ethnicity, cases_aggregated_by_deprivation_score, all_registered_cases_for_cohort_and_abstraction_level, aggregate_all_eligible_kpi_fields, return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel
from ..general_functions import get_current_cohort_data, value_from_key


@login_required
def organisation_reports(request):

    # Audit trail - filter all models and sort in order of updated_at, returning the latest 5 updates
    first_paediatric_assessment = FirstPaediatricAssessment.objects.filter()
    site = Site.objects.filter()
    epilepsy_context = EpilepsyContext.objects.filter()
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.filter()
    episode = Episode.objects.filter()
    syndrome = Syndrome.objects.filter()
    comorbidity = Comorbidity.objects.filter()
    assessment = Assessment.objects.filter()
    investigations = Investigations.objects.filter()
    management = Management.objects.filter()
    registration = Registration.objects.filter()

    # all_models = sorted(
    #     chain(registration, first_paediatric_assessment, site, epilepsy_context, multiaxial_diagnosis,
    #           episode, syndrome, comorbidity, assessment, investigations, management),
    #     key=lambda x: x.updated_at, reverse=True)[:5]

    template_name = 'epilepsy12/organisation.html'

    cohort_data = get_current_cohort_data()

    if request.user.organisation_employer is not None:
        # current user is affiliated with an existing organisation - set viewable trust to this
        selected_organisation = Organisation.objects.get(
            OrganisationName=request.user.organisation_employer)
    else:
        # current user is a member of the RCPCH audit team and also not affiliated with a organisation
        # therefore set selected organisation to first of organisation on the list
        selected_organisation = Organisation.objects.filter(
            Sector="NHS Sector"
        ).order_by('OrganisationName').first()

    # query to return all completed E12 cases in the current cohort in this organisation
    count_of_current_cohort_registered_completed_cases_in_this_organisation = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='organisation'
    ).count()
    # query to return all completed E12 cases in the current cohort in this organisation trust
    count_of_current_cohort_registered_completed_cases_in_this_trust = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='trust'
    ).count()
    # query to return all cases registered in the current cohort at this organisation
    count_of_current_cohort_registered_cases_in_this_organisation = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=False,
        abstraction_level='organisation'
    ).count()
    # query to return all cases registered in the current cohort at this organisation trust
    count_of_current_cohort_registered_cases_in_this_trust = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=False,
        abstraction_level='trust'
    ).count()

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_organisation = round((count_of_current_cohort_registered_completed_cases_in_this_organisation /
                                            count_of_current_cohort_registered_cases_in_this_organisation))
    else:
        total_percent_organisation = 0

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_trust = round((count_of_current_cohort_registered_completed_cases_in_this_trust /
                                    count_of_current_cohort_registered_cases_in_this_trust))
    else:
        total_percent_trust = 0

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'selected_organisation': selected_organisation,
        'organisation_list': Organisation.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity(selected_organisation=selected_organisation),
        'cases_aggregated_by_sex': cases_aggregated_by_sex(selected_organisation=selected_organisation),
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation_score(selected_organisation=selected_organisation),
        'percent_completed_organisation': total_percent_organisation,
        'percent_completed_trust': total_percent_trust,
        'count_of_current_cohort_registered_cases_in_this_organisation': count_of_current_cohort_registered_cases_in_this_organisation,
        'count_of_current_cohort_registered_completed_cases_in_this_organisation': count_of_current_cohort_registered_completed_cases_in_this_trust,
        'count_of_current_cohort_registered_cases_in_this_trust': count_of_current_cohort_registered_cases_in_this_trust,
        'count_of_current_cohort_registered_completed_cases_in_this_trust': count_of_current_cohort_registered_completed_cases_in_this_trust,
        'cohort_data': cohort_data,
        # 'all_models': all_models,
        'model_list': ('allregisteredcases', 'registration', 'firstpaediatricassessment', 'epilepsycontext', 'multiaxialdiagnosis', 'assessment', 'investigations', 'management', 'site', 'case', 'epilepsy12user', 'organisation', 'comorbidity', 'episode', 'syndrome', 'keyword'),
        'individual_kpi_choices': INDIVIDUAL_KPI_MEASURES
    })


@login_required
def selected_organisation_summary(request):
    """
    POST request from selected_organisation_summary.html on organisation select
    """

    selected_organisation = Organisation.objects.get(
        pk=request.POST.get('selected_organisation_summary'))

    cohort_data = get_current_cohort_data()

    # query to return all completed E12 cases in the current cohort in this organisation
    count_of_current_cohort_registered_completed_cases_in_this_organisation = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='organisation'
    ).count()
    # query to return all completed E12 cases in the current cohort in this organisation trust
    count_of_current_cohort_registered_completed_cases_in_this_trust = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='trust'
    ).count()
    # query to return all cases registered in the current cohort at this organisation
    count_of_current_cohort_registered_cases_in_this_organisation = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=False,
        abstraction_level='organisation'
    ).count()
    # query to return all cases registered in the current cohort at this organisation trust
    count_of_current_cohort_registered_cases_in_this_trust = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=selected_organisation,
        cohort=cohort_data['cohort'],
        case_complete=False,
        abstraction_level='trust'
    ).count()

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_organisation = round((count_of_current_cohort_registered_cases_in_this_organisation /
                                            count_of_current_cohort_registered_completed_cases_in_this_organisation))*10
    else:
        total_percent_organisation = 0

    if count_of_current_cohort_registered_completed_cases_in_this_organisation > 0:
        total_percent_trust = round((count_of_current_cohort_registered_cases_in_this_organisation /
                                    count_of_current_cohort_registered_completed_cases_in_this_organisation))*10
    else:
        total_percent_trust = 0

    return render(request=request, template_name='epilepsy12/partials/selected_organisation_summary.html', context={
        'user': request.user,
        'selected_organisation': selected_organisation,
        'organisation_list': Organisation.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity(selected_organisation=selected_organisation),
        'cases_aggregated_by_sex': cases_aggregated_by_sex(selected_organisation=selected_organisation),
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation_score(selected_organisation=selected_organisation),
        'percent_completed_organisation': total_percent_organisation,
        'percent_completed_trust': total_percent_trust,
        'count_of_current_cohort_registered_cases_in_this_organisation': count_of_current_cohort_registered_cases_in_this_organisation,
        'count_of_current_cohort_registered_completed_cases_in_this_organisation': count_of_current_cohort_registered_completed_cases_in_this_organisation,
        'count_of_current_cohort_registered_cases_in_this_trust': count_of_current_cohort_registered_cases_in_this_trust,
        'count_of_current_cohort_registered_completed_cases_in_this_trust': count_of_current_cohort_registered_completed_cases_in_this_trust,
        'cohort_data': cohort_data,
        'individual_kpi_choices': INDIVIDUAL_KPI_MEASURES
    })


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
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='organisation'
    )
    trust_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='trust'
    )
    icb_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='icb'
    )
    nhs_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='nhs_region'
    )
    open_uk_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='open_uk'
    )
    country_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='country'
    )
    national_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='national'
    )

    # aggregate at each level of abstraction
    organisation_kpis = aggregate_all_eligible_kpi_fields(
        organisation_level)
    trust_kpis = aggregate_all_eligible_kpi_fields(
        trust_level)
    icb_kpis = aggregate_all_eligible_kpi_fields(
        icb_level)
    nhs_kpis = aggregate_all_eligible_kpi_fields(
        nhs_level)
    open_uk_kpis = aggregate_all_eligible_kpi_fields(
        open_uk_level)
    country_kpis = aggregate_all_eligible_kpi_fields(
        country_level)
    national_kpis = aggregate_all_eligible_kpi_fields(
        national_level)

    # create an empty instance of KPI model to access the labels - this is a bit of a hack but works and
    # and has very little overhead
    organisation = Organisation.objects.get(pk=organisation_id)
    kpis = KPI.objects.create(
        organisation=organisation,
        parent_trust=organisation.ParentName
    )

    template_name = 'epilepsy12/partials/kpis/kpis.html'
    context = {
        'organisation': organisation,
        'organisation_kpis': organisation_kpis,
        'trust_kpis': trust_kpis,
        'icb_kpis': icb_kpis,
        'nhs_kpis': nhs_kpis,
        'open_uk_kpis': open_uk_kpis,
        'country_kpis': country_kpis,
        'national_kpis': national_kpis,
        'kpis': kpis,
    }

    # remove the temporary instance as otherwise would contribute to totals
    kpis.delete()

    response = render(
        request=request, template_name=template_name, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def child_organisation_select(request, organisation_id, template_name):
    """
    POST call back from organisation_select to allow user to toggle between organisations in selected trust
    """

    selected_organisation_id = request.POST.get('child_organisation_select')

    # get currently selected organisation
    organisation = Organisation.objects.get(pk=selected_organisation_id)

    # trigger page reload with new organisation
    return HttpResponseClientRedirect(reverse(template_name, kwargs={'organisation_id': organisation.pk}))


@login_required
def view_preference(request, organisation_id, template_name):
    """
    POST request from Toggle in has rcpch_view_preference.html template
    Users can toggle between national, trust and organisation views.
    Only RCPCH staff can request a national view.
    """
    organisation = Organisation.objects.get(pk=organisation_id)

    request.user.view_preference = request.htmx.trigger_name
    request.user.save()

    return HttpResponseClientRedirect(reverse(template_name, kwargs={'organisation_id': organisation.pk}))


def selected_trust_select_kpi(request, organisation_id):
    """
    POST request from dropdown in selected_organisation_summary.html

    It takes the kpi_name parameter in the HTMX request which contains the value of the selected KPI measure from
    the select field. This is then aggregated across the levels of abstraction
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    kpi_name = request.POST.get('kpi_name')
    if kpi_name is None:
        # on page load there may be no kpi_name - default to paediatrician_with_experise_in_epilepsy
        kpi_name = INDIVIDUAL_KPI_MEASURES[0][0]
    kpi_value = value_from_key(
        key=kpi_name, choices=INDIVIDUAL_KPI_MEASURES)

    organisation = Organisation.objects.get(pk=organisation_id)
    cohort_data = get_current_cohort_data()
    organisation_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='organisation'
    )
    trust_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='trust'
    )
    icb_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='icb'
    )
    nhs_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='nhs_region'
    )
    open_uk_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='open_uk'
    )
    country_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='country'
    )
    national_level = all_registered_cases_for_cohort_and_abstraction_level(
        organisation_instance=organisation,
        cohort=cohort_data['cohort'],
        case_complete=True,
        abstraction_level='national'
    )

    # aggregate at each level of abstraction
    # organisation_level.aggregate(**aggregation_fields)
    organisation_kpi = aggregate_all_eligible_kpi_fields(
        organisation_level, kpi_name)
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
        cohort=cohort_data['cohort'], abstraction_level='open_uk', kpi_measure=kpi_name)

    all_aggregated_kpis_by_nhs_region_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data['cohort'], abstraction_level='nhs_region', kpi_measure=kpi_name)

    all_aggregated_kpis_by_icb_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data['cohort'], abstraction_level='nhs_region', kpi_measure=kpi_name)

    all_aggregated_kpis_by_icb_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data['cohort'], abstraction_level='icb', kpi_measure=kpi_name)

    all_aggregated_kpis_by_country_in_current_cohort = return_all_aggregated_kpis_for_cohort_and_abstraction_level_annotated_by_sublevel(
        cohort=cohort_data['cohort'], abstraction_level='country', kpi_measure=kpi_name)
    context = {
        'kpi_name': kpi_name,
        'kpi_value': kpi_value,
        'selected_organisation': organisation,
        'organisation_kpi': organisation_kpi[kpi_name],
        'total_organisation_kpi_cases': organisation_kpi['total_number_of_cases'],
        'trust_kpi': trust_kpi[kpi_name],
        'total_trust_kpi_cases': trust_kpi['total_number_of_cases'],
        'icb_kpi': icb_kpi[kpi_name],
        'total_icb_kpi_cases': icb_kpi['total_number_of_cases'],
        'nhs_kpi': nhs_kpi[kpi_name],
        'total_nhs_kpi_cases': nhs_kpi['total_number_of_cases'],
        'open_uk_kpi': open_uk_kpi[kpi_name],
        'total_open_uk_kpi_cases': open_uk_kpi['total_number_of_cases'],
        'country_kpi': country_kpi[kpi_name],
        'total_country_kpi_cases': country_kpi['total_number_of_cases'],
        'national_kpi': national_kpi[kpi_name],
        'total_national_kpi_cases': national_kpi['total_number_of_cases'],
        'open_uk': all_aggregated_kpis_by_open_uk_region_in_current_cohort,
        'open_uk_title': f'{kpi_value} by OPEN UK Region',
        'open_uk_id': 'open_uk_id',
        'icb': all_aggregated_kpis_by_icb_in_current_cohort,
        'icb_title': f'{kpi_value} by Integrated Care Board',
        'icb_id': 'icb_id',
        'nhs_region': all_aggregated_kpis_by_nhs_region_in_current_cohort,
        'nhs_region_title': f'{kpi_value} by NHS Region',
        'nhs_region_id': 'nhs_region_id',
        'country': all_aggregated_kpis_by_country_in_current_cohort,
        'country_title': f'{kpi_value} by Country',
        'country_id': 'country_id'
    }

    template_name = 'epilepsy12/partials/organisation/metric.html'

    return render(request=request, template_name=template_name, context=context)
