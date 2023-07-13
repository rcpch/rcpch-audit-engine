from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.urls import reverse
from django.contrib.gis.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.core.mail import send_mail, BadHeaderError

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.html import strip_tags

# 3rd party
from django_htmx.http import HttpResponseClientRedirect

# epilepsy12
from ..models import Epilepsy12User, Organisation, VisitActivity
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserAdminCreationForm
from ..general_functions import construct_confirm_email, match_in_choice_key
from ..common_view_functions import group_for_role
from ..decorator import user_may_view_this_organisation
from ..constants import (
    RCPCH_AUDIT_TEAM_ROLES,
    AUDIT_CENTRE_ROLES,
    AUDIT_CENTRE_LEAD_CLINICIAN,
    TRUST_AUDIT_TEAM_FULL_ACCESS,
    AUDIT_CENTRE_CLINICIAN,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    AUDIT_CENTRE_ADMINISTRATOR,
    TRUST_AUDIT_TEAM_EDIT_ACCESS,
    RCPCH_AUDIT_TEAM,
    EPILEPSY12_AUDIT_TEAM_FULL_ACCESS,
    RCPCH_AUDIT_PATIENT_FAMILY,
    PATIENT_ACCESS,
    TRUST_AUDIT_TEAM_VIEW_ONLY,
)
from epilepsy12.forms_folder.epilepsy12_user_form import (
    Epilepsy12UserCreationForm,
    Epilepsy12LoginForm,
)


def signup(request, *args, **kwargs):
    """
    Part of the registration process. Signing up for a new account, returns empty form as a GET request
    or validates the form, creates an account and allocates a group if part of a POST request. It is not possible
    to create a superuser account through this route.
    """
    user = request.user
    if user.is_authenticated:
        return HttpResponse(f"{user} is already logged in!")

    if request.method == "POST":
        form = Epilepsy12UserCreationForm(request.POST)
        if form.is_valid():
            logged_in_user = form.save()
            logged_in_user.is_active = True
            """
            Allocate Roles
            """
            logged_in_user.is_superuser = False
            if logged_in_user.role == AUDIT_CENTRE_LEAD_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = False
            elif logged_in_user.role == AUDIT_CENTRE_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = False
            elif logged_in_user.role == AUDIT_CENTRE_ADMINISTRATOR:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = False
            elif logged_in_user.role == RCPCH_AUDIT_TEAM:
                group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = True
            elif logged_in_user.role == RCPCH_AUDIT_PATIENT_FAMILY:
                group = Group.objects.get(name=PATIENT_ACCESS)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = False
            else:
                # no group
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
                logged_in_user.is_staff = False
                logged_in_user.is_rcpch_staff = False

            logged_in_user.save()
            logged_in_user.groups.add(group)
            login(
                request,
                logged_in_user,
                backend="django.contrib.auth.backends.ModelBackend",
            )
            messages.success(request, "Sign up successful.")
            if user.organisation_employer is not None:
                # current user is affiliated with an existing organisation - set viewable trust to this
                selected_organisation = Organisation.objects.get(
                    OrganisationName=request.user.organisation_employer
                )
            else:
                # current user is a member of the RCPCH audit team and also not affiliated with a organisation
                # therefore set selected organisation to first of organisation on the list
                selected_organisation = Organisation.objects.order_by(
                    "OrganisationName"
                ).first()
            return redirect("organisation_reports")
        for msg in form.error_messages:
            messages.error(
                request, f"Registration Unsuccessful: {form.error_messages[msg]}"
            )

    form = Epilepsy12UserCreationForm()
    return render(
        request=request,
        template_name="registration/signup.html",
        context={"form": form},
    )


def epilepsy12_login(request):
    """
    Callback from the login form
    """
    if request.method == "POST":
        form = Epilepsy12LoginForm(request, data=request.POST)

        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            print(email)
            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.organisation_employer is not None:
                    # select the first hospital in the list if no allocated employing hospital
                    selected_organisation = Organisation.objects.get(
                        OrganisationName=user.organisation_employer
                    )
                else:
                    selected_organisation = Organisation.objects.first()
                if user.email_confirmed == False:
                    user.email_confirmed = True
                    user.save()
                login(request, user)
                last_logged_in = VisitActivity.objects.filter(
                    activity=1, epilepsy12user=user
                ).order_by("-activity_datetime")[:2]
                if last_logged_in.count() > 1:
                    messages.info(
                        request,
                        f"You are now logged in as {email}. You last logged in at {timezone.localtime(last_logged_in[1].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[1].ip_address}",
                    )
                else:
                    messages.info(
                        request,
                        f"You are now logged in as {email}. Welcome to Epilepsy12! This is your first time logging in ({timezone.localtime(last_logged_in[0].activity_datetime).strftime('%H:%M %p on %A, %d %B %Y')} from {last_logged_in[0].ip_address}).",
                    )

                    if request.user.organisation_employer is not None:
                        # current user is affiliated with an existing organisation - set viewable trust to this
                        selected_organisation = Organisation.objects.get(
                            OrganisationName=request.user.organisation_employer
                        )
                    else:
                        # current user is a member of the RCPCH audit team and also not affiliated with a organisation
                        # therefore set selected organisation to first of organisation on the list
                        selected_organisation = Organisation.objects.order_by(
                            "OrganisationName"
                        ).first()
                return redirect(
                    "selected_organisation_summary",
                    organisation_id=selected_organisation.pk,
                )
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    form = Epilepsy12LoginForm()
    return render(
        request=request, template_name="registration/login.html", context={"form": form}
    )


