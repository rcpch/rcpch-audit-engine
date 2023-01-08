
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import authenticate, logout, login
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError

from django_htmx.http import HttpResponseClientRedirect
from ..models import Epilepsy12User, HospitalTrust
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserAdminCreationForm

User = get_user_model()


@login_required
def epilepsy12_user_management(request):

    if request.user.hospital_employer is not None:
        # current user is affiliated with an existing hospital - set viewable trust to this
        selected_hospital = HospitalTrust.objects.get(
            OrganisationName=request.user.hospital_employer)

    else:
        # current user is a member of the RCPCH audit team and also not affiliated with a hospital
        # therefore set selected hospital to first of hospital on the list

        selected_hospital = HospitalTrust.objects.filter(
            Sector="NHS Sector"
        ).order_by('OrganisationName').first()

    template_name = 'epilepsy12/epilepsy12_user_management.html'

    context = {
        'selected_hospital': selected_hospital,
    }
    return render(request=request, template_name=template_name, context=context)


@login_required
def epilepsy12_user_list(request, hospital_id):
    """
    Returns the list of users for the selected hospitals
    Currently this includes RCPCH staff who are not associated with a hospital, though this breaks the update/delete and cancel
    buttons.
    """

    # get currently selected hospital
    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    sort_flag = None

    filter_term = request.GET.get('filtered_epilepsy12_user_list')

    # get all hospitals which are in the same parent trust
    hospital_children = HospitalTrust.objects.filter(
        ParentName=hospital_trust.ParentName).all()

    if filter_term:
        # filter_term is called if filtering by search box
        if request.user.view_preference == 0:
            # user has requested hospital level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(hospital_employer__OrganisationName__contains=hospital_trust.OrganisationName) &
                Q(first_name__icontains=filter_term) |
                Q(surname__icontains=filter_term) |
                Q(hospital_employer__icontains=filter_term) |
                Q(email__icontains=filter_term)
            ).order_by('surname').all()
        elif request.user.view_preference == 1:
            # user has requested trust level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(hospital_employer__OrganisationName__contains=hospital_trust.ParentName) &
                Q(first_name__icontains=filter_term) |
                Q(surname__icontains=filter_term) |
                Q(hospital_employer__icontains=filter_term) |
                Q(email__icontains=filter_term)
            ).order_by('surname').all()
        elif request.user.view_preference == 2:
            # user has requested national level view
            epilepsy12_user_list = Epilepsy12User.objects.filter(
                Q(first_name__icontains=filter_term) |
                Q(surname__icontains=filter_term) |
                Q(hospital_employer__OrganisationName__icontains=filter_term) |
                Q(email__icontains=filter_term)
            ).order_by('surname').all()
    else:

        """
        Epilepsy12Users are filtered based on user preference (request.user.view_preference), where 0 is hospital level,
        1 is trust level and 2 is national level
        Only RCPCH audit staff have this final option.
        """

        if request.user.view_preference == 2:
            # this is an RCPCH audit team member requesting national view
            filtered_epilepsy12_users = Epilepsy12User.objects.all()
        elif request.user.view_preference == 1:

            # filters all primary Trust level centres, irrespective of if active or inactive
            filtered_epilepsy12_users = Epilepsy12User.objects.filter(
                hospital_employer__ParentName__contains=hospital_trust.ParentName,
            )
        else:
            # filters all primary centres at hospital level, irrespective of if active or inactive
            filtered_epilepsy12_users = Epilepsy12User.objects.filter(
                hospital_employer__OrganisationName__contains=hospital_trust.OrganisationName,
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
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_hospital_employer_up" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_hospital_employer_up":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'hospital_employer').all()
            sort_flag = "sort_epilepsy12_users_by_hospital_employer_down"
        elif request.htmx.trigger_name == "sort_epilepsy12_users_by_hospital_employer_down" or request.GET.get('sort_flag') == "sort_epilepsy12_users_by_hospital_employer_down":
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                '-hospital_employer').all()
            sort_flag = "sort_epilepsy12_users_by_hospital_employer_down"
        else:
            epilepsy12_user_list = filtered_epilepsy12_users.order_by(
                'surname').all()

    rcpch_choices = (
        (0, f'Hospital View ({hospital_trust.OrganisationName})'),
        (1, f'Trust View ({hospital_trust.ParentName})'),
        (2, 'National View'),
    )

    paginator = Paginator(epilepsy12_user_list, 10)
    page_number = request.GET.get('page', 1)
    epilepsy12_user_list = paginator.page(page_number)

    context = {
        'epilepsy12_user_list': epilepsy12_user_list,
        'rcpch_choices': rcpch_choices,
        'hospital_trust': hospital_trust,
        'hospital_children': hospital_children,
        'sort_flag': sort_flag
    }

    if request.htmx:
        template_name = 'registration/user_management/epilepsy12_user_table.html'
        return render(request=request, template_name=template_name, context=context)

    template_name = 'registration/user_management/epilepsy12_user_list.html'

    return render(request=request, template_name=template_name, context=context)


