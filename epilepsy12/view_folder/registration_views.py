from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import Q

from epilepsy12.models.hospital_trust import HospitalTrust

from ..models import Registration
from ..models import Case


@login_required
def register(request, id):

    case = Case.objects.get(pk=id)
    try:
        # create a registration object
        registration, created = Registration.objects.get_or_create(case=case)
    except Exception as error:
        print(f'got or created exception {error}')
        registration = None

    if registration:
        registration_object = registration
        active_template = "unchosen"
    else:
        registration_object = created
        active_template = "none"

    context = {
        "registration": registration_object,
        "case_id": id,
        "initial_assessment_complete": False,
        "assessment_complete": False,
        "epilepsy_context_complete": False,
        "multiaxial_description_complete": False,
        "investigation_management_complete": False,
        "active_template": active_template
    }
    return render(request=request, template_name='epilepsy12/register.html', context=context)


# HTMX endpoints

@login_required
def registration_date(request, case_id):

    registration_date = date.today()
    case = Case.objects.get(pk=case_id)

    Registration.objects.update_or_create(
        registration_date=registration_date,
        case=case,
        initial_assessment_complete=False,
        assessment_complete=False,
        epilepsy_context_complete=False,
        multiaxial_description_complete=False,
        investigation_management_complete=False
    )
    registration = Registration.objects.filter(case=case).first()
    context = {
        'case_id': case_id,
        'registration': registration
    }
    return render(request=request, template_name='epilepsy12/partials/registration_dates.html', context=context)


@login_required
def lead_centre(request, registration_id):

    user_input = request.GET.get('lead_hospital')
    if user_input is not None:
        hospital_list = HospitalTrust.objects.filter(
            Q(OrganisationName__icontains=user_input)
        ).filter(Sector="NHS Sector").order_by('ParentName')
    else:
        hospital_list = HospitalTrust.objects.filter(
            Sector="NHS Sector").order_by('ParentName')

    registration = Registration.objects.get(pk=registration_id)
    if registration.lead_hospital:
        selected_lead_hospital = registration.lead_hospital
    else:
        selected_lead_hospital = request.user.hospital_trust

    context = {
        'hospital_list': hospital_list,
        'selected_lead_hospital': selected_lead_hospital,
        'registration_id': registration_id
    }

    return render(request=request, template_name='epilepsy12/partials/hospital_list_select.html', context=context)


@login_required
def hospital_trust_select(request, registration_id):
    Registration.objects.update_or_create(pk=registration_id, defaults={
        'lead_hospital': request.POST.get('hospital_trust')
    })
    hospital_list = hospital_list = HospitalTrust.objects.filter(
        Sector="NHS Sector").order_by('ParentName')
    context = {
        'hospital_list': hospital_list,
        'selected_lead_hospital': request.POST.get('hospital_trust'),
        'registration_id': registration_id
    }
    return HttpResponse("success")


@login_required
def confirm_eligible(request, registration_id):
    context = {
        'has_error': False,
        'message': 'Eligibility Criteria Confirmed.'
    }
    try:
        Registration.objects.update_or_create(pk=registration_id, defaults={
            'eligibility_criteria_met': True
        })
    except Exception as error:
        context = {
            'has_error': True,
            'message': error
        }

    response = render(
        request=request, template_name='epilepsy12/partials/is_eligible_label.html', context=context)

    return response
