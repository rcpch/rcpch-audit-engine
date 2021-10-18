from django import template
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import TemplateView
from django.shortcuts import render
from .snomed import get_description_by_id


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    # get_description_by_id(230437002)
    return render(request, template_name, {})

def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})

def hospital(request):
    template_name = 'epilepsy12/hospital.html'
    return render(request, template_name, {})

def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})
    
def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})
