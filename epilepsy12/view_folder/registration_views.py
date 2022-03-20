from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..models import Registration
from ..models import Case
from ..forms_folder import RegistrationForm


@login_required
def register(request, id):
    form = RegistrationForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            case = Case.objects.get(id=id)
            obj = form.save(commit=False)
            obj.case = case
            obj.save()
            return redirect('cases')
        else:
            print('not valid')
    context = {
        "form": form,
        "case_id": id,
        "initial_assessment_complete": False,
        "epilepsy_context_complete": False,
        "multiaxial_description_complete": False,
        "investigation_management_complete": False,
        "active_template": "none"
    }
    return render(request=request, template_name='epilepsy12/register.html', context=context)


@login_required
def update_registration(request, id):
    registration = Registration.objects.filter(case=id).first()
    form = RegistrationForm(instance=registration)

    if request.method == "POST":
        if ('delete') in request.POST:
            registration.delete()
            return redirect('cases')
        form = RegistrationForm(request.POST, instance=registration)
        if form.is_valid:
            obj = form.save()
            obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')
    case = Case.objects.get(id=id)
    context = {
        "form": form,
        "case_id": id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "none"
    }

    return render(request=request, template_name='epilepsy12/register.html', context=context)


@login_required
def delete_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    registration.delete()
    return redirect('cases')
