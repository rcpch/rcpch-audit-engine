# Logging setup
import logging

# Django
from django.utils import timezone
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.gis.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.conf import settings
from django.http import (
    HttpResponseForbidden,
    HttpResponse,
)
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.html import strip_tags
from django_htmx.http import HttpResponseClientRedirect


# Other dependencies
from two_factor.views import LoginView as TwoFactorLoginView
from django_otp import devices_for_user, user_has_device

import pandas as pd
from datetime import datetime, timedelta

# epilepsy12
from ..models import Epilepsy12User, Organisation, VisitActivity, Site
from epilepsy12.forms_folder.epilepsy12_user_form import (
    Epilepsy12UserAdminCreationForm,
    CaptchaAuthenticationForm,
    Epilepsy12PasswordResetForm,
)
from ..general_functions import (
    construct_confirm_email,
    match_in_choice_key,
    send_email_to_recipients,
)
from ..common_view_functions import group_for_role
from ..decorator import (
    user_may_view_this_organisation,
    user_can_access_user,
    login_and_otp_required,
)
from ..constants import (
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
)

logger = logging.getLogger(__name__)


@login_and_otp_required()
@user_may_view_this_organisation()
def epilepsy12_user_list(request, organisation_id):
    """
    Returns the list of users for the selected organisations
    Currently this includes RCPCH staff who are not associated with a organisation, though this breaks the update/delete and cancel
    buttons.
    """

    # get currently selected organisation
    organisation = Organisation.objects.get(pk=organisation_id)

    sort_flag = None

    filter_term = request.GET.get("filtered_epilepsy12_user_list")

    # get trust or health board
    if organisation.country.boundary_identifier == "W92000004":
        parent_trust = organisation.local_health_board
        # Wales - get all organisations which are in the same local health board
        organisation_children = Organisation.objects.filter(
            local_health_board=parent_trust, active=True
        ).all()
    else:
        parent_trust = organisation.trust
        # England - get all organisations which are in the same parent trust
        organisation_children = Organisation.objects.filter(
            trust=parent_trust, active=True
        ).all()

    if filter_term:
        filter_term_Q = (
            Q(first_name__icontains=filter_term)
            | Q(surname__icontains=filter_term)
            | Q(organisation_employer=organisation)
            | Q(email__icontains=filter_term)
        )

        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested organisation level view
            basic_filter = Q(organisation_employer=organisation)
        elif request.user.view_preference == 1:
            # user has requested trust level view
            if organisation.country.boundary_identifier == "W92000004":
                parent_trust = organisation.local_health_board
            else:
                parent_trust = organisation.trust
            basic_filter = Q(organisation_employer__trust=parent_trust)
        elif request.user.view_preference == 2:
            # user has requested national level view
            basic_filter = None

        if basic_filter:
            # the basic filter filters users based on the selected organisation view
            # the filter_term_Q filters based on what the user has put in the search box
            if (
                request.user.is_rcpch_staff
                or request.user.is_rcpch_audit_team_member
                or request.user.is_superuser
            ):
                # user is RCPCH or E12 audit staff so can see RCPCH staff also
                # who will not be affiliated with any organisation
                epilepsy12_user_list = (
                    Epilepsy12User.objects.filter(
                        basic_filter
                        | Q(organisation_employer__isnull=True) & filter_term_Q
                    )
                    .order_by("surname")
                    .all()
                )
            else:
                # These are non RCPCH staff / not superusers
                epilepsy12_user_list = (
                    Epilepsy12User.objects.filter(basic_filter & filter_term_Q)
                    .order_by("surname")
                    .all()
                )
        else:
            # national view
            epilepsy12_user_list = (
                Epilepsy12User.objects.filter(filter_term_Q).order_by("surname").all()
            )

    else:
        """
        Epilepsy12Users are filtered based on user preference (request.user.view_preference), where 0 is organisation level,
        1 is trust level and 2 is national level
        Only RCPCH audit staff have this final option.
        """
        if request.user.view_preference == 2:
            # this is an RCPCH audit team member requesting National level
            # No filter requirements - see all users, including those with no trust affiliation
            basic_filter = None

        elif request.user.view_preference == 1:
            # filters all primary Trust level centres, irrespective of if active or inactive
            if organisation.country.boundary_identifier == "W92000004":
                parent_trust = organisation.local_health_board
                basic_filter = Q(organisation_employer__local_health_board=parent_trust)
            else:
                parent_trust = organisation.trust
                basic_filter = Q(organisation_employer__trust__name=parent_trust)

        elif request.user.view_preference == 0:
            # filters all primary centres at organisation level, irrespective of if active or inactive
            basic_filter = Q(organisation_employer=organisation)
        else:
            raise Exception("No View Preference supplied")

        if (
            request.user.is_rcpch_staff
            or request.user.is_rcpch_audit_team_member
            or request.user.is_superuser
        ):
            if basic_filter:
                # organisational or trust view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter(
                        basic_filter | Q(organisation_employer__isnull=True)
                    )
                    .order_by("surname")
                    .all()
                )
            else:
                # national view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter().order_by("surname").all()
                )
        else:
            # not RCPCH staff or superusers
            if basic_filter:
                # organisation or trust view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter(basic_filter)
                    .order_by("surname")
                    .all()
                )
            else:
                # national view
                filtered_epilepsy12_users = (
                    Epilepsy12User.objects.filter().order_by("surname").all()
                )

        if (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_name_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_name_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()
            sort_flag = "sort_epilepsy12_users_by_name_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_name_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_name_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-surname").all()
            sort_flag = "sort_epilepsy12_users_by_name_down"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_email_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_email_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()
            sort_flag = "sort_epilepsy12_users_by_email_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_email_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_email_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-surname").all()
            sort_flag = "sort_epilepsy12_users_by_email_down"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_role_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_role_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("role").all()
            sort_flag = "sort_epilepsy12_users_by_role_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_role_down"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_role_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("-role").all()
            sort_flag = "sort_epilepsy12_users_by_role_down"
        elif (
            request.htmx.trigger_name
            == "sort_epilepsy12_users_by_organisation_employer_up"
            or request.GET.get("sort_flag")
            == "sort_epilepsy12_users_by_organisation_employer_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                "organisation_employer"
            ).all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_up"
        elif (
            request.htmx.trigger_name
            == "sort_epilepsy12_users_by_organisation_employer_down"
            or request.GET.get("sort_flag")
            == "sort_epilepsy12_users_by_organisation_employer_down"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                "-organisation_employer"
            ).all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_down"
        else:
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("surname").all()

    if organisation.country.boundary_identifier == "W92000004":
        parent_trust = organisation.local_health_board
    else:
        parent_trust = organisation.trust

    if (
        request.user.is_rcpch_audit_team_member
        or request.user.is_rcpch_staff
        or request.user.is_superuser
    ):
        if organisation.country.boundary_identifier == "W92000004":
            rcpch_choices = (
                (0, "Organisation level"),
                (1, "Local Health Board level"),
                (2, "National level"),
            )
        else:
            rcpch_choices = (
                (0, "Organisation level"),
                (1, "Trust level"),
                (2, "National level"),
            )
    else:
        if organisation.country.boundary_identifier == "W92000004":
            rcpch_choices = (
                (0, "Organisation level"),
                (1, "Local Health Board level"),
            )
        else:
            rcpch_choices = (
                (0, "Organisation level"),
                (1, "Trust level"),
            )

    paginator = Paginator(epilepsy12_user_list, 10)
    page_number = request.GET.get("page", 1)
    epilepsy12_user_list = paginator.page(page_number)

    context = {
        "epilepsy12_user_list": epilepsy12_user_list,
        "rcpch_choices": rcpch_choices,
        "organisation": organisation,
        "organisation_children": organisation_children,
        "sort_flag": sort_flag,
    }

    if request.htmx:
        template_name = "registration/user_management/epilepsy12_user_table.html"
        return render(request=request, template_name=template_name, context=context)

    template_name = "registration/user_management/epilepsy12_user_list.html"

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_organisation()
@permission_required("epilepsy12.add_epilepsy12user", raise_exception=True)
def create_epilepsy12_user(request, organisation_id, user_type, epilepsy12_user_id):
    """
    Creates an epilepsy12 user. It is called from epilepsy12 list of users
    If from the create epilepsy12 user button, the originating organisation is added to
    the saved user. If from the create rcpch-staff button, the originating organisation is removed.
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    if user_type == "organisation-staff":
        admin_title = "Add Epilepsy12 User"
        prepopulated_data = {
            "organisation_employer": organisation,
        }
        form = Epilepsy12UserAdminCreationForm(
            rcpch_organisation=user_type,
            requesting_user=request.user,
            initial=prepopulated_data,
        )
    elif user_type == "rcpch-staff":
        admin_title = "Add RCPCH Epilepsy12 staff member"
        form = Epilepsy12UserAdminCreationForm(
            rcpch_organisation=user_type, requesting_user=request.user, initial=None
        )

    if request.method == "POST":
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.user,
            request.POST or None,
        )

        if form.is_valid():
            # save new user and add to group - return to user list with success message
            # send sign up email asynchronously
            # If signup unsuccessful, user not saved return to list with error message. Email not sent.
            new_user = form.save(commit=False)
            new_user.set_unusable_password()
            new_user.is_active = True
            new_user.email_confirmed = False
            new_user.view_preference = 0
            try:
                new_user.save()
            except Exception as error:
                messages.error(
                    request,
                    f"Error: {error}. Account not created. Please contact Epilepsy12 if this issue persists.",
                )
                return redirect(
                    "epilepsy12_user_list",
                    organisation_id=organisation_id,
                )

            new_group = group_for_role(new_user.role)

            try:
                new_user.groups.add(new_group)
            except Exception as error:
                messages.error(
                    request,
                    f"Error: {error}. Account not created. Please contact Epilepsy12 if this issue persists.",
                )
                return redirect(
                    "epilepsy12_user_list",
                    organisation_id=organisation_id,
                )

            # user created - send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(request=request, user=new_user)

            send_email_to_recipients(
                recipients=[new_user.email], subject=subject, message=email
            )

            messages.success(
                request,
                f"Account created successfully. Confirmation email has been sent to {new_user.email}.",
            )
            return redirect(
                "epilepsy12_user_list",
                organisation_id=organisation_id,
            )

    context = {
        "form": form,
        "organisation_id": organisation_id,
        "admin_title": admin_title,
        "user_type": user_type,
    }

    return render(
        request=request,
        template_name="registration/admin_create_user.html",
        context=context,
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@user_can_access_user()
@permission_required("epilepsy12.change_epilepsy12user", raise_exception=True)
def edit_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    """
    Django model form to edit/update Epilepsy12user
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user_to_edit = get_object_or_404(Epilepsy12User, pk=epilepsy12_user_id)
    can_edit = False
    if (
        request.user.is_rcpch_staff
        or request.user.organisation_employer == organisation
        or request.user.is_rcpch_audit_team_member
    ):
        can_edit = True
    if match_in_choice_key(AUDIT_CENTRE_ROLES, epilepsy12_user_to_edit.role):
        user_type = "organisation-staff"
    elif match_in_choice_key(RCPCH_AUDIT_TEAM_ROLES, epilepsy12_user_to_edit.role):
        user_type = "rcpch-staff"
    if can_edit:
        # EMAIL INPUT FIELD IS DISABLED SO WILL NOT BE INCLUDED IN REQUEST.POST -> ADD IN MANUALLY
        if request.POST:
            request.POST = request.POST.copy()  # request.POST object is immutable
            request.POST["email"] = epilepsy12_user_to_edit.email
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.user,
            request.POST or None,
            instance=epilepsy12_user_to_edit,
        )

    else:
        return HttpResponseForbidden()

    if request.method == "POST":
        if "delete" in request.POST:
            # This call back from the user form, not the table.
            # Rather than delete user, instead set is_active to False as prevents cascade delete error for any cases/registrations
            # updated by this user (see issue #813)
            epilepsy12_user_to_edit.is_active = False
            epilepsy12_user_to_edit.save(update_fields=["is_active"])
            messages.success(
                request, f"{epilepsy12_user_to_edit.email} Deleted successfully."
            )
            redirect_url = reverse(
                "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
            )
            return redirect(redirect_url)
        if "cancel" in request.POST:
            redirect_url = reverse(
                "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
            )
            return redirect(redirect_url)
        if "resend" in request.POST:
            # send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(
                request=request, user=epilepsy12_user_to_edit
            )

            send_email_to_recipients(
                recipients=[epilepsy12_user_to_edit.email],
                subject=subject,
                message=email,
            )

            messages.success(
                request,
                f"Confirmation and password reset request resent to {epilepsy12_user_to_edit.email}.",
            )
            redirect_url = reverse(
                "epilepsy12_user_list",
                kwargs={
                    "organisation_id": organisation_id,
                },
            )
            return redirect(redirect_url)

        else:
            if form.is_valid():
                # this will not include the password which will be empty
                new_user = form.save()

                # update group
                new_group = group_for_role(new_user.role)
                new_user.groups.clear()
                new_user.groups.add(new_group)

                # adds success message
                messages.success(
                    request,
                    f"You have successfully updated {epilepsy12_user_to_edit}'s details",
                )

                # Save was successful, so redirect to another page
                redirect_url = reverse(
                    "epilepsy12_user_list",
                    kwargs={
                        "organisation_id": organisation_id,
                    },
                )
                return redirect(redirect_url)

    template_name = "registration/admin_create_user.html"

    if epilepsy12_user_to_edit.is_rcpch_staff:
        admin_title = "Edit RCPCH Epilepsy12 staff member"
        user_type = "rcpch-staff"
    else:
        admin_title = "Edit Epilepsy12 User"
        user_type = "organisation-staff"

    return render(
        request,
        template_name,
        {
            "organisation_id": organisation_id,
            "form": form,
            "admin_title": admin_title,
            "user_type": user_type,
        },
    )


