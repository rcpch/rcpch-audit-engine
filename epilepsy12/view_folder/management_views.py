from django.utils import timezone
from datetime import datetime
from operator import itemgetter
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.common import SEX_TYPE

from epilepsy12.constants.medications import ANTIEPILEPSY_MEDICINES, BENZODIAZEPINE_TYPES
from ..decorator import group_required
from epilepsy12.general_functions.fetch_snomed import fetch_concept, fetch_ecl, snomed_medicine_search
from epilepsy12.models import Management, Registration, AntiEpilepsyMedicine, AuditProgress, AntiEpilepsyMedicine, antiepilepsy_medicine
from django_htmx.http import trigger_client_event
from .common_view_functions import recalculate_form_generate_response


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

    context = {
        "case_id": case_id,
        "registration": registration,
        "management": management,
        "rescue_medicines": rescue_medicines,
        "antiepilepsy_medicines": antiepilepsy_medicines,
        # 'snomed_items': snomed_items,
        "audit_progress": registration.audit_progress,
        "active_template": "management"
    }

    template_name = 'epilepsy12/management.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    if request.htmx.trigger_name == 'button-true':
        has_an_aed_been_given = True
    elif request.htmx.trigger_name == 'button-false':
        has_an_aed_been_given = False
        # delete any AEMs that exist
        if AntiEpilepsyMedicine.objects.filter(
            management=management,
            is_rescue_medicine=False
        ).exists():
            AntiEpilepsyMedicine.objects.filter(
                management=management,
                is_rescue_medicine=False
            ).delete()

    management.has_an_aed_been_given = has_an_aed_been_given
    management.save()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management,
        is_rescue_medicine=False
    )

    # if medicines.filter(antiepilepsy_medicine_snomed_code=10049011000001109).exists() and management.registration.case.gender == 2:
    #     # patient is female and valproate has been prescribed
    #     valproate_pregnancy_advice_needs_addressing = True

    context = {
        'management': management,
        'antiepilepsy_medicines': antiepilepsy_medicines
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicines.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def add_antiepilepsy_medicine(request, management_id, is_rescue_medicine):
    """
    Callback POST request from aed_list.html partial to add new AEM to antiepilepsy_medicine model
    """

    management = Management.objects.get(pk=management_id)

    if is_rescue_medicine == 'is_rescue_medicine':
        is_rescue = True
    else:
        is_rescue = False

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.create(
        medicine_id=None,
        medicine_name=None,
        is_rescue_medicine=is_rescue,
        antiepilepsy_medicine_snomed_code=None,
        antiepilepsy_medicine_snomed_preferred_name=None,
        antiepilepsy_medicine_start_date=None,
        antiepilepsy_medicine_stop_date=None,
        antiepilepsy_medicine_risk_discussed=None,
        management=management
    )

    if is_rescue:

        context = {
            'choices': sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1)),
            'antiepilepsy_medicine': antiepilepsy_medicine,
            'management_id': management_id,
            'is_rescue_medicine': is_rescue
        }

    else:

        context = {
            'choices': sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1)),
            'antiepilepsy_medicine': antiepilepsy_medicine,
            'management_id': management_id,
            'is_rescue_medicine': is_rescue
        }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicines.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def remove_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    POST request from either the rescue_medicine_list or the epilepsy_medicine_list
    Returns the epilepsy_medicine_list template filtered with a list of medicines depending whether are rescue
    or antiepilepsy medicines
    """

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)
    management = antiepilepsy_medicine.management
    is_rescue_medicine = antiepilepsy_medicine.is_rescue_medicine

    # delete record
    antiepilepsy_medicine.delete()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management,
        is_rescue_medicine=is_rescue_medicine
    ).all()

    context = {
        'medicines': antiepilepsy_medicines,
        'management_id': management.pk,
        'is_rescue_medicine': is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine_list.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def edit_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    Call back from onclick of edit button in antiepilepsy_medicine_list partial
    returns the antiepilepsy_medicine partial form populated with the medicine fields for editing
    """

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1))
    else:
        choices = sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1))

    context = {
        'choices': choices,
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def close_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    Call back from onclick of edit button in antiepilepsy_medicine_list partial
    returns the antiepilepsy_medicine partial form populated with the medicine fields for editing
    """
    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)

    is_rescue_medicine = antiepilepsy_medicine.is_rescue_medicine

    # if all the fields are none this was not completed - delete the record
    if (
        antiepilepsy_medicine.antiepilepsy_medicine_start_date is None and antiepilepsy_medicine.antiepilepsy_medicine_stop_date is None and antiepilepsy_medicine.medicine_id is None and antiepilepsy_medicine.antiepilepsy_medicine_risk_discussed is None
    ):
        antiepilepsy_medicine.delete()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=antiepilepsy_medicine.management,
        is_rescue_medicine=is_rescue_medicine
    )

    context = {
        'medicines': antiepilepsy_medicines,
        'management_id': antiepilepsy_medicine.management.pk,
        'is_rescue_medicine': is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine_list.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def medicine_id(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update medicine_name
    """

    # get the medicine to update
    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = BENZODIAZEPINE_TYPES
    else:
        choices = ANTIEPILEPSY_MEDICINES

    # get id of medicine - TODO this should be the SNOMEDCTID
    medicine_id = request.POST.get('medicine_id')

    # look up the medicine name from the constant
    medicine_name = None
    for medicine in choices:
        if int(medicine_id) == int(medicine[0]):
            medicine_name = medicine[1]

    antiepilepsy_medicine.medicine_name = medicine_name
    antiepilepsy_medicine.medicine_id = medicine_id

    if int(antiepilepsy_medicine.medicine_id) == 21 and int(antiepilepsy_medicine.management.registration.case.sex) == 2:
        # sodium valproate selected and patient is female
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = True
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = None
    else:
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = False
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = None

    antiepilepsy_medicine.save()

    context = {
        'choices': sorted(choices, key=itemgetter(1)),
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def antiepilepsy_medicine_start_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_start_date
    """

    antiepilepsy_medicine_start_date = request.POST.get(
        'antiepilepsy_medicine_start_date')

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)
    antiepilepsy_medicine.antiepilepsy_medicine_start_date = datetime.strptime(
        antiepilepsy_medicine_start_date, "%Y-%m-%d").date()
    antiepilepsy_medicine.updated_at = timezone.now(),
    antiepilepsy_medicine.updated_by = request.user
    antiepilepsy_medicine.save()

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1))
    else:
        choices = sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1))

    context = {
        'choices': choices,
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def antiepilepsy_medicine_stop_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_stop_date
    """

    antiepilepsy_medicine_stop_date = request.POST.get(
        'antiepilepsy_medicine_stop_date')

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)
    antiepilepsy_medicine.antiepilepsy_medicine_stop_date = datetime.strptime(
        antiepilepsy_medicine_stop_date, "%Y-%m-%d").date()
    antiepilepsy_medicine.updated_at = timezone.now(),
    antiepilepsy_medicine.updated_by = request.user
    antiepilepsy_medicine.save()

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1))
    else:
        choices = sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1))

    context = {
        'choices': choices,
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def antiepilepsy_medicine_risk_discussed(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_risk_discussed
    """

    if request.htmx.trigger_name == 'button-true':
        antiepilepsy_medicine_risk_discussed = True
    elif request.htmx.trigger_name == 'button-false':
        antiepilepsy_medicine_risk_discussed = False

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)
    antiepilepsy_medicine.antiepilepsy_medicine_risk_discussed = antiepilepsy_medicine_risk_discussed
    antiepilepsy_medicine.updated_at = timezone.now(),
    antiepilepsy_medicine.updated_by = request.user
    antiepilepsy_medicine.save()

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1))
    else:
        choices = sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1))

    context = {
        'choices': choices,
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
def is_a_pregnancy_prevention_programme_in_place(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update is_a_pregnancy_prevention_programme_in_place
    """

    if request.htmx.trigger_name == 'button-true':
        is_a_pregnancy_prevention_programme_in_place = True
    elif request.htmx.trigger_name == 'button-false':
        is_a_pregnancy_prevention_programme_in_place = False

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id)
    antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = is_a_pregnancy_prevention_programme_in_place
    antiepilepsy_medicine.updated_at = timezone.now(),
    antiepilepsy_medicine.updated_by = request.user
    antiepilepsy_medicine.save()

    if antiepilepsy_medicine.is_rescue_medicine:
        choices = sorted(BENZODIAZEPINE_TYPES, key=itemgetter(1))
    else:
        choices = sorted(ANTIEPILEPSY_MEDICINES, key=itemgetter(1))

    context = {
        'choices': choices,
        'antiepilepsy_medicine': antiepilepsy_medicine,
        'is_rescue_medicine': antiepilepsy_medicine.is_rescue_medicine
    }

    template_name = 'epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html'

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name
    )

    return response


