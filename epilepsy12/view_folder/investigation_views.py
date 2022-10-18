from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..decorator import group_required
from epilepsy12.models import Investigations, Registration, AuditProgress, Site
from django_htmx.http import trigger_client_event


@login_required
def investigations(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    investigations, created = Investigations.objects.get_or_create(
        registration=registration)

    test_fields_update_audit_progress(investigations)

    context = {
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "audit_progress": registration.audit_progress,
        "active_template": "investigations"
    }

    response = render(
        request=request, template_name='epilepsy12/investigations.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


# htmx
@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def eeg_indicated(request, investigations_id):
    """
    This is an HTMX callback from the eeg_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """

    if Investigations.objects.filter(pk=investigations_id, eeg_indicated=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Investigations.objects.filter(pk=investigations_id).update(
                eeg_indicated=True,
                updated_at=timezone.now())
        elif request.htmx.trigger_name == 'button-false':
            Investigations.objects.filter(pk=investigations_id).update(
                eeg_indicated=False,
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # there is a selection. If this has become false, set all associated fields to None
        Investigations.objects.filter(pk=investigations_id).update(
            eeg_indicated=Q(eeg_indicated=False),
            eeg_request_date=None,
            eeg_performed_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    # return the updated model
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def eeg_request_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    naive_eeg_request_date = datetime.strptime(
        request.POST.get('eeg_request_date'), "%Y-%m-%d").date()

    # aware_eeg_request_date = make_aware(naive_eeg_request_date)

    Investigations.objects.filter(pk=investigations_id).update(
        eeg_request_date=naive_eeg_request_date,
        updated_at=timezone.now(),
        updated_by=request.user)

    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def eeg_performed_date(request, investigations_id):
    """
    This is an HTMX callback from the ecg_information.html partial template
    which contains fields on eeg_indicated, eeg_request_date and eeg_performed_date.
    It also contains a calculated field showing time to EEG from request.
    It is triggered by a toggle in the partial generating a post request on change in the date field.
    This updates the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    naive_eeg_performed_date = datetime.strptime(
        request.POST.get('eeg_performed_date'), "%Y-%m-%d").date()

    Investigations.objects.filter(pk=investigations_id).update(
        eeg_performed_date=naive_eeg_performed_date,
        updated_at=timezone.now(),
        updated_by=request.user)
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def twelve_lead_ecg_status(request, investigations_id):
    """
    This is an HTMX callback from the ecg_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    twelve_lead_ecg_status = not investigations.twelve_lead_ecg_status
    Investigations.objects.filter(pk=investigations_id).update(
        twelve_lead_ecg_status=twelve_lead_ecg_status,
        updated_at=timezone.now(),
        updated_by=request.user)
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/ecg_status.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def ct_head_scan_status(request, investigations_id):
    """
    This is an HTMX callback from the ct_head_status.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    ct_head_scan_status = not investigations.ct_head_scan_status
    Investigations.objects.filter(pk=investigations_id).update(
        ct_head_scan_status=ct_head_scan_status,
        updated_at=timezone.now(),
        updated_by=request.user
    )
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/ct_head_status.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mri_indicated(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, or makes a selection if none is made, 
    and returns the same partial.
    """
    if Investigations.objects.filter(pk=investigations_id, mri_indicated=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Investigations.objects.filter(pk=investigations_id).update(
                mri_indicated=True)
        elif request.htmx.trigger_name == 'button-false':
            Investigations.objects.filter(pk=investigations_id).update(
                mri_indicated=False,
                updated_at=timezone.now(),
                updated_by=request.user
            )
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # there is a selection. If this has become false, set all associated fields to None
        Investigations.objects.filter(pk=investigations_id).update(
            mri_indicated=Q(mri_indicated=False),
            mri_brain_requested_date=None,
            mri_brain_reported_date=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    # return the updated model
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/mri_brain_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mri_brain_requested_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    mri_brain_requested_date = request.POST.get(request.htmx.trigger_name)

    Investigations.objects.filter(pk=investigations_id).update(
        mri_brain_requested_date=datetime.strptime(
            mri_brain_requested_date, "%Y-%m-%d").date(),
        updated_at=timezone.now(),
        updated_by=request.user)
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/mri_brain_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def mri_brain_reported_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    mri_brain_reported_date = request.POST.get(request.htmx.trigger_name)

    Investigations.objects.filter(pk=investigations_id).update(
        mri_brain_reported_date=datetime.strptime(
            mri_brain_reported_date, "%Y-%m-%d").date(),
        updated_at=timezone.now(),
        updated_by=request.user)
    investigations = Investigations.objects.get(pk=investigations_id)

    test_fields_update_audit_progress(investigations)

    context = {
        'investigations': investigations
    }

    response = render(
        request=request, template_name="epilepsy12/partials/investigations/mri_brain_information.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


def total_fields_expected(model_instance):
    # all fields would be:
    #  eeg_indicated
    # eeg_request_date
    # eeg_performed_date
    # twelve_lead_ecg_status
    # ct_head_scan_status
    # mri_indicated
    # mri_brain_requested_date
    # mri_brain_reported_date

    cumulative_fields = 0
    if model_instance.eeg_indicated:
        cumulative_fields += 3
    else:
        cumulative_fields += 1

    if model_instance.twelve_lead_ecg_status:
        cumulative_fields += 1
    else:
        cumulative_fields += 1

    if model_instance.ct_head_scan_status:
        cumulative_fields += 1
    else:
        cumulative_fields += 1

    if model_instance.mri_indicated:
        cumulative_fields += 3
    else:
        cumulative_fields += 1

    return cumulative_fields


def total_fields_completed(model_instance):
    # counts the number of completed fields
    fields = model_instance._meta.get_fields()
    counter = 0
    for field in fields:
        if (
                getattr(model_instance, field.name) is not None
                and field.name not in ['id', 'registration', 'created_by', 'created_at', 'updated_by', 'updated_at']):
            counter += 1
    return counter

# test all fields


def test_fields_update_audit_progress(model_instance):
    all_completed_fields = total_fields_completed(model_instance)
    all_fields = total_fields_expected(model_instance)
    AuditProgress.objects.filter(registration=model_instance.registration).update(
        investigations_total_expected_fields=all_fields,
        investigations_total_completed_fields=all_completed_fields,
        investigations_complete=all_completed_fields == all_fields
    )


"""
<div class="three fields">

                <div class="field">
                    {% if investigations.eeg_request_date is None %}
                        <span data-tooltip="Uncompleted field. This must be scored to complete the record." data-inverted="" data-position="{{data_position}}">
                            <i class="blue dot circle outline icon"></i>
                            <label class='toggle_button_label'>Date EEG requested</label>
                        </span>
                    {% else %}
                        <span>
                            <i class="green check circle outline icon"></i>
                            <label class='toggle_button_label'>Date EEG requested</label>
                        </span>
                    {% endif %}
                    <input 
                        class="ui input" 
                        type="date"
                        hx-target="#eeg_information"
                        name="eeg_request_date"
                        hx-trigger='change' 
                        hx-post="{% url 'eeg_request_date' investigations_id=investigations.pk %}"
                        hx-swap="innerHTML"
                        value="{{investigations.eeg_request_date|date:'Y-m-d'}}"/>
                </div>
                
                <div class="field">
                    {% if investigations.eeg_performed_date is None %}
                        <span data-tooltip="Uncompleted field. This must be scored to complete the record." data-inverted="" data-position="{{data_position}}">
                            <i class="blue dot circle outline icon"></i>
                            <label class='toggle_button_label'>Date EEG performed</label>
                        </span>
                    {% else %}
                        <span>
                            <i class="green check circle outline icon"></i>
                            <label class='toggle_button_label'>Date EEG performed</label>
                        <span>
                    {% endif %}
                    <input 
                        class="ui input" 
                        type="date"
                        name="eeg_performed_date"
                        hx-target="#eeg_information"
                        hx-trigger='change' 
                        hx-post="{% url 'eeg_performed_date' investigations_id=investigations.pk %}"
                        hx-swap="innerHTML"
                        value="{{investigations.eeg_performed_date|date:'Y-m-d'}}"/>
                </div>
                
                <div class="field">
                    <label class='toggle_button_label'>Time to EEG</label>
                    <input class="ui input" type="text" value="{{investigations.eeg_wait}}" disabled/>
                </div>
            
            </div>
"""
