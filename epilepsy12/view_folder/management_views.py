from dateutil import relativedelta
from datetime import date
from django.utils import timezone
from operator import itemgetter
from django.contrib.gis.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from epilepsy12.constants.medications import (
    ANTIEPILEPSY_MEDICINES,
    BENZODIAZEPINE_TYPES,
)
from epilepsy12.models import (
    Management,
    Registration,
    AntiEpilepsyMedicine,
    AntiEpilepsyMedicine,
    Site,
    MedicineEntity,
)
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.view_management", raise_exception=True)
def management(request, case_id):
    # function called on form load
    # creates a new management object if one does not exist
    # loads historical medicines and passes them to template

    registration = Registration.objects.filter(case=case_id).first()

    if Management.objects.filter(registration=registration).exists():
        management = Management.objects.filter(registration=registration).get()
    else:
        Management.objects.create(registration=registration)
        management = Management.objects.filter(registration=registration).get()

    rescue_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=True
    ).all()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=False
    ).all()

    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    context = {
        "case_id": case_id,
        "registration": registration,
        "management": management,
        "rescue_medicines": rescue_medicines,
        "antiepilepsy_medicines": antiepilepsy_medicines,
        "audit_progress": registration.audit_progress,
        "active_template": "management",
        "organisation_id": organisation_id,
    }

    template_name = "epilepsy12/management.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


