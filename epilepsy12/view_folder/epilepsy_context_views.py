from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..forms_folder.epilepsy_context_form import EpilepsyContextForm


@login_required
def create_epilepsy_context(request, id):
    form = EpilepsyContextForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            # case = Case.objects.get(id=id)
            # obj.case = case
            obj.save()
            return redirect('cases')
        else:
            print('not valid')
    context = {
        "form": form
    }
    return render(request=request, template_name='epilepsy12/epilepsy_context.html', context=context)


@login_required
def update_epilepsy_context(request, id):
    # registration = Registration.objects.filter(case=id).first()
    form = EpilepsyContextForm(instance=registration)

    if request.method == "POST":
        if ('delete') in request.POST:
            # registration.delete()
            return redirect('cases')
        # form = EpilepsyContextForm(request.POST, instance=registration)
        if form.is_valid:
            obj = form.save()
            obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')

    context = {
        "form": form,
        "case_id": id
    }

    return render(request=request, template_name='epilepsy12/register.html', context=context)


@login_required
def delete_epilepsy_context(request, id):
    # registration = get_object_or_404(Registration, id=id)
    registration.delete()
    return redirect('cases')
