from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.forms_folder.investigation_management_form import InvestigationForm, MedicationForm

from epilepsy12.models.case import Case

from ..models import Registration, Investigations, RescueMedicine


@login_required
def create_investigation_management(request, case_id):
    investigation_form = InvestigationForm(request.POST or None)
    medication_form = MedicationForm(request.POST or None)
    if request.method == "POST":
        if investigation_form.is_valid() and medication_form.is_valid():
            investigation_obj = investigation_form.save(commit=False)
            medication_obj = medication_form.save(commit=False)

            registration = Registration.objects.filter(case=id)
            investigation_obj.registration = registration
            medication_obj.registration = registration

            investigation_obj.save()
            medication_obj.save()
            return redirect('cases')
        else:
            print('not valid')
    case = Case.objects.get(id=case_id)
    registration = Registration.objects.filter(case=case_id).first()
    context = {
        "investigation_form": investigation_form,
        "medication_form": medication_form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
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
    investigations = Investigations.objects.filter(
        registration__case=case_id).first()
    medications = RescueMedicine.objects.filter(
        registration__case=case_id).first()

    investigations_form = InvestigationForm(instance=investigations)
    medications_form = MedicationForm(instance=medications)

    if request.method == "POST":
        if ('delete') in request.POST:
            investigations_form.delete()
            medications_form.delete()
            return redirect('cases')
        if investigations_form.is_valid and medications_form.is_valid():
            investigation_obj = investigations_form.save(commit=False)
            medication_obj = medications_form.save(commit=False)
            Registration.objects.filter(case=case_id).update(
                investigation_management_complete=True)
            investigation_obj.save()
            medication_obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')

    case = Case.objects.get(id=case_id)
    registration = Registration.objects.filter(case=case_id).first()
    context = {
        "investigation_form": investigations_form,
        "medication_form": medications_form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
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
