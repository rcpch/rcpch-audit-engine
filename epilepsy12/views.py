
# django
from datetime import datetime
from django.apps import apps
from django.db.models import Count, When, Value, CharField, PositiveSmallIntegerField, Case as DJANGO_CASE
from django.conf import settings
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

# django rest framework
from rest_framework import permissions, viewsets

# python
import csv
from itertools import chain

# third party libraries
from django_htmx.http import HttpResponseClientRedirect

# epilepsy12
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserCreationForm, Epilepsy12LoginForm

from epilepsy12.constants.ethnicities import ETHNICITIES
from epilepsy12.models import Case, Epilepsy12User, FirstPaediatricAssessment, Assessment
from .view_folder import *
from .decorator import rcpch_full_access_only
from .serializers import *

user = get_user_model()


def epilepsy12_login(request):
    if request.method == "POST":
        form = Epilepsy12LoginForm(request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.email_confirmed == False:
                    user.email_confirmed = True
                    user.save()
                login(request, user)
                messages.info(request, f"You are now logged in as {email}.")
                return redirect("hospital_reports")
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = Epilepsy12LoginForm()
    return render(request=request, template_name="registration/login.html", context={"form": form})


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    return render(request, template_name, {})


def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})


@login_required
def hospital_reports(request):
    """
    !!!!
    One time statement only for development
    Drops all registration and related records
    !!!!
    """

    # Registration.objects.all().delete()
    # Episode.objects.all().delete()

    # this snippet forces a resave on all registration objects to recalculate submission date
    # it is a one time only step
    # all_registration = Registration.objects.all()
    # for reg in all_registration:
    #     # if reg.audit_submission_date:
    #     #     print(f'audit close: {reg.case}: {reg.audit_submission_date}')
    #     if reg.registration_date:
    #         print(
    #             f'registration date: {reg.case}: {reg.registration_date} audit close: {reg.case}: {reg.audit_submission_date}')
    #         reg.save()
    #     else:
    #         print('nothing to see here')

    """
    !!!
    """

    """
    Remove duplicates
    """
    # for duplicates in Epilepsy12User.objects.values("email").annotate(
    #     records=Count("email")
    # ).filter(records__gt=1):
    #     for epilepsy12user in Epilepsy12User.objects.filter(name=duplicates["email"])[1:]:
    #         epilepsy12user.delete()

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

    # aggregate queries on trust level cases
    deprivation_quintiles = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    ethnicity_long_list = [When(ethnicity=k, then=Value(v))
                           for k, v in ETHNICITIES]
    imd_long_list = [When(index_of_multiple_deprivation_quintile=k, then=Value(v))
                     for k, v in deprivation_quintiles]
    sex_long_list = [When(sex=k, then=Value(v))
                     for k, v in SEX_TYPE]

    cases_aggregated_by_ethnicity = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('ethnicity')
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values('ethnicity_display')
        .annotate(
            ethnicities=Count('ethnicity')).order_by('ethnicities')
    )

    cases_aggregated_by_sex = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('sex')
        .annotate(
            sex_display=DJANGO_CASE(
                *sex_long_list, output_field=CharField()
            )
        )
        .values('sex_display')
        .annotate(
            sexes=Count('sex')).order_by('sexes')
    )

    cases_aggregated_by_deprivation = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('index_of_multiple_deprivation_quintile')
        .annotate(
            index_of_multiple_deprivation_quintile_display=DJANGO_CASE(
                *imd_long_list, output_field=PositiveSmallIntegerField()
            )
        )
        .values('index_of_multiple_deprivation_quintile_display')
        .annotate(
            cases_aggregated_by_deprivation=Count('index_of_multiple_deprivation_quintile'))
        .order_by('cases_aggregated_by_deprivation')
    )

    total_referred_to_paediatrics = Assessment.objects.filter(
        consultant_paediatrician_referral_made=True).count()
    total_referred_to_neurology = Assessment.objects.filter(
        paediatric_neurologist_referral_made=True).count()
    total_referred_to_surgery = Assessment.objects.filter(
        childrens_epilepsy_surgical_service_referral_made=True).count()

    if all_cases > 0:
        total_percent = round((all_registrations/all_cases)*100)
    else:
        total_percent = 0

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'selected_hospital': selected_hospital,
        'hospital_list': HospitalTrust.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity,
        'cases_aggregated_by_sex': cases_aggregated_by_sex,
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation,
        'percent_completed_registrations': total_percent,
        'total_registrations': all_registrations,
        'total_cases': all_cases,
        'total_referred_to_paediatrics': total_referred_to_paediatrics,
        'total_referred_to_neurology': total_referred_to_neurology,
        'total_referred_to_surgery': total_referred_to_surgery,
        'all_models': all_models,
        'model_list': ('allregisteredcases', 'registration', 'firstpaediatricassessment', 'epilepsycontext', 'multiaxialdiagnosis', 'assessment', 'investigations', 'management', 'site', 'case', 'epilepsy12user', 'hospitaltrust', 'comorbidity', 'episode', 'syndrome', 'keyword'),
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

    # aggregate queries on trust level cases
    deprivation_quintiles = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )

    ethnicity_long_list = [When(ethnicity=k, then=Value(v))
                           for k, v in ETHNICITIES]
    imd_long_list = [When(index_of_multiple_deprivation_quintile=k, then=Value(v))
                     for k, v in deprivation_quintiles]
    sex_long_list = [When(sex=k, then=Value(v))
                     for k, v in SEX_TYPE]

    cases_aggregated_by_ethnicity = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('ethnicity')
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values('ethnicity_display')
        .annotate(
            ethnicities=Count('ethnicity')).order_by('ethnicities')
    )

    cases_aggregated_by_sex = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('sex')
        .annotate(
            sex_display=DJANGO_CASE(
                *sex_long_list, output_field=CharField()
            )
        )
        .values('sex_display')
        .annotate(
            sexes=Count('sex')).order_by('sexes')
    )

    cases_aggregated_by_deprivation = (
        Case.objects.filter(
            hospital_trusts__OrganisationName__contains=selected_hospital)
        .values('index_of_multiple_deprivation_quintile')
        .annotate(
            index_of_multiple_deprivation_quintile_display=DJANGO_CASE(
                *imd_long_list, output_field=PositiveSmallIntegerField()
            )
        )
        .values('index_of_multiple_deprivation_quintile_display')
        .annotate(
            cases_aggregated_by_deprivation=Count('index_of_multiple_deprivation_quintile'))
        .order_by('cases_aggregated_by_deprivation')
    )

    total_referred_to_paediatrics = Assessment.objects.filter(
        consultant_paediatrician_referral_made=True).count()
    total_referred_to_neurology = Assessment.objects.filter(
        paediatric_neurologist_referral_made=True).count()
    total_referred_to_surgery = Assessment.objects.filter(
        childrens_epilepsy_surgical_service_referral_made=True).count()

    if all_cases > 0:
        total_percent = round((all_registrations/all_cases)*100)
    else:
        total_percent = 0

    return render(request=request, template_name='epilepsy12/partials/selected_hospital_summary.html', context={
        'user': request.user,
        'selected_hospital': selected_hospital,
        'hospital_list': HospitalTrust.objects.filter(Sector="NHS Sector").order_by('OrganisationName').all(),
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity,
        'cases_aggregated_by_sex': cases_aggregated_by_sex,
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation,
        'percent_completed_registrations': total_percent,
        'total_registrations': all_registrations,
        'total_cases': all_cases,
        'total_referred_to_paediatrics': total_referred_to_paediatrics,
        'total_referred_to_neurology': total_referred_to_neurology,
        'total_referred_to_surgery': total_referred_to_surgery,
    })


