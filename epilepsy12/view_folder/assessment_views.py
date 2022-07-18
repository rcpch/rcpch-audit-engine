from datetime import datetime
from email.policy import default
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Registration
from ..models import Assessment
from ..models import Case
from ..forms_folder import AssessmentForm


@login_required
def childrens_epilepsy_surgical_service_referral_criteria_met(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    print(request.POST.get('childrens_epilepsy_surgical_service_referral_criteria_met'))

    if request.POST.get('childrens_epilepsy_surgical_service_referral_criteria_met') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'childrens_epilepsy_surgical_service_referral_criteria_met': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'childrens_epilepsy_surgical_service_referral_criteria_met': False,
            'childrens_epilepsy_surgical_service_referral_date': None,
            'childrens_epilepsy_surgical_service_referral_date': None,
            'registration': registration
        })

    if created:
        assessment_object = created
    else:
        assessment_object = assessment

    context = {
        'registration_id': registration.pk,
        'assessment': assessment_object
    }
    return render(request=request, template_name="epilepsy12/partials/epilepsy_surgery_dates.html", context=context)


@login_required
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    new_date = request.POST.get(
        'childrens_epilepsy_surgical_service_referral_date')
    message = "Children's epilepsy surgery service referral date updated."

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_referral_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
    return HttpResponse(message)


@login_required
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    new_date = request.POST.get(
        'childrens_epilepsy_surgical_service_input_date')
    message = "Children's epilepsy surgery service input date updated."

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_input_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
    return HttpResponse(message)


@login_required
def create_assessment(request, case_id):
    form = AssessmentForm(request.POST or None)
    registration = Registration.objects.filter(case=case_id).first()
    if request.method == "POST":
        print(form)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.registration = registration
            Registration.objects.filter(case=case_id).update(
                assessment_complete=True)
            obj.save()
            messages.success(
                request, "You successfully added new milestones!")
            return redirect('update_assessment', case_id)
        else:
            print('not valid')

    context = {
        "form": form,
        "case_id": case_id,
        "registration": registration,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "assessment"
    }
    return render(request=request, template_name='epilepsy12/assessment.html', context=context)


@login_required
def update_assessment(request, case_id):
    assessment = Assessment.objects.filter(
        registration__case=case_id).first()
    registration = Registration.objects.filter(case=case_id).first()
    form = AssessmentForm(instance=assessment)

    if request.method == "POST":
        if ('delete') in request.POST:
            assessment.delete()
            Registration.objects.filter(case=case_id).update(
                assessment_complete=False)
            messages.success(
                request, "You successfully deleted the milestones!")
            return redirect('cases')
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid:
            obj = form.save()
            obj.save()
            Registration.objects.filter(case=case_id).update(
                assessment_complete=True)
            messages.success(
                request, "You successfully updated the milestones!")
            return redirect('cases')

    context = {
        "form": form,
        "case_id": case_id,
        "registration": registration,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "assessment"
    }

    return render(request=request, template_name='epilepsy12/assessment.html', context=context)
