from django import template
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import TemplateView
from django.shortcuts import render

from .models import Case, Assessment, InitialAssessment


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    return render(request, template_name, {})

def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})

def hospital(request):
    case_list = Case.objects.order_by('surname')[:10]
    context = {'case_list': case_list}
    template_name = 'epilepsy12/hospital.html'
    return render(request, template_name, context)

def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})
    
def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})