@user_may_view_this_organisation()
@login_required
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

    # get all organisations which are in the same parent trust
    organisation_children = Organisation.objects.filter(
        ParentOrganisation_OrganisationName=organisation.ParentOrganisation_OrganisationName
    ).all()

    if filter_term:
        filter_term_Q = (
            Q(first_name__icontains=filter_term)
            | Q(surname__icontains=filter_term)
            | Q(organisation_employer__OrganisationName__icontains=filter_term)
            | Q(email__icontains=filter_term)
        )

        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested organisation level view
            basic_filter = Q(
                organisation_employer__OrganisationName__icontains=organisation.OrganisationName
            )
        elif request.user.view_preference == 1:
            # user has requested trust level view
            basic_filter = Q(
                organisation_employer__OrganisationName__icontains=organisation.ParentOrganisation_OrganisationName
            )
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
            basic_filter = Q(
                organisation_employer__ParentOrganisation_OrganisationName__contains=organisation.ParentOrganisation_OrganisationName
            )

        elif request.user.view_preference == 0:
            # filters all primary centres at organisation level, irrespective of if active or inactive
            basic_filter = Q(
                organisation_employer__OrganisationName__contains=organisation.OrganisationName
            )
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
            sort_flag = "sort_epilepsy12_users_by_role_up"
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
            sort_flag = "sort_epilepsy12_users_by_role_up"
        elif (
            request.htmx.trigger_name == "sort_epilepsy12_users_by_role_up"
            or request.GET.get("sort_flag") == "sort_epilepsy12_users_by_role_up"
        ):
            epilepsy12_user_list = filtered_epilepsy12_users.order_by("role").all()
            sort_flag = "sort_epilepsy12_users_by_role_down"
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
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_down"
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

    if (
        request.user.is_rcpch_audit_team_member
        or request.user.is_rcpch_staff
        or request.user.is_superuser
    ):
        rcpch_choices = (
            (0, f"Organisation level ({organisation.OrganisationName})"),
            (1, f"Trust level ({organisation.ParentOrganisation_OrganisationName})"),
            (2, "National level"),
        )
    else:
        rcpch_choices = (
            (0, f"Organisation level ({organisation.OrganisationName})"),
            (1, f"Trust level ({organisation.ParentOrganisation_OrganisationName})"),
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


@login_required
@user_may_view_this_organisation()
@permission_required("epilepsy12.add_epilepsy12user", raise_exception=True)
def create_epilepsy12_user(request, organisation_id, user_type):
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
            rcpch_organisation=user_type, initial=prepopulated_data
        )
    elif user_type == "rcpch-staff":
        admin_title = "Add RCPCH Epilepsy12 staff member"
        form = Epilepsy12UserAdminCreationForm(
            rcpch_organisation=user_type, initial=None
        )

    if request.method == "POST":
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.POST or None,
        )

        if form.is_valid():
            # success message - return to user list
            new_user = form.save(commit=False)
            new_user.set_unusable_password()
            new_user.is_active = True
            new_user.email_confirmed = False
            new_user.view_preference = 0
            new_user.save()

            new_group = group_for_role(new_user.role)
            new_user.groups.add(new_group)

            # user created - send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(request=request, user=new_user)
            try:
                send_mail(
                    subject=subject,
                    from_email="admin@epilepsy12.rcpch.tech",
                    recipient_list=[new_user.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email,
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

            messages.success(request, f"{new_user.email} account created successfully.")
            return redirect("epilepsy12_user_list", organisation_id=organisation_id)

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


@login_required
@user_may_view_this_organisation()
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
        form = Epilepsy12UserAdminCreationForm(
            user_type,
            request.POST or None,
            instance=epilepsy12_user_to_edit,
        )
    else:
        return HttpResponseForbidden()

    if request.method == "POST":
        if "delete" in request.POST:
            epilepsy12_user_to_edit.delete()
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
            try:
                send_mail(
                    subject=subject,
                    from_email="admin@epilepsy12.rcpch.tech",
                    recipient_list=[epilepsy12_user_to_edit.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email,
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")

            messages.success(
                request,
                f"Confirmation request sent to {epilepsy12_user_to_edit.email}.",
            )
            redirect_url = reverse(
                "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
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
                    "epilepsy12_user_list", kwargs={"organisation_id": organisation_id}
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


@login_required
@user_may_view_this_organisation()
@permission_required("epilepsy12.delete_epilepsy12user", raise_exception=True)
def delete_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    try:
        Epilepsy12User.objects.get(pk=epilepsy12_user_id).delete()
    except ValueError as error:
        messages.error(request, f"Delete User Unsuccessful: {error}")

    return HttpResponseClientRedirect(
        reverse("epilepsy12_user_list", kwargs={"organisation_id": organisation_id})
    )


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "registration/password_reset.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("index")


@login_required
def logs(request, organisation_id, epilepsy12_user_id):
    """
    returns logs for given organisation
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user = Epilepsy12User.objects.get(pk=epilepsy12_user_id)

    activities = VisitActivity.objects.filter(epilepsy12user=epilepsy12_user).all()

    template_name = "epilepsy12/logs.html"
    context = {
        "epilepsy12_user": epilepsy12_user,
        "organisation": organisation,
        "activities": activities,
    }

    return render(request=request, template_name=template_name, context=context)


@login_required
def log_list(request, organisation_id, epilepsy12_user_id):
    """
    GET request to return log table
    """
    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user = Epilepsy12User.objects.get(pk=epilepsy12_user_id)

    activities = VisitActivity.objects.filter(epilepsy12user=epilepsy12_user).all()

    template_name = "epilepsy12/logs.html"
    context = {
        "epilepsy12_user": epilepsy12_user,
        "organisation": organisation,
        "activities": activities,
    }

    return render(request=request, template_name=template_name, context=context)