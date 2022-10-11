from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from ..decorator import group_required
from epilepsy12.general_functions.fetch_snomed import fetch_concept, snomed_medicine_search
from epilepsy12.models import Management, Registration, AntiEpilepsyMedicine, AuditProgress, AntiEpilepsyMedicine
from django_htmx.http import trigger_client_event


@login_required
def management(request, case_id):
    # function called on form load
    # creates a new management object if one does not exist
    # loads historical medicines and passes them to template

    registration = Registration.objects.filter(case=case_id).first()

    if Management.objects.filter(
            registration=registration).exists():
        management = Management.objects.filter(
            registration=registration).get()
    else:
        Management.objects.create(registration=registration)
        management = Management.objects.filter(registration=registration).get()

    rescue_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=True).all()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=False).all()

    valproate_pregnancy_advice_needs_addressing = False

    if antiepilepsy_medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
        # patient is female and valproate has been prescribed
        valproate_pregnancy_advice_needs_addressing = True

    test_fields_update_audit_progress(management)

    context = {
        "case_id": case_id,
        "registration": registration,
        "management": management,
        "rescue_medicines": rescue_medicines,
        "antiepilepsy_medicines": antiepilepsy_medicines,
        "valproate_pregnancy_advice_needs_addressing": valproate_pregnancy_advice_needs_addressing,
        "audit_progress": registration.audit_progress,
        "active_template": "management"
    }

    response = render(
        request=request, template_name='epilepsy12/management.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


"""
HTMX fields
There is a function/hx route for each field in the form
Each one is protected by @login_required
Each one updates the record.




Fields relating to rescue medication begin here
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_an_aed_been_given(request, management_id):
    # HTMX call back from management template
    # POST request on toggle button click
    # if AED has been prescribed returns partial template comprising AED search box and dropdown

    management = Management.objects.get(pk=management_id)

    has_an_aed_been_given = not management.has_an_aed_been_given

    management.has_an_aed_been_given = has_an_aed_been_given
    management.save()

    medicines = AntiEpilepsyMedicine.objects.filter(management=management)

    valproate_pregnancy_advice_needs_addressing = False

    if medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
        # patient is female and valproate has been prescribed
        valproate_pregnancy_advice_needs_addressing = True

    context = {
        'valproate_pregnancy_advice_needs_addressing': valproate_pregnancy_advice_needs_addressing,
        'management': management
    }

    response = render(
        request=request, template_name="epilepsy12/partials/management/aeds.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    test_fields_update_audit_progress(management)
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def antiepilepsy_medicine_search(request, management_id):
    """
    HTMX callback from management template
    GET request filtering query to SNOMED server using keyup from input
    Returns snomed list of terms
    """
    antiepilepsy_medicine_search_text = request.GET.get(
        'antiepilepsy_medicine_search')
    items = snomed_medicine_search(antiepilepsy_medicine_search_text)

    management = Management.objects.get(pk=management_id)

    context = {
        'items': items,
        'management_id': management_id
    }
    response = render(
        request=request, template_name="epilepsy12/partials/management/antiepilepsy_medicine_select.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps
    test_fields_update_audit_progress(management)
    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def save_selected_antiepilepsy_medicine(request, management_id):
    """
    HTMX callback from antiepilepsy_medicine_select template
    POST request from select populated by SNOMED rescue medicine terms on save button click. Returned value is conceptId of 
    rescue medicine currently selected.
    This function uses the conceptId to fetch the preferredDescription from the SNOMED server which is also persisted
    Returns the partial template medicines/rescue_medicine_list with a list of rescue medicines used in that child
    """

    management = Management.objects.get(pk=management_id)
    snomed_concept = fetch_concept(request.POST.get(
        'selected_antiepilepsy_medicine')
    )

    concept_id = snomed_concept['concept']['id']

    if snomed_concept["preferredDescription"]:
        name = snomed_concept["preferredDescription"]["term"]
    else:
        name = "No SNOMED preferred term"

    AntiEpilepsyMedicine.objects.create(
        antiepilepsy_medicine_type=None,
        is_rescue_medicine=False,
        antiepilepsy_medicine_snomed_code=concept_id,
        antiepilepsy_medicine_snomed_preferred_name=name,
        antiepilepsy_medicine_start_date=None,
        antiepilepsy_medicine_stop_date=None,
        antiepilepsy_medicine_risk_discussed=None,
        is_a_pregnancy_prevention_programme_in_place=False,
        management=management
    )

    medicines = AntiEpilepsyMedicine.objects.filter(management=management)

    valproate_pregnancy_advice_needs_addressing = False

    if medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
        # patient is female and valproate has been prescribed
        valproate_pregnancy_advice_needs_addressing = True

    context = {
        'management': management,
        'antiepilepsy_medicines': medicines,
        'valproate_pregnancy_advice_needs_addressing': valproate_pregnancy_advice_needs_addressing,
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name="epilepsy12/partials/medicines/antiepilepsy_medicine_list.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def is_a_pregnancy_prevention_programme_in_place(request, management_id):
    """
    This is an HTMX callback from antiepilepsy_medicine_list template on click of toggle is_a_pregnancy_prevention_programme_in_place
    (relating to field in the management model).
    The toggle is only offered if patient is female and one of the drugs selected is valproate
    Selecting the toggle calls this function which persists the selection in the management model and returns the partial template
    """

    Management.objects.filter(pk=management_id).update(
        is_a_pregnancy_prevention_programme_in_place=Q(
            is_a_pregnancy_prevention_programme_in_place=False),
        updated_at=timezone.now(),
        updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    medicines = AntiEpilepsyMedicine.objects.filter(management=management)

    valproate_pregnancy_advice_needs_addressing = False

    if medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
        # patient is female and valproate has been prescribed
        valproate_pregnancy_advice_needs_addressing = True

    context = {
        'management': management,
        'antiepilepsy_medicines': medicines,
        'valproate_pregnancy_advice_needs_addressing': valproate_pregnancy_advice_needs_addressing,
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name="epilepsy12/partials/medicines/antiepilepsy_medicine_list.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


""" 
Fields relating to rescue medication begin here
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def rescue_medication_prescribed(request, management_id):
    """
    HTMX call from management template
    POST request on toggle button click
    If rescue medicine has been prescribed, return partial template comprising input search and dropdown
    """

    # TODO if rescue medicine toggled from true to false, need to delete previous rescue medicines with modal warning

    management = Management.objects.get(pk=management_id)

    has_rescue_medication_been_prescribed = not management.has_rescue_medication_been_prescribed

    management.has_rescue_medication_been_prescribed = has_rescue_medication_been_prescribed
    management.save()

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name="epilepsy12/partials/management/rescue_medicines.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def rescue_medicine_search(request, management_id):
    """
    HTMX callback from management template
    GET request filtering query to SNOMED server using keyup from input
    Returns snomed list of terms
    """
    rescue_medicine_search_text = request.GET.get('rescue_medicine_search')
    items = snomed_medicine_search(rescue_medicine_search_text)

    management = Management.objects.get(pk=management_id)

    context = {
        'items': items,
        'management_id': management_id
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name="epilepsy12/partials/management/rescue_medicine_select.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def save_selected_rescue_medicine(request, management_id):
    """
    HTMX callback from rescue_medicine_select template
    POST request from select populated by SNOMED rescue medicine terms on save button click. Returned value is conceptId of 
    rescue medicine currently selected.
    This function uses the conceptId to fetch the preferredDescription from the SNOMED server which is also persisted
    Returns the partial template medicines/rescue_medicine_list with a list of rescue medicines used in that child
    """

    management = Management.objects.get(pk=management_id)
    snomed_concept = fetch_concept(request.POST.get(
        'selected_rescue_medicine')
    )

    if snomed_concept["preferredDescription"]["term"]:
        name = snomed_concept["preferredDescription"]["term"]
    else:
        name = "No SNOMED preferred term"

    AntiEpilepsyMedicine.objects.create(
        antiepilepsy_medicine_type=None,
        is_rescue_medicine=True,
        antiepilepsy_medicine_snomed_code=request.POST.get(
            'selected_rescue_medicine'),
        antiepilepsy_medicine_snomed_preferred_name=name,
        antiepilepsy_medicine_start_date=None,
        antiepilepsy_medicine_stop_date=None,
        antiepilepsy_medicine_risk_discussed=None,
        is_a_pregnancy_prevention_programme_in_place=False,
        management=management
    )

    medicines = AntiEpilepsyMedicine.objects.filter(management=management)

    context = {
        'rescue_medicines': medicines
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name="epilepsy12/partials/medicines/rescue_medicine_list.html", context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


"""
Fields relating to individual care plans begin here
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_in_place(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists, 
    and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_in_place=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_in_place=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_in_place=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_in_place=Q(
                individualised_care_plan_in_place=False),
            individualised_care_plan_date=None,
            individualised_care_plan_has_parent_carer_child_agreement=None,
            individualised_care_plan_includes_service_contact_details=None,
            individualised_care_plan_include_first_aid=None,
            individualised_care_plan_parental_prolonged_seizure_care=None,
            individualised_care_plan_includes_general_participation_risk=None,
            individualised_care_plan_addresses_water_safety=None,
            individualised_care_plan_addresses_sudep=None,
            # individualised_care_plan_includes_aihp=None,
            individualised_care_plan_includes_ehcp=None,
            has_individualised_care_plan_been_updated_in_the_last_year=None,
            updated_at=timezone.now(),
            updated_by=request.user
        )

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_date(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This persists the care plan date value, and returns the same partial.
    """

    # TODO date validation needed
    Management.objects.filter(pk=management_id).update(
        individualised_care_plan_date=datetime.strptime(
            request.POST.get(request.htmx.trigger_name), "%Y-%m-%d").date(),
        updated_at=timezone.now(),
        updated_by=request.user)
    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_has_parent_carer_child_agreement(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if request.htmx.trigger_name == 'button-true':
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_has_parent_carer_child_agreement=True,
            updated_at=timezone.now(),
            updated_by=request.user)

    elif request.htmx.trigger_name == 'button-false':

        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_has_parent_carer_child_agreement=False,
            updated_at=timezone.now(),
            updated_by=request.user)
    else:
        print(
            "Some kind of error - this will need to be raised and returned to template")
        return HttpResponse("Error")

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_includes_service_contact_details(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_includes_service_contact_details=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_service_contact_details=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_service_contact_details=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_service_contact_details=Q(
                individualised_care_plan_includes_service_contact_details=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_include_first_aid(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_include_first_aid=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_include_first_aid=True,
                updated_at=timezone.now())
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_include_first_aid=False,
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_include_first_aid=Q(
                individualised_care_plan_include_first_aid=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_parental_prolonged_seizure_care(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_parental_prolonged_seizure_care=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_parental_prolonged_seizure_care=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_parental_prolonged_seizure_care=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_parental_prolonged_seizure_care=Q(
                individualised_care_plan_parental_prolonged_seizure_care=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_includes_general_participation_risk(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_includes_general_participation_risk=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_general_participation_risk=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_general_participation_risk=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_general_participation_risk=Q(
                individualised_care_plan_includes_general_participation_risk=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }

    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_addresses_water_safety(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_addresses_water_safety=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_water_safety=True,
                updated_at=timezone.now())
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_water_safety=False,
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_addresses_water_safety=Q(
                individualised_care_plan_addresses_water_safety=False),
            updated_at=timezone.now(),
            updated_by=request.user
        )

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)
    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_addresses_sudep(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_addresses_sudep=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_sudep=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_sudep=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_addresses_sudep=Q(
                individualised_care_plan_addresses_sudep=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    test_fields_update_audit_progress(management)

    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def individualised_care_plan_includes_ehcp(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_includes_ehcp=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_ehcp=True,
                updated_at=timezone.now())
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_ehcp=False,
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_ehcp=Q(
                individualised_care_plan_includes_ehcp=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }

    test_fields_update_audit_progress(management)

    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_individualised_care_plan_been_updated_in_the_last_year(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, has_individualised_care_plan_been_updated_in_the_last_year=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                has_individualised_care_plan_been_updated_in_the_last_year=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                has_individualised_care_plan_been_updated_in_the_last_year=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            has_individualised_care_plan_been_updated_in_the_last_year=Q(
                has_individualised_care_plan_been_updated_in_the_last_year=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }

    test_fields_update_audit_progress(management)

    response = render(
        request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)

    # trigger a GET request from the steps template
    trigger_client_event(
        response=response,
        name="registration_active",
        params={})  # reloads the form to show the active steps

    return response

# calculate the score


def total_fields_expected(model_instance):
    # all fields would be:
    # has_an_aed_been_given
    # has_rescue_medication_been_prescribed
    # is_a_pregnancy_prevention_programme_in_place
    # rescue_medication_prescribed
    # individualised_care_plan_in_place
    # individualised_care_plan_date
    # individualised_care_plan_has_parent_carer_child_agreement
    # individualised_care_plan_includes_service_contact_details
    # individualised_care_plan_include_first_aid
    # individualised_care_plan_parental_prolonged_seizure_care
    # individualised_care_plan_includes_general_participation_risk
    # individualised_care_plan_addresses_water_safety
    # individualised_care_plan_addresses_sudep

    # individualised_care_plan_includes_ehcp
    # has_individualised_care_plan_been_updated_in_the_last_year

    valproate = False
    if AntiEpilepsyMedicine.objects.filter(
            management=model_instance, antiepilepsy_medicine_snomed_code=10049011000001109).exists():
        valproate = True

    cumulative_fields = 0
    if model_instance.has_an_aed_been_given and model_instance.has_an_aed_been_given is not None:
        cumulative_fields += 2
    else:
        cumulative_fields += 1

    if model_instance.has_rescue_medication_been_prescribed and model_instance.has_rescue_medication_been_prescribed is not None:
        cumulative_fields += 2
    else:
        cumulative_fields += 1

    if valproate:
        cumulative_fields += 1

    if model_instance.individualised_care_plan_in_place and model_instance.individualised_care_plan_in_place is not None:
        cumulative_fields += 11
    else:
        cumulative_fields += 1

    return cumulative_fields


def total_fields_completed(model_instance):
    # counts the number of completed fields
    fields = model_instance._meta.get_fields()

    counter = 0
    for field in fields:
        if (
                field.name is not None
                and field.name not in ['id', 'registration', 'antiepilepsymedicine', 'created_by', 'created_at', 'updated_by', 'updated_at']):
            if getattr(model_instance, field.name) is not None:
                counter += 1
    return counter

# test all fields


def test_fields_update_audit_progress(model_instance):
    all_completed_fields = total_fields_completed(model_instance)
    all_fields = total_fields_expected(model_instance)
    AuditProgress.objects.filter(registration=model_instance.registration).update(
        management_total_expected_fields=all_fields,
        management_total_completed_fields=all_completed_fields,
        management_complete=all_completed_fields == all_fields
    )
