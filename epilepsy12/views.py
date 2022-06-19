from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

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
    return render(request=request, template_name=template_name, context={
        'user': request.user,
        'hospital': hospital_object
    })


def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})


def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
