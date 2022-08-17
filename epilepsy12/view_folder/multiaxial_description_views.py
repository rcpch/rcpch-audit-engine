from operator import itemgetter
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from epilepsy12.constants.causes import AUTOANTIBODIES, EPILEPSY_CAUSES, EPILEPSY_GENE_DEFECTS, EPILEPSY_GENETIC_CAUSE_TYPES, EPILEPSY_STRUCTURAL_CAUSE_TYPES, IMMUNE_CAUSES, METABOLIC_CAUSES
from epilepsy12.constants.semiology import EPILEPSY_SEIZURE_TYPE, EPIS_MISC, MIGRAINES, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, NON_EPILEPSY_PAROXYSMS, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPTIC_SYNCOPES
from epilepsy12.constants.syndromes import SYNDROMES
from epilepsy12.constants.epilepsy_types import EPIL_TYPE_CHOICES, EPILEPSY_DIAGNOSIS_STATUS, EPIS_TYPE
from epilepsy12.models import desscribe
from epilepsy12.models.comorbidity import Comorbidity

from ..general_functions import fuzzy_scan_for_keywords

from ..models import Registration, Keyword, DESSCRIBE

from ..general_functions import *

"""
DESSCRIBE Field lists and supporting functions
"""

FOCAL_EPILEPSY_FIELDS = [
    "experienced_prolonged_focal_seizures",
    "focal_onset_impaired_awareness",
    "focal_onset_automatisms",
    "focal_onset_atonic",
    "focal_onset_clonic",
    "focal_onset_left",
    "focal_onset_right",
    "focal_onset_epileptic_spasms",
    "focal_onset_hyperkinetic",
    "focal_onset_myoclonic",
    "focal_onset_tonic",
    "focal_onset_autonomic",
    "focal_onset_behavioural_arrest",
    "focal_onset_cognitive",
    "focal_onset_emotional",
    "focal_onset_sensory",
    "focal_onset_centrotemporal",
    "focal_onset_temporal",
    "focal_onset_frontal",
    "focal_onset_parietal",
    "focal_onset_occipital",
    "focal_onset_gelastic",
    "focal_onset_focal_to_bilateral_tonic_clonic",
    "focal_onset_other",
    "focal_onset_other_details"
]

GENERALISED_ONSET_EPILEPSY_FIELDS = [
    'prolonged_generalized_convulsive_seizures',
    "epileptic_generalised_onset",
    "epileptic_generalised_onset_other_details",
]

ONSET_NONEPILEPSY = [
    'nonepileptic_seizure_unknown_onset',
    'nonepileptic_seizure_unknown_onset_other_details',
    'nonepileptic_seizure_syncope',
    'nonepileptic_seizure_behavioural',
    'nonepileptic_seizure_sleep',
    'nonepileptic_seizure_paroxysmal',
    'nonepileptic_seizure_migraine',
    'nonepileptic_seizure_miscellaneous',
    'nonepileptic_seizure_other',
]

EPILEPSY_FIELDS = ['were_any_of_the_epileptic_seizures_convulsive'] + \
    FOCAL_EPILEPSY_FIELDS + GENERALISED_ONSET_EPILEPSY_FIELDS
NONEPILEPSY_FIELDS = ONSET_NONEPILEPSY

SEIZURE_CAUSE = [
    'syndrome',
    'seizure_cause_main',
    'seizure_cause_main_snomed_code',
    'seizure_cause_structural',
    'seizure_cause_structural_snomed_code',
    'seizure_cause_genetic',
    'seizure_cause_gene_abnormality',
    'seizure_cause_genetic_other',
    'seizure_cause_gene_abnormality_snomed_code',
    'seizure_cause_chromosomal_abnormality',
    'seizure_cause_infectious',
    'seizure_cause_infectious_snomed_code',
    'seizure_cause_metabolic',
    'seizure_cause_mitochondrial_sctid',
    'seizure_cause_metabolic_other',
    'seizure_cause_metabolic_snomed_code',
    'seizure_cause_immune',
    'seizure_cause_immune_antibody',
    'seizure_cause_immune_antibody_other',
    'seizure_cause_immune_snomed_code',
    'relevant_impairments_behavioural_educational'
]

