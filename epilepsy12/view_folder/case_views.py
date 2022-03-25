from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from epilepsy12.forms import CaseForm
from epilepsy12.models.registration import Registration
from ..models import Case
from django.contrib import messages


@login_required
def case_list(request):
    case_list = Case.objects.all().order_by('surname')
    registered_cases = Registration.objects.all().count()
    case_count = Case.objects.all().count()
    context = {
        'case_list': case_list,
        'total_cases': case_count,
        'total_registrations': registered_cases
    }
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
            messages.success(request, "You successfully updated the post")
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
