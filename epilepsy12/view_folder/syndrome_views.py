from django.utils import timezone
from datetime import datetime
from operator import itemgetter
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..decorator import group_required
from django_htmx.http import trigger_client_event

from epilepsy12.models.syndrome import Syndrome
from epilepsy12.view_folder.multiaxial_diagnosis_views import multiaxial_diagnosis
from epilepsy12.constants.syndromes import SYNDROMES


def syndrome_diagnosis_date(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on date change
    """

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

    response = render(
        request=request, template_name='epilepsy12/partials/multiaxial_diagnosis/syndrome.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
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

    response = render(
        request=request, template_name='epilepsy12/partials/multiaxial_diagnosis/syndrome.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def syndrome_diagnosis_active(request, syndrome_id):
    """
    HTMX post request from syndrome.html partial on syndrome name change
    """
    if request.htmx.trigger_name == 'button-true':
        syndrome_diagnosis_active = True
    elif request.htmx.trigger_name == 'button-false':
        syndrome_diagnosis_active = False
    else:
        syndrome_diagnosis_active = None

    Syndrome.objects.filter(pk=syndrome_id).update(
        syndrome_diagnosis_active=syndrome_diagnosis_active,
        updated_at=timezone.now(),
        updated_by=request.user
    )

    syndrome = Syndrome.objects.get(pk=syndrome_id)

    context = {
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        'syndrome': syndrome
    }

    response = render(
        request=request, template_name='epilepsy12/partials/multiaxial_diagnosis/syndrome.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    return response
