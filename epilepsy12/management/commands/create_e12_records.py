# python dependencies
from random import randint, getrandbits
from dateutil.relativedelta import relativedelta

# epilepsy12 dependencies
from ...models import FirstPaediatricAssessment, EpilepsyContext, MultiaxialDiagnosis, Syndrome, Episode, Keyword, Comorbidity, Assessment, Site, Organisation, Management, AntiEpilepsyMedicine, Case, AuditProgress, Registration, KPI, Investigations, SyndromeEntity, EpilepsyCauseEntity, ComorbidityEntity
from ...constants import OPT_OUT_UNCERTAIN, SYNDROMES, EPILEPSY_CAUSES, NEUROPSYCHIATRIC, DATE_ACCURACY, EPISODE_DEFINITION, EPILEPSY_DIAGNOSIS_STATUS, EPILEPSY_SEIZURE_TYPE, FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS, FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS, FOCAL_EPILEPSY_EEG_MANIFESTATIONS, LATERALITY, GENERALISED_SEIZURE_TYPE, NON_EPILEPSY_SEIZURE_ONSET, NON_EPILEPSY_SEIZURE_TYPE, NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, MIGRAINES, EPIS_MISC, NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, NON_EPILEPTIC_SYNCOPES, NON_EPILEPSY_PAROXYSMS, ANTIEPILEPSY_MEDICINES, BENZODIAZEPINE_TYPES
from ...general_functions import random_date, current_cohort_start_date, first_tuesday_in_january, fetch_ecl
from ...common_view_functions import test_fields_update_audit_progress, calculate_kpis


def create_registrations():
    """
    run through all newly created cases and create registrations
    """
    for case in Case.objects.all():
        # create  a registration
        audit_progress = AuditProgress.objects.create(
            registration_complete=False,
            first_paediatric_assessment_complete=False,
            assessment_complete=False,
            epilepsy_context_complete=False,
            multiaxial_diagnosis_complete=False,
            management_complete=False,
            investigations_complete=False,
            registration_total_expected_fields=3,
            registration_total_completed_fields=0,
            first_paediatric_assessment_total_expected_fields=0,
            first_paediatric_assessment_total_completed_fields=0,
            assessment_total_expected_fields=0,
            assessment_total_completed_fields=0,
            epilepsy_context_total_expected_fields=0,
            epilepsy_context_total_completed_fields=0,
            multiaxial_diagnosis_total_expected_fields=0,
            multiaxial_diagnosis_total_completed_fields=0,
            investigations_total_expected_fields=0,
            investigations_total_completed_fields=0,
            management_total_expected_fields=0,
            management_total_completed_fields=0,
        )
        lead_organisation = Site.objects.filter(
            case=case,
            site_is_primary_centre_of_epilepsy_care=True,
            site_is_actively_involved_in_epilepsy_care=True
        ).get()
        kpi = KPI.objects.create(
            organisation=lead_organisation.organisation,
            parent_trust=lead_organisation.organisation.ParentName,
            paediatrician_with_expertise_in_epilepsies=0,
            epilepsy_specialist_nurse=0,
            tertiary_input=0,
            epilepsy_surgery_referral=0,
            ecg=0,
            mri=0,
            assessment_of_mental_health_issues=0,
            mental_health_support=0,
            sodium_valproate=0,
            comprehensive_care_planning_agreement=0,
            patient_held_individualised_epilepsy_document=0,
            patient_carer_parent_agreement_to_the_care_planning=0,
            care_planning_has_been_updated_when_necessary=0,
            comprehensive_care_planning_content=0,
            parental_prolonged_seizures_care_plan=0,
            water_safety=0,
            first_aid=0,
            general_participation_and_risk=0,
            service_contact_details=0,
            sudep=0,
            school_individual_healthcare_plan=0
        )
        Registration.objects.create(
            case=case,
            audit_progress=audit_progress,
            kpi=kpi
        )


def create_epilepsy12_record(registration_instance):
    """
    Creates a full randomised record for a given registration instance.
    """
    # score registration_instance
    test_fields_update_audit_progress(
        model_instance=registration_instance)

    # create random first paediatric assessment
    first_paediatric_assessment = create_first_paediatric_assessment(
        registration_instance=registration_instance)
    test_fields_update_audit_progress(
        model_instance=first_paediatric_assessment)

    # create random EpilepsyContext
    epilepsy_context = create_epilepsy_context(
        registration_instance=registration_instance)
    test_fields_update_audit_progress(model_instance=epilepsy_context)

    # create random Multiaxial Diagnosis
    multiaxial_diagnosis = create_multiaxial_diagnosis(
        registration_instance=registration_instance)
    test_fields_update_audit_progress(model_instance=multiaxial_diagnosis)

    # create random Assessment
    assessment = create_assessment(registration_instance=registration_instance)
    test_fields_update_audit_progress(model_instance=assessment)

    # create random Investigations
    assessment = create_investigations(
        registration_instance=registration_instance)
    test_fields_update_audit_progress(model_instance=assessment)

    # create random Management
    management = create_management(registration_instance=registration_instance)
    test_fields_update_audit_progress(model_instance=management)

    # calculate all the kpis
    calculate_kpis(registration_instance=registration_instance)


