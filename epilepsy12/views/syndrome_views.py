from operator import itemgetter
from django.contrib.auth.decorators import permission_required

from ..models import Syndrome, SyndromeList
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child, login_and_otp_required


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.add_syndrome", raise_exception=True)
def syndrome_diagnosis_date(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on date change
    """

    try:
        syndrome = Syndrome.objects.get(pk=syndrome_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Syndrome,
            model_id=syndrome_id,
            field_name="syndrome_diagnosis_date",
            page_element="date_field",
            # earliest_allowable_date=syndrome.multiaxial_diagnosis.registration.first_paediatric_assessment_date,
        )
    except ValueError as error:
        error_message = error

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    # create list of syndromesentities, removing already selected items, excluding current
    multiaxial_diagnosis = syndrome.multiaxial_diagnosis
    all_selected_syndromes = (
        Syndrome.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)
        .exclude(pk=syndrome_id)
        .values_list("syndrome", flat=True)
    )
    syndrome_selection = SyndromeList.objects.exclude(
        pk__in=all_selected_syndromes
    ).order_by("syndrome_name")

    context = {
        "syndrome_selection": syndrome_selection,
        "syndrome": syndrome,
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template="epilepsy12/partials/multiaxial_diagnosis/syndrome.html",
        context=context,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_syndrome", raise_exception=True)
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
            field_name="syndrome",
            page_element="select",
        )
    except ValueError as error:
        error_message = error

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    # create list of syndromesentities, removing already selected items, excluding current
    multiaxial_diagnosis = syndrome.multiaxial_diagnosis
    all_selected_syndromes = (
        Syndrome.objects.filter(multiaxial_diagnosis=multiaxial_diagnosis)
        .exclude(pk=syndrome_id)
        .values_list("syndrome", flat=True)
    )
    syndrome_selection = SyndromeList.objects.exclude(
        pk__in=all_selected_syndromes
    ).order_by("syndrome_name")

    context = {
        "syndrome_selection": syndrome_selection,
        "syndrome": syndrome,
    }

    response = recalculate_form_generate_response(
        model_instance=syndrome.multiaxial_diagnosis,
        request=request,
        template="epilepsy12/partials/multiaxial_diagnosis/syndrome.html",
        context=context,
        error_message=error_message,
    )

    return response
