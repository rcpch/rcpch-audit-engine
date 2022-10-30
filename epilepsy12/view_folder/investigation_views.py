from django.utils import timezone
from django.contrib.auth.decorators import login_required
from ..decorator import group_required
from epilepsy12.models import Investigations, Registration
from ..decorator import update_model
from .common_view_functions import recalculate_form_generate_response


@login_required
def investigations(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    investigations, created = Investigations.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "audit_progress": registration.audit_progress,
        "active_template": "investigations"
    }

    template_name = 'epilepsy12/investigations.html'

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


# htmx
@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'eeg_indicated', 'toggle_button')
def eeg_indicated(request, investigations_id):
    """
    This is an HTMX callback from the eeg_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """

    investigations = Investigations.objects.get(pk=investigations_id)
    # if eeg not indicated but previously selected, set dependent fields to None
    if investigations.eeg_indicated == False:
        investigations.eeg_request_date = None
        investigations.eeg_performed_date = None
        investigations.updated_at = timezone.now()
        investigations.updated_by = request.user
        investigations.save()

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'eeg_request_date', 'date_field')
def eeg_request_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'eeg_performed_date', 'date_field')
def eeg_performed_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'twelve_lead_ecg_status', 'toggle_button')
def twelve_lead_ecg_status(request, investigations_id):
    """
    This is an HTMX callback from the ecg_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/ecg_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'ct_head_scan_status', 'toggle_button')
def ct_head_scan_status(request, investigations_id):
    """
    This is an HTMX callback from the ct_head_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/ct_head_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'mri_indicated', 'toggle_button')
def mri_indicated(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """

    investigations = Investigations.objects.get(pk=investigations_id)

    # if mri nolonger indicated (status changed), set previous dates to none
    if investigations.mri_indicated == False:
        investigations.mri_brain_requested_date = None
        investigations.mri_brain_reported_date = None
        investigations.updated_at = timezone.now()
        investigations.updated_by = request.user
        investigations.save()

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'mri_brain_requested_date', 'date_field')
def mri_brain_requested_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
@update_model(Investigations, 'mri_brain_reported_date', 'date_field')
def mri_brain_reported_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name
    )

    return response
