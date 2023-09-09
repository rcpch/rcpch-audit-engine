from datetime import date
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from epilepsy12.models import Investigations, Registration, Site
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child


@login_required
@permission_required("epilepsy12.view_investigations", raise_exception=True)
@user_may_view_this_child()
def investigations(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    investigations, created = Investigations.objects.get_or_create(
        registration=registration
    )

    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "audit_progress": registration.audit_progress,
        "active_template": "investigations",
        "organisation_id": organisation_id,
        "eeg_declined": eeg_declined,
        "mri_brain_declined": mri_brain_declined,
    }

    template_name = "epilepsy12/investigations.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
    )

    return response


# htmx
@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_indicated(request, investigations_id):
    """
    This is an HTMX callback from the eeg_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="eeg_indicated",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)
    # if eeg not indicated but previously selected, set dependent fields to None
    if investigations.eeg_indicated == False:
        investigations.eeg_request_date = None
        investigations.eeg_performed_date = None
        investigations.updated_at = timezone.now()
        investigations.updated_by = request.user
        investigations.save()

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    context = {"investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_request_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """
    try:
        investigations = Investigations.objects.get(pk=investigations_id)
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="eeg_request_date",
            page_element="date_field",
            comparison_date_field_name="eeg_performed_date",
            is_earliest_date=True,
            earliest_allowable_date=investigations.registration.first_paediatric_assessment_date,
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    context = {"investigations": investigations, "eeg_declined": eeg_declined}

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_performed_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """

    try:
        investigations = Investigations.objects.get(pk=investigations_id)
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="eeg_performed_date",
            page_element="date_field",
            comparison_date_field_name="eeg_request_date",
            is_earliest_date=False,
            earliest_allowable_date=investigations.registration.first_paediatric_assessment_date,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    context = {"investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_declined(request, investigations_id, confirm):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on click in the eeg_declined button.
    EEGs might be declined if the child is not cooperative or practical/technical issues relating to the EEG test.
    Failure to provide a completion date of the EEG however results in a fail for this measure.
    To denote failure, the completion date is persisted as 15/4/1915, the date of birth of Jean Henri Gestaut
    The confirm flag can either be set to 'decline' or 'edit' reflecting the toggle state in the template
    This updates the model and returns the same partial.
    """

    error_message = None

    investigations = Investigations.objects.get(pk=investigations_id)
    if confirm == "decline":
        investigations.eeg_performed_date = date(year=1915, month=4, day=15)
        eeg_declined = True
    elif confirm == "edit":
        investigations.eeg_performed_date = None
        eeg_declined = False
    else:
        raise ValueError("No confirm parameter passed to eeg_decline path.")

    investigations.save()

    context = {"investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def twelve_lead_ecg_status(request, investigations_id):
    """
    This is an HTMX callback from the ecg_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="twelve_lead_ecg_status",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    context = {"investigations": investigations}

    template_name = "epilepsy12/partials/investigations/ecg_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def ct_head_scan_status(request, investigations_id):
    """
    This is an HTMX callback from the ct_head_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="ct_head_scan_status",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    context = {"investigations": investigations}

    template_name = "epilepsy12/partials/investigations/ct_head_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_indicated(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="mri_indicated",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    # if mri nolonger indicated (status changed), set previous dates to none
    if investigations.mri_indicated == False:
        investigations.mri_brain_requested_date = None
        investigations.mri_brain_reported_date = None
        investigations.updated_at = timezone.now()
        investigations.updated_by = request.user
        investigations.save()

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "investigations": investigations,
        "mri_brain_declined": mri_brain_declined,
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_requested_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """

    try:
        investigations = Investigations.objects.get(pk=investigations_id)
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="mri_brain_requested_date",
            page_element="date_field",
            comparison_date_field_name="mri_brain_reported_date",
            is_earliest_date=True,
            earliest_allowable_date=investigations.registration.first_paediatric_assessment_date,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "investigations": investigations,
        "mri_brain_declined": mri_brain_declined,
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_reported_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """

    try:
        investigations = Investigations.objects.get(pk=investigations_id)
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="mri_brain_reported_date",
            page_element="date_field",
            comparison_date_field_name="mri_brain_requested_date",
            is_earliest_date=False,
            earliest_allowable_date=investigations.registration.first_paediatric_assessment_date,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "investigations": investigations,
        "mri_brain_declined": mri_brain_declined,
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_declined(request, investigations_id, confirm):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    which contains fields on mri_indicated, mri_request_date and mri_performed_date.
    It also contains a calculated field showing time to MRI from request.
    It is triggered by a toggle in the partial generating a post request on click in the eeg_declined button.
    MRIs might be declined if the child is not cooperative or practical/technical issues relating to the MRI test.
    Failure to provide a completion date of the MRI however results in a fail for this measure.
    To denote failure, the completion date is persisted as 15/4/1915, the date of birth of Jean Henri Gestaut
    The confirm flag can either be set to 'decline' or 'edit' reflecting the toggle state in the template
    This updates the model and returns the same partial.
    """

    error_message = None

    investigations = Investigations.objects.get(pk=investigations_id)

    if confirm == "decline":
        investigations.mri_brain_reported_date = date(year=1915, month=4, day=15)
        mri_brain_declined = True
    elif confirm == "edit":
        investigations.mri_brain_reported_date = None
        mri_brain_declined = False
    else:
        raise ValueError("No confirm parameter passed to eeg_decline path.")

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "investigations": investigations,
        "mri_brain_declined": mri_brain_declined,
    }

    template_name = "epilepsy12/partials/investigations/mri_brain_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response
