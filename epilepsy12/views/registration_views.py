# python
from datetime import date

# django imports
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required
from django.utils import timezone
from django.contrib.gis.db.models import Q
from django.urls import reverse
from django.contrib import messages
from django.conf import settings

# 3rd party
from django_htmx.http import trigger_client_event
from django_htmx.http import HttpResponseClientRedirect

# RCPCH
from ..models import (
    Case,
    AuditProgress,
    Organisation,
    Registration,
    Site,
    KPI,
    Epilepsy12User,
)
from ..common_view_functions import (
    validate_and_update_model,
    recalculate_form_generate_response,
)
from ..decorator import user_may_view_this_child, login_and_otp_required
from ..general_functions import (
    construct_transfer_epilepsy12_site_email,
    cohorts_and_dates,
    send_email_to_recipients,
)


@login_and_otp_required()
@permission_required("epilepsy12.view_registration", raise_exception=True)
@user_may_view_this_child()
def register(request, case_id):
    """
    Called on registration form page load. If first time, creates new Registration object KPI object and
    AuditProgress object. Creates a new Site with selected organisation and associates with this case.
    Returns register.html template.
    """
    case = Case.objects.get(pk=case_id)

    if not Registration.objects.filter(case=case).exists():
        audit_progress = AuditProgress.objects.create(
            registration_complete=False,
            first_paediatric_assessment_complete=False,
            assessment_complete=False,
            epilepsy_context_complete=False,
            multiaxial_diagnosis_complete=False,
            management_complete=False,
            investigations_complete=False,
            registration_total_expected_fields=3,
            registration_total_completed_fields=0,
            first_paediatric_assessment_total_expected_fields=0,
            first_paediatric_assessment_total_completed_fields=0,
            assessment_total_expected_fields=0,
            assessment_total_completed_fields=0,
            epilepsy_context_total_expected_fields=0,
            epilepsy_context_total_completed_fields=0,
            multiaxial_diagnosis_total_expected_fields=0,
            multiaxial_diagnosis_total_completed_fields=0,
            investigations_total_expected_fields=0,
            investigations_total_completed_fields=0,
            management_total_expected_fields=0,
            management_total_completed_fields=0,
        )
        lead_organisation = Site.objects.filter(
            case=case,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True,
        ).get()

        kpi = KPI.objects.create(
            organisation=lead_organisation.organisation,
            paediatrician_with_expertise_in_epilepsies=0,
            epilepsy_specialist_nurse=0,
            tertiary_input=0,
            epilepsy_surgery_referral=0,
            ecg=0,
            mri=0,
            assessment_of_mental_health_issues=0,
            mental_health_support=0,
            sodium_valproate=0,
            comprehensive_care_planning_agreement=0,
            patient_held_individualised_epilepsy_document=0,
            patient_carer_parent_agreement_to_the_care_planning=0,
            care_planning_has_been_updated_when_necessary=0,
            comprehensive_care_planning_content=0,
            parental_prolonged_seizures_care_plan=0,
            water_safety=0,
            first_aid=0,
            general_participation_and_risk=0,
            service_contact_details=0,
            sudep=0,
            school_individual_healthcare_plan=0,
        )
        registration = Registration.objects.create(
            case=case, audit_progress=audit_progress, kpi=kpi
        )

    else:
        registration = Registration.objects.filter(case=case).get()

    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    previously_registered = 0

    lead_site = None

    registered_sites = Site.objects.filter(case=case)
    for registered_site in registered_sites:
        if (
            registered_site.site_is_primary_centre_of_epilepsy_care
            and registered_site.site_is_actively_involved_in_epilepsy_care
        ):
            lead_site = registered_site
        elif not registered_site.site_is_actively_involved_in_epilepsy_care:
            previously_registered += 1

    previously_registered_sites = None
    if previously_registered > 0:
        previously_registered_sites = Site.objects.filter(
            case=case,
            site_is_actively_involved_in_epilepsy_care=False,
            site_is_primary_centre_of_epilepsy_care=True,
        ).all()

    # test if first_paediatric_assessment_date and lead_centre exist, and eligibility criteria met
    if (
        registration.first_paediatric_assessment_date
        and lead_site
        and registration.eligibility_criteria_met
    ):
        active_template = "register"
    else:
        active_template = "none"

    context = {
        "registration": registration,
        "case_id": case_id,
        "organisation_list": organisation_list,
        "site": lead_site,
        "previously_registered_sites": previously_registered_sites,
        "audit_progress": registration.audit_progress,
        "active_template": active_template,
        # pass back organisation_id to steps for return to cases button
        "organisation_id": lead_site.organisation.pk,
        "field_enabled": False,
    }

    template_name = "epilepsy12/register.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    return response


