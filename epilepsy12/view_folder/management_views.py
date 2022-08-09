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
