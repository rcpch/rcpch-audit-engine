from curses.ascii import HT
from random import choices
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from epilepsy12.constants.causes import EPILEPSY_GENE_DEFECTS, EPILEPSY_GENETIC_CAUSE_TYPES, EPILEPSY_STRUCTURAL_CAUSE_TYPES, IMMUNE_CAUSES, METABOLIC_CAUSES
from epilepsy12.constants.epilepsy_types import EPIL_TYPE_CHOICES
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE
from epilepsy12.forms_folder import multiaxial_description_form
from epilepsy12.forms_folder.multiaxial_description_form import MultiaxialDescriptionForm

from epilepsy12.models import desscribe
from ..general_functions import fuzzy_scan_for_keywords

from epilepsy12.models.desscribe import DESSCRIBE
from epilepsy12.models.keyword import Keyword
from ..forms_folder import DescriptionForm

from epilepsy12.models.case import Case

from ..models import Registration
from ..general_functions import *


@login_required
def edit_description(request, desscribe_id):
    """
    This function is triggered by an htmx post request from the partials/description.html form for the desscribe description.
    This component comprises the input free text describing a seizure episode and labels for each of the keywords identified.
    The htmx post request is triggered on every key up.
    This function returns html to the browser.
    TODO #33 implement 5000 character cut off
    """

    description = request.POST.get('description')

    keywords = Keyword.objects.all()
    matched_keywords = fuzzy_scan_for_keywords(description, keywords)

    update_field = {
        'description': description,
        'description_keywords': matched_keywords
    }

    DESSCRIBE.objects.update_or_create(
        id=desscribe_id, defaults=update_field)
    desscribe = DESSCRIBE.objects.get(id=desscribe_id)

    stem = f"<div class='ui field'><label>{len(description)} characters</label></div>"
    for index, keyword in enumerate(desscribe.description_keywords):
        url = reverse('delete_description_keyword', kwargs={
                      'desscribe_id': desscribe_id, 'description_keyword_id': index})
        stem += f"<div class='ui blue label' style='margin: 5px;'>{keyword}<i class='icon close' hx-post='{url}' hx-target='#description_results' hx-trigger='click' hx-swap='innerHTML'></i></div>"

    return HttpResponse(stem)


@login_required
def delete_description_keyword(request, desscribe_id, description_keyword_id):
    """
    This function is triggered by an htmx post request from the partials/description.html form for the desscribe description_keyword.
    This component comprises the input free text describing a seizure episode and labels for each of the keywords identified.
    The htmx post request is triggered on click of a keyword. It removes that keyword from the saved list.
    This function returns html to the browser.
    """
    description_keyword_list = DESSCRIBE.objects.filter(
        id=desscribe_id).values('description_keywords')
    description_keywords = description_keyword_list[0]['description_keywords']
    del description_keywords[description_keyword_id]

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        description_keywords=description_keywords)
    desscribe = DESSCRIBE.objects.get(id=desscribe_id)

    stem = f"<div class='ui field'><label>{len(desscribe.description)} characters</label></div>"
    for index, keyword in enumerate(desscribe.description_keywords):
        url = reverse('delete_description_keyword', kwargs={
                      'desscribe_id': desscribe_id, 'description_keyword_id': index})
        stem += f"<div class='ui blue label' style='margin: 5px;'>{keyword}<i class='icon close' hx-post='{url}' hx-target='#description_results' hx-trigger='click' hx-swap='innerHTML'></i></div>"
    return HttpResponse(stem)


@login_required
def seizure_cause_main(request, desscribe_id):

    selection = request.POST.get('seizure_cause_main')

    added_select = []

    if selection == 'Met':
        select_list = METABOLIC_CAUSES
    if selection == 'Str':
        select_list = EPILEPSY_STRUCTURAL_CAUSE_TYPES
    elif selection == 'Gen':
        select_list = EPILEPSY_GENETIC_CAUSE_TYPES
        added_select = EPILEPSY_GENE_DEFECTS
    elif selection == 'Imm':
        select_list = IMMUNE_CAUSES
    elif selection == 'NK':
        select_list = []
    else:
        # inf - this is a text input
        return

    context = {
        'select_list': select_list,
        'added_select': added_select
    }

    return render(request, 'epilepsy12/partials/seizure_cause_select.html', context)


@login_required
def epilepsy_or_nonepilepsy_status_changed(request, desscribe_id):
    """
    Function triggered by a change in the epilepsy_or_nonepilepsy_status_changed dropdown leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    """
    if request.POST:
        epilepsy_or_nonepilepsy_status = request.POST.get(
            'epilepsy_or_nonepilepsy_status')
        DESSCRIBE.objects.filter(pk=desscribe_id).update(
            epilepsy_or_nonepilepsy_status=epilepsy_or_nonepilepsy_status
        )

    template = ""
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    if epilepsy_or_nonepilepsy_status == 'E':

        selection = desscribe.epileptic_seizure_onset_type[0]
        # return epilepsy dropdowns
        template = 'epilepsy12/partials/epilepsy_dropdowns.html'
        context = {
            'epilepsy_onset_types': EPILEPSY_SEIZURE_TYPE,
            'desscribe_id': desscribe_id
        }
    elif epilepsy_or_nonepilepsy_status == "NE":
        # return nonepilepsy dropdowns
        template = 'epilepsy12/partials/nonepilepsy_dropdowns.html'
        context = {
            'nonepilepsy_generalised_onset_types': NON_EPILEPSY_SEIZURE_ONSET,
            'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_TYPE
        }
    else:
        # not known
        context = {

        }
        template = None

    return render(request, template, context)


