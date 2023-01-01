from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import Epilepsy12User, HospitalTrust


@login_required
def epilepsy12_user_list(request, hospital_id):

    # get currently selected hospital
    hospital_trust = HospitalTrust.objects.get(pk=hospital_id)

    sort_flag = None

    filter_term = request.GET.get('filtered_case_list')

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
                Q(hospital_employer__icontains=filter_term) |
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


def update_epilepsy12_user(request, hospital_id, epilepsy12_user_id):
    return
