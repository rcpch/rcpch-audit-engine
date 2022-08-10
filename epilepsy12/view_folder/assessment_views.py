from datetime import datetime
from email.policy import default
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import Registration
from ..models import Assessment


@login_required
def consultant_paediatrician_referral_made(request, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    consultant_paediatrician_referral_made = not assessment.consultant_paediatrician_referral_made

    if consultant_paediatrician_referral_made:
        assessment.consultant_paediatrician_referral_made = consultant_paediatrician_referral_made
        assessment.save()
    else:
        assessment.consultant_paediatrician_referral_made = consultant_paediatrician_referral_made
        assessment.consultant_paediatrician_referral_date = None
        assessment.consultant_paediatrician_input_date = None
        assessment.save()

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def consultant_paediatrician_referral_date(request, assessment_id):
    new_date = request.POST.get(
        'consultant_paediatrician_referral_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.consultant_paediatrician_referral_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
        return HttpResponse(message)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def consultant_paediatrician_input_date(request, assessment_id):
    new_date = request.POST.get(
        'consultant_paediatrician_input_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.consultant_paediatrician_input_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
        return HttpResponse(message)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def paediatric_neurologist_referral_made(request, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    paediatric_neurologist_referral_made = not assessment.paediatric_neurologist_referral_made
    if paediatric_neurologist_referral_made:
        assessment.paediatric_neurologist_referral_made = paediatric_neurologist_referral_made
        assessment.save()
    else:
        assessment.paediatric_neurologist_referral_made = paediatric_neurologist_referral_made
        assessment.paediatric_neurologist_referral_date = None
        assessment.paediatric_neurologist_input_date = None
        assessment.save()

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@login_required
def paediatric_neurologist_referral_date(request, assessment_id):
    new_date = request.POST.get(
        'paediatric_neurologist_referral_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.paediatric_neurologist_referral_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@login_required
def paediatric_neurologist_input_date(request, assessment_id):
    new_date = request.POST.get(
        'paediatric_neurologist_input_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.paediatric_neurologist_input_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
        return HttpResponse(message)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@login_required
def childrens_epilepsy_surgical_service_referral_criteria_met(request, assessment_id):

    assessment = Assessment.objects.get(pk=assessment_id)
    childrens_epilepsy_surgical_service_referral_criteria_met = not assessment.childrens_epilepsy_surgical_service_referral_criteria_met

    if childrens_epilepsy_surgical_service_referral_criteria_met:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_referral_criteria_met = childrens_epilepsy_surgical_service_referral_criteria_met
        assessment.save()
    else:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_referral_criteria_met = childrens_epilepsy_surgical_service_referral_criteria_met
        assessment.childrens_epilepsy_surgical_service_referral_date = None
        assessment.childrens_epilepsy_surgical_service_input_date = None
        assessment.save()

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@login_required
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    new_date = request.POST.get(
        'childrens_epilepsy_surgical_service_referral_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_referral_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        return HttpResponse(error)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@login_required
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    new_date = request.POST.get(
        'childrens_epilepsy_surgical_service_input_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.childrens_epilepsy_surgical_service_input_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error
        return HttpResponse(message)

    context = {
        'assessment': assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@login_required
def epilepsy_specialist_nurse_referral_made(request, assessment_id):
    assessment = Assessment.objects.get(pk=assessment_id)
    epilepsy_specialist_nurse_referral_made = not assessment.epilepsy_specialist_nurse_referral_made

    try:
        Assessment.objects.filter(pk=assessment_id).update(
            epilepsy_specialist_nurse_referral_made=epilepsy_specialist_nurse_referral_made)
    except Exception as error:
        return HttpResponse(error)

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@login_required
def epilepsy_specialist_nurse_referral_date(request, assessment_id):
    new_date = request.POST.get(
        'epilepsy_specialist_nurse_referral_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.epilepsy_specialist_nurse_referral_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        return HttpResponse(error)

    context = {
        "assessment": assessment,
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@login_required
def epilepsy_specialist_nurse_input_date(request, assessment_id):
    new_date = request.POST.get(
        'epilepsy_specialist_nurse_input_date')

    try:
        assessment = Assessment.objects.get(pk=assessment_id)
        assessment.epilepsy_specialist_nurse_input_date = datetime.strptime(
            new_date, "%Y-%m-%d").date()
        assessment.save()
    except Exception as error:
        message = error

    context = {
        "assessment": assessment,
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@login_required
def were_any_of_the_epileptic_seizures_convulsive(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('were_any_of_the_epileptic_seizures_convulsive') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'were_any_of_the_epileptic_seizures_convulsive': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'were_any_of_the_epileptic_seizures_convulsive': False,
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
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@login_required
def prolonged_generalized_convulsive_seizures(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('prolonged_generalized_convulsive_seizures') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'prolonged_generalized_convulsive_seizures': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'prolonged_generalized_convulsive_seizures': False,
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
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@login_required
def experienced_prolonged_focal_seizures(request, registration_id):

    registration = Registration.objects.get(pk=registration_id)

    if request.POST.get('experienced_prolonged_focal_seizures') == 'on':
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'experienced_prolonged_focal_seizures': True,
            'registration': registration
        })
    else:
        assessment, created = Assessment.objects.update_or_create(registration=registration, defaults={
            'experienced_prolonged_focal_seizures': False,
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
    return render(request=request, template_name="epilepsy12/partials/assessment/seizure_length_checkboxes.html", context=context)


@login_required
def assessment(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    context = {
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
