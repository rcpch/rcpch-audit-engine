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
            obj = form.save(commit=False)
            case = Case.objects.get(id=id)
            obj.case = case
            obj.save()
            return redirect('cases')
        else:
            print('not valid')
    context = {
        "form": form
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

    context = {
        "form": form
    }

    return render(request=request, template_name='epilepsy12/register.html', context=context)


@login_required
def delete_registration(request, id):
    registration = get_object_or_404(Registration, id=id)
    registration.delete()
    return redirect('cases')