def tsandcs(request):
    template_name = 'epilepsy12/terms_and_conditions.html'
    return render(request, template_name, {})


def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})


def documentation(request):
    template_name = 'epilepsy12/docs.html'
    return render(request, template_name, {})


def signup(request, *args, **kwargs):
    """
    Part of the registration process. Signing up for a new account, returns empty form as a GET request
    or validates the form, creates an account and allocates a group if part of a POST request. It is not possible 
    to create a superuser account through this route.
    """
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f'{user} is already logged in!')

    if request.method == 'POST':
        form = Epilepsy12UserCreationForm(request.POST)
        if form.is_valid():
            logged_in_user = form.save()
            logged_in_user.is_active = True
            """
            Allocate Roles
            """
            logged_in_user.is_superuser = False
            if logged_in_user.role == AUDIT_CENTRE_LEAD_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
                logged_in_user.is_staff = True
            elif logged_in_user.role == AUDIT_CENTRE_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
                logged_in_user.is_staff = True
            elif logged_in_user.role == AUDIT_CENTRE_ADMINISTRATOR:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
                logged_in_user.is_staff = True
            elif logged_in_user.role == RCPCH_AUDIT_LEAD:
                group = Group.objects.get(
                    name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
            elif logged_in_user.role == RCPCH_AUDIT_ANALYST:
                group = Group.objects.get(
                    name=EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS)
            elif logged_in_user.role == RCPCH_AUDIT_ADMINISTRATOR:
                group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_VIEW_ONLY)
            elif logged_in_user.role == RCPCH_AUDIT_PATIENT_FAMILY:
                group = Group.objects.get(name=PATIENT_ACCESS)
            else:
                # no group
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)

            logged_in_user.save()
            logged_in_user.groups.add(group)
            login(request, logged_in_user,
                  backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Sign up successful.")
            return redirect('hospital_reports')
        for msg in form.error_messages:
            messages.error(
                request, f"Registration Unsuccessful: {form.error_messages[msg]}")

    form = Epilepsy12UserCreationForm()
    return render(request=request, template_name='registration/signup.html', context={'form': form})


# HTMX generic partials
def registration_active(request, case_id, active_template):
    """
    Call back from GET request in steps partial template
    Triggered also on registration in the audit
    """
    registration = Registration.objects.get(case=case_id)
    audit_progress = registration.audit_progress

    # enable the steps if has just registered
    if audit_progress.registration_complete:
        if active_template == 'none':
            active_template = 'register'

    context = {
        'audit_progress': audit_progress,
        'active_template': active_template,
        'case_id': case_id
    }

    return render(request=request, template_name='epilepsy12/steps.html', context=context)


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


@login_required
@rcpch_full_access_only()
def download_select(request):
    """
    POST request from frida_button.html
    """
    model = request.POST.get('model')

    context = {
        'selected_model': model,
        'model_list': ('allregisteredcases', 'registration', 'firstpaediatricassessment', 'epilepsycontext', 'multiaxialdiagnosis', 'assessment', 'investigations', 'management', 'site', 'case', 'epilepsy12user', 'hospitaltrust', 'comorbidity', 'episode', 'syndrome', 'keyword'),
        'is_selected': True
    }

    return render(request, template_name='epilepsy12/partials/frida_button.html', context=context)


@login_required
@rcpch_full_access_only()
def download(request, model_name):
    """
    POST request to download table as csv
    """

    field_list = []

    if model_name == 'allregisteredcases':
        one_to_one_tables = ['registration', 'case', 'firstpaediatricassessment',
                             'epilepsycontext', 'multiaxialdiagnosis', 'assessment', 'investigations', 'management']

        for index, one_to_one_table in enumerate(one_to_one_tables):
            model_class = apps.get_model(
                app_label='epilepsy12', model_name=one_to_one_table)
            fields = model_class._meta.get_fields()

            for field in fields:
                if field.name in ['id', 'episode', 'syndrome', 'antiepilepsymedicine', 'comorbidity']:
                    pass
                else:
                    if one_to_one_table == 'registration':
                        relative_field_name = field.name
                    else:
                        relative_field_name = f'{one_to_one_table}__{field.name}'
                        if field.name == 'hospital_trusts':
                            relative_field_name += '__OrganisationName'
                    field_list.append(relative_field_name)
        model_class = Registration
    else:
        model_class = apps.get_model(
            app_label='epilepsy12', model_name=model_name)

        fields = model_class._meta.get_fields()
        for field in fields:
            field_list.append(field.name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="all_registered_cases.csv"'

    writer = csv.writer(response)

    all_fields = model_class.objects.all().values(*field_list)

    for index, p in enumerate(all_fields):
        if index == 0:
            # csv headings - format the name to be readable from the key and add to the header
            headers = p.keys()

            header_list = []
            for header in headers:
                # loop through the headings and remove the model name which prefixes the field by __
                split_header = header.split('__')
                header_list.append(split_header[-1])
            writer.writerow(header_list)
        else:
            # discard the keys and store only the values in each row. If the value represents a choice,
            # get the choice key from the value
            # this is a bit tedious but because a queryset is not an instance of the model, we have to create
            # one in order to use the get_field_display() model instance method to look up the key name.
            # This function has been abstracted out to the return_choice_for_instance_and_value function below
            if p.get('case__sex') is not None:
                field_value = p.get(
                    'case__sex')
                choice = return_choice_for_instance_and_value(
                    Case, 'sex', field_value)
                p['case__sex'] = choice

            if p.get('case__ethnicity') is not None:
                field_value = p.get(
                    'case__ethnicity')
                choice = return_choice_for_instance_and_value(
                    Case, 'ethnicity', field_value)
                p['case__ethnicity'] = choice

            if p.get('firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting') is not None:
                field_value = p.get(
                    'firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting')
                choice = return_choice_for_instance_and_value(
                    FirstPaediatricAssessment, 'first_paediatric_assessment_in_acute_or_nonacute_setting', field_value)
                p['firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting'] = choice

            if p.get('epilepsycontext__previous_febrile_seizure') is not None:
                field_value = p.get(
                    'epilepsycontext__previous_febrile_seizure')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'previous_febrile_seizure', field_value)
                p['epilepsycontext__previous_febrile_seizure'] = choice

            if p.get('epilepsycontext__previous_acute_symptomatic_seizure') is not None:
                field_value = p.get(
                    'epilepsycontext__previous_acute_symptomatic_seizure')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'previous_acute_symptomatic_seizure', field_value)
                p['epilepsycontext__previous_acute_symptomatic_seizure'] = choice

            if p.get('epilepsycontext__is_there_a_family_history_of_epilepsy') is not None:
                field_value = p.get(
                    'epilepsycontext__is_there_a_family_history_of_epilepsy')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'is_there_a_family_history_of_epilepsy', field_value)
                p['epilepsycontext__is_there_a_family_history_of_epilepsy'] = choice

            if p.get('epilepsycontext__previous_neonatal_seizures') is not None:
                field_value = p.get(
                    'epilepsycontext__previous_neonatal_seizures')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'previous_neonatal_seizures', field_value)
                p['epilepsycontext__previous_neonatal_seizures'] = choice

            if p.get('epilepsycontext__experienced_prolonged_generalized_convulsive_seizures') is not None:
                field_value = p.get(
                    'epilepsycontext__experienced_prolonged_generalized_convulsive_seizures')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'experienced_prolonged_generalized_convulsive_seizures', field_value)
                p['epilepsycontext__experienced_prolonged_generalized_convulsive_seizures'] = choice

            if p.get('epilepsycontext__experienced_prolonged_focal_seizures') is not None:
                field_value = p.get(
                    'epilepsycontext__experienced_prolonged_focal_seizures')
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, 'experienced_prolonged_focal_seizures', field_value)
                p['epilepsycontext__experienced_prolonged_focal_seizures'] = choice

            if p.get('multiaxialdiagnosis__mental_health_issue') is not None:
                field_value = p.get('multiaxialdiagnosis__mental_health_issue')
                choice = return_choice_for_instance_and_value(
                    MultiaxialDiagnosis, 'mental_health_issue', field_value)
                p['multiaxialdiagnosis__mental_health_issue'] = choice

            # write the formated data to a new row in the csv
            writer.writerow(p.values())

    return response