focal_epilepsy_motor_manifestations = [
    {'name': 'focal_onset_atonic', 'text': "Atonic"},
    {'name': 'focal_onset_clonic', 'text': 'Clonic'},
    {'name': 'focal_onset_epileptic_spasms', 'text': 'Spasms'},
    {'name': 'focal_onset_hyperkinetic', 'text': 'Hyperkinetic'},
    {'name': 'focal_onset_myoclonic', 'text': 'Myoclonic'},
    {'name': 'focal_onset_tonic', 'text': 'Tonic'},
    {'name': 'focal_onset_focal_to_bilateral_tonic_clonic', 'text': 'Tonic-Clonic'},
]
focal_epilepsy_nonmotor_manifestations = [
    {'name': 'focal_onset_automatisms', 'text': 'Automatisms'},
    {'name': 'focal_onset_impaired_awareness', 'text': 'Impaired Awareness'},
    {'name': 'focal_onset_gelastic', 'text': 'Gelastic'},
    {'name': 'focal_onset_autonomic', 'text': 'Autonomic'},
    {'name': 'focal_onset_behavioural_arrest', 'text': 'Behavioural Arrest'},
    {'name': 'focal_onset_cognitive', 'text': 'Cognitive'},
    {'name': 'focal_onset_emotional', 'text': 'Emotional'},
    {'name': 'focal_onset_sensory', 'text': 'Sensory'}
]
focal_epilepsy_eeg_manifestations = [
    {'name': 'focal_onset_centrotemporal', 'text': 'Centrotemporal'},
    {'name': 'focal_onset_temporal', 'text': 'Temporal'},
    {'name': 'focal_onset_frontal', 'text': 'Frontal'},
    {'name': 'focal_onset_parietal', 'text': 'Parietal'},
    {'name': 'focal_onset_occipital', 'text': 'Occipital'},
]
laterality = [
    {'name': 'focal_onset_left', 'text': 'Left'},
    {'name': 'focal_onset_right', 'text': 'Right'}
]


def set_epilepsy_fields_to_none(desscribe_id):
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
    DESSCRIBE.objects.filter(registration=desscribe.registration).update(
        were_any_of_the_epileptic_seizures_convulsive=None,
        epileptic_seizure_onset_type=None,
        epileptic_generalised_onset=None,
        epileptic_generalised_onset_other_details=None,
        prolonged_generalized_convulsive_seizures=None,
        focal_onset_impaired_awareness=None,
        focal_onset_automatisms=None,
        focal_onset_atonic=None,
        focal_onset_clonic=None,
        focal_onset_left=None,
        focal_onset_right=None,
        focal_onset_epileptic_spasms=None,
        focal_onset_hyperkinetic=None,
        focal_onset_myoclonic=None,
        focal_onset_tonic=None,
        focal_onset_autonomic=None,
        focal_onset_behavioural_arrest=None,
        focal_onset_cognitive=None,
        focal_onset_emotional=None,
        focal_onset_sensory=None,
        focal_onset_centrotemporal=None,
        focal_onset_temporal=None,
        focal_onset_frontal=None,
        focal_onset_parietal=None,
        focal_onset_occipital=None,
        focal_onset_gelastic=None,
        focal_onset_focal_to_bilateral_tonic_clonic=None,
        focal_onset_other=None,
        focal_onset_other_details=None
    )
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)


