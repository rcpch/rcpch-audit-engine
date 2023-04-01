
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.core.mail import send_mail, BadHeaderError, EmailMessage

from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.html import strip_tags

from django_htmx.http import HttpResponseClientRedirect
from ..models import Epilepsy12User, Organisation
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserAdminCreationForm
from ..general_functions.construct_confirm_email import construct_confirm_email

User = get_user_model()


@login_required
def epilepsy12_user_management(request):

    if request.user.organisation_employer is not None:
        # current user is affiliated with an existing organisation - set viewable trust to this
        selected_organisation = Organisation.objects.get(
            OrganisationName=request.user.organisation_employer)

    else:
        # current user is a member of the RCPCH audit team and also not affiliated with a organisation
        # therefore set selected organisation to first of organisation on the list

        selected_organisation = Organisation.objects.filter(
            Sector="NHS Sector"
        ).order_by('OrganisationName').first()

    template_name = 'epilepsy12/epilepsy12_user_management.html'

    context = {
        'selected_organisation': selected_organisation,
    }
    return render(request=request, template_name=template_name, context=context)


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

    filter_term = request.GET.get('filtered_epilepsy12_user_list')

    # get all organisations which are in the same parent trust
    organisation_children = Organisation.objects.filter(
        ParentName=organisation.ParentName).all()

    if filter_term:
        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested organisation level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(organisation_employer__OrganisationName__icontains=organisation.OrganisationName) &
                (Q(first_name__icontains=filter_term) |
                 Q(surname__icontains=filter_term) |
                 Q(organisation_employer__OrganisationName__icontains=filter_term) |
                 Q(email__icontains=filter_term))
            ).order_by('surname').all()
        elif request.user.view_preference == 1:
            # user has requested trust level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(organisation_employer__OrganisationName__icontains=organisation.ParentName) &
                (Q(first_name__icontains=filter_term) |
                 Q(surname__icontains=filter_term) |
                 Q(organisation_employer__OrganisationName__icontains=filter_term) |
                 Q(email__icontains=filter_term))
            ).order_by('surname').all()
        elif request.user.view_preference == 2:
            # user has requested national level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(first_name__icontains=filter_term) |
                Q(surname__icontains=filter_term) |
                Q(organisation_employer__OrganisationName__icontains=filter_term) |
                Q(email__icontains=filter_term)
            ).order_by('surname').all()
    else:

        """
        Epilepsy12Users are filtered based on user preference (request.user.view_preference), where 0 is organisation level,
        1 is trust level and 2 is national level
        Only RCPCH audit staff have this final option.
        """

        if request.user.view_preference == 2:
            # this is an RCPCH audit team member requesting national view
            filtered_epilepsy12_users = Epilepsy12User.objects.all()
        elif request.user.view_preference == 1:

            # filters all primary Trust level centres, irrespective of if active or inactive
            filtered_epilepsy12_users = Epilepsy12User.objects.filter(
                organisation_employer__ParentName__contains=organisation.ParentName,
            )
        else:
            # filters all primary centres at organisation level, irrespective of if active or inactive
            filtered_epilepsy12_users = Epilepsy12User.objects.filter(
                organisation_employer__OrganisationName__contains=organisation.OrganisationName,
            )

        if request.htmx.trigger_name == "sort_epilepsy12_users_by_name_up" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_name_up":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'surname').all()
            sort_flag = "sort_epilepsy12_users_by_name_up"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_name_down" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_name_down":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                '-surname').all()
            sort_flag = "sort_epilepsy12_users_by_role_up"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_email_up" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_email_up":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'surname').all()
            sort_flag = "sort_epilepsy12_users_by_email_up"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_email_down" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_email_down":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                '-surname').all()
            sort_flag = "sort_epilepsy12_users_by_role_up"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_role_up" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_role_up":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'role').all()
            sort_flag = "sort_epilepsy12_users_by_role_down"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_role_down" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_role_down":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                '-role').all()
            sort_flag = "sort_epilepsy12_users_by_role_down"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_organisation_employer_up" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_organisation_employer_up":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'organisation_employer').all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_down"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_organisation_employer_down" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_organisation_employer_down":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                '-organisation_employer').all()
            sort_flag = "sort_epilepsy12_users_by_organisation_employer_down"
        else:
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'surname').all()

    rcpch_choices = (
        (0, f'Hospital View ({organisation.OrganisationName})'),
        (1, f'Trust View ({organisation.ParentName})'),
        (2, 'National View'),
    )

    paginator = Paginator(epilepsy12_user_list, 10)
    page_number = request.GET.get('page', 1)
    epilepsy12_user_list = paginator.page(page_number)

    context = {
        'epilepsy12_user_list': epilepsy12_user_list,
        'rcpch_choices': rcpch_choices,
        'organisation': organisation,
        'organisation_children': organisation_children,
        'sort_flag': sort_flag
    }

    if request.htmx:
        template_name = 'registration/user_management/epilepsy12_user_table.html'
        return render(request=request, template_name=template_name, context=context)

    template_name = 'registration/user_management/epilepsy12_user_list.html'

    return render(request=request, template_name=template_name, context=context)


