# Python/Django imports
from itertools import chain
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
# third party libraries
from django_htmx.http import HttpResponseClientRedirect

# E12 imports
from epilepsy12.constants import ETHNICITIES, INDIVIDUAL_KPI_MEASURES, SEX_TYPE, INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES
from epilepsy12.models import Case, FirstPaediatricAssessment, Assessment, Case, FirstPaediatricAssessment, Assessment, Site, EpilepsyContext, MultiaxialDiagnosis, Syndrome, Investigations, Management, Comorbidity, Registration, Episode, HospitalTrust, KPI
from ..common_view_functions import trigger_client_event, hospital_level_kpis, trust_level_kpis, national_level_kpis, cases_aggregated_by_sex, cases_aggregated_by_ethnicity, cases_aggregated_by_deprivation_score
from ..general_functions import value_from_key


@login_required
def hospital_reports(request):

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

    all_models = sorted(
        chain(registration, first_paediatric_assessment, site, epilepsy_context, multiaxial_diagnosis,
              episode, syndrome, comorbidity, assessment, investigations, management),
        key=lambda x: x.updated_at, reverse=True)[:5]

    template_name = 'epilepsy12/hospital.html'

    if request.user.hospital_employer is not None:
        # current user is affiliated with an existing hospital - set viewable trust to this
        selected_hospital = HospitalTrust.objects.get(
            OrganisationName=request.user.hospital_employer)

        # query to return all cases and registrations of hospital of logged in user if clinician
        all_cases = Case.objects.filter(
            hospital_trusts__OrganisationName__contains=request.user.hospital_employer).all().count()
        all_registrations = Case.objects.filter(
            hospital_trusts__OrganisationName__contains=request.user.hospital_employer).all().filter(
                registration__isnull=False).count()
    else:
        # current user is a member of the RCPCH audit team and also not affiliated with a hospital
        # therefore set selected hospital to first of hospital on the list

        selected_hospital = HospitalTrust.objects.filter(
            Sector="NHS Sector"
        ).order_by('OrganisationName').first()

        all_registrations = Registration.objects.all().count()
        all_cases = Case.objects.all().count()

    total_referred_to_paediatrics = Assessment.objects.filter(
        consultant_paediatrician_referral_made=True).count()
    total_referred_to_neurology = Assessment.objects.filter(
        paediatric_neurologist_referral_made=True).count()
    total_referred_to_surgery = Assessment.objects.filter(
        childrens_epilepsy_surgical_service_referral_made=True).count()

    if all_cases > 0:
        total_percent = round((all_registrations / all_cases) * 100)
    else:
        total_percent = 0

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'selected_hospital': selected_hospital,
        'hospital_list': HospitalTrust.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity(selected_hospital=selected_hospital),
        'cases_aggregated_by_sex': cases_aggregated_by_sex(selected_hospital=selected_hospital),
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation_score(selected_hospital=selected_hospital),
        'percent_completed_registrations': total_percent,
        'total_registrations': all_registrations,
        'total_cases': all_cases,
        'total_referred_to_paediatrics': total_referred_to_paediatrics,
        'total_referred_to_neurology': total_referred_to_neurology,
        'total_referred_to_surgery': total_referred_to_surgery,
        'all_models': all_models,
        'model_list': ('allregisteredcases', 'registration', 'firstpaediatricassessment', 'epilepsycontext', 'multiaxialdiagnosis', 'assessment', 'investigations', 'management', 'site', 'case', 'epilepsy12user', 'hospitaltrust', 'comorbidity', 'episode', 'syndrome', 'keyword'),
        'individual_kpi_choices': INDIVIDUAL_KPI_MEASURES
    })


