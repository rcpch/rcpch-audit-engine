from django.contrib.auth.decorators import login_required
from ..decorator import group_required, update_model
from epilepsy12.constants.common import OPT_OUT_UNCERTAIN
from epilepsy12.models.registration import Registration
from ..models import EpilepsyContext
from .common_view_functions import recalculate_form_generate_response


@login_required
def epilepsy_context(request, case_id):

    registration = Registration.objects.filter(case=case_id).first()

    epilepsy_context, created = EpilepsyContext.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN,
        "audit_progress": epilepsy_context.registration.audit_progress,
        "active_template": "epilepsy_context"
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template='epilepsy12/epilepsy_context.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'previous_febrile_seizure', 'single_choice_multiple_toggle_button')
def previous_febrile_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_febrile_seizure.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'previous_acute_symptomatic_seizure', 'single_choice_multiple_toggle_button')
def previous_acute_symptomatic_seizure(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_acute_symptomatic_seizure.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'is_there_a_family_history_of_epilepsy', 'single_choice_multiple_toggle_button')
def is_there_a_family_history_of_epilepsy(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/is_there_a_family_history_of_epilepsy.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'previous_neonatal_seizures', 'single_choice_multiple_toggle_button')
def previous_neonatal_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/previous_neonatal_seizures.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'were_any_of_the_epileptic_seizures_convulsive', 'toggle_button')
def were_any_of_the_epileptic_seizures_convulsive(request, epilepsy_context_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template='epilepsy12/partials/epilepsy_context/were_any_of_the_epileptic_seizures_convulsive.html',
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'experienced_prolonged_generalized_convulsive_seizures', 'single_choice_multiple_toggle_button')
def experienced_prolonged_generalized_convulsive_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the experienced_prolonged_generalized_convulsive_seizures partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/experienced_prolonged_generalized_convulsive_seizures.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'experienced_prolonged_focal_seizures', 'single_choice_multiple_toggle_button')
def experienced_prolonged_focal_seizures(request, epilepsy_context_id):
    """
    HTMX callback from the experienced_prolonged_focal_seizures partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context,
        "uncertain_choices": OPT_OUT_UNCERTAIN
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/experienced_prolonged_focal_seizures.html",
        context=context
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(EpilepsyContext, 'diagnosis_of_epilepsy_withdrawn', 'toggle_button')
def diagnosis_of_epilepsy_withdrawn(request, epilepsy_context_id):
    """
    HTMX callback from the previous_febrile_seizure partial, 
    parent of single_choice_multiple_toggle
    Updates the model and returns the same partial
    """

    epilepsy_context = EpilepsyContext.objects.get(pk=epilepsy_context_id)

    context = {
        "epilepsy_context": epilepsy_context
    }

    response = recalculate_form_generate_response(
        model_instance=epilepsy_context,
        request=request,
        template="epilepsy12/partials/epilepsy_context/epilepsy_diagnosis_withdrawn.html",
        context=context
    )

    return response