def create_first_paediatric_assessment(registration_instance):
    """
    Complete the first paediatric assessment aspect of the audit
    """
    return FirstPaediatricAssessment.objects.create(
        first_paediatric_assessment_in_acute_or_nonacute_setting=bool(
            getrandbits(1)),
        has_number_of_episodes_since_the_first_been_documented=bool(
            getrandbits(1)),
        general_examination_performed=bool(getrandbits(1)),
        neurological_examination_performed=bool(getrandbits(1)),
        developmental_learning_or_schooling_problems=bool(getrandbits(1)),
        behavioural_or_emotional_problems=bool(getrandbits(1)),
        registration=registration_instance
    )


def create_epilepsy_context(registration_instance):
    """
    Complete the epilepsy_context aspect of the audit
    """
    return EpilepsyContext.objects.create(
        previous_febrile_seizure=OPT_OUT_UNCERTAIN[randint(0, 2)][0],
        previous_acute_symptomatic_seizure=OPT_OUT_UNCERTAIN[randint(0, 2)][0],
        is_there_a_family_history_of_epilepsy=OPT_OUT_UNCERTAIN[randint(
            0, 2)][0],
        previous_neonatal_seizures=OPT_OUT_UNCERTAIN[randint(0, 2)][0],
        diagnosis_of_epilepsy_withdrawn=bool(getrandbits(1)),
        were_any_of_the_epileptic_seizures_convulsive=bool(getrandbits(1)),
        experienced_prolonged_generalized_convulsive_seizures=OPT_OUT_UNCERTAIN[randint(
            0, 2)][0],
        experienced_prolonged_focal_seizures=OPT_OUT_UNCERTAIN[randint(
            0, 2)][0],
        registration=registration_instance
    )


