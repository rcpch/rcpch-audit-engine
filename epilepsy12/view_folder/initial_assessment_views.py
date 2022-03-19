from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from ..models import Registration
from ..models import InitialAssessment
from ..forms_folder import InitialAssessmentForm


@login_required
def create_intial_assessment(request, id):
    form = InitialAssessmentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            registration = Registration.objects.filter(case=id)
            obj.registration = registration
            obj.save()
            return redirect('cases')
        else:
            print('not valid')
    context = {
        "form": form
    }
    return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


@login_required
def update_initial_assessment(request, id):
    initial_assessment = InitialAssessment.objects.filter(
        registration__case=id).first()
    form = InitialAssessmentForm(instance=initial_assessment)

    if request.method == "POST":
        if ('delete') in request.POST:
            initial_assessment.delete()
            return redirect('cases')
        form = InitialAssessmentForm(request.POST, instance=initial_assessment)
        if form.is_valid:
            obj = form.save()
            obj.save()
            # messages.success(request, "You successfully updated the post")
            return redirect('cases')

    context = {
        "form": form
    }

    return render(request=request, template_name='epilepsy12/initial_assessment.html', context=context)


@login_required
def delete_initial_assessment(request, id):
    initial_assessment = get_object_or_404(InitialAssessmentForm, id=id)
    initial_assessment.delete()
    return redirect('cases')