# HTMX endpoints


"""
Lead site allocation, deletion, updating and transfer
"""


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.can_edit_epilepsy12_lead_centre", raise_exception=True)
def allocate_lead_site(request, registration_id):
    """
    Allocate site when none have been assigned
    """
    registration = Registration.objects.get(pk=registration_id)
    organisation_id = request.POST.get("allocate_lead_site")
    selected_organisation = Organisation.objects.get(pk=organisation_id)

    # test if site exists
    if Site.objects.filter(
        case=registration.case,
        organisation=selected_organisation,
        site_is_actively_involved_in_epilepsy_care=True,
    ).exists():
        # this site already plays an active role in the care of this child
        # update the status therefore to include the lead role

        Site.objects.filter(
            case=registration.case,
            organisation=selected_organisation,
            site_is_actively_involved_in_epilepsy_care=True,
        ).update(
            site_is_primary_centre_of_epilepsy_care=True,
            updated_at=timezone.now(),
            updated_by=request.user,
            active_transfer=True,
            transfer_request_date=timezone.now(),
        )
    else:
        # this site may still be associated with this registration but not actively
        # it is therefore safe to create a new record
        Site.objects.create(
            case=registration.case,
            organisation=selected_organisation,
            site_is_actively_involved_in_epilepsy_care=True,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_childrens_epilepsy_surgery_centre=False,
            site_is_paediatric_neurology_centre=False,
            site_is_general_paediatric_centre=True,
            created_at=timezone.now(),
            created_by=request.user,
            active_transfer=True,
            transfer_request_date=timezone.now(),
        )

    # retrieve the current active site
    site = Site.objects.filter(
        case=registration.case,
        organisation=selected_organisation,
        site_is_primary_centre_of_epilepsy_care=True,
        site_is_actively_involved_in_epilepsy_care=True,
    ).get()

    # get the new

    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "organisation_list": organisation_list,
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False,
    }

    template_name = "epilepsy12/partials/registration/lead_site.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_transfer_epilepsy12_lead_centre", raise_exception=True
)
def transfer_lead_site(request, registration_id, site_id):
    """
    POST request from lead_site.html on click of transfer lead centre button
    Does not update model
    Returns a edit_or_transfer_lead_site partial
    """
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)

    # remove the currently selected organisation from the list - should not be able to
    # transfer to the current organisation
    organisation_list = (
        Organisation.objects.filter(active=True)
        .exclude(pk=site.organisation.pk)
        .order_by("name")
        .all()
    )

    context = {
        "organisation_list": organisation_list,
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": True,
    }

    template_name = "epilepsy12/partials/registration/edit_or_transfer_lead_site.html"

    response = render(
        request=request,
        template_name=template_name,
        context=context,
    )

    # activate registration button if eligibility and lead centre set
    trigger_client_event(
        response=response, name="registration_status", params={}
    )  # updates the registration status bar with date in the client
    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.view_registration", raise_exception=True)
