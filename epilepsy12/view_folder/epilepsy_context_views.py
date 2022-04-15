
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from epilepsy12.models.comorbidity import Comorbidity

from epilepsy12.models.registration import Registration

from ..forms_folder.epilepsy_context_form import EpilepsyContextForm
from ..models import Case
from ..models import EpilepsyContext


@login_required
def create_epilepsy_context(request, case_id):
    form = EpilepsyContextForm(request.POST or None)
    registration = Registration.objects.filter(case=case_id).first()
    comorbidities = Comorbidity.objects.filter(
        case=case_id).all()
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.registration = registration
            Registration.objects.filter(case=case_id).update(
                epilepsy_context_complete=True)
            obj.save()
            messages.success(
                request, "You successfully added some epilepsy risk factors!")
            return redirect('update_epilepsy_context', case_id)
        else:
            print('not valid')

    context = {
        "form": form,
        "case_id": case_id,
        "case_name": registration.case.first_name + " " + registration.case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }
    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)


@login_required
def update_epilepsy_context(request, case_id):
    epilepsy_context = EpilepsyContext.objects.filter(
        registration__case=case_id).first()
    registration = Registration.objects.filter(case=case_id).first()
    comorbidities = Comorbidity.objects.filter(
        case=case_id).all()
    form = EpilepsyContextForm(instance=epilepsy_context)

    if request.method == "POST":
        if ('delete') in request.POST:
            epilepsy_context.delete()
            Registration.objects.filter(case=case_id).update(
                epilepsy_context_complete=False)
            messages.success(
                request, "You successfully deleted the epilepsy risk factors!")
            return redirect('cases')
        form = EpilepsyContextForm(request.POST, instance=epilepsy_context)
        if form.is_valid:
            obj = form.save()
            obj.save()
            messages.success(
                request, "You successfully updated the epilepsy risk factors!")
            # return redirect('cases')

    case = Case.objects.get(id=case_id)

    context = {
        "form": form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "epilepsy_decimal_years": epilepsy_context.epilepsy_decimal_years,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }

    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)