def return_choice_for_instance_and_value(model, field, choice_value):
    query_object = {
        field: choice_value
    }
    temp_instance = model(**query_object)
    choice = getattr(temp_instance, 'get_{}_display'.format(field))()
    return choice


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" /
            "images/favicon-16x16.png").open("rb")
    return FileResponse(file)


def rcpch_403(request, exception):
    # this view is necessary to trigger a page refresh
    # it is called on raise PermissionDenied()
    # If a 403 template were to be returned at this point as in standard django,
    # the 403 template would be inserted into the target. This way the HttpReponseClientRedirect
    # from django-htmx middleware forces a redirect. Neat.
    if request.htmx:
        redirect = reverse_lazy('redirect_403')
        return HttpResponseClientRedirect(redirect)
    else:
        return render(request, template_name='epilepsy12/error_pages/rcpch_403.html', context={})


def redirect_403(request):
    # return the custom 403 template. There is not context to add.
    return render(request, template_name='epilepsy12/error_pages/rcpch_403.html', context={})


"""
Django Rest Framework Viewsets
"""


class Epilepsy12UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Epilepsy12User.objects.all().order_by('-surname')
    serializer_class = Epilepsy12UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class CaseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Case.objects.all().order_by('-surname')
    serializer_class = CaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_case_to_hospital_list(self, request):
        # params
        nhs_number = request.POST.get('nhs_number')
        organisationID = request.POST.get('OrganisationID')
        case_params = {
            'nhs_number': request.POST.get('nhs_number'),
            'first_name': request.POST.get('first_name'),
            'surname': request.POST.get('surname'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'sex': request.POST.get('sex'),
            'ethnicity': request.POST.get('ethnicity'),
        }
        if nhs_number:
            if Case.objects.filter(nhs_number=nhs_number).exists():
                case = Case.objects.filter(nhs_number=nhs_number).get()
                raise serializers.ValidationError(
                    {'Case': f'{case} already exists. No record created.'})
            else:
                serializer = self.serializer(data=case_params)

                if organisationID:

                    if serializer.is_valid(raise_exception=True):
                        if HospitalTrust.objects.filter(OrganisationID=request.POST.get('OrganisationID')).exists():
                            hospital_trust = HospitalTrust.objects.filter(
                                OrganisationID=request.POST.get('OrganisationID')).get()
                        else:
                            raise serializers.ValidationError(
                                {'Case': f'Organisation {organisationID} does not exist. No record saved.'})

                        try:
                            case = Case.objects.create(**case_params)
                        except Exception as error:
                            raise serializers.ValidationError(
                                {'Case': error})

                        print(f'{case} created')

                        try:
                            Site.objects.create(
                                case=case,
                                hospital_trust=hospital_trust,
                                site_is_actively_involved_in_epilepsy_care=True,
                                site_is_primary_centre_of_epilepsy_care=True
                            )
                        except Exception as error:
                            case.delete()
                            raise serializers.ValidationError(
                                {'Case': error})

                        return Response(
                            {
                                "status": "success",
                                "data": case_params
                            },
                            status=status.HTTP_200_OK
                        )

                else:
                    raise serializers.ValidationError(
                        {'Case': f'OrganisationID Not supplied. No record created.'})
        else:
            raise serializers.ValidationError(
                {'Case': f'NHS number not supplied. No record created.'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegistrationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows registrations in Epilepsy12 to be viewed or edited.
    """
    queryset = Registration.objects.all().order_by('-registration_date')
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register_case(self, request):
        """
        Create an active registration in the audit.
        Essential parameters:
        nhs_number: 10 digit number
        lead_centre: OrganisationID
        registration_date: date of first paediatric assessment
        eligibility_criteria_met: confirmation that child is eligible for audit
        """
        # collect parameters:
        registration_date = request.POST.get('registration_date')
        eligibility_criteria_met = request.POST.get(
            'eligibility_criteria_met')
        nhs_number = request.POST.get('nhs_number')
        lead_centre_id = request.POST.get('lead_centre')

        # validate those params within the serializer
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            # validate parameters relating to related models
            if lead_centre_id:
                if HospitalTrust.objects.filter(OrganisationID=lead_centre_id).exists():
                    lead_centre = HospitalTrust.objects.get(
                        OrganisationID=lead_centre_id)
                else:
                    raise serializers.ValidationError(
                        {'lead_centre': f'A valid lead centre identifier must be supplied. No record saved.'})
            else:
                raise serializers.ValidationError(
                    {'lead_centre': f'A lead centre identifier must be supplied. No record saved.'})

            if nhs_number:
                if Case.objects.filter(nhs_number=nhs_number).exists():
                    case = Case.objects.filter(nhs_number=nhs_number).get()
                    if Registration.objects.filter(case=case).exists():
                        raise serializers.ValidationError(
                            {'nhs_number': f'{case} is already registered. No record saved.'})
                else:
                    raise serializers.ValidationError(
                        {'nhs_number': f'{nhs_number} is not a recognised NHS Number. No record saved.'})
            else:
                raise serializers.ValidationError(
                    {'nhs_number': f'Please supply an NHS Number. No record saved.'})

            # create site
            try:
                site = Site.objects.create(
                    site_is_actively_involved_in_epilepsy_care=True,
                    site_is_primary_centre_of_epilepsy_care=True,
                    case=case,
                    hospital_trust=lead_centre
                )
            except Exception as error:
                raise serializers.ValidationError(error)

            # update AuditProgress
            try:
                audit_progress = AuditProgress.objects.create(
                    registration_complete=True,
                    registration_total_expected_fields=3,
                    registration_total_completed_fields=3
                )
            except Exception as error:
                # delete the site instance as some error
                site.delete()
                raise serializers.ValidationError(error)

            # create registration
            try:
                registration = Registration.objects.create(
                    case=case,
                    registration_date=datetime.strptime(
                        registration_date, '%Y-%m-%d').date(),
                    eligibility_criteria_met=eligibility_criteria_met,
                    audit_progress=audit_progress
                )
            except Exception as error:
                site.delete()
                audit_progress.delete()
                raise serializers.ValidationError(error)

            return Response(
                {
                    "status": "success",
                    "data": RegistrationSerializer(
                        instance=registration,
                        context={
                            'request': request
                        }).data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FirstPaediatricAssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows details relating to the first paediatric assessment to be viewed or edited.
    """
    queryset = FirstPaediatricAssessment.objects.all()
    serializer_class = FirstPaediatricAssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class EpilepsyContextViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows children's epilepsy risk factors to be viewed or edited.
    """
    queryset = EpilepsyContext.objects.all()
    serializer_class = EpilepsyContextSerializer
    permission_classes = [permissions.IsAuthenticated]


class MultiaxialDiagnosisViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a multiaxial diagnosis of the child's epilepsy to be viewed or edited.
    """
    queryset = MultiaxialDiagnosis.objects.all()
    serializer_class = MultiaxialDiagnosisSerializer
    permission_classes = [permissions.IsAuthenticated]


class EpisodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each seizure episode to be viewed or edited.
    """
    queryset = Episode.objects.all()
    serializer_class = EpisodeSerializer
    permission_classes = [permissions.IsAuthenticated]


class SyndromeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each syndrome to be viewed or edited.
    """
    queryset = Syndrome.objects.all()
    serializer_class = SyndromeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ComorbidityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows each comorbidity to be viewed or edited.
    """
    queryset = Comorbidity.objects.all()
    serializer_class = ComorbiditySerializer
    permission_classes = [permissions.IsAuthenticated]


class InvestigationsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a panel of investigations for each registration to be viewed or edited.
    """
    queryset = Investigations.objects.all()
    serializer_class = InvestigationsSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows key Epilepsy12 milestones to be viewed or edited.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ManagementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows management plans (including medications and individualised care plans) to be viewed or edited.
    """
    queryset = Management.objects.all()
    serializer_class = ManagementSerializer
    permission_classes = [permissions.IsAuthenticated]


class AntiEpilepsyMedicineViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows antiseizure medicines to be viewed or edited.
    """
    queryset = AntiEpilepsyMedicine.objects.all()
    serializer_class = AntiEpilepsyMedicineSerializer
    permission_classes = [permissions.IsAuthenticated]


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows allocated sites to be viewed or edited.
    """
    queryset = Site.objects.all()
    serializer_class = SiteSerializer
    permission_classes = [permissions.IsAuthenticated]


class HospitalTrustViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a list of hospital and community trusts to be viewed or edited.
    """
    queryset = HospitalTrust.objects.all()
    serializer_class = HospitalTrustSerializer
    permission_classes = [permissions.IsAuthenticated]


class KeywordViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows epilepsy semiology keywords to be viewed or edited.
    """
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer
    permission_classes = [permissions.IsAuthenticated]


class AuditProgressViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a child's progress through audit completion to be viewed or edited.
    """
    queryset = AuditProgress.objects.all()
    serializer_class = AuditProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