def set_all_nonepilepsy_fields_to_none(desscribe_id: int):
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
    DESSCRIBE.objects.filter(registration=desscribe.registration).update(
        nonepileptic_seizure_unknown_onset=None,
        nonepileptic_seizure_unknown_onset_other_details=None,
        nonepileptic_seizure_syncope=None,
        nonepileptic_seizure_behavioural=None,
        nonepileptic_seizure_sleep=None,
        nonepileptic_seizure_paroxysmal=None,
        nonepileptic_seizure_migraine=None,
        nonepileptic_seizure_miscellaneous=None,
        nonepileptic_seizure_other=None
    )


@login_required
def edit_description(request, desscribe_id):
    """
    This function is triggered by an htmx post request from the partials/desscribe/description.html form for the desscribe description.
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
    if (len(description) <= 5000):
        DESSCRIBE.objects.update_or_create(
            id=desscribe_id, defaults=update_field)
    desscribe = DESSCRIBE.objects.get(id=desscribe_id)

    context = {
        'desscribe': desscribe
    }

    return render(request, 'epilepsy12/partials/desscribe/description_labels.html', context)


@login_required
def delete_description_keyword(request, desscribe_id, description_keyword_id):
    """
    This function is triggered by an htmx post request from the partials/desscribe/description.html form for the desscribe description_keyword.
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

    context = {
        'desscribe': desscribe
    }

    return render(request, 'epilepsy12/partials/desscribe/description_labels.html', context)

# epilepsy onset


@login_required
def epilepsy_or_nonepilepsy_status(request, desscribe_id):
    """
    Function triggered by a click in the epilepsy_or_nonepilepsy_status partial leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    Selections for epilepsy set all nonepilepsy related fields to None, and selections for
    nonepilepsy set all epilepsy fields to None. Selections to not known set all 
    selections to none. The epilepsy_or_nonepilepsy_status partial is returned.
    """
    epilepsy_or_nonepilepsy_status = request.htmx.trigger_name

    if epilepsy_or_nonepilepsy_status == 'E':
        # epilepsy selected - set all nonepilepsy to none
        set_epilepsy_fields_to_none(desscribe_id=desscribe_id)
    elif epilepsy_or_nonepilepsy_status == 'NE':
        # nonepilepsy selected - set all epilepsy to none
        set_all_nonepilepsy_fields_to_none(desscribe_id=desscribe_id)
    elif epilepsy_or_nonepilepsy_status == 'NK':
        # notknown selected - set all epilepsy and nonepilepsy to none
        set_epilepsy_fields_to_none(desscribe_id=desscribe_id)
        set_all_nonepilepsy_fields_to_none(desscribe_id=desscribe_id)

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        epilepsy_or_nonepilepsy_status=epilepsy_or_nonepilepsy_status
    )
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    template = 'epilepsy12/partials/desscribe/epilepsy_or_nonepilepsy_status.html'
    context = {
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'nonepilepsy_onset_types': sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
        'desscribe': desscribe
    }

    return render(request, template, context)


@login_required
def were_any_of_the_epileptic_seizures_convulsive(request, desscribe_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    if request.htmx.trigger_name == 'button-true':
        were_any_of_the_epileptic_seizures_convulsive = True
    elif request.htmx.trigger_name == 'button-false':
        were_any_of_the_epileptic_seizures_convulsive = False
    else:
        were_any_of_the_epileptic_seizures_convulsive = None

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        were_any_of_the_epileptic_seizures_convulsive=were_any_of_the_epileptic_seizures_convulsive
    )

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {
        'desscribe': desscribe,
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
    }

    return render(request=request, template_name='epilepsy12/partials/desscribe/epilepsy.html', context=context)


@login_required
def prolonged_generalized_convulsive_seizures(request, desscribe_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    if request.htmx.trigger_name == 'button-true':
        prolonged_generalized_convulsive_seizures = True
    elif request.htmx.trigger_name == 'button-false':
        prolonged_generalized_convulsive_seizures = False
    else:
        prolonged_generalized_convulsive_seizures = None

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        prolonged_generalized_convulsive_seizures=prolonged_generalized_convulsive_seizures
    )

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {
        'desscribe': desscribe
    }

    return render(request=request, template_name='epilepsy12/partials/desscribe/generalised_onset_epilepsy.html', context=context)


