from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.forms_folder.investigation_management_form import InvestigationManagementForm
from epilepsy12.models import investigation_management

from epilepsy12.models.case import Case

from ..models import Registration, Investigation_Management


@login_required
def create_investigation_management(request, case_id):
    investigation_management_form = InvestigationManagementForm(
        request.POST or None)
    registration = Registration.objects.filter(case=case_id).first()
    investigation_management = Investigation_Management.objects.filter(
        registration=registration)
    if request.method == "POST":
        if investigation_management_form.is_valid():
            investigation_management_obj = investigation_management_form.save(
                commit=False)
            investigation_management_obj.registration = registration
            Registration.objects.filter(case=case_id).update(
                investigation_management_complete=True)
            investigation_management_obj.save()
            return redirect('cases')
        else:
            print('not valid')
    case = Case.objects.get(id=case_id)

    context = {
        "investigation_management_form": investigation_management_form,
        "investigation_management": investigation_management,
        "case_id": case_id,
        "registration": registration,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "investigation_management"
    }
    return render(request=request, template_name='epilepsy12/investigation_management.html', context=context)


@login_required
def update_investigation_management(request, case_id):
    investigation_management_milestones = Investigation_Management.objects.filter(
        registration__case=case_id).first()
    investigation_management_form = InvestigationManagementForm(
        instance=investigation_management_milestones)

    if request.method == "POST":
        if ('delete') in request.POST:
            investigation_management_form.delete()
            return redirect('cases')
        if investigation_management_form.is_valid():
            investigation_managment_obj = investigation_management_form.save(
                commit=False)
            Registration.objects.filter(case=case_id).update(
                investigation_management_complete=True)
            investigation_managment_obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')

    case = Case.objects.get(id=case_id)
    registration = Registration.objects.filter(case=case_id).first()
    context = {
        "investigation_management_form": investigation_management_form,
        "case_id": case_id,
        "registration": registration,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "investigation_management"
    }

    return render(request=request, template_name='epilepsy12/investigation_management.html', context=context)


@login_required
def delete_investigation_management(request, case_id):
    # investigation_management = get_object_or_404(InvestigationManagmentForm, id=id)
    # investigation_management.delete()
    return redirect('cases')


# HX endpoints

def medication_lookup(request, investigation_management_id):
    print(request.POST.get('medication_lookup'))
    return HttpResponse("Medications")
