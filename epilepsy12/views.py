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
    template_name = 'epilepsy12/hospital.html'
    hospital_object = HospitalTrust.objects.get(
        OrganisationName=request.user.hospital_trust)

    # all_registrations = Registration.objects.all()
    # for registration in all_registrations.iterator():
    #     ap = AuditProgress.objects.create(
    #         initial_assessment_complete=False,
    #         assessment_complete=False,
    #         epilepsy_context_complete=False,
    #         multiaxial_description_complete=False,
    #         investigation_management_complete=False
    #     )
    #     registration.audit_progress = ap
    #     registration.save()

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

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'hospital': hospital_object,
        'cases_aggregated_by_ethnicity': cases_aggregated_by_ethnicity,
        'cases_aggregated_by_gender': cases_aggregated_by_gender,
        'cases_aggregated_by_deprivation': cases_aggregated_by_deprivation
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

def hospital_list(request):
    """
    HTMX call back from hospital_list partial.
    Receives a GET request, returns just a hospital list
    Returns the same dropdown partial populated with hospitals
    It also receives the name of the selected value and uses this to
    identify which template to return, including params such as text in the button
    returned parameter include on create:
    hx_post_url : url name
    hx_post = full url with params
    hx_label = label for button
    hx_assessment_id = assessment pk
    hx_target = target id of element to replace with template
    hx_site_id = id of site selected in dropdown
    site = site object
    hx_default_text : populates the default prompt text in the input box
    hx_name : the name for the dropdown to identify selected hospital in the view
    """

    hx_post_url = None
    hx_post = None
    hx_label = None
    hx_site_id = None
    site = None
    hx_label = None
    hx_default_text = None
    hx_name = None

    # common params to return
    hx_assessment_id = request.GET.get('hx_assessment_id')
    hx_target = request.GET.get('hx_target')
    hx_name = request.GET.get('hx_name')

    if request.htmx.trigger_name == "epilepsy_surgery_centre":
        # request is coming from assessment tab to add a new surgical centre
        hx_post_url = 'epilepsy_surgery_centre'
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id})
        hx_label = "Allocate Children's Surgical Centre"
        hx_default_text = "Search for a children's epilepsy surgery centre..."

    elif request.htmx.trigger_name == "edit_epilepsy_surgery_centre":
        # request if coming from assessment tab to update/edit an existing centre
        hx_post_url = 'edit_epilepsy_surgery_centre'
        hx_label = "Update Children's Surgical Centre"
        hx_site_id = request.GET.get('hx_site_id')
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id, 'site_id': hx_site_id})
        site = Site.objects.get(pk=hx_site_id)
        hx_default_text = "Search for a children's epilepsy surgery centre..."

    elif request.htmx.trigger_name == "paediatric_neurology_centre":
        # request is coming from assessment tab to add a new paediatric neurology centre
        hx_post_url = 'paediatric_neurology_centre'
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id})
        hx_label = "Allocate Paediatric Neurology Centre"
        hx_default_text = "Search for a paediatric neurology centre..."

    elif request.htmx.trigger_name == "edit_paediatric_neurology_centre":
        # request if coming from assessment tab to update/edit an existing paediatric neurology centre
        hx_post_url = 'edit_paediatric_neurology_centre'
        hx_label = "Update Paediatric Neurology Centre"
        hx_site_id = request.GET.get('hx_site_id')
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id, 'site_id': hx_site_id})
        site = Site.objects.get(pk=hx_site_id)
        hx_default_text = "Search for a paediatric neurology centre..."
    elif request.htmx.trigger_name == "general_paediatric_centre":
        # request is coming from assessment tab to add a new paediatric neurology centre
        hx_post_url = 'general_paediatric_centre'
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id})
        hx_label = "Allocate General Paediatric Centre"
        hx_default_text = "Search for a general paediatric centre..."

    elif request.htmx.trigger_name == "edit_general_paediatric_centre":
        # request if coming from assessment tab to update/edit an existing paediatric neurology centre
        hx_post_url = 'edit_general_paediatric_centre'
        hx_label = "Update General Paediatric Centre"
        hx_site_id = request.GET.get('hx_site_id')
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id, 'site_id': hx_site_id})
        site = Site.objects.get(pk=hx_site_id)
        hx_default_text = "Search for a general paediatric centre..."

    # filter list to include only NHS hospitals
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
    context = {
        "hospital_list": hospital_list,
        "hx_post": hx_post,
        "label": hx_label,
        "default_text": hx_default_text,
        "assessment_id": hx_assessment_id,
        "hx_target": hx_target,
        "hx_site_id": hx_site_id,
        "hx_name": hx_name,
        "site": site
    }
    return render(request=request, template_name="epilepsy12/partials/page_elements/hospitals_select.html", context=context)
