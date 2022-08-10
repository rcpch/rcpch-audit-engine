from datetime import datetime
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.models.management import Management

from epilepsy12.models.registration import Registration


@login_required
def management(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    management, created = Management.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "management": management,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "investigations"
    }
    return render(request=request, template_name='epilepsy12/management.html', context=context)


@login_required
def has_an_aed_been_given(request, management_id):

    management = Management.objects.get(pk=management_id)

    has_an_aed_been_given = not management.has_an_aed_been_given

    management.has_an_aed_been_given = has_an_aed_been_given
    management.save()

    context = {
        'management': management
    }

    return render(request=request, template_name="epilepsy12/partials/management/aeds.html", context=context)


@login_required
def rescue_medication_prescribed(request, management_id):

    management = Management.objects.get(pk=management_id)

    has_rescue_medication_been_prescribed = not management.has_rescue_medication_been_prescribed

    management.has_rescue_medication_been_prescribed = has_rescue_medication_been_prescribed
    management.save()

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }

    return render(request=request, template_name="epilepsy12/partials/management/rescue_medicines.html", context=context)