def create_multiaxial_diagnosis(registration_instance):
    """
    Complete the multiaxial diagnosis aspect of the audit, including episodes, 
    syndromes, causes and comorbidities
    """
    multiaxial_diagnosis = MultiaxialDiagnosis.objects.create(
        syndrome_present=bool(getrandbits(1)),
        epilepsy_cause_known=bool(getrandbits(1)),
        relevant_impairments_behavioural_educational=bool(getrandbits(1)),
        mental_health_screen=bool(getrandbits(1)),
        mental_health_issue_identified=bool(getrandbits(1)),
        registration=registration_instance
    )

    if multiaxial_diagnosis.syndrome_present:
        # create a related syndrome
        syndrome_entity = SyndromeEntity.objects.filter(
            syndrome_name=SYNDROMES[randint(0, len(SYNDROMES)-1)][1]).get()
        Syndrome.objects.create(
            syndrome_diagnosis_date=random_date(
                start=registration_instance.registration_date, end=registration_instance.registration_close_date),
            syndrome=syndrome_entity,
            multiaxial_diagnosis=multiaxial_diagnosis
        )

    if multiaxial_diagnosis.epilepsy_cause_known:
        ecl = '<< 363235000'
        epilepsy_causes = fetch_ecl(ecl)
        random_cause = EpilepsyCauseEntity.objects.filter(
            conceptId=epilepsy_causes[randint(0, len(epilepsy_causes)-1)]['conceptId']).first()

        multiaxial_diagnosis.epilepsy_cause = random_cause
        total_cause_choices = len(EPILEPSY_CAUSES)
        random_number_of_choices = randint(1, total_cause_choices)
        choices = []
        for choice in range(0, random_number_of_choices):
            choices.append(EPILEPSY_CAUSES
                           [randint(0, len(EPILEPSY_CAUSES)-1)][0])
        multiaxial_diagnosis.epilepsy_cause_categories = choices

    if multiaxial_diagnosis.mental_health_issue_identified:
        multiaxial_diagnosis.mental_health_issue = NEUROPSYCHIATRIC[randint(
            0, len(NEUROPSYCHIATRIC)-1)][0]

    if multiaxial_diagnosis.relevant_impairments_behavioural_educational:
        # add upto 5 comorbidities
        for count_item in range(1, randint(1, 5)):
            ecl = '<< 35919005'
            comorbidity_choices = fetch_ecl(ecl)
            random_comorbidities = comorbidity_choices[randint(
                0, len(comorbidity_choices)-1)]
            random_comorbidity = ComorbidityEntity.objects.filter(
                conceptId=random_comorbidities['conceptId']).first()

            Comorbidity.objects.create(
                multiaxial_diagnosis=multiaxial_diagnosis,
                comorbidity_diagnosis_date=random_date(
                    start=registration_instance.registration_date, end=registration_instance.registration_close_date),
                comorbidity=random_comorbidity
            )

    # create a random number of episodes to a maximum of 5
    for count_item in range(1, randint(1, 5)):
        current_cohort_end_date = first_tuesday_in_january(
            current_cohort_start_date().year+2)+relativedelta(days=7)
        episode = Episode.objects.create(
            multiaxial_diagnosis=multiaxial_diagnosis,
            seizure_onset_date=random_date(
                start=registration_instance.registration_date, end=current_cohort_end_date),
            seizure_onset_date_confidence=DATE_ACCURACY[randint(
                0, len(DATE_ACCURACY)-1)][0],
            episode_definition=EPISODE_DEFINITION[randint(
                0, len(EPISODE_DEFINITION)-1)][0]
        )

        if count_item == 1:
            # the first episode must be epileptic, subsequent ones are random
            episode.epilepsy_or_nonepilepsy_status = 'E'
        else:
            episode.epilepsy_or_nonepilepsy_status = EPILEPSY_DIAGNOSIS_STATUS[randint(
                0, len(EPILEPSY_DIAGNOSIS_STATUS)-1)][0]

        episode.has_description_of_the_episode_or_episodes_been_gathered = bool(
            getrandbits(1))

        if episode.has_description_of_the_episode_or_episodes_been_gathered:
            keyword_array = []
            activity_choices = (
                'running', 'sleeping', 'on their way to school', 'watching YouTube', 'gaming')
            description_string = f'{registration_instance.case} was '
            for random_number in range(randint(1, 5)):
                random_keyword = Keyword.objects.order_by('?').first()
                keyword_array.append(random_keyword)

            description_string += f'{activity_choices[random_number]} when they developed '
            for index, semiology_keyword in enumerate(keyword_array):
                if index == len(keyword_array)-1:
                    description_string += f'and {semiology_keyword}.'
                else:
                    description_string += f'{semiology_keyword}, '

            episode.description = description_string
            episode.description_keywords = keyword_array

        if episode.epilepsy_or_nonepilepsy_status == 'E':
            episode.epileptic_seizure_onset_type = EPILEPSY_SEIZURE_TYPE[randint(
                0, len(EPILEPSY_SEIZURE_TYPE)-1)][0]

            if episode.epileptic_seizure_onset_type == 'FO':
                laterality = LATERALITY[randint(0, len(LATERALITY)-1)]
                motor_manifestation = FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS[randint(
                    0, len(FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS)-1)]
                nonmotor_manifestation = FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS[randint(
                    0, len(FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS)-1)]
                eeg_manifestations = FOCAL_EPILEPSY_EEG_MANIFESTATIONS[randint(
                    0, len(FOCAL_EPILEPSY_EEG_MANIFESTATIONS)-1)]
                setattr(episode, laterality['name'], True)
                setattr(episode, motor_manifestation['name'], True)
                setattr(episode, nonmotor_manifestation['name'], True)
                setattr(episode, eeg_manifestations['name'], True)

            elif episode.epileptic_seizure_onset_type == 'GO':
                episode.epileptic_generalised_onset = GENERALISED_SEIZURE_TYPE[randint(
                    0, len(GENERALISED_SEIZURE_TYPE)-1)][0]

        elif episode.epilepsy_or_nonepilepsy_status == 'NE':
            episode.nonepileptic_seizure_unknown_onset = NON_EPILEPSY_SEIZURE_ONSET[randint(
                0, len(NON_EPILEPSY_SEIZURE_ONSET)-1)][0]
            episode.nonepileptic_seizure_type = NON_EPILEPSY_SEIZURE_TYPE[randint(
                0, len(NON_EPILEPSY_SEIZURE_TYPE)-1)][0]

            if episode.nonepileptic_seizure_type == 'BPP':
                episode.nonepileptic_seizure_behavioural = NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS[len(
                    NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)-1][0]
            elif episode.nonepileptic_seizure_type == 'MAD':
                episode.nonepileptic_seizure_migraine = MIGRAINES[len(
                    MIGRAINES)-1][0]
            elif episode.nonepileptic_seizure_type == 'ME':
                episode.nonepileptic_seizure_miscellaneous = EPIS_MISC[len(
                    EPIS_MISC)-1][0]
            elif episode.nonepileptic_seizure_type == 'SRC':
                episode.nonepileptic_seizure_sleep = NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS[len(
                    NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)-1][0]
            elif episode.nonepileptic_seizure_type == 'SAS':
                episode.nonepileptic_seizure_syncope = NON_EPILEPTIC_SYNCOPES[len(
                    NON_EPILEPTIC_SYNCOPES)-1][0]
            elif episode.nonepileptic_seizure_type == 'PMD':
                episode.nonepileptic_seizure_paroxysmal = NON_EPILEPSY_PAROXYSMS[len(
                    NON_EPILEPSY_PAROXYSMS)-1][0]
            else:
                print("Other likely selected")

        episode.save()

    multiaxial_diagnosis.save()
    return multiaxial_diagnosis


