from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
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
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        consultant_paediatrician_referral_date=datetime.strptime(
            request.POST.get('consultant_paediatrician_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@login_required
def consultant_paediatrician_input_date(request, assessment_id):
    """
    This is an HTMX callback from the consultant_paediatrician partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the consultant paediatrician input date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        consultant_paediatrician_input_date=datetime.strptime(
            request.POST.get('consultant_paediatrician_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/consultant_paediatrician.html", context=context)


@ login_required
def paediatric_neurologist_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, paediatric_neurologist_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                paediatric_neurologist_referral_made=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                paediatric_neurologist_referral_made=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            paediatric_neurologist_referral_made=Q(
                paediatric_neurologist_referral_made=False),
            paediatric_neurologist_referral_date=None,
            paediatric_neurologist_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@ login_required
def paediatric_neurologist_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        paediatric_neurologist_referral_date=datetime.strptime(
            request.POST.get('paediatric_neurologist_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@ login_required
def paediatric_neurologist_input_date(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the paediatric neurologist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        paediatric_neurologist_input_date=datetime.strptime(
            request.POST.get('paediatric_neurologist_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/paediatric_neurologist.html", context=context)


@ login_required
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


@ login_required
def childrens_epilepsy_surgical_service_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the paediatric_neurologist partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, childrens_epilepsy_surgical_service_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_made=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                childrens_epilepsy_surgical_service_referral_made=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            childrens_epilepsy_surgical_service_referral_made=Q(
                childrens_epilepsy_surgical_service_referral_made=False),
            childrens_epilepsy_surgical_service_referral_date=None,
            childrens_epilepsy_surgical_service_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def childrens_epilepsy_surgical_service_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        childrens_epilepsy_surgical_service_referral_date=datetime.strptime(
            request.POST.get('childrens_epilepsy_surgical_service_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def childrens_epilepsy_surgical_service_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_surgery partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the children's epilepsy surgery referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        childrens_epilepsy_surgical_service_input_date=datetime.strptime(
            request.POST.get('childrens_epilepsy_surgical_service_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_surgery.html", context=context)


@ login_required
def epilepsy_specialist_nurse_referral_made(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    if Assessment.objects.filter(pk=assessment_id, epilepsy_specialist_nurse_referral_made=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Assessment.objects.filter(pk=assessment_id).update(
                individualised_care_plan_in_place=True)
        elif request.htmx.trigger_name == 'button-false':
            Assessment.objects.filter(pk=assessment_id).update(
                individualised_care_plan_in_place=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Assessment.objects.filter(pk=assessment_id).update(
            epilepsy_specialist_nurse_referral_made=Q(
                epilepsy_specialist_nurse_referral_made=False),
            epilepsy_specialist_nurse_referral_date=None,
            epilepsy_specialist_nurse_input_date=None
        )

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        "assessment": assessment
    }

    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@login_required
def epilepsy_specialist_nurse_referral_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        epilepsy_specialist_nurse_referral_date=datetime.strptime(
            request.POST.get('epilepsy_specialist_nurse_referral_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
    }
    return render(request=request, template_name="epilepsy12/partials/assessment/epilepsy_nurse.html", context=context)


@login_required
def epilepsy_specialist_nurse_input_date(request, assessment_id):
    """
    This is an HTMX callback from the epilepsy_nurse partial template
    It is triggered by a change in custom date input in the partial, generating a post request.
    This persists the epilepsy nurse specialist referral date value, and returns the same partial.
    """

    # TODO date validation needed
    Assessment.objects.filter(pk=assessment_id).update(
        epilepsy_specialist_nurse_input_date=datetime.strptime(
            request.POST.get('epilepsy_specialist_nurse_input_date'), "%Y-%m-%d").date())

    assessment = Assessment.objects.get(pk=assessment_id)

    context = {
        'assessment': assessment
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
