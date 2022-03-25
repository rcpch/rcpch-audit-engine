from django.shortcuts import render

from .view_folder import *


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    return render(request, template_name, {})


def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})


def hospital_reports(request):
    template_name = 'epilepsy12/hospital.html'
    return render(request=request, template_name=template_name, context={})


def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})


def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})
