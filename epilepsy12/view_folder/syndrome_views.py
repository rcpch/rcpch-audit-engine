from django.utils import timezone
from datetime import datetime
from operator import itemgetter
from django.contrib.auth.decorators import login_required
from ..decorator import group_required

from ..models import Syndrome
from epilepsy12.constants.syndromes import SYNDROMES
from ..common_view_functions import validate_and_update_model, recalculate_form_generate_response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_diagnosis_date(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on date change
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Syndrome,
            model_id=syndrome_id,
            field_name='syndrome_diagnosis_date',
            page_element='date_field',
        )
    except ValueError as error:
        error_message = error

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    context = {
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        'syndrome': syndrome
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context,
        error_message=error_message
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_name(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on syndrome name change
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Syndrome,
            model_id=syndrome_id,
            field_name='syndrome_name',
            page_element='select',
        )
    except ValueError as error:
        error_message = error

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    context = {
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        'syndrome': syndrome
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template='epilepsy12/partials/multiaxial_diagnosis/syndrome.html',
        context=context,
        error_message=error_message
    )

    return response