@login_and_otp_required()
@user_may_view_this_organisation()
@user_can_access_user()
@permission_required("epilepsy12.delete_epilepsy12user", raise_exception=True)
def delete_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    """
    HTMX callback from epilepsy12user table
    Sets user is_active flag to False
    """
    try:
        # This call back from the table, not the form
        # rather than delete user, instead set is_active to False as prevents cascade delete error for any cases/registrations
        # updated by this user (see issue #813)
        Epilepsy12User.objects.filter(pk=epilepsy12_user_id).update(is_active=False)
    except ValueError as error:
        messages.error(request, f"Delete User Unsuccessful: {error}")

    return HttpResponseClientRedirect(
        reverse(
            "epilepsy12_user_list",
            kwargs={
                "organisation_id": organisation_id,
            },
        )
    )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "registration/password_reset.html"
    html_email_template_name = "registration/password_reset_email.html"
    email_template_name = strip_tags("registration/password_reset_email.html")
    subject_template_name = "registration/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    extra_email_context = {
        "reset_password_link_expires_at": datetime.now()
        + timedelta(seconds=int(settings.PASSWORD_RESET_TIMEOUT))
    }
    success_url = reverse_lazy("index")
    form_class = Epilepsy12PasswordResetForm

    # extend form_valid to set user.password_last_set
    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if Epilepsy12User.objects.filter(email=email, is_active=True).exists():
            e12user = Epilepsy12User.objects.filter(email=email, is_active=True).get()
            # password reset link sent
            VisitActivity.objects.create(epilepsy12user=e12user, activity=4)
        else:
            messages.warning(
                self.request, f"This email ({email}) is not attached to a user account."
            )
            return redirect(reverse("password_reset"))

        return super().form_valid(form)