@login_required
@permission_required('epilepsy12.add_epilepsy12user')
def create_epilepsy12_user(request, organisation_id):

    organisation = Organisation.objects.get(pk=organisation_id)
    prepopulated_data = {
        'organisation_employer': organisation,
    }
    form = Epilepsy12UserAdminCreationForm(initial=prepopulated_data)

    if request.method == 'POST':

        form = Epilepsy12UserAdminCreationForm(request.POST or None)

        if form.is_valid():

            # success message - return to user list
            new_user = form.save(commit=False)
            new_user.set_unusable_password()
            new_user.is_active = True
            new_user.email_confirmed = False
            new_user.view_preference = 0
            new_user.save()
            get_user_model().objects.allocate_group_based_on_role(new_user)

            # user created - send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(request=request, user=new_user)
            try:
                send_mail(
                    subject=subject, from_email='admin@epilepsy12.rcpch.tech',
                    recipient_list=[new_user.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email
                )
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            messages.success(
                request, f"{new_user.email} account created successfully.")
            return redirect('epilepsy12_user_list', organisation_id=organisation_id)

    context = {
        'form': form,
        'organisation_id': organisation_id,
        'admin_title': 'Add Epilepsy12 User',
        'is_superuser': False,
        'is_staff': False,
        'is_rcpch_audit_team_member': False
    }

    return render(request=request, template_name='registration/admin_create_user.html', context=context)


@login_required
@permission_required('epilepsy12.change_epilepsy12user')
def edit_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    """
    Django model form to edit/update Epilepsy12user
    """

    organisation = Organisation.objects.get(pk=organisation_id)
    epilepsy12_user_to_edit = get_object_or_404(
        Epilepsy12User, pk=epilepsy12_user_id)
    can_edit = False
    if request.user.is_staff or request.user.organisation_employer == organisation or request.user.is_rcpch_audit_team_member:
        can_edit = True
    if can_edit:
        form = Epilepsy12UserAdminCreationForm(
            request.POST or None, instance=epilepsy12_user_to_edit)
    else:
        return HttpResponseForbidden()

    if request.method == 'POST':
        if 'delete' in request.POST:
            epilepsy12_user_to_edit.delete()
            messages.success(
                request, f"{epilepsy12_user_to_edit.email} Deleted successfully.")
            redirect_url = reverse('epilepsy12_user_list', kwargs={
                'organisation_id': organisation_id})
            return redirect(redirect_url)
        if 'cancel' in request.POST:
            redirect_url = reverse('epilepsy12_user_list', kwargs={
                'organisation_id': organisation_id})
            return redirect(redirect_url)
        if 'resend' in request.POST:
            # send email with reset link to new user
            subject = "Password Reset Requested"
            email = construct_confirm_email(
                request=request, user=epilepsy12_user_to_edit)
            try:
                send_mail(
                    subject=subject, from_email='admin@epilepsy12.rcpch.tech',
                    recipient_list=[epilepsy12_user_to_edit.email],
                    fail_silently=False,
                    message=strip_tags(email),
                    html_message=email
                )
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            messages.success(
                request, f"Confirmation request sent to {epilepsy12_user_to_edit.email}.")
            redirect_url = reverse('epilepsy12_user_list', kwargs={
                'organisation_id': organisation_id})
            return redirect(redirect_url)

        if request.POST and form.is_valid():
            form.save()

            # adds success message
            messages.success(
                request, f"You successfully updated {epilepsy12_user_to_edit}'s details")

            # Save was successful, so redirect to another page
            redirect_url = reverse('epilepsy12_user_list', kwargs={
                'organisation_id': organisation_id})
            return redirect(redirect_url)

    template_name = 'registration/admin_create_user.html'

    return render(request, template_name, {
        'organisation_id': organisation_id,
        'form': form,
        'admin_title': 'Edit Epilepsy12 User'
    })


@login_required
@permission_required('epilepsy12.delete_epilepsy12user')
def delete_epilepsy12_user(request, organisation_id, epilepsy12_user_id):
    try:
        Epilepsy12User.objects.get(pk=epilepsy12_user_id).delete()
    except ValueError as error:
        messages.error(
            request, f"Delete User Unsuccessful: {error}")

    return HttpResponseClientRedirect(reverse('epilepsy12_user_list', kwargs={'organisation_id': organisation_id}))


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('index')