def cancel_lead_site(request, registration_id, site_id):
    registration = Registration.objects.get(pk=registration_id)
    site = Site.objects.get(pk=site_id)
    organisation_list = Organisation.objects.filter(active=True).order_by("name")

    context = {
        "registration": registration,
        "site": site,
        "edit": False,
        "transfer": False,
        "organisation_site": organisation_list,
    }

    template_name = "epilepsy12/partials/registration/lead_site.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_transfer_epilepsy12_lead_centre", raise_exception=True
)
def update_lead_site(request, registration_id, site_id, update):
    """
    HTMX POST request on button click from the lead_site partial
    If the update parameter is 'transfer',
    updates the lead centre by creating a new Site and
    setting site_is_actively_involved_in_epilepsy_care
    to False in the current record - this is a transfer of care.
    If the update parameter is 'edit'
    this updates updating the current site to a new centre.

    Transfers trigger an email to the new lead centre lead clinician and the rcpch audit team
    Edits can only be performed by superusers or the RCPCH audit team - no emails are sent with this option
    so it is reserved for editing lead centres centrally in rare situations.

    Redirects to the cases table
    """

    registration = Registration.objects.get(pk=registration_id)
    previous_lead_site = Site.objects.get(pk=site_id)
    origin_organisation = previous_lead_site.organisation

    if update == "transfer":
        new_organisation_id = request.POST.get("transfer_lead_site")
        new_organisation = Organisation.objects.get(pk=new_organisation_id)

        # create new record in Site table for child against new centre, or update existing record if
        # organisation already involved in child's care
        if Site.objects.filter(
            organisation=new_organisation,
            case=registration.case,
            site_is_actively_involved_in_epilepsy_care=True,
        ).exists():
            # this new site already cares actively for this child in some capacity
            new_lead_site = Site.objects.filter(
                organisation=new_organisation,
                case=registration.case,
                site_is_actively_involved_in_epilepsy_care=True,
            ).get()
            new_lead_site.site_is_primary_centre_of_epilepsy_care = True
            new_lead_site.site_is_actively_involved_in_epilepsy_care = True
            new_lead_site.active_transfer = True
            new_lead_site.transfer_origin_organisation = origin_organisation
            new_lead_site.transfer_request_date = timezone.now()
            new_lead_site.save(
                update_fields=[
                    "site_is_primary_centre_of_epilepsy_care",
                    "site_is_actively_involved_in_epilepsy_care",
                    "active_transfer",
                    "transfer_origin_organisation",
                    "transfer_request_date",
                ]
            )

        else:
            # this new organisation does not care for this child. Create a new site associated with this organisation
            new_lead_site = Site.objects.create(
                organisation=new_organisation,
                site_is_primary_centre_of_epilepsy_care=True,
                site_is_actively_involved_in_epilepsy_care=True,
                active_transfer=True,
                transfer_origin_organisation=origin_organisation,
                transfer_request_date=timezone.now(),
                updated_at=timezone.now(),
                updated_by=request.user,
                case=registration.case,
            )

        if (
            previous_lead_site.site_is_childrens_epilepsy_surgery_centre
            or previous_lead_site.site_is_paediatric_neurology_centre
            or previous_lead_site.site_is_general_paediatric_centre
        ):
            # the old site retains responsibility for one/all of neuro/gen paeds/surgery
            # but is not the lead site anymore
            # To allow us to track the fact that this site was once the lead site for this child,
            # we must create a new record to track the fact that this site is still involved in the care

            Site.objects.create(
                case=registration.case,
                organisation=origin_organisation,
                site_is_primary_centre_of_epilepsy_care=False,
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_childrens_epilepsy_surgery_centre=previous_lead_site.site_is_childrens_epilepsy_surgery_centre,
                site_is_paediatric_neurology_centre=previous_lead_site.site_is_paediatric_neurology_centre,
                site_is_general_paediatric_centre=previous_lead_site.site_is_general_paediatric_centre,
            )

        # update current site record to show nolonger actively involved in care as primary centre
        previous_lead_site.site_is_primary_centre_of_epilepsy_care = True
        previous_lead_site.site_is_actively_involved_in_epilepsy_care = False
        previous_lead_site.save(
            update_fields=[
                "site_is_primary_centre_of_epilepsy_care",
                "site_is_actively_involved_in_epilepsy_care",
            ]
        )

        # update KPI reference to new organisation
        KPI.objects.filter(registration=registration).update(
            organisation=new_organisation
        )

        """
        Update complete
        Send emails to lead clinicians +/- E12
        """

        # find clinical lead of organisation to which child transfered
        if Epilepsy12User.objects.filter(
            organisation_employer=new_organisation
        ).exists():
            # send to all Clinical Leads of new organisation
            recipients = list(
                Epilepsy12User.objects.filter(
                    (
                        Q(organisation_employer=new_organisation)
                        & Q(is_active=True)
                        & Q(role=1)  # Audit Centre Lead Clinician
                    )
                ).values_list("email", flat=True)
            )
            subject = "Epilepsy12 Lead Site Transfer"
        else:
            # there is no allocated clinical lead. Send to SITE_CONTACT_EMAIL
            recipients = [settings.SITE_CONTACT_EMAIL]
            subject = "Epilepsy12 Lead Site Transfer - NO LEAD CLINICIAN"

        email = construct_transfer_epilepsy12_site_email(
            request=request,
            target_organisation=new_organisation,
            origin_organisation=origin_organisation,
        )

        send_email_to_recipients(recipients=recipients, subject=subject, message=email)

        if new_organisation.country.boundary_identifier == "W92000004":
            parent_trust = new_organisation.local_health_board.name
        else:
            parent_trust = new_organisation.trust.name

        messages.success(
            request,
            f"{registration.case} has been successfully transferred to {parent_trust}. Email notifications have been sent to the lead clinician(s) for {parent_trust}.",
        )

    return HttpResponseClientRedirect(
        reverse("cases", kwargs={"organisation_id": previous_lead_site.organisation.pk})
    )


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.view_registration", raise_exception=True)
def previous_sites(request, registration_id):
    registration = Registration.objects.get(pk=registration_id)
    previous_sites = Site.objects.filter(
        case=registration.case,
        site_is_actively_involved_in_epilepsy_care=False,
        site_is_primary_centre_of_epilepsy_care=True,
    )

    context = {
        "previously_registered_sites": previous_sites,
        "registration": registration,
    }

    template_name = "epilepsy12/partials/registration/lead_site.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    return response


