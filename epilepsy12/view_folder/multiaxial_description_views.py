from curses.ascii import HT
from random import choices
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from epilepsy12.constants import comorbidities
from epilepsy12.constants.causes import AUTOANTIBODIES, EPILEPSY_GENE_DEFECTS, EPILEPSY_GENETIC_CAUSE_TYPES, EPILEPSY_STRUCTURAL_CAUSE_TYPES, IMMUNE_CAUSES, METABOLIC_CAUSES
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, EPIS_MISC, MIGRAINES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPTIC_SYNCOPES
from epilepsy12.forms_folder.multiaxial_description_form import MultiaxialDescriptionForm
from epilepsy12.models.comorbidity import Comorbidity

from ..general_functions import fuzzy_scan_for_keywords

from ..models import Registration, Keyword, DESSCRIBE, Case

from ..forms_folder import DescriptionForm
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

    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_main=selection)

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    added_select = []

    context = {}

    if selection == 'Met':
        select_list = METABOLIC_CAUSES
        currently_selected = desscribe.seizure_cause_metabolic
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected
        })
    elif selection == 'Str':
        select_list = EPILEPSY_STRUCTURAL_CAUSE_TYPES
        currently_selected = desscribe.seizure_cause_structural
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected,
        })
    elif selection == 'Gen':
        select_list = EPILEPSY_GENETIC_CAUSE_TYPES
        currently_selected = desscribe.seizure_cause_genetic
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected,
        })
    elif selection == 'Imm':
        select_list = IMMUNE_CAUSES
        currently_selected = desscribe.seizure_cause_immune
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected,
        })
    elif selection == 'Inf':
        context.update({
            'currently_selected': desscribe.seizure_cause_infectious
        })

    elif selection == 'NK':
        return HttpResponse("Not Known")
    else:
        # inf - this is a text input
        return HttpResponse("No Selection")

    context.update({
        'seizure_cause_main': selection,
        'desscribe_id': desscribe_id
    })

    return render(request, 'epilepsy12/partials/seizure_cause_main.html', context)


@login_required
def seizure_cause_main_choice(request, desscribe_id, seizure_cause_main):
    seizure_cause_main_choice = request.POST.get('seizure_cause_main_choice')

    if seizure_cause_main == 'Met':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_metabolic=seizure_cause_main_choice)

    elif seizure_cause_main == 'Str':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_structural=seizure_cause_main_choice)

    elif seizure_cause_main == 'Imm':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_immune=seizure_cause_main_choice)

        if seizure_cause_main_choice == "AnM":
            desscribe = DESSCRIBE.objects.get(id=desscribe_id)
            context = {
                'selected_autoantibody': desscribe.seizure_cause_immune_antibody,
                'selection': AUTOANTIBODIES,
                'desscribe_id': desscribe_id
            }
            # antibody mediated - offer antibodies select
            return render(request, "epilepsy12/partials/autoantibodies.html", context)
        else:
            return HttpResponse("Success")

    elif seizure_cause_main == 'Gen':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_genetic=seizure_cause_main_choice)
        desscribe = DESSCRIBE.objects.get(id=desscribe_id)
        context = {
            'desscribe_id': desscribe_id,
            'seizure_cause_main': seizure_cause_main,
            'selected_choice': seizure_cause_main_choice,
            'selection': EPILEPSY_GENE_DEFECTS,
            'selected_gene_defect': desscribe.seizure_cause_gene_abnormality
        }
        if seizure_cause_main_choice == "GeA":
            # gene abnormality selected
            return render(request, "epilepsy12/partials/gene_defect.html", context)
        else:
            return HttpResponse("Success")
    else:
        return HttpResponse('Error!')
    return HttpResponse("Selected")


@login_required
def seizure_cause_infectious(request, desscribe_id):
    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_infectious=request.POST.get('seizure_cause_infectious'))
    return HttpResponse("Success!")


@login_required
def seizure_cause_genetic_choice(request, desscribe_id):
    gene_abnormality = request.POST.get('seizure_cause_genetic_choice')
    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_gene_abnormality=gene_abnormality)
    return HttpResponse('Selected')


@login_required
def autoantibodies(request, desscribe_id):
    autoantibodies = request.POST.get('autoantibodies')
    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_immune_antibody=autoantibodies)
    return HttpResponse('Selected')


