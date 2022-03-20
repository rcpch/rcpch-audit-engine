from django.shortcuts import render

from .view_folder import *
from .models import Case


def index(request):
    template_name = 'epilepsy12/epilepsy12index.html'
    return render(request, template_name, {})


def database(request):
    template_name = 'epilepsy12/database.html'
    return render(request, template_name, {})


def hospital(request):
    case_list = Case.objects.all().order_by('surname')
    registered_cases = Registration.objects.all().count()
    case_count = Case.objects.all().count()
    context = {
        'case_list': case_list,
        'total_cases': case_count,
        'total_registrations': registered_cases
    }
    template_name = 'epilepsy12/cases/cases.html'
    return render(request, template_name, context)


def eeg(request):
    template_name = 'epilepsy12/eeg.html'
    return render(request, template_name, {})


def patient(request):
    template_name = 'epilepsy12/patient.html'
    return render(request, template_name, {})