@login_required
def epileptic_seizure_onset_type(request, desscribe_id):
    """
    Defines type of onset if considered to be epilepsy
    Accepts POST request from epilepsy partial and returns the same having
    updated the model with the selection
    If focal onset, sent general onset fields to none, or both 
    to none if not known
    """
    epileptic_seizure_onset_type = request.htmx.trigger_name

    update_fields = {}
    if epileptic_seizure_onset_type == "FO":
        # focal onset - set all generalised onset fields to none
        for field in GENERALISED_ONSET_EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })
    elif epileptic_seizure_onset_type == "GO":
        # generalised onset - set focal onset fields to none
        for field in FOCAL_EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })
    else:
        # unknown or unclassified onset. Set all to none
        for field in EPILEPSY_FIELDS:
            update_fields.update({
                field: None
            })

    # update the fields object to include latest selection
    update_fields.update({
        'epileptic_seizure_onset_type': epileptic_seizure_onset_type
    })

    # update the model
    DESSCRIBE.objects.filter(pk=desscribe_id).update(**update_fields)

    # retrieve updated object instance
    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {
        'desscribe': desscribe,
        'epileptic_seizure_onset_types': sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
    }

    return render(request=request, template_name='epilepsy12/partials/desscribe/epilepsy.html', context=context)


@login_required
def focal_onset_epilepsy_checked_changed(request, desscribe_id):
    """
    Function triggered by a change in any checkbox/toggle in the focal_onset_epilepsy template leading to a post request.
    The desscribe_id is also passed in allowing update of the model.
    The id of the radio button clicked holds the name of the field in the desscribe model to update
    the name of the radiobutton group clicked holds the name of the list from which to select model fields to update
    """

    if request.htmx.trigger_name == 'focal_epilepsy_motor_manifestations':
        focal_fields = focal_epilepsy_motor_manifestations
    elif request.htmx.trigger_name == 'focal_epilepsy_nonmotor_manifestations':
        focal_fields = focal_epilepsy_nonmotor_manifestations
    elif request.htmx.trigger_name == 'focal_epilepsy_eeg_manifestations':
        focal_fields = focal_epilepsy_eeg_manifestations
    elif request.htmx.trigger_name == 'laterality':
        focal_fields = laterality
    else:
        # TODO this is an error that needs handling
        focal_fields = ()

    update_fields = {}
    for item in focal_fields:
        if request.htmx.trigger == item.get('name'):
            update_fields.update({
                item.get('name'): True
            })
        else:
            update_fields.update({
                item.get('name'): False
            })

    DESSCRIBE.objects.filter(pk=desscribe_id).update(**update_fields)

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {
        'desscribe': desscribe,
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
    }

    return render(request=request, template_name="epilepsy12/partials/desscribe/focal_onset_epilepsy.html", context=context)


@login_required
def experienced_prolonged_focal_seizures(request, desscribe_id):
    """
    Post request from multiple choice toggle within epilepsy partial.
    Updates the model and returns the epilepsy partial and parameters
    """

    if request.htmx.trigger_name == 'button-true':
        experienced_prolonged_focal_seizures = True
    elif request.htmx.trigger_name == 'button-false':
        experienced_prolonged_focal_seizures = False
    else:
        experienced_prolonged_focal_seizures = None

    DESSCRIBE.objects.filter(pk=desscribe_id).update(
        experienced_prolonged_focal_seizures=experienced_prolonged_focal_seizures
    )

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {
        'desscribe': desscribe,
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
    }

    return render(request=request, template_name="epilepsy12/partials/desscribe/focal_onset_epilepsy.html", context=context)