@login_required
def epilepsy_onset_changed(request, desscribe_id):
    """
    Function triggered by a change in the epilepsy_onset dropdown leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    """
    epilepsy_onset = request.POST.get('epilepsy_onset_changed')
    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        epileptic_seizure_onset_type=epilepsy_onset)
    if epilepsy_onset == 'FO':
        template = "epilepsy12/partials/focal_onset_epilepsy.html"
        desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
        # multiaxial_description_form = MultiaxialDescriptionForm(
        #     instance=desscribe)
        context = {
            # 'multiaxial_description_form': multiaxial_description_form,
            'desscribe': desscribe
        }
    elif epilepsy_onset == 'GO':
        desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
        context = {
            'desscribe': desscribe
        }
        template = "epilepsy12/partials/generalised_onset_epilepsy.html"
    return render(request, template, context)


@login_required
def focal_onset_epilepsy_checked_changed(request, desscribe_id):
    """
    Function triggered by a change in any checkbox/toggle in the focal_onset_epilepsy template leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    """
    focal_fields = ('focal_onset_atonic', 'focal_onset_clonic', 'focal_onset_left', 'focal_onset_right', 'focal_onset_epileptic_spasms', 'focal_onset_hyperkinetic', 'focal_onset_myoclonic', 'focal_onset_tonic', 'focal_onset_focal_to_bilateral_tonic_clonic', 'focal_onset_automatisms', 'focal_onset_impaired_awareness',
                    'focal_onset_gelastic', 'focal_onset_autonomic', 'focal_onset_behavioural_arrest', 'focal_onset_cognitive', 'focal_onset_emotional', 'focal_onset_sensory', 'focal_onset_centrotemporal', 'focal_onset_temporal', 'focal_onset_frontal', 'focal_onset_parietal', 'focal_onset_occipital',)

    update_fields = {}
    for item in focal_fields:
        if item in request.POST:
            update_fields.update({
                item: True
            })
        else:
            update_fields.update({
                item: False
            })

    DESSCRIBE.objects.filter(pk=desscribe_id).update(**update_fields)

    return HttpResponse("Saved!")


@ login_required
def multiaxial_description(request, case_id):
    case = Case.objects.get(pk=case_id)
    registration = Registration.objects.filter(case=case_id).first()
    if DESSCRIBE.objects.filter(registration=registration).exists():
        # there is already a desscribe object for this registration
        desscribe = DESSCRIBE.objects.filter(registration=registration).first()
    else:
        # this is not yet a desscribe object for this description - create one
        desscribe = DESSCRIBE.objects.create(registration=registration)

    multiaxial_description_form = MultiaxialDescriptionForm(instance=desscribe)
    description_form = DescriptionForm(instance=desscribe)

    # epilepsy_or_nonepilepsy_status_form = EpilepsyOrNonEpilepsyStatusForm(instance=desscribe)
    # if request.method == "POST":
    #     if form.is_valid():
    #         obj = form.save(commit=False)
    #         registration = Registration.objects.filter(case=id)
    #         obj.registration = registration
    #         obj.save()
    #         return redirect('cases')
    #     else:
    #         print('not valid')
    choices = Keyword.objects.all()

    context = {
        "desscribe": desscribe,
        "registration": registration,
        "description_form": description_form,
        "multiaxial_description_form": multiaxial_description_form,
        # "epilepsy_or_nonepilepsy_status_form": epilepsy_or_nonepilepsy_status_form,
        "choices": choices,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "multiaxial_description"
    }

    return render(request=request, template_name='epilepsy12/multiaxial_description.html', context=context)


@ login_required
def update_multiaxial_description(request, case_id):
    # multiaxial_description_form = MultiaxialDescriptionForm.objects.filter(
    #     registration__case=id).first()
    registration = Registration.objects.filter(case=case_id).first()
    # form = MultiaxialDescriptionForm(instance=multiaxial_description_form)
    desscribe = DESSCRIBE.objects.filter(registration=registration).first()

    if request.method == "POST":
        if ('delete') in request.POST:
            # multiaxial_description.delete()
            return redirect('cases')
        # form = MultiaxialDescriptionForm(request.POST, instance=)
        # if form.is_valid:
        #     obj = form.save()
        #     obj.save()
        #     # messages.success(request, "You successfully updated the post")
        #     return redirect('cases')

    case = Case.objects.get(id=case_id)

    context = {
        "desscribe": desscribe,
        # "form": form,
        "case_id": case_id,
        "case_name": case.first_name + " " + case.surname,
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "multiaxial_description"
    }

    return render(request=request, template_name='epilepsy12/multiaxial_description.html', context=context)


@ login_required
def delete_multiaxial_description(request, id):
    # multiaxial_description = get_object_or_404(
    #     MultiaxialDescriptionForm, id=id)
    # multiaxial_description.delete()
    return redirect('cases')
