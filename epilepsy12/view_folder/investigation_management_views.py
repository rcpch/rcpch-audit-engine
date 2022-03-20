from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..models import Registration


@login_required
def create_investigation_management(request, id):
    # form = InvestigationManagmentForm(request.POST or None)
    # if request.method == "POST":
    #     if form.is_valid():
    #         obj = form.save(commit=False)
    #         # registration = Registration.objects.filter(case=id)
    #         # obj.registration = registration
    #         obj.save()
    #         return redirect('cases')
    #     else:
    #         print('not valid')
    # context = {
    #     "form": form
    # }
    # context=context)
    return render(request=request, template_name='epilepsy12/investigation_management.html')


@login_required
def update_investigation_management(request, id):
    # investigation_management = .objects.filter(
    # registration__case = id).first()
    # form = InvestigationManagmentForm(instance=)

    # if request.method == "POST":
    #     if ('delete') in request.POST:
    #         investigation_management.delete()
    #         return redirect('cases')
    #     # form = InvestigationManagmentForm(request.POST, instance=)
    #     if form.is_valid:
    #         obj=form.save()
    #         obj.save()
    #         # messages.success(request, "You successfully updated the post")
    #         return redirect('cases')

    # context={
    #     "form": form
    # }

    # , context=context)
    return render(request=request, template_name='epilepsy12/investigation_management.html')


@login_required
def delete_investigation_management(request, id):
    # investigation_management = get_object_or_404(InvestigationManagmentForm, id=id)
    # investigation_management.delete()
    return redirect('cases')