def create_assessment(registration_instance):
    """
    Complete the assessment aspect of the audit, including specialist sites, 
    """
    assessment = Assessment.objects.create(
        childrens_epilepsy_surgical_service_referral_criteria_met=bool(
            getrandbits(1)),
        consultant_paediatrician_referral_made=bool(getrandbits(1)),
        paediatric_neurologist_referral_made=bool(getrandbits(1)),
        childrens_epilepsy_surgical_service_referral_made=bool(getrandbits(1)),
        epilepsy_specialist_nurse_referral_made=bool(getrandbits(1)),
        registration=registration_instance
    )

    if assessment.consultant_paediatrician_referral_made:
        assessment.consultant_paediatrician_referral_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        assessment.consultant_paediatrician_input_date = assessment.consultant_paediatrician_referral_date + \
            relativedelta(weeks=randint(1, 5))
        random_organisation = Organisation.objects.filter(
            Sector="NHS Sector").order_by("?").first()
        if Site.objects.filter(
            site_is_actively_involved_in_epilepsy_care=True,
            case=registration_instance.case,
            organisation=random_organisation
        ).exists():
            site = Site.objects.filter(
                site_is_actively_involved_in_epilepsy_care=True,
                case=registration_instance.case,
                organisation=random_organisation
            ).get()
            site.site_is_general_paediatric_centre = True
            site.save()
        else:
            Site.objects.create(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_general_paediatric_centre=True,
                case=registration_instance.case,
                organisation=random_organisation
            )

    if assessment.paediatric_neurologist_referral_made:
        assessment.paediatric_neurologist_referral_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        assessment.paediatric_neurologist_input_date = assessment.paediatric_neurologist_referral_date + \
            relativedelta(weeks=randint(1, 5))
        random_organisation = Organisation.objects.filter(
            Sector="NHS Sector").order_by("?").first()
        if Site.objects.filter(
            site_is_actively_involved_in_epilepsy_care=True,
            case=registration_instance.case,
            organisation=random_organisation
        ).exists():
            site = Site.objects.filter(
                site_is_actively_involved_in_epilepsy_care=True,
                case=registration_instance.case,
                organisation=random_organisation
            ).get()
            site.site_is_general_paediatric_centre = True
            site.save()
        else:
            Site.objects.create(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_paediatric_neurology_centre=True,
                case=registration_instance.case,
                organisation=random_organisation
            )

    if assessment.childrens_epilepsy_surgical_service_referral_made:
        assessment.childrens_epilepsy_surgical_service_referral_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        assessment.childrens_epilepsy_surgical_service_input_date = assessment.childrens_epilepsy_surgical_service_referral_date + \
            relativedelta(weeks=randint(1, 5))
        random_organisation = Organisation.objects.filter(
            Sector="NHS Sector").order_by("?").first()
        if Site.objects.filter(
            site_is_actively_involved_in_epilepsy_care=True,
            case=registration_instance.case,
            organisation=random_organisation
        ).exists():
            site = Site.objects.filter(
                site_is_actively_involved_in_epilepsy_care=True,
                case=registration_instance.case,
                organisation=random_organisation
            ).get()
            site.site_is_general_paediatric_centre = True
            site.save()
        else:
            Site.objects.create(
                site_is_actively_involved_in_epilepsy_care=True,
                site_is_childrens_epilepsy_surgery_centre=True,
                case=registration_instance.case,
                organisation=random_organisation
            )

    if assessment.epilepsy_specialist_nurse_referral_made:
        assessment.epilepsy_specialist_nurse_referral_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        assessment.epilepsy_specialist_nurse_input_date = assessment.epilepsy_specialist_nurse_referral_date + \
            relativedelta(weeks=randint(1, 12))

    assessment.save()
    return assessment


