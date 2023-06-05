# python imports
from dateutil.relativedelta import relativedelta
from typing import Literal

# django imports
from django.contrib.gis.db.models import Q, Sum

# E12 imports
from ..models import *
from ..constants import ALL_NHS_TRUSTS, KPI_SCORE
from ..general_functions import has_all_attributes


def calculate_age_at_first_paediatric_assessment_in_years(registration_instance) -> int:
    """
    Helper fn returns age in years as int
    """
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.registration_date,
        registration_instance.case.date_of_birth,
    )

    return age_at_first_paediatric_assessment.years


def check_is_registered(registration_instance) -> bool:
    """
    Helper fn returns True if registered
    """
    return (
        registration_instance.registration_date is not None
        and registration_instance.eligibility_criteria_met
    )


def score_kpi_1(registration_instance) -> int:
    """
    1. `paediatrician_with_expertise_in_epilepsies`

    % of children and young people with epilepsy, with input by a ‘consultant paediatrician with expertise in epilepsies’ within 2 weeks of initial referral

    Calculation Method

    Numerator = Number of children and young people [diagnosed with epilepsy] at first year AND (who had [input from a paediatrician with expertise in epilepsy] OR a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)

    Denominator = Number of and young people [diagnosed with epilepsy] at first year
    """

    assessment = registration_instance.assessment

    # never saw a consultant OR neurologist!
    if (assessment.consultant_paediatrician_referral_made == False) and (
        assessment.paediatric_neurologist_referral_made == False
    ):
        return KPI_SCORE["FAIL"]

    # check all fields complete for either consultant or neurologist
    all_consultant_paediatrician_fields_complete = (
        (assessment.consultant_paediatrician_referral_made is not None)
        and (assessment.consultant_paediatrician_referral_date is not None)
        and (assessment.consultant_paediatrician_input_date is not None)
    )
    all_paediatric_neurologist_fields_complete = (
        (assessment.paediatric_neurologist_referral_made is not None)
        and (assessment.paediatric_neurologist_referral_date is not None)
        and (assessment.paediatric_neurologist_input_date is not None)
    )

    # incomplete
    if (not all_consultant_paediatrician_fields_complete) and (
        not all_paediatric_neurologist_fields_complete
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score KPI
    if all_consultant_paediatrician_fields_complete:
        passed_metric = (
            relativedelta(
                assessment.consultant_paediatrician_input_date,
                assessment.consultant_paediatrician_referral_date,
            ).days
            <= 14
        )
        if passed_metric:
            return KPI_SCORE["PASS"]
        else:
            return KPI_SCORE["FAIL"]

    elif all_paediatric_neurologist_fields_complete:
        passed_metric = (
            relativedelta(
                assessment.paediatric_neurologist_input_date,
                assessment.paediatric_neurologist_referral_date,
            ).days
            <= 14
        )
        if passed_metric:
            return KPI_SCORE["PASS"]
        else:
            return KPI_SCORE["FAIL"]


def score_kpi_2(registration_instance) -> int:
    """2. epilepsy_specialist_nurse

    % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

    Calculation Method

    Numerator= Number of children and young people [diagnosed with epilepsy] AND who had [input from or referral to an Epilepsy Specialist Nurse] by first year

    Denominator = Number of children and young people [diagnosed with epilepsy] at first year
    """

    assessment = registration_instance.assessment

    # no nurse referral, fail
    if assessment.epilepsy_specialist_nurse_referral_made is False:
        return KPI_SCORE["FAIL"]

    # if not all filled, incomplete form
    if (
        assessment.epilepsy_specialist_nurse_referral_made is None
        or assessment.epilepsy_specialist_nurse_referral_date is None
        or assessment.epilepsy_specialist_nurse_input_date is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score check
    has_seen_nurse_before_close_date = (
        assessment.epilepsy_specialist_nurse_input_date
        <= registration_instance.registration_close_date
        or assessment.epilepsy_specialist_nurse_referral_date
        <= registration_instance.registration_close_date
    )

    if has_seen_nurse_before_close_date:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_3(registration_instance, age_at_first_paediatric_assessment) -> int:
    """3. tertiary_input
    % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care

    Calculation Method

    Numerator = Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]

    Denominator = Number of children [less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year )OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] OR (Number of children less than 4 years old at first assessment with epilepsy AND  [myoclonic seizures])
    """

    assessment = registration_instance.assessment

    # EVALUATE ELIGIBILITY CRITERIA

    # first gather relevant data
    aems_count = AntiEpilepsyMedicine.objects.filter(
        management=registration_instance.management,
        is_rescue_medicine=False,
        antiepilepsy_medicine_start_date__lt=registration_instance.registration_close_date,
    ).count()
    has_myoclonic_epilepsy_episode = Episode.objects.filter(
        Q(multiaxial_diagnosis=registration_instance.multiaxialdiagnosis)
        & Q(epilepsy_or_nonepilepsy_status="E")
        & Q(epileptic_generalised_onset="MyC")
    ).exists()

    # List of True/False assessing if meets any of criteria
    eligibility_criteria = [
        (age_at_first_paediatric_assessment <= 3),
        (age_at_first_paediatric_assessment < 4 and has_myoclonic_epilepsy_episode),
        (aems_count >= 3),
        (
            assessment.childrens_epilepsy_surgical_service_referral_criteria_met
        ),  # NOTE: CESS_referral_criteria_met is only one that could be None (rest must be True/False), however, only checking whether it is True or not True here so doesn't matter
    ]

    # None of eligibility criteria are True -> set ineligible with guard clause
    if not any(eligibility_criteria):
        return KPI_SCORE["INELIGIBLE"]

    # Eligible for measure - EVALUATE IF AT LEAST REFERRED FROM NEUROLOGIST OR CESS. NOTE: technically the Assessment model allows a referral_date & input_date filled WITHOUT referral_made, but this is a rare edge case just for API-use. The UI does not allow you to enter either date, if referral_made is False. If the API has an endpoint for this measure, need to ensure referral_made==True, if dates are both valid.

    # first evaluate relevant fields complete
    tertiary_input_complete = (
        assessment.paediatric_neurologist_referral_made is not None
    ) or (assessment.childrens_epilepsy_surgical_service_referral_made is not None)

    if not tertiary_input_complete:
        return KPI_SCORE["NOT_SCORED"]

    pass_criteria = [
        (assessment.paediatric_neurologist_referral_made is True),
        (assessment.childrens_epilepsy_surgical_service_referral_made is True),
    ]

    # if referral made to either neurologist or CESS, they pass
    if any(pass_criteria):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_3b(registration_instance) -> int:
    """3b. epilepsy_surgery_referral

    % of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral
    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy AND met [CESS criteria] at first year AND had [evidence of referral or involvement of CESS]

    Denominator = Number of children and young people diagnosed with epilepsy AND met CESS criteria at first year
    """

    assessment = registration_instance.assessment

    # not scored
    if assessment.childrens_epilepsy_surgical_service_referral_criteria_met is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if assessment.childrens_epilepsy_surgical_service_referral_criteria_met is False:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    if (
        assessment.childrens_epilepsy_surgical_service_referral_made is None
        and assessment.paediatric_neurologist_referral_made is None
    ):
        return KPI_SCORE["NOT_SCORED"]

    # score KPI
    if (
        assessment.childrens_epilepsy_surgical_service_referral_made
        or assessment.paediatric_neurologist_referral_made
    ):
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_4(registration_instance) -> int:
    """4. ECG

    % of children and young people with convulsive seizures and epilepsy, with an ECG at first year

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year AND who have [12 lead ECG obtained]

    Denominator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year
    """
    epilepsy_context = registration_instance.epilepsycontext
    investigations = registration_instance.investigations

    # not scored / ineligible guard clauses
    if (epilepsy_context.were_any_of_the_epileptic_seizures_convulsive is None) or (
        investigations.twelve_lead_ecg_status is None
    ):
        return KPI_SCORE["NOT_SCORED"]
    if epilepsy_context.were_any_of_the_epileptic_seizures_convulsive is False:
        return KPI_SCORE["INELIGIBLE"]

    # Convulsive seizure - score ECG status

    if investigations.twelve_lead_ecg_status is True:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_5(registration_instance, age_at_first_paediatric_assessment) -> int:
    """5. MRI

    Calculation Method

    Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic OR number of children aged under 2 years at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request

    Denominator = Number of children and young people diagnosed with epilepsy at first year AND ((who are NOT JME or JAE or CAE or BECTS) OR (number of children aged under 2 years  at first assessment with a diagnosis of epilepsy at first year))
    """
    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis
    investigations = registration_instance.investigations

    # not scored
    if multiaxial_diagnosis.syndrome_present is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if age_at_first_paediatric_assessment >= 2:
        return KPI_SCORE["INELIGIBLE"]
    ineligible_syndrome_present = Syndrome.objects.filter(
        Q(multiaxial_diagnosis=multiaxial_diagnosis)
        &
        # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
        Q(
            syndrome__syndrome_name__in=[
                "Self-limited epilepsy with centrotemporal spikes",
                "Juvenile myoclonic epilepsy",
                "Juvenile absence epilepsy",
                "Childhood absence epilepsy",
            ]
        )
    ).exists()
    if ineligible_syndrome_present:
        return KPI_SCORE["INELIGIBLE"]

    # not scored
    mri_dates_are_none = [
        (investigations.mri_brain_requested_date is None),
        (investigations.mri_brain_reported_date is None),
    ]
    if any(mri_dates_are_none):
        return KPI_SCORE["NOT_SCORED"]

    # eligible for this measure - score kpi
    passing_criteria_met = (
        abs(
            (
                investigations.mri_brain_requested_date
                - investigations.mri_brain_reported_date
            ).days
        )
        <= 42
    )

    if passing_criteria_met:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def score_kpi_6(registration_instance, age_at_first_paediatric_assessment) -> int:
    """6. assessment_of_mental_health_issues
    Calculation Method

    Numerator = Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health

    Denominator = = Number of children and young people over 5 years diagnosed with epilepsy
    denominator"""

    multiaxial_diagnosis = registration_instance.multiaxialdiagnosis

    # not scored
    if multiaxial_diagnosis.mental_health_screen is None:
        return KPI_SCORE["NOT_SCORED"]

    # ineligible
    if age_at_first_paediatric_assessment < 5:
        return KPI_SCORE["INELIGIBLE"]

    # score kpi
    if multiaxial_diagnosis.mental_health_screen:
        return KPI_SCORE["PASS"]
    else:
        return KPI_SCORE["FAIL"]


def calculate_kpis(registration_instance):
    """
    Function called on update of every field
    Identifies completed KPIs for a given registered child and passes these back to update the KPI model
    It accepts the registration instance and is called each time a related model is updated
    The outcome of a measure follows 4 potential states:
    0 - measure failed
    1 - measure achieved
    2 - measure not applicable (eg ECG in nonconvulsive seizure)
    None - measure not scored yet
    """

    # important metric for calculations that follow
    age_at_first_paediatric_assessment = (
        calculate_age_at_first_paediatric_assessment_in_years(registration_instance)
    )

    # child must be registered in the audit for the KPI to be counted
    if not check_is_registered(registration_instance):
        # cannot proceed any further if registration incomplete.
        # In theory it should not be possible to get this far.
        return None

    if hasattr(registration_instance, "assessment"):
        paediatrician_with_expertise_in_epilepsies = score_kpi_1(registration_instance)

    if hasattr(registration_instance, "assessment"):
        epilepsy_specialist_nurse = score_kpi_2(registration_instance)

    if has_all_attributes(
        registration_instance, ["management", "assessment", "multiaxialdiagnosis"]
    ):
        tertiary_input = score_kpi_3(
            registration_instance, age_at_first_paediatric_assessment
        )

    if hasattr(registration_instance, "assessment"):
        epilepsy_surgery_referral = score_kpi_3b(registration_instance)

    if has_all_attributes(registration_instance, ["epilepsycontext", "investigations"]):
        ecg = score_kpi_4(registration_instance)

    if has_all_attributes(
        registration_instance, ["multiaxialdiagnosis", "investigations"]
    ):
        mri = score_kpi_5(registration_instance, age_at_first_paediatric_assessment)

    if hasattr(registration_instance, "multiaxialdiagnosis"):
        assessment_of_mental_health_issues = score_kpi_6(
            registration_instance, age_at_first_paediatric_assessment
        )

    # 7. mental_health_support
    # Percentage of children with epilepsy and a mental health problem who have evidence of mental health support
    # Calculation Method
    # Numerator =  Number of children and young people diagnosed with epilepsy AND had a mental health issue identified AND had evidence of mental health support received
    # Denominator= Number of children and young people diagnosed with epilepsy AND had a mental health issue identified

    mental_health_support = None
    if hasattr(registration_instance, "multiaxialdiagnosis") and hasattr(
        registration_instance, "management"
    ):
        # denominator
        if registration_instance.multiaxialdiagnosis.mental_health_issue_identified:
            # eligible for this measure
            mental_health_support = 0
            if (
                registration_instance.multiaxialdiagnosis.mental_health_issue_identified
                and registration_instance.management.has_support_for_mental_health_support
            ):
                # criteria met
                mental_health_support = 1
        else:
            # not eligible for this measure
            mental_health_support = 2

    # 8. Sodium Valproate
    # Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed
    # Calculation Method
    # Numerator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate AND annual risk acknowledgement forms completed AND pregnancy prevention programme in place
    # Denominator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate
    sodium_valproate = None

    if hasattr(registration_instance, "management"):
        # denominator
        if (
            age_at_first_paediatric_assessment >= 12
            and registration_instance.case.sex == 2
        ) and (
            registration_instance.management.has_an_aed_been_given
            and AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                medicine_entity=MedicineEntity.objects.filter(
                    medicine_name__icontains="valproate"
                ).first(),
            ).exists()
        ):
            # eligible for this measure
            sodium_valproate = 0
            if (
                age_at_first_paediatric_assessment >= 12
                and registration_instance.case.sex == 2
            ) and (
                registration_instance.management.has_an_aed_been_given
                and AntiEpilepsyMedicine.objects.filter(
                    management=registration_instance.management,
                    medicine_entity=MedicineEntity.objects.filter(
                        medicine_name__icontains="valproate"
                    ).first(),
                    is_a_pregnancy_prevention_programme_needed=True,
                    has_a_valproate_annual_risk_acknowledgement_form_been_completed=True,
                ).exists()
            ):
                # criteria met
                sodium_valproate = 1
        else:
            # not eligible for this measure
            sodium_valproate = 2

    # 9A. comprehensive_care_planning_agreement
    # % of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with an individualised epilepsy document or copy clinic letter that includes care planning information )AND evidence of agreement AND care plan is up to date including elements where appropriate as below
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    comprehensive_care_planning_agreement = None
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_in_place
            is not None
            and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
            is not None
        ):
            # eligible for this measure
            if (
                registration_instance.management.individualised_care_plan_in_place
                and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
            ):
                # criteria met
                comprehensive_care_planning_agreement = 1
            else:
                comprehensive_care_planning_agreement = 0

    # i. patient_held_individualised_epilepsy_document
    # % of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with individualised epilepsy document or copy clinic letter that includes care planning information )
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    patient_held_individualised_epilepsy_document = None
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_in_place
            is not None
            and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
            is not None
            and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
            is not None
        ):
            if (
                registration_instance.management.individualised_care_plan_in_place
                and registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
                and registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
            ):
                # criteria met
                patient_held_individualised_epilepsy_document = 1
            else:
                patient_held_individualised_epilepsy_document = 0

    # ii patient_carer_parent_agreement_to_the_care_planning
    # % of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of agreement
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    patient_carer_parent_agreement_to_the_care_planning = None
    if hasattr(registration_instance, "management"):
        if (
            registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
            is not None
        ):
            if (
                registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
            ):
                patient_carer_parent_agreement_to_the_care_planning = 1
            else:
                patient_carer_parent_agreement_to_the_care_planning = 0

    # iii. care_planning_has_been_updated_when_necessary
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    care_planning_has_been_updated_when_necessary = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
        ):
            # criteria met
            care_planning_has_been_updated_when_necessary = 1

    # 9B. comprehensive_care_planning_content
    # Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning.
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND evidence of written prolonged seizures plan if prescribed rescue medication AND evidence of discussion regarding water safety AND first aid AND participation and risk AND service contact details AND SUDEP
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    comprehensive_care_planning_content = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.has_rescue_medication_been_prescribed
            and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_include_first_aid
            and registration_instance.management.individualised_care_plan_addresses_water_safety
            and registration_instance.management.individualised_care_plan_includes_service_contact_details
            and registration_instance.management.individualised_care_plan_includes_general_participation_risk
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            # criteria met
            comprehensive_care_planning_content = 1

    # i. parental_prolonged_seizures_care_plan
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication

    parental_prolonged_seizures_care_plan = None
    if hasattr(registration_instance, "management"):
        # denominator
        if registration_instance.management.has_rescue_medication_been_prescribed:
            # eligible for this measure
            parental_prolonged_seizures_care_plan = 0
            if (
                registration_instance.management.has_rescue_medication_been_prescribed
                and registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            ):
                # criteria met
                parental_prolonged_seizures_care_plan = 1
        else:
            # not eligible for this measure
            parental_prolonged_seizures_care_plan = 2

    # ii. water_safety
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    water_safety = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_addresses_water_safety
        ):
            water_safety = 1

    # iii. first_aid
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    first_aid = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if registration_instance.management.individualised_care_plan_include_first_aid:
            first_aid = 1

    # iv. general_participation_and_risk
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    general_participation_and_risk = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_includes_general_participation_risk
        ):
            general_participation_and_risk = 1

    # v. service_contact_details
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details
    # Denominator = Number of children and young people diagnosed with epilepsy at first year

    service_contact_details = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_includes_service_contact_details
        ):
            service_contact_details = 1

    # vi. sudep
    # Calculation Method
    # Numerator = Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP AND evidence of a written prolonged seizures plan at first year
    # Denominator = Number of children diagnosed with epilepsy at first year

    sudep = 0
    if hasattr(registration_instance, "management"):
        # denominator is all children with epilepsy - no denominator
        if (
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
            and registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            sudep = 1

    # 10. school_individual_healthcare_plan
    # Percentage of children and young people with epilepsy aged 5 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.
    # Calculation Method
    # Numerator = Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP
    # Denominator =Number of children and young people aged 5 years and above diagnosed with epilepsy at first year

    school_individual_healthcare_plan = None
    if hasattr(registration_instance, "management"):
        # denominator
        if age_at_first_paediatric_assessment >= 5:
            # eligible for this measure
            school_individual_healthcare_plan = 0
            if (age_at_first_paediatric_assessment >= 5) and (
                registration_instance.management.individualised_care_plan_includes_ehcp
            ):
                school_individual_healthcare_plan = 1
        else:
            # not eligible for this measure
            school_individual_healthcare_plan = 2

    """
    Store the KPIs in AuditProgress
    """

    kpis = {
        "paediatrician_with_expertise_in_epilepsies": paediatrician_with_expertise_in_epilepsies,
        "epilepsy_specialist_nurse": epilepsy_specialist_nurse,
        "tertiary_input": tertiary_input,
        "epilepsy_surgery_referral": epilepsy_surgery_referral,
        "ecg": ecg,
        "mri": mri,
        "assessment_of_mental_health_issues": assessment_of_mental_health_issues,
        "mental_health_support": mental_health_support,
        "sodium_valproate": sodium_valproate,
        "comprehensive_care_planning_agreement": comprehensive_care_planning_agreement,
        "patient_held_individualised_epilepsy_document": patient_held_individualised_epilepsy_document,
        "patient_carer_parent_agreement_to_the_care_planning": patient_carer_parent_agreement_to_the_care_planning,
        "care_planning_has_been_updated_when_necessary": care_planning_has_been_updated_when_necessary,
        "comprehensive_care_planning_content": comprehensive_care_planning_content,
        "parental_prolonged_seizures_care_plan": parental_prolonged_seizures_care_plan,
        "water_safety": water_safety,
        "first_aid": first_aid,
        "general_participation_and_risk": general_participation_and_risk,
        "service_contact_details": service_contact_details,
        "sudep": sudep,
        "school_individual_healthcare_plan": school_individual_healthcare_plan,
    }

    KPI.objects.filter(pk=registration_instance.kpi.pk).update(**kpis)


def annotate_kpis(filtered_organisations, kpi_name="all"):
    """
    Single function to rationalize all functions calculatirng KPIs
    Accepts query_list of organisations
    Accepts flag for kpi_name if only individual kpi_name requested
    """
    if kpi_name == "all":
        return (
            filtered_organisations.annotate(
                paediatrician_with_expertise_in_epilepsies_sum=Sum(
                    "kpi__paediatrician_with_expertise_in_epilepsies"
                )
            )
            .annotate(
                epilepsy_specialist_nurse_sum=Sum("kpi__epilepsy_specialist_nurse")
            )
            .annotate(tertiary_input_sum=Sum("kpi__tertiary_input"))
            .annotate(
                epilepsy_surgery_referral_sum=Sum("kpi__epilepsy_surgery_referral")
            )
            .annotate(ecg_sum=Sum("kpi__ecg"))
            .annotate(mri_sum=Sum("kpi__mri"))
            .annotate(
                assessment_of_mental_health_issues_sum=Sum(
                    "kpi__assessment_of_mental_health_issues"
                )
            )
            .annotate(mental_health_support_sum=Sum("kpi__mental_health_support"))
            .annotate(
                comprehensive_care_planning_agreement_sum=Sum(
                    "kpi__comprehensive_care_planning_agreement"
                )
            )
            .annotate(
                patient_held_individualised_epilepsy_document_sum=Sum(
                    "kpi__patient_held_individualised_epilepsy_document"
                )
            )
            .annotate(
                care_planning_has_been_updated_when_necessary_sum=Sum(
                    "kpi__care_planning_has_been_updated_when_necessary"
                )
            )
            .annotate(
                comprehensive_care_planning_content_sum=Sum(
                    "kpi__comprehensive_care_planning_content"
                )
            )
            .annotate(
                parental_prolonged_seizures_care_plan_sum=Sum(
                    "kpi__parental_prolonged_seizures_care_plan"
                )
            )
            .annotate(water_safety_sum=Sum("kpi__water_safety"))
            .annotate(first_aid_sum=Sum("kpi__first_aid"))
            .annotate(
                general_participation_and_risk_sum=Sum(
                    "kpi__general_participation_and_risk"
                )
            )
            .annotate(service_contact_details_sum=Sum("kpi__service_contact_details"))
            .annotate(sudep_sum=Sum("kpi__sudep"))
            .annotate(
                school_individual_healthcare_plan_sum=Sum(
                    "kpi__school_individual_healthcare_plan"
                )
            )
        )
    else:
        ans = filtered_organisations.annotate(kpi_sum=Sum(f"kpi__{kpi_name}"))
        return ans