""" 
Fields relating to rescue medication begin here
"""


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_rescue_medication_been_prescribed(request, management_id):
    """
    HTMX call from management template
    POST request on toggle button click
    If rescue medicine has been prescribed, return partial template comprising input search and dropdown
    """

    # TODO if rescue medicine toggled from true to false, need to delete previous rescue medicines with modal warning

    management = Management.objects.get(pk=management_id)

    if request.htmx.trigger_name == 'button-true':
        has_rescue_medication_been_prescribed = True
    elif request.htmx.trigger_name == 'button-false':
        has_rescue_medication_been_prescribed = False
        # delete any associated rescue medicines
        if AntiEpilepsyMedicine.objects.filter(
            management=management,
            is_rescue_medicine=True
        ).exists():
            AntiEpilepsyMedicine.objects.filter(
                management=management,
                is_rescue_medicine=True
            ).delete()

    management.has_rescue_medication_been_prescribed = has_rescue_medication_been_prescribed
    management.save()

    management = Management.objects.get(pk=management_id)
    rescue_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management,
        is_rescue_medicine=True
    ).all()

    context = {
        'management': management,
        'rescue_medicines': rescue_medicines,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/rescue_medicines.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

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

    template_name = 'epilepsy12/partials/management/individualised_care_plan.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_been_referred_for_mental_health_support(request, management_id):
    """
    This is an HTMX callback from the has_been_referred_for_mental_health_support partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, has_been_referred_for_mental_health_support=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                has_been_referred_for_mental_health_support=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                has_been_referred_for_mental_health_support=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            has_been_referred_for_mental_health_support=Q(
                has_been_referred_for_mental_health_support=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }

    template_name = 'epilepsy12/partials/management/mental_health_support.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

    return response


@login_required
@group_required('epilepsy12_audit_team_edit_access', 'epilepsy12_audit_team_full_access', 'trust_audit_team_edit_access', 'trust_audit_team_full_access')
def has_support_for_mental_health_support(request, management_id):
    """
    This is an HTMX callback from the has_support_for_mental_health_support partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    if Management.objects.filter(pk=management_id, has_support_for_mental_health_support=None).exists():
        # no selection - get the name of the button
        if request.htmx.trigger_name == 'button-true':
            Management.objects.filter(pk=management_id).update(
                has_support_for_mental_health_support=True,
                updated_at=timezone.now(),
                updated_by=request.user)
        elif request.htmx.trigger_name == 'button-false':
            Management.objects.filter(pk=management_id).update(
                has_support_for_mental_health_support=False,
                updated_at=timezone.now(),
                updated_by=request.user)
        else:
            print(
                "Some kind of error - this will need to be raised and returned to template")
            return HttpResponse("Error")
    else:
        Management.objects.filter(pk=management_id).update(
            has_support_for_mental_health_support=Q(
                has_support_for_mental_health_support=False),
            updated_at=timezone.now(),
            updated_by=request.user)

    management = Management.objects.get(pk=management_id)

    context = {
        'management': management
    }

    template_name = 'epilepsy12/partials/management/mental_health_support.html'

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name
    )

    return response