"""
HTMX fields
There is a function/hx route for each field in the form
Each one is protected by @login_required
@user_may_view_this_child()
Each one updates the record.




Fields relating to rescue medication begin here
"""


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def has_an_aed_been_given(request, management_id):
    # HTMX call back from management template
    # POST request on toggle button click
    # if AED has been prescribed returns partial template comprising AED search box and dropdown

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="has_an_aed_been_given",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    # tidy up
    if management.has_an_aed_been_given == False:
        #     # delete any AEMs that exist
        if AntiEpilepsyMedicine.objects.filter(
            management=management, is_rescue_medicine=False
        ).exists():
            AntiEpilepsyMedicine.objects.filter(
                management=management, is_rescue_medicine=False
            ).delete()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=False
    )

    context = {
        "management": management,
        "antiepilepsy_medicines": antiepilepsy_medicines,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicines.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.add_antiepilepsymedicine", raise_exception=True)
def add_antiepilepsy_medicine(request, management_id, is_rescue_medicine):
    """
    Callback POST request from aed_list.html partial to add new AEM to antiepilepsy_medicine model
    """

    management = Management.objects.get(pk=management_id)

    if is_rescue_medicine == "is_rescue_medicine":
        is_rescue = True
    else:
        is_rescue = False

    # medicine = MedicineEntity.objects.filter(is_rescue=is_rescue).first()

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.create(
        is_rescue_medicine=is_rescue,
        antiepilepsy_medicine_start_date=None,
        antiepilepsy_medicine_stop_date=None,
        antiepilepsy_medicine_risk_discussed=None,
        is_a_pregnancy_prevention_programme_needed=None,
        management=management,
        medicine_entity=None,
    )

    context = {
        "choices": MedicineEntity.objects.filter(is_rescue=is_rescue).order_by(
            "medicine_name"
        ),
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "management_id": management_id,
        "is_rescue_medicine": is_rescue,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.delete_antiepilepsymedicine", raise_exception=True)
def remove_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    POST request from either the rescue_medicine_list or the epilepsy_medicine_list
    Returns the epilepsy_medicine_list template filtered with a list of medicines depending whether are rescue
    or antiepilepsy medicines
    """

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )
    management = antiepilepsy_medicine.management
    is_rescue_medicine = antiepilepsy_medicine.is_rescue_medicine

    # delete record
    antiepilepsy_medicine.delete()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=is_rescue_medicine
    ).all()

    context = {
        "medicines": antiepilepsy_medicines,
        "management_id": management.pk,
        "is_rescue_medicine": is_rescue_medicine,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine_list.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def edit_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    Call back from onclick of edit button in antiepilepsy_medicine_list partial
    returns the antiepilepsy_medicine partial form populated with the medicine fields for editing
    """

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    ).order_by("medicine_name")

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.view_antiepilepsymedicine", raise_exception=True)
def close_antiepilepsy_medicine(request, antiepilepsy_medicine_id):
    """
    Call back from onclick of edit button in antiepilepsy_medicine_list partial
    returns the antiepilepsy_medicine partial form populated with the medicine fields for editing
    """
    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    is_rescue_medicine = antiepilepsy_medicine.is_rescue_medicine

    # if all the fields are none this was not completed - delete the record
    if (
        antiepilepsy_medicine.antiepilepsy_medicine_start_date is None
        and antiepilepsy_medicine.antiepilepsy_medicine_stop_date is None
        and antiepilepsy_medicine.medicine_entity is None
        and antiepilepsy_medicine.antiepilepsy_medicine_risk_discussed is None
    ):
        antiepilepsy_medicine.delete()

    antiepilepsy_medicines = AntiEpilepsyMedicine.objects.filter(
        management=antiepilepsy_medicine.management,
        is_rescue_medicine=is_rescue_medicine,
    )

    context = {
        "medicines": antiepilepsy_medicines,
        "management_id": antiepilepsy_medicine.management.pk,
        "is_rescue_medicine": is_rescue_medicine,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine_list.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def medicine_id(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update medicine_name
    """

    # get the medicine to update
    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    ).order_by("medicine_name")

    # get id of medicine entity
    medicine_id = request.POST.get("medicine_id")

    # look up the medicine from the pk
    medicine_entity = MedicineEntity.objects.get(pk=medicine_id)

    antiepilepsy_medicine.medicine_entity = medicine_entity

    if hasattr(antiepilepsy_medicine, "medicine_entity"):
        if antiepilepsy_medicine.medicine_entity is not None:
            if (
                antiepilepsy_medicine.medicine_entity.medicine_name
                == "Sodium valproate"
                and int(antiepilepsy_medicine.management.registration.case.sex) == 2
            ):
                today = date.today()
                calculated_age = relativedelta.relativedelta(
                    today,
                    antiepilepsy_medicine.management.registration.case.date_of_birth,
                )
                if calculated_age.years >= 12:
                    # sodium valproate selected and patient is female
                    antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = (
                        True
                    )
                    antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = (
                        None
                    )
                    antiepilepsy_medicine.has_a_valproate_annual_risk_acknowledgement_form_been_completed = (
                        None
                    )
                else:
                    antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = (
                        False
                    )
                    antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = (
                        None
                    )
                    antiepilepsy_medicine.has_a_valproate_annual_risk_acknowledgement_form_been_completed = (
                        None
                    )
            else:
                antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = False
                antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = (
                    None
                )
                antiepilepsy_medicine.has_a_valproate_annual_risk_acknowledgement_form_been_completed = (
                    None
                )
    else:
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = False
        antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = None
        antiepilepsy_medicine.has_a_valproate_annual_risk_acknowledgement_form_been_completed = (
            None
        )

    antiepilepsy_medicine.save()

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def antiepilepsy_medicine_start_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_start_date
    """

    try:
        antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
            pk=antiepilepsy_medicine_id
        )
        error_message = None
        validate_and_update_model(
            request=request,
            model=AntiEpilepsyMedicine,
            model_id=antiepilepsy_medicine_id,
            field_name="antiepilepsy_medicine_start_date",
            page_element="date_field",
            comparison_date_field_name="antiepilepsy_medicine_stop_date",
            is_earliest_date=True,
            earliest_allowable_date=antiepilepsy_medicine.management.registration.registration_date,
        )
    except ValueError as error:
        error_message = error

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    ).order_by("medicine_name")

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def antiepilepsy_medicine_add_stop_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to toggle antiepilepsy_medicine_end_date
    """

    error_message = ""

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    ).order_by("medicine_name")

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": True,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def antiepilepsy_medicine_remove_stop_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to toggle closed antiepilepsy_medicine_end_date
    """

    error_message = ""

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    # set antiepilepsy_medicine_stop_date to None and save
    antiepilepsy_medicine.antiepilepsy_medicine_stop_date = None
    antiepilepsy_medicine.save()

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    ).order_by("medicine_name")

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": False,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def antiepilepsy_medicine_stop_date(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_stop_date
    """

    try:
        antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
            pk=antiepilepsy_medicine_id
        )
        error_message = None
        validate_and_update_model(
            request=request,
            model=AntiEpilepsyMedicine,
            model_id=antiepilepsy_medicine_id,
            field_name="antiepilepsy_medicine_stop_date",
            page_element="date_field",
            comparison_date_field_name="antiepilepsy_medicine_start_date",
            is_earliest_date=False,
            earliest_allowable_date=antiepilepsy_medicine.management.registration.registration_date,
        )
    except ValueError as error:
        error_message = error

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    )

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": True,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def antiepilepsy_medicine_risk_discussed(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update antiepilepsy_medicine_risk_discussed
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=AntiEpilepsyMedicine,
            model_id=antiepilepsy_medicine_id,
            field_name="antiepilepsy_medicine_risk_discussed",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    )

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def is_a_pregnancy_prevention_programme_in_place(request, antiepilepsy_medicine_id):
    """
    POST callback from antiepilepsy_medicine.html partial to update is_a_pregnancy_prevention_programme_in_place
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=AntiEpilepsyMedicine,
            model_id=antiepilepsy_medicine_id,
            field_name="is_a_pregnancy_prevention_programme_in_place",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    )

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def has_a_valproate_annual_risk_acknowledgement_form_been_completed(
    request, antiepilepsy_medicine_id
):
    """
    POST callback from antiepilepsy_medicine.html partial to update has_a_valproate_annual_risk_acknowledgement_form_been_completed
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=AntiEpilepsyMedicine,
            model_id=antiepilepsy_medicine_id,
            field_name="has_a_valproate_annual_risk_acknowledgement_form_been_completed",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
        pk=antiepilepsy_medicine_id
    )

    choices = MedicineEntity.objects.filter(
        is_rescue=antiepilepsy_medicine.is_rescue_medicine
    )

    if antiepilepsy_medicine.antiepilepsy_medicine_stop_date:
        show_end_date = True
    else:
        show_end_date = False

    context = {
        "choices": choices,
        "antiepilepsy_medicine": antiepilepsy_medicine,
        "is_rescue_medicine": antiepilepsy_medicine.is_rescue_medicine,
        "show_end_date": show_end_date,
    }

    template_name = "epilepsy12/partials/management/antiepilepsy_medicines/antiepilepsy_medicine.html"

    response = recalculate_form_generate_response(
        model_instance=antiepilepsy_medicine.management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


""" 
Fields relating to rescue medication begin here
"""


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_antiepilepsymedicine", raise_exception=True)
def has_rescue_medication_been_prescribed(request, management_id):
    """
    HTMX call from management template
    POST request on toggle button click
    If rescue medicine has been prescribed, return partial template comprising input search and dropdown
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="has_rescue_medication_been_prescribed",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    if management.has_rescue_medication_been_prescribed == False:
        # nolonger prescribed: remove any previously stored medicines
        if AntiEpilepsyMedicine.objects.filter(
            management=management, is_rescue_medicine=True
        ).exists():
            AntiEpilepsyMedicine.objects.filter(
                management=management, is_rescue_medicine=True
            ).delete()

    rescue_medicines = AntiEpilepsyMedicine.objects.filter(
        management=management, is_rescue_medicine=True
    ).all()

    context = {
        "management": management,
        "rescue_medicines": rescue_medicines,
    }

    template_name = (
        "epilepsy12/partials/management/antiepilepsy_medicines/rescue_medicines.html"
    )

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