@login_required
def seizure_cause_main(request, desscribe_id):

    selection = request.POST.get('seizure_cause_main')

    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_main=selection)

    desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

    context = {}

    if selection == 'Met':
        select_list = sorted(METABOLIC_CAUSES, key=itemgetter(1))
        currently_selected = desscribe.seizure_cause_metabolic

        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected
        })
    elif selection == 'Str':
        select_list = sorted(
            EPILEPSY_STRUCTURAL_CAUSE_TYPES, key=itemgetter(1))
        currently_selected = desscribe.seizure_cause_structural
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected,
        })
    elif selection == 'Gen':
        select_list = sorted(EPILEPSY_GENETIC_CAUSE_TYPES, key=itemgetter(1))
        currently_selected = desscribe.seizure_cause_genetic
        context.update({
            'select_list': select_list,
            'currently_selected': currently_selected,
        })
    elif selection == 'Imm':
        select_list = sorted(IMMUNE_CAUSES, key=itemgetter(1))
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

    return render(request, 'epilepsy12/partials/desscribe/seizure_cause_main.html', context)


@login_required
def seizure_cause_main_choice(request, desscribe_id, seizure_cause_main):
    seizure_cause_main_choice = request.POST.get('seizure_cause_main_choice')

    if seizure_cause_main == 'Met':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_metabolic=seizure_cause_main_choice,
            seizure_cause_immune=None,
            seizure_cause_immune_antibody=None,
            seizure_cause_immune_antibody_other=None,
            seizure_cause_immune_snomed_code=None,
            seizure_cause_infectious=None,
            seizure_cause_infectious_snomed_code=None,
            seizure_cause_gene_abnormality_snomed_code=None,
            seizure_cause_genetic_other=None,
            seizure_cause_gene_abnormality=None,
            seizure_cause_genetic=None,
            seizure_cause_chromosomal_abnormality=None,
            seizure_cause_structural=None,
            seizure_cause_structural_snomed_code=None
        )
        desscribe = DESSCRIBE.objects.get(id=desscribe_id)

        if seizure_cause_main_choice == "Mit":
            mitochondrial_selection = fetch_snomed(
                sctid=240096000, syntax='childSelfOf')

            if desscribe.seizure_cause_mitochondrial_sctid:
                seizure_cause_mitochondrial_sctid = int(
                    desscribe.seizure_cause_mitochondrial_sctid)
            else:
                seizure_cause_mitochondrial_sctid = None

            context = {
                'mitochondrial_selection': mitochondrial_selection,
                'desscribe_id': desscribe_id,
                'seizure_cause_mitochondrial_sctid': seizure_cause_mitochondrial_sctid
            }
            return render(request, 'epilepsy12/partials/desscribe/mitochondrial_selection_dropdown.html', context)

    elif seizure_cause_main == 'Str':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_structural=seizure_cause_main_choice,
            seizure_cause_immune=None,
            seizure_cause_immune_antibody=None,
            seizure_cause_immune_antibody_other=None,
            seizure_cause_immune_snomed_code=None,
            seizure_cause_infectious=None,
            seizure_cause_infectious_snomed_code=None,
            seizure_cause_gene_abnormality_snomed_code=None,
            seizure_cause_genetic_other=None,
            seizure_cause_gene_abnormality=None,
            seizure_cause_genetic=None,
            seizure_cause_chromosomal_abnormality=None,
            seizure_cause_metabolic=None,
            seizure_cause_mitochondrial_sctid=None,
            seizure_cause_metabolic_other=None,
            seizure_cause_metabolic_snomed_code=None
        )

    elif seizure_cause_main == 'Imm':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_immune=seizure_cause_main_choice,
            seizure_cause_infectious=None,
            seizure_cause_infectious_snomed_code=None,
            seizure_cause_gene_abnormality_snomed_code=None,
            seizure_cause_genetic_other=None,
            seizure_cause_gene_abnormality=None,
            seizure_cause_genetic=None,
            seizure_cause_chromosomal_abnormality=None,
            seizure_cause_metabolic=None,
            seizure_cause_mitochondrial_sctid=None,
            seizure_cause_metabolic_other=None,
            seizure_cause_metabolic_snomed_code=None,
            seizure_cause_structural=None,
            seizure_cause_structural_snomed_code=None
        )

        if seizure_cause_main_choice == "AnM":
            desscribe = DESSCRIBE.objects.get(id=desscribe_id)
            context = {
                'selected_autoantibody': desscribe.seizure_cause_immune_antibody,
                'selection': sorted(AUTOANTIBODIES, key=itemgetter(1)),
                'desscribe_id': desscribe_id
            }
            # antibody mediated - offer antibodies select
            return render(request, "epilepsy12/partials/desscribe/autoantibodies.html", context)
        else:
            return HttpResponse("Success")

    elif seizure_cause_main == 'Gen':
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            seizure_cause_genetic=seizure_cause_main_choice,
            seizure_cause_immune=None,
            seizure_cause_immune_antibody=None,
            seizure_cause_immune_antibody_other=None,
            seizure_cause_immune_snomed_code=None,
            seizure_cause_infectious=None,
            seizure_cause_infectious_snomed_code=None,
            seizure_cause_metabolic=None,
            seizure_cause_mitochondrial_sctid=None,
            seizure_cause_metabolic_other=None,
            seizure_cause_metabolic_snomed_code=None,
            seizure_cause_structural=None,
            seizure_cause_structural_snomed_code=None
        )
        desscribe = DESSCRIBE.objects.get(id=desscribe_id)
        context = {
            'desscribe_id': desscribe_id,
            'seizure_cause_main': seizure_cause_main,
            'selected_choice': seizure_cause_main_choice,
            'selection': sorted(EPILEPSY_GENE_DEFECTS, key=itemgetter(1)),
            'selected_gene_defect': desscribe.seizure_cause_gene_abnormality
        }
        if seizure_cause_main_choice == "GeA":
            # gene abnormality selected
            return render(request, "epilepsy12/partials/desscribe/gene_defect.html", context)
        else:
            return HttpResponse("Success")
    else:
        return HttpResponse('Error!')
    return HttpResponse("Selected")