def create_investigations(registration_instance):
    """
    Complete the investigations aspect of the audit, including medications
    """
    investigations = Investigations.objects.create(
        eeg_indicated=bool(getrandbits(1)),
        twelve_lead_ecg_status=bool(getrandbits(1)),
        ct_head_scan_status=bool(getrandbits(1)),
        mri_indicated=bool(getrandbits(1)),
        registration=registration_instance
    )
    if investigations.eeg_indicated:
        investigations.eeg_request_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        investigations.eeg_performed_date = investigations.eeg_request_date + \
            relativedelta(weeks=randint(1, 5))
    if investigations.mri_indicated:
        investigations.mri_brain_requested_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        investigations.mri_brain_reported_date = investigations.mri_brain_requested_date + \
            relativedelta(weeks=randint(1, 5))
    investigations.save()
    return investigations


def create_management(registration_instance):
    """
    Complete the management aspect of the audit, including medications
    """
    management = Management.objects.create(
        registration=registration_instance,
        has_an_aed_been_given=bool(getrandbits(1)),
        has_rescue_medication_been_prescribed=bool(getrandbits(1)),
        individualised_care_plan_in_place=bool(getrandbits(1)),
    )

    if management.has_an_aed_been_given:
        for count_item in range(1, randint(1, 3)):
            # add a random number of medicines up to a total of 3
            antiepilepsy_medicine = AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=False,
                antiepilepsy_medicine_start_date=random_date(
                    start=registration_instance.registration_date, end=registration_instance.registration_close_date),
                antiepilepsy_medicine_risk_discussed=bool(getrandbits(1)),
                medicine_id=ANTIEPILEPSY_MEDICINES[randint(
                    0, len(ANTIEPILEPSY_MEDICINES)-1)][0],
                medicine_name=ANTIEPILEPSY_MEDICINES[randint(
                    0, len(ANTIEPILEPSY_MEDICINES)-1)][1]
            )
            if registration_instance.case.sex == 2 and antiepilepsy_medicine.medicine_id == 21:
                antiepilepsy_medicine.is_a_pregnancy_prevention_programme_needed = bool(
                    getrandbits(1))
                antiepilepsy_medicine.has_a_valproate_annual_risk_acknowledgement_form_been_completed
                antiepilepsy_medicine.is_a_pregnancy_prevention_programme_in_place = bool(
                    getrandbits(1))
            antiepilepsy_medicine.save()

    if management.has_rescue_medication_been_prescribed:
        for count_item in range(1, randint(1, 3)):
            # add a random number of medicines up to a total of 3
            AntiEpilepsyMedicine.objects.create(
                management=management,
                is_rescue_medicine=True,
                antiepilepsy_medicine_start_date=random_date(
                    start=registration_instance.registration_date, end=registration_instance.registration_close_date),
                antiepilepsy_medicine_risk_discussed=bool(getrandbits(1)),
                medicine_id=BENZODIAZEPINE_TYPES[randint(
                    0, len(BENZODIAZEPINE_TYPES)-1)][0],
                medicine_name=BENZODIAZEPINE_TYPES[randint(
                    0, len(BENZODIAZEPINE_TYPES)-1)][1]
            )

    if management.individualised_care_plan_in_place:
        management.individualised_care_plan_date = random_date(
            start=registration_instance.registration_date, end=registration_instance.registration_close_date)
        management.individualised_care_plan_has_parent_carer_child_agreement = bool(
            getrandbits(1))
        management.individualised_care_plan_includes_service_contact_details = bool(
            getrandbits(1))
        management.individualised_care_plan_include_first_aid = bool(
            getrandbits(1))
        management.individualised_care_plan_parental_prolonged_seizure_care = bool(
            getrandbits(1))
        management.individualised_care_plan_includes_general_participation_risk = bool(
            getrandbits(1))
        management.individualised_care_plan_addresses_water_safety = bool(
            getrandbits(1))
        management.individualised_care_plan_addresses_sudep = bool(
            getrandbits(1))
        management.individualised_care_plan_includes_ehcp = bool(
            getrandbits(1))
        management.has_individualised_care_plan_been_updated_in_the_last_year = bool(
            getrandbits(1))
        management.has_been_referred_for_mental_health_support = bool(
            getrandbits(1))
        management.has_support_for_mental_health_support = bool(getrandbits(1))

    management.save()
    return management
