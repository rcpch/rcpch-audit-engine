
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants import comorbidities
from epilepsy12.models import epilepsy_context
from epilepsy12.models.comorbidity import Comorbidity

from epilepsy12.models.registration import Registration

from ..forms_folder.epilepsy_context_form import EpilepsyContextForm
from ..models import Case
from ..models import EpilepsyContext


@login_required
def create_epilepsy_context(request, case_id):
    form = EpilepsyContextForm(request.POST or None)
    registration = Registration.objects.filter(case=case_id).first()
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.registration = registration
            Registration.objects.filter(case=case_id).update(
                epilepsy_context_complete=True)
            obj.save()
            return redirect('cases')
        else:
            print('not valid')
    # case = Case.objects.get(id=case_id)
    # registration = Registration.objects.filter(case=case_id).first()
    context = {
        "form": form,
        "case_id": case_id,
        "case_name": registration.case.first_name + " " + registration.case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context"
    }
    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)


@login_required
def update_epilepsy_context(request, case_id):
    epilepsy_context = EpilepsyContext.objects.filter(
        registration__case=case_id).first()
    registration = Registration.objects.filter(case=case_id).first()
    comorbidities = Comorbidity.objects.filter(
        epilepsy_context=epilepsy_context.id)
    form = EpilepsyContextForm(instance=epilepsy_context)

    if request.method == "POST":
        if ('delete') in request.POST:
            epilepsy_context.delete()
            return redirect('cases')
        form = EpilepsyContextForm(request.POST, instance=epilepsy_context)
        if form.is_valid:
            obj = form.save()
            obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')

    case = Case.objects.get(id=case_id)

    context = {
        "form": form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context",
        "comorbidities": comorbidities
    }

    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)


@login_required
def delete_epilepsy_context(request, case_id):
    registration = get_object_or_404(Registration, id=id)
    registration.delete()
    return redirect('cases')