class ResetPasswordConfirmView(PasswordResetConfirmView):
    # overridden custom django password reset work flow. User has submitted a valid password for reset
    # their email is stored in session for use later to update logs if they are successful
    def form_valid(self, form):
        # Store the user's email in the session
        self.request.session["user_email"] = form.user.email
        logging.info(f"Password reset requested for {form.user.email}")
        return super().form_valid(form)


class ResetPasswordComplete(PasswordResetCompleteView):
    # Overridden custom django password reset work flow. Picks up user email who has reset password from session
    # and updates VisitActivity,
    template_name = "registration/password_reset_complete.html"

    def dispatch(self, request, *args, **kwargs):
        # Call the dispatch method of the superclass
        response = super().dispatch(request, *args, **kwargs)

        # Get the user's email from the session (or request)
        user_email = request.session.get("user_email")
        if (
            user_email
            and Epilepsy12User.objects.filter(email=user_email, is_active=True).exists()
        ):
            updated_user = Epilepsy12User.objects.filter(
                email=user_email, is_active=True
            ).get()
            try:
                # log that User has successfully reset password
                VisitActivity.objects.create(
                    activity_datetime=timezone.now(),
                    activity=5,  # successful password reset
                    ip_address=request.META.get("REMOTE_ADDR"),
                    epilepsy12user=updated_user,
                )
                # reset the password_last_set field to current date/time
                updated_user.password_last_set = timezone.now()
                updated_user.save(update_fields=["password_last_set"])
            except Epilepsy12User.DoesNotExist:
                pass

        # Clear the session variable
        request.session.pop("user_email", None)

        return response


