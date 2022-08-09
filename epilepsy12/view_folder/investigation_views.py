from datetime import datetime
from django.utils.timezone import make_aware
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.models.investigations import Investigation

from epilepsy12.models.registration import Registration


@login_required
def investigations(request, case_id):
    registration = Registration.objects.filter(case=case_id).first()

    investigations, created = Investigation.objects.get_or_create(
        registration=registration)

    context = {
        "case_id": case_id,
        "registration": registration,
        "investigations": investigations,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "investigations"
    }
    return render(request=request, template_name='epilepsy12/investigations.html', context=context)


# htmx

def eeg_indicated(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    eeg_indicated = not investigations.eeg_indicated
    Investigation.objects.filter(pk=investigations_id).update(
        eeg_indicated=eeg_indicated)
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def eeg_request_date(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    naive_eeg_request_date = datetime.strptime(
        request.POST.get('eeg_request_date'), "%Y-%m-%d").date()

    # aware_eeg_request_date = make_aware(naive_eeg_request_date)

    Investigation.objects.filter(pk=investigations_id).update(
        eeg_request_date=naive_eeg_request_date)
    investigations = Investigation.objects.get(pk=investigations_id)

    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def eeg_performed_date(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    naive_eeg_performed_date = datetime.strptime(
        request.POST.get('eeg_performed_date'), "%Y-%m-%d").date()

    Investigation.objects.filter(pk=investigations_id).update(
        eeg_performed_date=naive_eeg_performed_date)
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def twelve_lead_ecg_status(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    twelve_lead_ecg_status = not investigations.twelve_lead_ecg_status
    Investigation.objects.filter(pk=investigations_id).update(
        twelve_lead_ecg_status=twelve_lead_ecg_status)
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def ct_head_scan_status(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    ct_head_scan_status = not investigations.ct_head_scan_status
    Investigation.objects.filter(pk=investigations_id).update(
        ct_head_scan_status=ct_head_scan_status)
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def mri_indicated(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    mri_indicated = not investigations.mri_indicated
    Investigation.objects.filter(pk=investigations_id).update(
        mri_indicated=mri_indicated)
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)


def mri_brain_date(request, investigations_id):
    investigations = Investigation.objects.get(pk=investigations_id)
    mri_brain_date = request.POST.get('mri_brain_date')

    Investigation.objects.filter(pk=investigations_id).update(
        eeg_requested=datetime.strptime(
            mri_brain_date, "%Y-%m-%d").date())
    investigations = Investigation.objects.get(pk=investigations_id)
    context = {
        'investigations': investigations
    }

    return render(request=request, template_name="epilepsy12/partials/investigations/eeg_indicated.html", context=context)