@login_required
def mitochondrial(request, desscribe_id):
    mitochondrial_type_sctid = request.POST.get('mitochondrial_type')
    DESSCRIBE.objects.filter(id=desscribe_id).update(
        seizure_cause_mitochondrial_sctid=mitochondrial_type_sctid)
    return HttpResponse("Saved Mitochondrial")


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

    toggle = request.POST.get('ribe')

    if toggle == 'on':
        toggle = True
    else:
        toggle = False

    desscribe = DESSCRIBE.objects.get(
        pk=desscribe_id)

    registration = desscribe.registration
    case = registration.case
    comorbidities = Comorbidity.objects.filter(case=case)

    if comorbidities.count() > 0:
        toggle = True

    DESSCRIBE.objects.filter(id=desscribe_id).update(
        relevant_impairments_behavioural_educational=toggle)

    updated_desscribe = DESSCRIBE.objects.get(
        pk=desscribe_id)

    context = {
        'desscribe': updated_desscribe,
        'comorbidities': comorbidities,
        'case_id': case.id
    }

    return render(request, "epilepsy12/partials/desscribe/ribe.html", context)


# @login_required
# def epilepsy_onset_changed(request, desscribe_id):
#     """
#     Function triggered by a change in the epilepsy_onset dropdown leading to a post request.
#     The desscribe_id is also passed in allowing update of the model.
#     """
#     epilepsy_onset = request.POST.get('epilepsy_onset_changed')
#     DESSCRIBE.objects.filter(pk=desscribe_id).update(
#         epileptic_seizure_onset_type=epilepsy_onset)
#     if epilepsy_onset == 'FO':
#         template = "epilepsy12/partials/desscribe/focal_onset_epilepsy.html"
#         desscribe = DESSCRIBE.objects.get(pk=desscribe_id)


