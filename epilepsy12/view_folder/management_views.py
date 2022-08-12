from datetime import datetime
from django.http import HttpResponse
from django.utils.timezone import make_aware
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from epilepsy12.general_functions.fetch_snomed import fetch_concept, snomed_medicine_search
from epilepsy12.models.management import Management
from epilepsy12.models.antiepilepsy_medicine import AntiEpilepsyMedicine

from epilepsy12.models.registration import Registration


@login_required
def management(request, case_id):
    # function called on form load
    # creates a new management object if one does not exist
    # loads historical medicines and passes them to template

    registration = Registration.objects.filter(case=case_id).first()

    management, created = Management.objects.get_or_create(
        registration=registration)

    rescue_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=True).all()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=False).all()

    valproate_pregnancy_advice_needs_addressing = False

    if antiepilepsy_medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
        # patient is female and valproate has been prescribed
        valproate_pregnancy_advice_needs_addressing = True

    context = {
        "case_id": case_id,
        "registration": registration,
        "management": management,
        "rescue_medicines": rescue_medicines,
        "antiepilepsy_medicines": antiepilepsy_medicines,
        "valproate_pregnancy_advice_needs_addressing": valproate_pregnancy_advice_needs_addressing,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "management_complete": registration.investigation_management_complete,
        "active_template": "management"
    }

    return render(request=request, template_name='epilepsy12/management.html', context=context)

# HTMX


@login_required
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

    return render(request=request, template_name="epilepsy12/partials/management/aeds.html", context=context)


@login_required
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

    return render(request=request, template_name="epilepsy12/partials/management/rescue_medicines.html", context=context)


@login_required
def rescue_medicine_search(request, management_id):
    """
    HTMX callback from management template
    GET request filtering query to SNOMED server using keyup from input
    Returns snomed list of terms
    """
    rescue_medicine_search_text = request.GET.get('rescue_medicine_search')
    items = snomed_medicine_search(rescue_medicine_search_text)

    context = {
        'items': items,
        'management_id': management_id
    }

    return render(request=request, template_name="epilepsy12/partials/management/rescue_medicine_select.html", context=context)


@login_required
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

    return render(request=request, template_name="epilepsy12/partials/medicines/rescue_medicine_list.html", context=context)


@login_required
def antiepilepsy_medicine_search(request, management_id):
    """
    HTMX callback from management template
    GET request filtering query to SNOMED server using keyup from input
    Returns snomed list of terms
    """
    antiepilepsy_medicine_search_text = request.GET.get(
        'antiepilepsy_medicine_search')
    items = snomed_medicine_search(antiepilepsy_medicine_search_text)

    context = {
        'items': items,
        'management_id': management_id
    }

    return render(request=request, template_name="epilepsy12/partials/management/antiepilepsy_medicine_select.html", context=context)


@login_required
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

    return render(request=request, template_name="epilepsy12/partials/medicines/antiepilepsy_medicine_list.html", context=context)


@login_required
def is_a_pregnancy_prevention_programme_in_place(request, management_id):
    """
    This is an HTMX callback from antiepilepsy_medicine_list template on click of toggle is_a_pregnancy_prevention_programme_in_place
    (relating to field in the management model).
    The toggle is only offered if patient is female and one of the drugs selected is valproate
    Selecting the toggle calls this function which persists the selection in the management model and returns the partial template
    """

    Management.objects.filter(pk=management_id).update(
        is_a_pregnancy_prevention_programme_in_place=Q(is_a_pregnancy_prevention_programme_in_place=False))

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

    return render(request=request, template_name="epilepsy12/partials/medicines/antiepilepsy_medicine_list.html", context=context)


@login_required
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
                individualised_care_plan_in_place=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_in_place=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_in_place=Q(individualised_care_plan_in_place=False))

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
def individualised_care_plan_date(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This persists the care plan date value, and returns the same partial.
    """
    # TODO date validation needed
    Management.objects.filter(pk=management_id).update(
        individualised_care_plan_date=datetime.strptime(
            request.POST.get('individualised_care_plan_date'), "%Y-%m-%d").date())
    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
def individualised_care_plan_has_parent_carer_child_agreement(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_has_parent_carer_child_agreement=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_has_parent_carer_child_agreement=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_has_parent_carer_child_agreement=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_has_parent_carer_child_agreement=Q(individualised_care_plan_has_parent_carer_child_agreement=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                individualised_care_plan_includes_service_contact_details=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_service_contact_details=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_service_contact_details=Q(individualised_care_plan_includes_service_contact_details=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                individualised_care_plan_include_first_aid=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_include_first_aid=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_include_first_aid=Q(individualised_care_plan_include_first_aid=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
            individualised_care_plan_parental_prolonged_seizure_care=Q(individualised_care_plan_parental_prolonged_seizure_care=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
            individualised_care_plan_includes_general_participation_risk=Q(individualised_care_plan_includes_general_participation_risk=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                individualised_care_plan_addresses_water_safety=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_water_safety=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_addresses_water_safety=Q(individualised_care_plan_addresses_water_safety=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                individualised_care_plan_addresses_sudep=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_addresses_sudep=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_addresses_sudep=Q(individualised_care_plan_addresses_sudep=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
def individualised_care_plan_includes_aihp(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, individualised_care_plan_includes_aihp=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_aihp=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_aihp=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_aihp=Q(individualised_care_plan_includes_aihp=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                individualised_care_plan_includes_ehcp=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                individualised_care_plan_includes_ehcp=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_includes_ehcp=Q(individualised_care_plan_includes_ehcp=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)


@login_required
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
                has_individualised_care_plan_been_updated_in_the_last_year=True)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                has_individualised_care_plan_been_updated_in_the_last_year=False)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            has_individualised_care_plan_been_updated_in_the_last_year=Q(has_individualised_care_plan_been_updated_in_the_last_year=False))

    management = Management.objects.get(pk=management_id)
    context = {
        'management': management
    }
    return render(request=request, template_name='epilepsy12/partials/management/individualised_care_plan.html', context=context)
