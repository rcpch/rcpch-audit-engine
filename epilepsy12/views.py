import django
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.ethnicities import ETHNICITIES
from epilepsy12.models.case import Case
from django.db.models import Count, When, Value, CharField
from django.db.models import Case as DJANGO_CASE

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

    ethnicity_long_list = [When(ethnicity=k, then=Value(v))
                           for k, v in ETHNICITIES]

    case = (
        Case.objects.values('ethnicity')
        .annotate(
            ethnicity_display=DJANGO_CASE(
                *ethnicity_long_list, output_field=CharField()
            )
        )
        .values('ethnicity_display')
        .annotate(
            ethnicities=Count('ethnicity')).order_by()
    )

    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'hospital': hospital_object,
        'cases': case
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
    If a GET request, returns just a hospital list
    If a POST request, differentiates between an edit/update of an existing surgical centre
    or creation of a new one.
    Returns the same dropdown partial
    """

    hx_post_url = None
    hx_post = None
    hx_label = None
    hx_assessment_id = None
    hx_target = None
    hx_site_id = None
    site = None
    hx_label = None

    if request.htmx.trigger_name == "epilepsy_surgery_centre":
        # request is coming from assessment tab to add a new surgical centre
        hx_post_url = 'epilepsy_surgery_centre'
        hx_assessment_id = request.GET.get('hx_assessment_id')
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id})
        hx_label = "Allocate Children's Surgical Centre"
        hx_target = request.GET.get('hx_target')
    elif request.htmx.trigger_name == "edit_epilepsy_surgery_centre":
        # request if coming from assessment tab to update/edit an existing centre
        hx_post_url = 'edit_epilepsy_surgery_centre'
        hx_label = "Update Children's Surgical Centre"
        hx_assessment_id = request.GET.get('hx_assessment_id')
        hx_target = request.GET.get('hx_target')
        hx_site_id = request.GET.get('hx_site_id')
        hx_post = reverse(hx_post_url, kwargs={
                          'assessment_id': hx_assessment_id, 'site_id': hx_site_id})
        site = Site.objects.get(pk=hx_site_id)
    hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('OrganisationName')
    context = {
        "hospital_list": hospital_list,
        "hx_post": hx_post,
        "label": hx_label,
        "assessment_id": hx_assessment_id,
        "hx_target": hx_target,
        "hx_site_id": hx_site_id,
        "site": site
    }
    return render(request=request, template_name="epilepsy12/partials/page_elements/hospitals_select.html", context=context)