@login_required
@permission_required('epilepsy12.add_epilepsy12user')
def create_epilepsy12_user(request, hospital_id):

    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    if request.method == 'POST':
        form = Epilepsy12UserAdminCreationForm(request.POST)

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
            email_template_name = "registration/admin_reset_password.html"
            c = {
                "email": new_user.email,
                'domain': '0.0.0.0:8000',
                'site_name': 'Website',
                "uid": urlsafe_base64_encode(force_bytes(new_user.pk)),
                "user": new_user,
                'token': default_token_generator.make_token(new_user),
                'protocol': 'http',
            }
            email = render_to_string(email_template_name, c)

            try:
                send_mail(subject, email, 'admin@epilepsy12.rcpch.tech',
                          [new_user.email], fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            messages.success(
                request, f"{new_user.email} account created successfully.")
            return redirect('epilepsy12_user_list', hospital_id=hospital_id)

        messages.error(
            request, f"Registration Unsuccessful: {form.errors}")

    prepopulated_data = {
        'hospital_employer': hospital_trust,
    }

    form = Epilepsy12UserAdminCreationForm(prepopulated_data)

    context = {
        'form': form,
        'admin_title': 'Add Epilepsy12 User',
        'is_superuser': False,
        'is_staff': False,
        'is_rcpch_audit_team_member': False
    }

    return render(request=request, template_name='registration/admin_create_user.html', context=context)


@login_required
@permission_required('epilepsy12.change_epilepsy12user')
def edit_epilepsy12_user(request, hospital_id, epilepsy12_user_id):
    """
    Django model form to edit/update Epilepsy12user
    """
    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)
    epilepsy12_user_to_edit = get_object_or_404(
        Epilepsy12User, pk=epilepsy12_user_id)
    can_edit = False
    if request.user.is_staff or request.user.hospital_employer == hospital_trust or request.user.is_rcpch_audit_team_member:
        can_edit = True
    if can_edit:
        form = Epilepsy12UserAdminCreationForm(
            request.POST or None, instance=epilepsy12_user_to_edit)
    else:
        return HttpResponseForbidden()

    if ('delete') in request.POST:
        epilepsy12_user_to_edit.delete()
        messages.success(request, "Sign up successful.")
        redirect_url = reverse('epilepsy12_user_list', kwargs={
                               'hospital_id': hospital_id})
        return redirect(redirect_url)
    if ('cancel') in request.POST:
        redirect_url = reverse('epilepsy12_user_list', kwargs={
                               'hospital_id': hospital_id})
        return redirect(redirect_url)

    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        redirect_url = reverse('epilepsy12_user_list', kwargs={
            'hospital_id': hospital_id})
        return redirect(redirect_url)

    template_name = 'registration/admin_create_user.html'

    return render(request, template_name, {
        'form': form,
        'admin_title': 'Edit/Update Epilepsy12 User'
    })


@login_required
@permission_required('epilepsy12.delete_epilepsy12user')
def delete_epilepsy12_user(request, hospital_id, epilepsy12_user_id):
    try:
        Epilepsy12User.objects.get(pk=epilepsy12_user_id).delete()
    except ValueError as error:
        messages.error(
            request, f"Delete User Unsuccessful: {error}")

    return HttpResponseClientRedirect(reverse('epilepsy12_user_list', kwargs={'hospital_id': hospital_id}))


# @require_http_methods(["GET", "POST"])
# def epilepsy12_password_reset_confirm(request, uidb64, token):
#     """
#     Endpoint from email link to reset password
#     """
#     print("called password reset")
#     if request.method == 'POST':
#         try:
#             uid = force_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(pk=uid)
#         except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
#             messages.add_message(request, messages.WARNING, str(e))
#             user = None
#         if user is not None and default_token_generator.check_token(user, token):
#             form = Epilepsy12UserPasswordResetForm(
#                 user=user, data=request.POST)
#             if form.is_valid():
#                 form.save()

#                 user.is_active = True
#                 user.email_confirmed = True
#                 user.save(commit=True)
#                 messages.add_message(
#                     request, messages.SUCCESS, 'Password reset successfully.')
#                 return redirect('login')
#             else:
#                 context = {
#                     'form': form,
#                     'uid': uidb64,
#                     'token': token
#                 }
#                 messages.add_message(
#                     request, messages.WARNING, 'Password could not be reset.')
#                 return render(request, 'account/password_reset_confirm.html', context)
#         else:
#             messages.add_message(request, messages.WARNING,
#                                  'Password reset link is invalid.')
#             messages.add_message(request, messages.WARNING,
#                                  'Please request a new password reset.')

#     try:
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
#         messages.add_message(request, messages.WARNING, str(e))
#         user = None

#     if user is not None and default_token_generator.check_token(user, token):
#         user.email_confirmed = True
#         user.save()
#         context = {
#             'form': Epilepsy12UserPasswordResetForm(user),
#             'uid': uidb64,
#             'token': token
#         }
#         return render(request, 'account/password_reset_confirm.html', context)
#     else:
#         messages.add_message(request, messages.WARNING,
#                              'Password reset link is invalid.')
#         messages.add_message(request, messages.WARNING,
#                              'Please request a new password reset.')

#     return redirect('home')