@login_required
def selected_hospital_summary(request):
    """
    POST request from selected_hospital_summary.html on hospital select
    """

    selected_hospital = HospitalTrust.objects.get(
        pk=request.POST.get('selected_hospital_summary'))

    # query to return all cases and registrations of selected hospital
    all_cases = Case.objects.filter(
        hospital_trusts__OrganisationName__contains=selected_hospital).all().count()
    all_registrations = Case.objects.filter(
        hospital_trusts__OrganisationName__contains=selected_hospital).all().filter(
            registration__isnull=False).count()

    total_referred_to_paediatrics = Assessment.objects.filter(
        consultant_paediatrician_referral_made=True).count()
    total_referred_to_neurology = Assessment.objects.filter(
        paediatric_neurologist_referral_made=True).count()
    total_referred_to_surgery = Assessment.objects.filter(
        childrens_epilepsy_surgical_service_referral_made=True).count()

    if all_cases > 0:
        total_percent = round((all_registrations / all_cases) * 100)
    else:
        total_percent = 0

    return render(request=request, template_name='epilepsy12/partials/selected_hospital_summary.html', context={
        'user': request.user,
        'selected_hospital': selected_hospital,
        'hospital_list': HospitalTrust.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity(selected_hospital=selected_hospital),
        'cases_aggregated_by_sex': cases_aggregated_by_sex(selected_hospital=selected_hospital),
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation_score(selected_hospital=selected_hospital),
        'percent_completed_registrations': total_percent,
        'total_registrations': all_registrations,
        'total_cases': all_cases,
        'total_referred_to_paediatrics': total_referred_to_paediatrics,
        'total_referred_to_neurology': total_referred_to_neurology,
        'total_referred_to_surgery': total_referred_to_surgery,
        'individual_kpi_choices': INDIVIDUAL_KPI_MEASURES
    })


def selected_trust_kpis(request, hospital_id):
    """
    HTMX get request returning trust_level_kpi.html partial
    """
    trust_kpis = trust_level_kpis(hospital_id=hospital_id)
    national_kpis = national_level_kpis()
    hospital_organisation = HospitalTrust.objects.get(pk=hospital_id)
    hospital_kpis = hospital_level_kpis(hospital_id=hospital_id)
    # create an empty instance of KPIs to access the labels
    kpis = KPI.objects.create(
        hospital_organisation=hospital_organisation,
        parent_trust=hospital_organisation.ParentName
    )
    template_name = 'epilepsy12/partials/kpis/kpis.html'
    context = {
        'hospital_organisation': hospital_organisation,
        'hospital_kpis': hospital_kpis,
        'trust_kpis': trust_kpis,
        'national_kpis': national_kpis,
        'kpis': kpis
    }

    response = render(
        request=request, template_name=template_name, context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
def child_hospital_select(request, hospital_id, template_name):
    """
    POST call back from hospital_select to allow user to toggle between hospitals in selected trust
    """

    selected_hospital_id = request.POST.get('child_hospital_select')

    # get currently selected hospital
    hospital_trust = HospitalTrust.objects.get(pk=selected_hospital_id)

    # trigger page reload with new hospital
    return HttpResponseClientRedirect(reverse(template_name, kwargs={'hospital_id': hospital_trust.pk}))


@login_required
def view_preference(request, hospital_id, template_name):
    """
    POST request from Toggle in has rcpch_view_preference.html template
    Users can toggle between national, trust and hospital views.
    Only RCPCH staff can request a national view.
    """
    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    request.user.view_preference = request.htmx.trigger_name
    request.user.save()

    return HttpResponseClientRedirect(reverse(template_name, kwargs={'hospital_id': hospital_trust.pk}))


def selected_trust_select_kpi(request, hospital_id):
    """
    POST request from dropdown in selected_hospital_summary.html
    """

    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    context = {
        'kpi_name': request.POST.get('kpi_name'),
        'kpi_value': value_from_key(key=request.POST.get('kpi_name'), choices=INDIVIDUAL_KPI_MEASURES),
        'selected_hospital': hospital_trust
    }

    template_name = 'epilepsy12/partials/hospital/metric.html'

    return render(request=request, template_name=template_name, context=context)


def selected_trust_selected_kpi(request, hospital_id, kpi_name):
    """
    GET request returning selected kpi for that trust
    """
    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    # for organisation in INTEGRATED_CARE_BOARDS_LOCAL_AUTHORITIES:
    #     if HospitalTrust.objects.filter(ParentODSCode=organisation["ODS Trust Code"]).exists():
    #         for hospital in HospitalTrust.objects.filter(ParentODSCode=organisation["ODS Trust Code"]):
    #             print(
    #                 f"{hospital.OrganisationName} ({hospital.ParentName} - {hospital.ParentODSCode})")

    context = {
        'selected_hospital': hospital_trust,
        'kpi_name': kpi_name,
        'kpi_value': value_from_key(key=kpi_name, choices=INDIVIDUAL_KPI_MEASURES)
    }

    template_name = 'epilepsy12/partials/hospital/metric.html'

    return render(request=request, template_name=template_name, context=context)
