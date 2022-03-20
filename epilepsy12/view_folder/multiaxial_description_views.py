from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..models import Registration


@login_required
def create_multiaxial_description(request, id):
    # form = MultiaxialDescriptionForm(request.POST or None)
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
    # , context=context)
    return render(request=request, template_name='epilepsy12/multiaxial_description.html')


@login_required
def update_multiaxial_description(request, id):
    # multiaxial_description = .objects.filter(registration__case = id).first()
    # form = MultiaxialDescriptionForm(instance=)

    # if request.method == "POST":
    #     if ('delete') in request.POST:
    #         multiaxial_description.delete()
    #         return redirect('cases')
    #     # form = MultiaxialDescriptionForm(request.POST, instance=)
    #     if form.is_valid:
    #         obj = form.save()
    #         obj.save()
    #         # messages.success(request, "You successfully updated the post")
    #         return redirect('cases')

    # context = {
    #     "form": form
    # }

    # , context=context)
    return render(request=request, template_name='epilepsy12/multiaxial_description.html')


@login_required
def delete_multiaxial_description(request, id):
    # multiaxial_description = get_object_or_404(
    #     MultiaxialDescriptionForm, id=id)
    # multiaxial_description.delete()
    return redirect('cases')