"""
Fields relating to individual care plans begin here
"""


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_in_place(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value or sets it based on user selection if none exists,
    and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_in_place",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    if management.individualised_care_plan_in_place == False:
        # There is no(longer) any individualised care plan in place - set all ICP related fields to None
        Management.objects.filter(pk=management_id).update(
            individualised_care_plan_date=None,
            individualised_care_plan_has_parent_carer_child_agreement=None,
            individualised_care_plan_includes_service_contact_details=None,
            individualised_care_plan_include_first_aid=None,
            individualised_care_plan_parental_prolonged_seizure_care=None,
            individualised_care_plan_includes_general_participation_risk=None,
            individualised_care_plan_addresses_water_safety=None,
            individualised_care_plan_addresses_sudep=None,
            individualised_care_plan_includes_ehcp=None,
            has_individualised_care_plan_been_updated_in_the_last_year=None,
            updated_at=timezone.now(),
            updated_by=request.user,
        )

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_date(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This persists the care plan date value, and returns the same partial.
    """

    try:
        management = Management.objects.get(pk=management_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_date",
            page_element="date_field",
            earliest_allowable_date=management.registration.registration_date,
            comparison_date_field_name=None,
            is_earliest_date=None,
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_has_parent_carer_child_agreement(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_has_parent_carer_child_agreement",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_includes_service_contact_details(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_includes_service_contact_details",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_include_first_aid(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_include_first_aid",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_parental_prolonged_seizure_care(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """

    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_parental_prolonged_seizure_care",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_includes_general_participation_risk(
    request, management_id
):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_includes_general_participation_risk",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_addresses_water_safety(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_addresses_water_safety",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_addresses_sudep(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_addresses_sudep",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def individualised_care_plan_includes_ehcp(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="individualised_care_plan_includes_ehcp",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)
    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def has_individualised_care_plan_been_updated_in_the_last_year(request, management_id):
    """
    This is an HTMX callback from the individualised_care_plan partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="has_individualised_care_plan_been_updated_in_the_last_year",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/individualised_care_plan.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def has_been_referred_for_mental_health_support(request, management_id):
    """
    This is an HTMX callback from the has_been_referred_for_mental_health_support partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="has_been_referred_for_mental_health_support",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/mental_health_support.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response


@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_management", raise_exception=True)
def has_support_for_mental_health_support(request, management_id):
    """
    This is an HTMX callback from the has_support_for_mental_health_support partial template
    It is triggered by a toggle in the partial generating a post request
    This inverts the boolean field value, and returns the same partial.
    """
    try:
        error_message = None
        validate_and_update_model(
            request=request,
            model=Management,
            model_id=management_id,
            field_name="has_support_for_mental_health_support",
            page_element="toggle_button",
        )
    except ValueError as error:
        error_message = error

    management = Management.objects.get(pk=management_id)

    context = {"management": management}

    template_name = "epilepsy12/partials/management/mental_health_support.html"

    response = recalculate_form_generate_response(
        model_instance=management,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response