class RCPCHLoginView(TwoFactorLoginView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override original Django Auth Form with Captcha field inserted
        self.form_list["auth"] = CaptchaAuthenticationForm

    # Override successful login redirect to org summary page
    def done(self, form_list, **kwargs):
        response = super().done(form_list)
        response_url = getattr(response, "url")
        login_redirect_url = reverse(settings.LOGIN_REDIRECT_URL)
        # Successful login, redirect to login page
        if response_url == login_redirect_url:
            user = self.get_user()
            if not user.organisation_employer:
                org_id = 1
            else:
                org_id = user.organisation_employer.id
                # check for outstanding transfers in to this organisation
                if Site.objects.filter(
                    active_transfer=True, organisation=user.organisation_employer
                ).exists() and user.has_perm(
                    "epilepsy12.can_transfer_epilepsy12_lead_centre"
                ):
                    # there is an outstanding request for transfer in to this user's organisation. User is a lead clinician and can act on this
                    transfers = Site.objects.filter(
                        active_transfer=True, organisation=user.organisation_employer
                    )
                    for transfer in transfers:
                        messages.info(
                            self.request,
                            f"{transfer.transfer_origin_organisation} have requested transfer of {transfer.case} to {user.organisation_employer} for their Epilepsy12 care. Please find {transfer.case} in the case table to accept or decline this transfer request.",
                        )

            # time since last set password
            delta = timezone.now() - user.password_last_set
            # if user has not renewed password in last 90 days, redirect to login page
            password_reset_date = user.password_last_set + timezone.timedelta(days=90)
            if user.is_active and (password_reset_date <= timezone.now()):
                messages.error(
                    request=self.request,
                    message=f"Your password has expired. Please reset it.",
                )
                # log user out
                logout(self.request)
                return redirect(reverse("password_reset"))
            last_logged_in = VisitActivity.objects.filter(
                activity=1, epilepsy12user=user
            ).order_by("-activity_datetime")[:2]
            if last_logged_in.count() > 1:
                messages.info(
                    self.request,
                    f"You are now logged in as {user.email}. You last logged in at {timezone.localtime(last_logged_in[1].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[1].ip_address}.\nYou have {90-delta.days} days remaining until your password needs resetting.",
                )
            else:
                messages.info(
                    self.request,
                    f"You are now logged in as {user.email}. Welcome to Epilepsy12! This is your first time logging in ({timezone.localtime(last_logged_in[0].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[0].ip_address}).",
                )

            return redirect(
                reverse(
                    "selected_organisation_summary",
                    kwargs={"organisation_id": org_id},
                )
            )
        return response


@login_and_otp_required()
@user_can_access_user()
def logs(request, organisation_id, epilepsy12_user_id):
    """
    returns logs for given organisation and user
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user = Epilepsy12User.objects.get(pk=epilepsy12_user_id)

    activities = (
        VisitActivity.objects.filter(epilepsy12user=epilepsy12_user)
        .all()
        .order_by("-activity_datetime")
    )
    devices = devices_for_user(user=epilepsy12_user)
    has_device = user_has_device(user=epilepsy12_user)

    if request.htmx:
        for device in devices:
            if device.name == request.htmx.trigger_name:
                device.delete()
        devices = devices_for_user(user=epilepsy12_user, confirmed=True)
        template_name = "epilepsy12/logs_user_summary.html"
    else:
        template_name = "epilepsy12/logs.html"

    context = {
        "epilepsy12_user": epilepsy12_user,
        "organisation": organisation,
        "activities": activities,
        "devices": devices,
        "has_device": has_device,
    }

    return render(request=request, template_name=template_name, context=context)


@login_and_otp_required()
@user_may_view_this_organisation()
def all_epilepsy12_users_list(request, organisation_id):
    allowed_groups = [EPILEPSY12_AUDIT_TEAM_FULL_ACCESS]

    if not (
        request.user.is_superuser or request.user.groups.filter(name__in=allowed_groups)
    ):
        raise PermissionDenied()

    all_users = Epilepsy12User.objects.all().values()

    df = pd.DataFrame(all_users)

    # Convert DataFrame to CSV format
    csv_data = df.to_csv(index=False)

    # Create an HTTP response with the CSV data
    response = HttpResponse(csv_data, content_type="text/csv")

    response["Content-Disposition"] = 'attachment; filename="epilepsy12users.csv"'

    return response
