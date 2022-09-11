from django.utils import timezone
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Q, Count
from epilepsy12.forms import CaseForm
from epilepsy12.models import Registration, HospitalTrust, Site, hospital_trust
from ..models import Case
from django.contrib import messages
from ..general_functions import fetch_snomed
from django.core.paginator import Paginator


@login_required
@permission_required('epilepsy12_audit_team_view_only')
def case_list(request):
    """
    Returns a list of all children registered under the user's service.
    Path is protected to those logged in only
    Params:
    request.user

    If the user is a clinician / centre lead, only the children under their care are seen (whether registered or not)
    If the user is an audit administrator, they have can view all cases in the audit, but cannot edit
    If the user is a superuser, they can view and edit all cases in the audit (but with great power comes great responsibility)

    #TODO #32 Audit trail of all viewing or touching the database

    """
    hospital_trust = HospitalTrust.objects.filter(
        OrganisationName=request.user.hospital_employer).get()

    sort_flag = None

    filter_term = request.GET.get('filtered_case_list')

    if filter_term:
        all_cases = Case.objects.filter(
            Q(hospital_trusts__OrganisationName__contains=request.user.hospital_employer) &
            Q(first_name__icontains=filter_term) |
            Q(surname__icontains=filter_term) |
            Q(nhs_number__icontains=filter_term)
        ).order_by('surname').all()
    else:
        if request.htmx.trigger_name == "sort_by_imd_up" or request.GET.get('sort_flag') == "sort_by_imd_up":
            # this is to sort on IMD
            all_cases = Case.objects.annotate(hospital_trust_count=Count('site')).filter(hospital_trust_count=1).order_by(
                'index_of_multiple_deprivation_quintile').all()
            sort_flag = "sort_by_imd_up"
        elif request.htmx.trigger_name == "sort_by_imd_down" or request.GET.get('sort_flag') == "sort_by_imd_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-index_of_multiple_deprivation_quintile').all()
            sort_flag = "sort_by_imd_down"
        elif request.htmx.trigger_name == "sort_by_nhs_number_up" or request.GET.get('sort_flag') == "sort_by_nhs_number_up":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                'nhs_number').all()
            sort_flag = "sort_by_nhs_number_up"
        elif request.htmx.trigger_name == "sort_by_nhs_number_down" or request.GET.get('sort_flag') == "sort_by_nhs_number_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-nhs_number').all()
            sort_flag = "sort_by_nhs_number_down"
        elif request.htmx.trigger_name == "sort_by_ethnicity_up" or request.GET.get('sort_flag') == "sort_by_ethnicity_up":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                'ethnicity').all()
            sort_flag = "sort_by_ethnicity_up"
        elif request.htmx.trigger_name == "sort_by_ethnicity_down" or request.GET.get('sort_flag') == "sort_by_ethnicity_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-ethnicity').all()
            sort_flag = "sort_by_ethnicity_down"
        elif request.htmx.trigger_name == "sort_by_gender_up" or request.GET.get('sort_flag') == "sort_by_gender_up":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                'gender').all()
            sort_flag = "sort_by_gender_up"
        elif request.htmx.trigger_name == "sort_by_gender_down" or request.GET.get('sort_flag') == "sort_by_gender_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-sex').all()
            sort_flag = "sort_by_gender_down"
        elif request.htmx.trigger_name == "sort_by_name_up" or request.GET.get('sort_flag') == "sort_by_name_up":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                'surname').all()
            sort_flag = "sort_by_name_up"
        elif request.htmx.trigger_name == "sort_by_name_down" or request.GET.get('sort_flag') == "sort_by_name_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-surname').all()
            sort_flag = "sort_by_name_down"
        elif request.htmx.trigger_name == "sort_by_id_up" or request.GET.get('sort_flag') == "sort_by_id_up":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                'id').all()
            sort_flag = "sort_by_id_up"
        elif request.htmx.trigger_name == "sort_by_id_down" or request.GET.get('sort_flag') == "sort_by_id_down":
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by(
                '-id').all()
            sort_flag = "sort_by_id_down"
        else:
            all_cases = Case.objects.filter(
                hospital_trusts__OrganisationName__contains=request.user.hospital_employer).order_by('surname').all()

    registered_cases = Registration.objects.filter(
        ~Q(registration_date=None),
    ).all()


#     fetch_snomed(365456003, 'descendentSelfOf')

    paginator = Paginator(all_cases, 10)
    page_number = request.GET.get('page', 1)
    case_list = paginator.page(page_number)

    case_count = Case.objects.all().count()
    registered_count = registered_cases.count()

    context = {
        'case_list': case_list,
        'total_cases': case_count,
        'total_registrations': registered_count,
        'sort_flag': sort_flag
    }
    if request.htmx:
        return render(request=request, template_name='epilepsy12/partials/case_table.html', context=context)

    template_name = 'epilepsy12/cases/cases.html'
    return render(request, template_name, context)


@login_required
@permission_required('epilepsy12.change_case')
def create_case(request):
    form = CaseForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            obj = form.save(commit=False)
            obj.created_at = datetime.now()
            obj.save()
            messages.success(request, "You successfully created the case")
            return redirect('cases')

    context = {
        "form": form
    }
    return render(request=request, template_name='epilepsy12/cases/case.html', context=context)


@login_required
@permission_required('epilepsy12.change_case')
def update_case(request, id):
    case = get_object_or_404(Case, id=id)
    form = CaseForm(instance=case)

    if request.method == "POST":
        if ('delete') in request.POST:
            case.delete()
            return redirect('cases')
        form = CaseForm(request.POST, instance=case)
        if form.is_valid:
            obj = form.save()
            if (case.locked != form.locked):
                # locked status has changed
                if (form.locked):
                    obj.locked_by = request.user
                    obj.locked_at = datetime.now()
                else:
                    obj.locked_by = None
                    obj.locked_at = None
            obj.save()
            messages.success(
                request, "You successfully updated the child's details")
            return redirect('cases')

    context = {
        "form": form
    }

    return render(request=request, template_name='epilepsy12/cases/case.html', context=context)


@login_required
@permission_required('epilepsy12.change_case')
def delete_case(request, id):
    case = get_object_or_404(Case, id=id)
    case.delete()
    return redirect('cases')
