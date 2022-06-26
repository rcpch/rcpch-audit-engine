from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from epilepsy12.forms import CaseForm
from epilepsy12.models import hospital_trust
from epilepsy12.models.registration import Registration
from epilepsy12.models.hospital_trust import HospitalTrust
from epilepsy12.view_folder.registration_views import register
from ..models import Case
from django.contrib import messages
from ..general_functions import fetch_snomed
from django.core.paginator import Paginator


@login_required
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
    filter_term = request.GET.get('filtered_case_list')
    if filter_term:
        all_cases = Case.objects.filter(
            Q(first_name__icontains=filter_term) |
            Q(surname__icontains=filter_term) |
            Q(nhs_number__icontains=filter_term)
        ).order_by('surname').all()
    else:
        all_cases = Case.objects.all().order_by('surname').all()

    registered_cases = Registration.objects.filter(
        lead_hospital=request.user.hospital_trust)


#     fetch_snomed(365456003, 'descendentSelfOf')

    case_list = Case.objects.all().order_by('surname')

    paginator = Paginator(all_cases, 10)
    page_number = request.GET.get('page', 1)
    case_list = paginator.page(page_number)

    case_count = Case.objects.all().count()
    registered_count = registered_cases.count()
    context = {
        'case_list': case_list,
        'total_cases': case_count,
        'total_registrations': registered_count
    }
    if request.htmx:
        return render(request=request, template_name='epilepsy12/partials/case_table.html', context=context)

    template_name = 'epilepsy12/cases/cases.html'
    return render(request, template_name, context)


@login_required
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
def delete_case(request, id):
    case = get_object_or_404(Case, id=id)
    case.delete()
    return redirect('cases')
