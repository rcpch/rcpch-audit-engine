import json
from datetime import date
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from epilepsy12.models import Investigations, Registration, Site
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child, login_and_otp_required
from ..constants.common import GENOME_TEST_CHOICES


def genome_sequencing_context(can_edit, investigations):
    genome_tests = []

    for test in ["r14", "r27", "r59"]:
        field_name = f"{test}_test_status"

        test_status = getattr(investigations, field_name)

        label_text = Investigations._meta.get_field(field_name).help_text["label"]

        test_requested_date_field_name = f"{test}_test_requested_date"
        test_requested_date = getattr(investigations, test_requested_date_field_name)

        test_achieved_date_field_name = f"{test}_test_achieved_date"
        test_achieved_date = getattr(investigations, test_achieved_date_field_name)

        genome_tests.append(
            {
                "test_name": test,
                "test_status": test_status,
                "label_text": label_text,
                "test_requested_date": test_requested_date,
                "test_requested_date_enabled": test_status in ["R", "A"],
                "test_requested_date_field_name": test_requested_date_field_name,
                "test_achieved_date": test_achieved_date,
                "test_achieved_date_enabled": test_status == "A",
                "test_achieved_date_field_name": test_achieved_date_field_name,
            }
        )

    return {
        "genome_tests": genome_tests,
        "genome_test_choices": GENOME_TEST_CHOICES,
    }


@login_and_otp_required()
@permission_required("epilepsy12.view_investigations", raise_exception=True)
@user_may_view_this_child()
def investigations(request, can_edit, case_id):
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
        "can_edit": can_edit and request.user.has_perm("epilepsy12.change_investigations"),
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "audit_progress": registration.audit_progress,
        "active_template": "investigations",
        "organisation_id": organisation_id,
        "eeg_declined": eeg_declined,
        "mri_brain_declined": mri_brain_declined,
    }

    context = context | genome_sequencing_context(can_edit, investigations)

    template_name = "epilepsy12/investigations.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
    )

    return response


# htmx
@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_indicated(request, can_edit, investigations_id):
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

    context = {"can_edit": can_edit, "investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_request_date(request, can_edit, investigations_id):
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
            earliest_allowable_date=investigations.registration.case.date_of_birth,
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    context = {"can_edit": can_edit, "investigations": investigations, "eeg_declined": eeg_declined}

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_performed_date(request, can_edit, investigations_id):
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
            earliest_allowable_date=investigations.registration.investigations.eeg_request_date,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.eeg_performed_date == date(year=1915, month=4, day=15):
        eeg_declined = True
    else:
        eeg_declined = False

    context = {"can_edit": can_edit, "investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def eeg_declined(request, can_edit, investigations_id, confirm):
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

    context = {"can_edit": can_edit, "investigations": investigations, "eeg_declined": eeg_declined}

    template_name = "epilepsy12/partials/investigations/eeg_information.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def twelve_lead_ecg_status(request, can_edit, investigations_id):
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

    context = {"can_edit": can_edit, "investigations": investigations}

    template_name = "epilepsy12/partials/investigations/ecg_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def ct_head_scan_status(request, can_edit, investigations_id):
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

    context = {"can_edit": can_edit, "investigations": investigations}

    template_name = "epilepsy12/partials/investigations/ct_head_status.html"

    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_indicated(request, can_edit, investigations_id):
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
        "can_edit": can_edit,
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


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_requested_date(request, can_edit, investigations_id):
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
            earliest_allowable_date=investigations.registration.case.date_of_birth,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "can_edit": can_edit,
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


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_reported_date(request, can_edit, investigations_id):
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
            earliest_allowable_date=investigations.mri_brain_requested_date,
        )

    except ValueError as errors:
        error_message = errors

    investigations = Investigations.objects.get(pk=investigations_id)

    if investigations.mri_brain_reported_date == date(year=1915, month=4, day=15):
        mri_brain_declined = True
    else:
        mri_brain_declined = False

    context = {
        "can_edit": can_edit,
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


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def mri_brain_declined(request, can_edit, investigations_id, confirm):
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
        "can_edit": can_edit,
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


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def genome_sequencing_requested(request, can_edit, investigations_id):
    try:
        error_message = None
        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name="genome_sequencing_requested",
            page_element="toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)
    # TODO MRB: if no, clear out old data on genetic testing fields if previously selected

    genome_context = genome_sequencing_context(can_edit, investigations)

    context = {
        "can_edit": can_edit,
        "investigations": investigations,
    } | genome_context

    template_name = "epilepsy12/partials/investigations/genetic_tests_information.html"

    # TODO MRB: update this to take genetic testing questions into account
    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def genetic_testing_status_callback(request, can_edit, investigations_id, test_name):
    try:
        error_message = None

        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            field_name=f"{test_name}_test_status",
            page_element="single_choice_multiple_toggle_button",
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)
    # TODO MRB: if no, clear out date

    genome_context = genome_sequencing_context(can_edit, investigations)

    context = {
        "can_edit": can_edit,
        "investigations": investigations,
    } | genome_context

    template_name = "epilepsy12/partials/investigations/genetic_tests_information.html"

    # TODO MRB: update this to take genetic testing questions into account
    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_investigations", raise_exception=True)
def genetic_testing_date_callback(request, can_edit, investigations_id, test_name, requested_or_achieved):
    try:
        error_message = None
        investigations = Investigations.objects.get(pk=investigations_id)
        
        if requested_or_achieved == "achieved":
            comparison_date_field_name=f"{test_name}_test_requested_date"
        else:
            comparison_date_field_name=None

        validation_args = {
            "field_name": f"{test_name}_test_{requested_or_achieved}_date",
            "page_element": "date_field",
            "comparison_date_field_name": comparison_date_field_name,
            "is_earliest_date": True,
            "earliest_allowable_date": investigations.registration.case.date_of_birth,
        }

        validate_and_update_model(
            request,
            investigations_id,
            Investigations,
            **validation_args
        )

    except ValueError as error:
        error_message = error

    investigations = Investigations.objects.get(pk=investigations_id)

    genome_context = genome_sequencing_context(can_edit, investigations)

    context = {
        "can_edit": can_edit,
        "investigations": investigations,
    } | genome_context

    template_name = "epilepsy12/partials/investigations/genetic_tests_information.html"

    # TODO MRB: update this to take genetic testing questions into account
    response = recalculate_form_generate_response(
        model_instance=investigations,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response