#         context = {
#             'desscribe': desscribe,
#             'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
#             'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
#             'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations
#         }
#     elif epilepsy_onset == 'GO':
#         desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
#         context = {
#             'desscribe': desscribe
#         }
#         template = "epilepsy12/partials/desscribe/generalised_onset_epilepsy.html"
#     return render(request, template, context)


# @login_required
# def nonepilepsy_generalised_onset(request, desscribe_id):

#     nonepilepsy_generalised_onset = request.POST.get(
#         'nonepilepsy_generalised_onset')
#     DESSCRIBE.objects.filter(id=desscribe_id).update(
#         nonepileptic_seizure_unknown_onset=nonepilepsy_generalised_onset)
#     desscribe = DESSCRIBE.objects.get(id=desscribe_id)
#     if nonepilepsy_generalised_onset == "Oth":
#         context = {
#             'desscribe': desscribe
#         }
#         return render(request, 'epilepsy12/partials/desscribe/nonepileptic_seizure_unknown_onset.html', context)
#     else:
#         return HttpResponse("")


# @login_required
# def nonepilepsy_generalised_onset_edit(request, desscribe_id):
#     nonepilepsy_generalised_onset_edit_text = request.POST.get(
#         'nonepilepsy_generalised_onset_edit')

#     DESSCRIBE.objects.filter(pk=desscribe_id).update(
#         nonepileptic_seizure_unknown_onset_other_details=nonepilepsy_generalised_onset_edit_text)
#     desscribe = DESSCRIBE.objects.get(pk=desscribe_id)
#     return HttpResponse(desscribe.nonepileptic_seizure_unknown_onset_other_details)


# @login_required
# def nonepilepsy_subtypes(request, desscribe_id):
#     """
#     Function triggered by a change or load in the nonepilepsy subtype dropdown leading to a post request.
#     The desscribe_id is also passed in allowing update of the model.
#     """
#     nonepilepsy_subtypes = request.POST.get('nonepilepsy_subtypes')

#     # persist the result
#     DESSCRIBE.objects.filter(pk=desscribe_id).update(
#         nonepileptic_seizure_type=nonepilepsy_subtypes)

#     desscribe = DESSCRIBE.objects.get(pk=desscribe_id)

#     return_list = []
#     subtype = ""
#     if nonepilepsy_subtypes == "SAS":
#         return_list = sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1))
#         subtype = "syncope/anoxic seizure"
#     if nonepilepsy_subtypes == "BPP":
#         return_list = sorted(
#             NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1))
#         subtype = "behavioural/psychological or psychiatric"
#     if nonepilepsy_subtypes == "SRC":
#         return_list = sorted(
#             NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1))
#         subtype = "sleep-related"
#     if nonepilepsy_subtypes == "PMD":
#         return_list = sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1))
#         subtype = "paroxysmal movement disorder"
#     if nonepilepsy_subtypes == "MAD":
#         return_list = sorted(MIGRAINES, key=itemgetter(1))
#         subtype = "migraine"
#     if nonepilepsy_subtypes == "ME":
#         return_list = sorted(EPIS_MISC, key=itemgetter(1))
#         subtype = "miscellaneous"
#     if nonepilepsy_subtypes == "Oth":
#         return HttpResponse("Other")

#     context = {
#         'nonepilepsy_subtype_list': return_list,
#         'nonepilepsy_selected_subtype': subtype,
#         'nonepilepsy_selected_subtype_code': nonepilepsy_subtypes,
#         'desscribe': desscribe
#     }

#     return render(request, 'epilepsy12/partials/desscribe/nonepilepsy_dropdowns.html', context)


# @login_required
# def nonepilepsy_subtype_selection(request, desscribe_id, nonepilepsy_selected_subtype_code):
#     # POST request receiving selection of nonepilepsy subtype and persisting the result

#     nonepilepsy_subtype_selection = request.POST.get(
#         "nonepilepsy_subtype_selection")

