from django.conf import settings
from django.http import FileResponse, HttpRequest, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from django.contrib.auth.models import Group
from django.shortcuts import render
# from django.contrib.auth.forms import UserCreationForm
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from epilepsy12.constants.ethnicities import ETHNICITIES
from epilepsy12.models.case import Case
from django.db.models import Count, When, Value, CharField, PositiveSmallIntegerField
from django.db.models import Case as DJANGO_CASE
from itertools import chain
from .view_folder import *
from django_htmx.http import HttpResponseClientRedirect

user = get_user_model()


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

    """
    !!!
    """

    """
    Remove duplicates
    """
    for duplicates in Epilepsy12User.objects.values("email").annotate(
        records=Count("email")
    ).filter(records__gt=1):
        for epilepsy12user in Epilepsy12User.objects.filter(name=duplicates["email"])[1:]:
            epilepsy12user.delete()

    # Audit trail - filter all models and sort in order of updated_at, returning the latest 5 updates
    initial_assessment = InitialAssessment.objects.filter()
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
        chain(registration, initial_assessment, site, epilepsy_context, multiaxial_diagnosis,
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
            Sector="NHS Sector").order_by('OrganisationName').first(),

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
        'all_models': all_models
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


@require_GET
@cache_control(max_age=60 * 60 * 24, immutable=True, public=True)  # one day
def favicon(request: HttpRequest) -> HttpResponse:
    file = (settings.BASE_DIR / "static" /
            "images/favicon-16x16.png").open("rb")
    return FileResponse(file)
