from datetime import datetime
from django.http import HttpResponse
from django.db.models import Q
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.models.investigations import Investigations

from epilepsy12.models.registration import Registration


@login_required
def investigations(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    investigations, created = Investigations.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "registration_complete": registration.audit_progress.registration_complete,
        "initial_assessment_complete": registration.audit_progress.initial_assessment_complete,
        "assessment_complete": registration.audit_progress.assessment_complete,
        "epilepsy_context_complete": registration.audit_progress.epilepsy_context_complete,
        "multiaxial_description_complete": registration.audit_progress.multiaxial_description_complete,
        "investigation_complete": registration.audit_progress.investigation_complete,
        "management_complete": registration.audit_progress.management_complete,
        "active_template": "investigations"
    }
    return render(request=request, template_name='epilepsy12/investigations.html', context=context)


# htmx

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
                eeg_indicated=True)
        elif request.htmx.trigger_name == 'button-false':
            Investigations.objects.filter(pk=investigations_id).update(
                eeg_indicated=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # there is a selection. If this has become false, set all associated fields to None
        Investigations.objects.filter(pk=investigations_id).update(
            eeg_indicated=Q(eeg_indicated=False),
            eeg_request_date=None,
            eeg_performed_date=None
        )

    # return the updated model
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)


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
        eeg_request_date=naive_eeg_request_date)
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)


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
        eeg_performed_date=naive_eeg_performed_date)
    investigations = Investigations.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_information.html", context=context)


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
        twelve_lead_ecg_status=twelve_lead_ecg_status)
    investigations = Investigations.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/ecg_status.html", context=context)


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
        ct_head_scan_status=ct_head_scan_status)
    investigations = Investigations.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/ct_head_status.html", context=context)


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
                mri_indicated=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # there is a selection. If this has become false, set all associated fields to None
        Investigations.objects.filter(pk=investigations_id).update(
            mri_indicated=Q(mri_indicated=False),
            mri_brain_date=None
        )

    # return the updated model
    investigations = Investigations.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/mri_brain_information.html", context=context)


def mri_brain_date(request, investigations_id):
    """
    This is an HTMX callback from the mri_brain_information.html partial template
    It is triggered by a change in the date_input_field partial generating a post request
    This returns a date value which is stored in the model and returns the same partial.
    """
    investigations = Investigations.objects.get(pk=investigations_id)
    mri_brain_date = request.POST.get('input_date_field')

    Investigations.objects.filter(pk=investigations_id).update(
        mri_brain_date=datetime.strptime(
            mri_brain_date, "%Y-%m-%d").date())
    investigations = Investigations.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/mri_brain_information.html", context=context)
