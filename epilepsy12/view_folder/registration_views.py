from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date

from ..models import Registration
from ..models import Case
from ..forms_folder import RegistrationForm


@login_required
def register(request, id):

    case = Case.objects.get(pk=id)
    try:
        registration = Registration.objects.get(case=case)
    except:
        registration = None

    context = {
        "registration": registration,
        "case_id": id,
        "initial_assessment_complete": False,
        "assessment_complete": False,
        "epilepsy_context_complete": False,
        "multiaxial_description_complete": False,
        "investigation_management_complete": False,
        "active_template": "none"
    }
    return render(request=request, template_name='epilepsy12/register.html', context=context)


@login_required
def delete_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    registration.delete()
    return redirect('cases')


# HTMX endpoints

@login_required
def registration_date(request, case_id):
    registration_date = date.today()
    case = Case.objects.get(pk=case_id)
    Registration.objects.update_or_create(
        registration_date=registration_date, case=case)
    registration = Registration.objects.filter(case=case).first()
    context = {
        'case_id': case_id,
        'registration': registration
    }
    return render(request=request, template_name='epilepsy12/partials/registration_dates.html', context=context)
