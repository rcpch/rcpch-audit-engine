from django.utils import timezone
from datetime import datetime
from operator import itemgetter
from django.contrib.auth.decorators import login_required
from ..decorator import group_required

from epilepsy12.models.syndrome import Syndrome
from epilepsy12.constants.syndromes import SYNDROMES

from .common_view_functions import recalculate_form_generate_response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_diagnosis_date(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on date change
    """

    print("hello")

    syndrome_diagnosis_date = request.POST.get(
        request.htmx.trigger_name)

    Syndrome.objects.filter(pk=syndrome_id).update(
        syndrome_diagnosis_date=datetime.strptime(
            syndrome_diagnosis_date, "%Y-%m-%d").date(),
        updated_at=timezone.now(),
        updated_by=request.user
    )

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    context = {
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        'syndrome': syndrome
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_name(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on syndrome name change
    """
    syndrome_name = request.POST.get(
        request.htmx.trigger_name)
    Syndrome.objects.filter(pk=syndrome_id).update(
        syndrome_name=syndrome_name,
        updated_at=timezone.now(),
        updated_by=request.user
    )

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    context = {
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        'syndrome': syndrome
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context
    )

    return response
