from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.forms import ComorbidityForm
from epilepsy12.models.registration import Registration
from ..models import Comorbidity
from ..models import Case
from django.contrib import messages


@login_required
def comorbidity_list(request, case_id):
    comorbidity_list = Comorbidity.objects.filter(
        case=case_id).order_by('comorbidity')
    comorbidity_count = Comorbidity.objects.filter(case=case_id).count()
    context = {
        'comorbidity_list': comorbidity_list,
        'total_comorbidities': comorbidity_count,
    }
    template_name = 'epilepsy12/epilepsy_context.html'
    return render(request, template_name, context)


@login_required
def create_comorbidity(request, case_id):
    form = ComorbidityForm(request.POST or None)
    registration = Registration.objects.filter(case=case_id).first()
    case = Case.objects.get(id=case_id)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.case = case
            obj.created_at = datetime.now()
            obj.save()
            messages.success(
                request, "You successfully created the comorbidity")
            return redirect('update_epilepsy_context', case_id=case_id)

    context = {
        "form": form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "epilepsy_context",
    }
    return render(request=request, template_name='epilepsy12/comorbidity.html', context=context)


@login_required
def update_comorbidity(request, id):
    comorbidity = get_object_or_404(Comorbidity, id=id)
    form = ComorbidityForm(instance=comorbidity)

    if request.method == "POST":
        if ('delete') in request.POST:
            comorbidity.delete()
            return redirect('comorbidity')
        form = ComorbidityForm(request.POST, instance=comorbidity)
        if form.is_valid:
            obj = form.save()
            obj.save()
            messages.success(
                request, "You successfully updated the comorbidity")
            return redirect('epilepsy_context')

    context = {
        "form": form
    }

    return render(request=request, template_name='epilepsy12/comorbidity.html', context=context)


@login_required
def delete_case(request, id):
    comorbidity = get_object_or_404(Comorbidity, id=id)
    comorbidity.delete()
    return redirect('cases')