#     try:
#         if nonepilepsy_selected_subtype_code == "SAS":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_syncope=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "BPP":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_behavioural=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "SRC":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_sleep=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "PMD":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_paroxysmal=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "MAD":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_migraine=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "ME":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_miscellaneous=nonepilepsy_subtype_selection)
#         if nonepilepsy_selected_subtype_code == "Oth":
#             DESSCRIBE.objects.filter(pk=desscribe_id).update(
#                 nonepileptic_seizure_other=nonepilepsy_subtype_selection)
#     except Exception as error:
#         return HttpResponse(error)
#     else:
#         return HttpResponse("Success")


@login_required
def syndrome_select(request, desscribe_id):
    syndrome_code = request.POST.get('syndrome_select')

    if syndrome_code:
        DESSCRIBE.objects.filter(id=desscribe_id).update(
            syndrome=syndrome_code)
        return HttpResponse("Success!")
    else:
        return HttpResponse('No dice')


@ login_required
def multiaxial_description(request, case_id):

    registration = Registration.objects.filter(case=case_id).first()
    if DESSCRIBE.objects.filter(registration=registration).exists():
        # there is already a desscribe object for this registration
        desscribe = DESSCRIBE.objects.filter(registration=registration).first()
    else:
        # this is not yet a desscribe object for this description - create one
        desscribe = DESSCRIBE.objects.create(registration=registration)

    choices = Keyword.objects.all()

    context = {
        "desscribe": desscribe,
        "registration": registration,
        "choices": choices,
        "case_id": case_id,
        "epilepsy_or_nonepilepsy_status_choices": sorted(EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)),
        "epileptic_seizure_onset_types": sorted(EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        'laterality': laterality,
        'focal_epilepsy_motor_manifestations': focal_epilepsy_motor_manifestations,
        'focal_epilepsy_nonmotor_manifestations': focal_epilepsy_nonmotor_manifestations,
        'focal_epilepsy_eeg_manifestations': focal_epilepsy_eeg_manifestations,
        "syndrome_selection": sorted(SYNDROMES, key=itemgetter(1)),
        "seizure_cause_selection": sorted(EPILEPSY_CAUSES, key=itemgetter(1)),
        "initial_assessment_complete": registration.initial_assessment_complete,
        "assessment_complete": registration.assessment_complete,
        "epilepsy_context_complete": registration.epilepsy_context_complete,
        "multiaxial_description_complete": registration.multiaxial_description_complete,
        "investigation_management_complete": registration.investigation_management_complete,
        "active_template": "multiaxial_description"
    }

    return render(request=request, template_name='epilepsy12/multiaxial_description.html', context=context)


def set_all_epilepsy_causes_to_none(except_field):
    set_to_none = {

    }
    if except_field is None:
        set_to_none.update({
            'seizure_cause_main': None,
            'seizure_cause_main_snomed_code': None
        })
    elif except_field != "Str":
        set_to_none.update({
            'seizure_cause_structural': None,
            'seizure_cause_structural_snomed_code': None
        })
    elif except_field != "Gen":
        set_to_none.update({
            'seizure_cause_genetic': None,
            'seizure_cause_gene_abnormality': None,
            'seizure_cause_genetic_other': None,
            'seizure_cause_gene_abnormality_snomed_code': None,
            'seizure_cause_chromosomal_abnormality': None,
        })
    elif except_field != "Inf":
        set_to_none.update({
            'seizure_cause_infectious': None,
            'seizure_cause_infectious_snomed_code': None
        })
    elif except_field != "Met":
        set_to_none.update({
            'seizure_cause_metabolic': None,
            'seizure_cause_metabolic_other': None,
            'seizure_cause_metabolic_snomed_code': None
        })
    elif except_field != "Imm":
        set_to_none.update({
            'seizure_cause_immune': None,
            'seizure_cause_immune_antibody': None,
            'seizure_cause_immune_antibody_other': None
        })
    elif except_field != "NK":
        set_to_none.update({'seizure_cause_immune_snomed_code': None})

    return set_to_none