@login_required
def ribe(request, desscribe_id):
    toggle = request.POST.get('NE')
    if toggle == 'on':
        toggle = True
    else:
        toggle = False

    registration_field = DESSCRIBE.objects.filter(
        pk=desscribe_id).select_related('registration').first()

    registration = Registration.objects.filter(
        id=registration_field.id).first()
    case = registration.case
    comorbidities = Comorbidity.objects.filter(case=case)

    if comorbidities.count() > 0:
        toggle = True

    DESSCRIBE.objects.filter(id=desscribe_id).update(
        relevant_impairments_behavioural_educational=toggle)
    context = {
        'comorbidities': comorbidities,
        'case_id': case.id
    }
    return render(request, "epilepsy12/partials/ribe.html", context)


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
        desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    if epilepsy_or_nonepilepsy_status == 'E':

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
            'nonepilepsy_onset_types': NON_EPILEPSY_SEIZURE_TYPE,
            'desscribe': desscribe
        }
    else:
        # not known
        return HttpResponse("The diagnosis of epilepsy is uncertain.")

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


@login_required
def nonepilepsy_generalised_onset(request, desscribe_id):

    nonepilepsy_generalised_onset = request.POST.get(
        'nonepilepsy_generalised_onset')
    DESSCRIBE.objects.filter(id=desscribe_id).update(
        nonepileptic_seizure_unknown_onset=nonepilepsy_generalised_onset)
    desscribe = DESSCRIBE.objects.get(id=desscribe_id)
    if nonepilepsy_generalised_onset == "Oth":
        context = {
            'desscribe': desscribe
        }
        return render(request, 'epilepsy12/partials/nonepileptic_seizure_unknown_onset.html', context)
    else:
        return HttpResponse("")


@login_required
def nonepilepsy_generalised_onset_edit(request, desscribe_id):
    nonepilepsy_generalised_onset_edit_text = request.POST.get(
        'nonepilepsy_generalised_onset_edit')

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        nonepileptic_seizure_unknown_onset_other_details=nonepilepsy_generalised_onset_edit_text)
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
    return HttpResponse(desscribe.nonepileptic_seizure_unknown_onset_other_details)


@login_required
def nonepilepsy_subtypes(request, desscribe_id):
    """
    Function triggered by a change or load in the nonepilepsy subtype dropdown leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    """
    nonepilepsy_subtypes = request.POST.get('nonepilepsy_subtypes')

    # persist the result
    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        nonepileptic_seizure_type=nonepilepsy_subtypes)

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    return_list = []
    subtype = ""
    if nonepilepsy_subtypes == "SAS":
        return_list = NON_EPILEPTIC_SYNCOPES
        subtype = "syncope/anoxic seizure"
    if nonepilepsy_subtypes == "BPP":
        return_list = NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS
        subtype = "behavioural/psychological or psychiatric"
    if nonepilepsy_subtypes == "SRC":
        return_list = NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS
        subtype = "sleep-related"
    if nonepilepsy_subtypes == "PMD":
        return_list = NON_EPILEPSY_PAROXYSMS
        subtype = "paroxysmal movement disorder"
    if nonepilepsy_subtypes == "MAD":
        return_list = MIGRAINES
        subtype = "migraine"
    if nonepilepsy_subtypes == "ME":
        return_list = EPIS_MISC
        subtype = "miscellaneous"
    if nonepilepsy_subtypes == "Oth":
        return HttpResponse("Other")

    context = {
        'nonepilepsy_subtype_list': return_list,
        'nonepilepsy_selected_subtype': subtype,
        'nonepilepsy_selected_subtype_code': nonepilepsy_subtypes,
        'desscribe': desscribe
    }

    return render(request, 'epilepsy12/partials/nonepilepsy_subtypes.html', context)


@login_required
def nonepilepsy_subtype_selection(request, desscribe_id, nonepilepsy_selected_subtype_code):
    # POST request receiving selection of nonepilepsy subtype and persisting the result

    nonepilepsy_subtype_selection = request.POST.get(
        "nonepilepsy_subtype_selection")

    try:
        if nonepilepsy_selected_subtype_code == "SAS":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_syncope=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "BPP":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_behavioural=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "SRC":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_sleep=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "PMD":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_paroxysmal=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "MAD":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_migraine=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "ME":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_miscellaneous=nonepilepsy_subtype_selection)
        if nonepilepsy_selected_subtype_code == "Oth":
            DESSCRIBE.objects.filter(pk=desscribe_id).update(
                nonepileptic_seizure_other=nonepilepsy_subtype_selection)
    except Exception as error:
        return HttpResponse(error)
    else:
        return HttpResponse("Success")


@login_required
def syndrome_select(request, desscribe_id):
    syndrome_code = request.POST.get('syndrome')
    if syndrome_code:
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            syndrome=syndrome_code)
        return HttpResponse("Success!")
    else:
        return HttpResponse('No dice')


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
