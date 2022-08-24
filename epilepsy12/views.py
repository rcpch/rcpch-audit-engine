import math
import operator
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.ethnicities import ETHNICITIES
from epilepsy12.models.case import Case
from django.db.models import Count, When, Value, CharField, PositiveSmallIntegerField
from django.db.models import Case as DJANGO_CASE
from .models import AuditProgress

from .view_folder import *

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

    Registration.objects.all().delete()

    """
    !!!
    """

    template_name = 'epilepsy12/hospital.html'
    hospital_object = HospitalTrust.objects.get(
        OrganisationName=request.user.hospital_trust)

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
    gender_long_list = [When(gender=k, then=Value(v))
                        for k, v in SEX_TYPE]

    cases_aggregated_by_ethnicity = (
        Case.objects
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

    cases_aggregated_by_gender = (
        Case.objects
        .values('gender')
        .annotate(
            gender_display=DJANGO_CASE(
                *gender_long_list, output_field=CharField()
            )
        )
        .values('gender_display')
        .annotate(
            genders=Count('gender')).order_by('genders')
    )

    cases_aggregated_by_deprivation = (
        Case.objects
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

    total_registrations = Registration.objects.all().count()
    total_cases = Case.objects.all().count()

    total_referred_to_paediatrics = Assessment.objects.filter(
        consultant_paediatrician_referral_made=True).count()
    total_referred_to_neurology = Assessment.objects.filter(
        paediatric_neurologist_referral_made=True).count()
    total_referred_to_surgery = Assessment.objects.filter(
        childrens_epilepsy_surgical_service_referral_made=True).count()

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'hospital': hospital_object,
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity,
        'cases_aggregated_by_gender': cases_aggregated_by_gender,
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation,
        'percent_completed_registrations': round((total_registrations/total_cases)*100),
        'total_registrations': total_registrations,
        'total_cases': total_cases,
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


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


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
