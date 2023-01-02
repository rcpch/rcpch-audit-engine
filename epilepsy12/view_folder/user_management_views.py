from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.models import Group
from django.contrib.auth import login, get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden
from django_htmx.http import trigger_client_event, HttpResponseClientRedirect
from ..models import Epilepsy12User, HospitalTrust
from epilepsy12.forms_folder.epilepsy12_user_form import Epilepsy12UserAdminCreationForm
from ..constants import AUDIT_CENTRE_LEAD_CLINICIAN, TRUST_AUDIT_TEAM_FULL_ACCESS, AUDIT_CENTRE_CLINICIAN, TRUST_AUDIT_TEAM_EDIT_ACCESS, AUDIT_CENTRE_ADMINISTRATOR, TRUST_AUDIT_TEAM_EDIT_ACCESS, RCPCH_AUDIT_LEAD, EPILEPSY12_AUDIT_TEAM_FULL_ACCESS, RCPCH_AUDIT_ANALYST, EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS, RCPCH_AUDIT_ADMINISTRATOR, EPILEPSY12_AUDIT_TEAM_VIEW_ONLY, RCPCH_AUDIT_PATIENT_FAMILY, PATIENT_ACCESS, TRUST_AUDIT_TEAM_VIEW_ONLY


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
            new_user = form.save()
            role = form.cleaned_data['role']

            """
            Allocate Roles
            """
            if role == AUDIT_CENTRE_LEAD_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
            elif role == AUDIT_CENTRE_CLINICIAN:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            elif role == AUDIT_CENTRE_ADMINISTRATOR:
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            elif role == RCPCH_AUDIT_LEAD:
                group = Group.objects.get(
                    name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
            elif role == RCPCH_AUDIT_ANALYST:
                group = Group.objects.get(
                    name=EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS)
            elif role == RCPCH_AUDIT_ADMINISTRATOR:
                group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_VIEW_ONLY)
            elif role == RCPCH_AUDIT_PATIENT_FAMILY:
                group = Group.objects.get(name=PATIENT_ACCESS)
            else:
                # no group
                group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)

            group.user_set.add(new_user)

            messages.success(request, "Sign up successful.")
            return redirect('epilepsy12_user_list', hospital_id=hospital_id)

        print("form not valid")
        for msg in form.error_messages:
            messages.error(
                request, f"Registration Unsuccessful: {form.error_messages[msg]}")

    prepopulated_data = {
        'hospital_employer': hospital_trust,
    }

    form = Epilepsy12UserAdminCreationForm(prepopulated_data)

    context = {
        'form': form,
        'title': 'Add Epilepsy12 User',
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
    if ('cancel') in request.POST:
        redirect_url = reverse('epilepsy12_user_list', kwargs={
                               'hospital_id': hospital_id})

    if request.POST and form.is_valid():
        form.save()

        # Save was successful, so redirect to another page
        redirect_url = reverse('epilepsy12_user_list', kwargs={
                               'hospital_id': hospital_id})
        return redirect(redirect_url)

    template_name = 'registration/admin_create_user.html'

    return render(request, template_name, {
        'form': form,
        'title': 'Edit/Update Epilepsy12 User'
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