"""
Validation process
"""


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_register_child_in_epilepsy12", raise_exception=True
)
def confirm_eligible(request, registration_id):
    """
    HTMX POST request on button press in registration_form confirming child
    meets eligibility criteria of the audit.
    This will set the eligibility_criteria_met flag in the Registration model
    to True and replace the button with the is_eligible partial, a label confirming
    eligibility. The button will not be shown again.
    """
    context = {
        "has_error": False,
        "message": "Eligibility Criteria Confirmed.",
        "is_positive": True,
    }
    try:
        Registration.objects.update_or_create(
            pk=registration_id, defaults={"eligibility_criteria_met": True}
        )
    except Exception as error:
        context = {"has_error": True, "message": error, "is_positive": False}

    registration = Registration.objects.filter(pk=registration_id).get()

    template_name = "epilepsy12/partials/registration/is_eligible_label.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    if (
        registration.eligibility_criteria_met
        and Site.objects.filter(
            case=registration.case, site_is_primary_centre_of_epilepsy_care=True
        ).exists()
    ):
        # activate registration button if eligibility and lead centre set
        trigger_client_event(
            response=response, name="registration_status", params={}
        )  # updates the registration status bar with date in the client

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required("epilepsy12.change_registration", raise_exception=True)
def registration_status(request, registration_id):
    registration = Registration.objects.get(pk=registration_id)
    case = registration.case

    context = {"case_id": case.pk, "registration": registration}

    template_name = "epilepsy12/partials/registration/registration_dates.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
    )

    return response


@login_and_otp_required()
@user_may_view_this_child()
@permission_required(
    "epilepsy12.can_register_child_in_epilepsy12", raise_exception=True
)
def first_paediatric_assessment_date(request, case_id):
    """
    This defines registration in the audit and refers to the date of first paediatric assessment.
    Call back from POST request on button press of register button
    in first_paediatric_assessment_dates partial.
    This sets the registration date, and in turn, the cohort number
    It also triggers htmx 'registration_active' to enable the steps
    """

    case = Case.objects.get(pk=case_id)
    registration = Registration.objects.filter(case=case).get()

    if request.user.is_superuser or request.user.is_rcpch_audit_team_member:
        earliest_allowable_date = case.date_of_birth
    else:
        # registering a new child in the audit by a clinical team
        # sets the minimum allowable date to the currently submitting cohort start date or the start of the previous cohort if it is still within its grace period
        cohort_dates = cohorts_and_dates(first_paediatric_assessment_date=date.today())
        if cohort_dates["within_grace_period"]:
            earliest_allowable_date = cohort_dates["grace_cohort"]["cohort_start_date"]
        else:
            earliest_allowable_date = cohort_dates["submitting_cohort_start_date"]

    try:
        error_message = None
        validate_and_update_model(
            request,
            registration.pk,
            Registration,
            field_name="first_paediatric_assessment_date",
            page_element="date_field",
            earliest_allowable_date=earliest_allowable_date,
        )

    except ValueError as error:
        error_message = error

    # requery to get most up to date instance
    registration = Registration.objects.filter(case=case).get()

    context = {"case_id": case_id, "registration": registration}

    template_name = "epilepsy12/partials/registration/registration_dates.html"

    response = recalculate_form_generate_response(
        model_instance=registration,
        request=request,
        context=context,
        template=template_name,
        error_message=error_message,
    )

    return response
