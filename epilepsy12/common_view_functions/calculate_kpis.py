# python imports
from dateutil.relativedelta import relativedelta
from typing import Literal
# django imports
from django.db.models import Q
# E12 imports
from ..models import *
from ..constants import ALL_NHS_TRUSTS


def calculate_kpis(registration_instance):
    """
    Function called on update of every field
    Identifies completed KPIs for a given registered child and passes these back to update the KPI model
    It accepts the registration instance
    """

    # child must be registered in the audit for the KPI to be counted
    is_registered = (
        registration_instance.registration_date is not None and registration_instance.eligibility_criteria_met) == True

    if not is_registered:
        # cannot proceed any further if registration incomplete.
        # In theory it should not be possible to get this far.
        return

    # 1. paediatrician_with_expertise_in_epilepsies
    # Calculation Method
    # Numerator = Number of children and young people [diagnosed with epilepsy] at first year AND (who had [input from a paediatrician with expertise in epilepsy] OR a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)
    # Denominator = Number of and young people [diagnosed with epilepsy] at first year
    paediatrician_with_expertise_in_epilepsies = 0
    if hasattr(registration_instance, 'assessment'):
        if registration_instance.assessment.consultant_paediatrician_referral_made and registration_instance.assessment.consultant_paediatrician_input_date is not None:
            if (
                registration_instance.assessment.consultant_paediatrician_input_date <= (
                    registration_instance.registration_date + relativedelta(days=+14))
            ):
                paediatrician_with_expertise_in_epilepsies = 1
        elif registration_instance.assessment.paediatric_neurologist_referral_made and registration_instance.assessment.paediatric_neurologist_input_date is not None:
            if (
                registration_instance.assessment.paediatric_neurologist_input_date <= (
                    registration_instance.registration_date + relativedelta(days=+14))
            ):
                paediatrician_with_expertise_in_epilepsies = 1

    # 2. epilepsy_specialist_nurse
    # Calculation Method
    # Numerator= Number of children and young people [diagnosed with epilepsy] AND who had [input from or referral to an Epilepsy Specialist Nurse] by first year
    # Denominator = Number of children and young people [diagnosed with epilepsy] at first year
    epilepsy_specialist_nurse = 0
    if hasattr(registration_instance, 'assessment'):
        if registration_instance.assessment.epilepsy_specialist_nurse_referral_made and registration_instance.assessment.epilepsy_specialist_nurse_input_date is not None:
            if (
                registration_instance.assessment.epilepsy_specialist_nurse_input_date <= registration_instance.registration_close_date
            ) or (
                registration_instance.assessment.epilepsy_specialist_nurse_referral_date <= registration_instance.registration_close_date
            ):
                epilepsy_specialist_nurse = 1

    # 3. tertiary_input
    # Calculation Method
    # Numerator = Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]
    # Denominator = Number of children [less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year )OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] OR (Number of children less than 4 years old at first assessment with epilepsy AND  [myoclonic seizures])
    age_at_first_paediatric_assessment = relativedelta(
        registration_instance.registration_date, registration_instance.case.date_of_birth).years
    tertiary_input = 0
    if hasattr(registration_instance, 'management') and hasattr(registration_instance, 'assessment') and hasattr(registration_instance, 'multiaxial_diagnosis'):
        if (
            # Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy]
            age_at_first_paediatric_assessment <= 3
        ) or (
            # (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year)
            AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                is_rescue_medicine=False,
                antiepilepsy_medicine_start_date__lt=registration_instance.registration_close_date
            ).count() >= 3
        ) or (
            # (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)
            age_at_first_paediatric_assessment <= 4 and
            Episode.objects.filter(
                Q(multiaxial_diagnosis=registration_instance.multiaxial_diagnosis) &
                Q(epilepsy_or_nonepilepsy_status='E') &
                Q(epileptic_generalised_onset='MyC')
            ).exists()
        ) or (
            # (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist]
            (registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met == registration_instance.assessment.paediatric_neurologist_referral_made) or
            (registration_instance.assessment.paediatric_neurologist_input_date is not None and registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met)
        ) or (
            # [evidence of referral or involvement of CESS]
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_made is not None or
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_date is not None or
            registration_instance.assessment.childrens_epilepsy_surgical_service_input_date is not None
        ):
            tertiary_input = 1

    # 4. epilepsy_surgery_referral
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy AND met [CESS criteria] at first year AND had [evidence of referral or involvement of CESS]
    # Denominator =Number of children and young people diagnosed with epilepsy AND met CESS criteria at first year
    epilepsy_surgery_referral = 0
    if hasattr(registration_instance, 'assessment'):
        if (
            registration_instance.assessment.childrens_epilepsy_surgical_service_referral_criteria_met and (
                registration_instance.assessment.childrens_epilepsy_surgical_service_referral_made is not None or
                registration_instance.assessment.childrens_epilepsy_surgical_service_referral_date is not None or
                registration_instance.assessment.childrens_epilepsy_surgical_service_input_date is not None
            )
        ):
            epilepsy_surgery_referral = 1

    # 5. ECG
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year AND who have [12 lead ECG obtained]
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year
    ecg = 0
    if hasattr(registration_instance, 'epilepsy_context') and hasattr(registration_instance, 'investigations'):
        if (
            registration_instance.epilepsy_context.were_any_of_the_epileptic_seizures_convulsive and
            registration_instance.investigations.twelve_lead_ecg_status
        ):
            ecg = 1

    # 6. MRI
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic OR number of children aged under 2 years at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND ((who are NOT JME or JAE or CAE or BECTS) OR (number of children aged under  2 years  at first assessment with a diagnosis of epilepsy at first year))
    mri = 0
    if hasattr(registration_instance, 'multiaxial_diagnosis'):
        if (
            registration_instance.multiaxial_diagnosis.syndrome_present and
                Syndrome.objects.filter(
                    Q(multiaxial_diagnosis=registration_instance.multiaxial_diagnosis) &
                    # ELECTROCLINICAL SYNDROMES: BECTS/JME/JAE/CAE currently not included
                    ~Q(syndrome_name__in=[3, 16, 17, 18])
                ).exists() or

            age_at_first_paediatric_assessment <= 2
        ) and (
            registration_instance.investigations.mri_brain_reported_date <= (
                registration_instance.investigations.mri_brain_requested_date + relativedelta(days=42))
        ):
            mri = 1

    # 7. assessment_of_mental_health_issues
    # Calculation Method
    # Numerator = Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health
    # Denominator = = Number of children and young people over 5 years diagnosed with epilepsy
    assessment_of_mental_health_issues = 0
    if hasattr(registration_instance, 'multiaxial_diagnosis'):
        if (
            age_at_first_paediatric_assessment >= 5
        ) and (
            registration_instance.multiaxial_diagnosis.mental_health_screen
        ):
            assessment_of_mental_health_issues = 1

    # 8. mental_health_support
    # Calculation Method
    # Numerator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate AND annual risk acknowledgement forms completed AND pregnancy prevention programme in place
    # Denominator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate
    mental_health_support = 0
    if hasattr(registration_instance, 'management'):
        if(
            age_at_first_paediatric_assessment >= 12 and
            registration_instance.case.sex == 2
        ) and (
            registration_instance.management.has_an_aed_been_given and
            AntiEpilepsyMedicine.objects.filter(
                management=registration_instance.management,
                medicine_id=21,
                is_a_pregnancy_prevention_programme_needed=True,
                has_a_valproate_annual_risk_acknowledgement_form_been_completed=True
            ).exists()
        ):
            mental_health_support = 1

    # 9. comprehensive_care_planning_agreement
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with an individualised epilepsy document or copy clinic letter that includes care planning information )AND evidence of agreement AND care plan is up to date including elements where appropriate as below
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    comprehensive_care_planning_agreement = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_in_place
        ):
            comprehensive_care_planning_agreement = 1

    # 10. patient_held_individualised_epilepsy_document
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with individualised epilepsy document or copy clinic letter that includes care planning information )
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    patient_held_individualised_epilepsy_document = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_has_parent_carer_child_agreement
        ):
            patient_held_individualised_epilepsy_document = 1

    # 11. care_planning_has_been_updated_when_necessary

    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    care_planning_has_been_updated_when_necessary = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.has_individualised_care_plan_been_updated_in_the_last_year
        ):
            care_planning_has_been_updated_when_necessary = 1

    # 12. comprehensive_care_planning_content
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND evidence of written prolonged seizures plan if prescribed rescue medication AND evidence of discussion regarding water safety AND first aid AND participation and risk AND service contact details AND SUDEP
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    comprehensive_care_planning_content = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.has_rescue_medication_been_prescribed and
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care and
            registration_instance.management.individualised_care_plan_include_first_aid and
            registration_instance.management.individualised_care_plan_addresses_water_safety and
            registration_instance.management.individualised_care_plan_includes_service_contact_details and
            registration_instance.management.individualised_care_plan_includes_general_participation_risk and
            registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            comprehensive_care_planning_content = 1

    # 13. parental_prolonged_seizures_care_plan
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan
    # Denominator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication
    parental_prolonged_seizures_care_plan = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.has_rescue_medication_been_prescribed and
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care
        ):
            parental_prolonged_seizures_care_plan = 1

    # 14. water_safety
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    water_safety = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_addresses_water_safety
        ):
            water_safety = 1

    # 15. first_aid
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    first_aid = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_include_first_aid
        ):
            first_aid = 1

    # 16. general_participation_and_risk
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    general_participation_and_risk = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_includes_general_participation_risk
        ):
            general_participation_and_risk = 1

    # 17. service_contact_details
    # Calculation Method
    # Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details
    # Denominator = Number of children and young people diagnosed with epilepsy at first year
    service_contact_details = 0
    if hasattr(registration_instance, 'management'):
        if(
            registration_instance.management.individualised_care_plan_includes_service_contact_details
        ):
            service_contact_details = 1

    # 18. sudep
    # Calculation Method
    # Numerator = Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP AND evidence of a written prolonged seizures plan at first year
    # Denominator = Number of children diagnosed with epilepsy at first year
    sudep = 0
    if hasattr(registration_instance, 'management'):
        if (
            registration_instance.management.individualised_care_plan_parental_prolonged_seizure_care and
            registration_instance.management.individualised_care_plan_addresses_sudep
        ):
            sudep = 1

    # 19. school_individual_healthcare_plan
    # Calculation Method
    # Numerator = Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP
    # Denominator =Number of children and young people aged 5 years and above diagnosed with epilepsy at first year
    school_individual_healthcare_plan = 0
    if hasattr(registration_instance, 'management'):
        if (
            age_at_first_paediatric_assessment >= 5
        ) and (
            registration_instance.management.individualised_care_plan_includes_ehcp
        ):
            school_individual_healthcare_plan = 1

    """
    Store the KPIs in AuditProgress
    """

    kpis = {
        'paediatrician_with_expertise_in_epilepsies': paediatrician_with_expertise_in_epilepsies,
        'epilepsy_specialist_nurse': epilepsy_specialist_nurse,
        'tertiary_input': tertiary_input,
        'epilepsy_surgery_referral': epilepsy_surgery_referral,
        'ecg': ecg,
        'mri': mri,
        'assessment_of_mental_health_issues': assessment_of_mental_health_issues,
        'mental_health_support': mental_health_support,
        'comprehensive_care_planning_agreement': comprehensive_care_planning_agreement,
        'patient_held_individualised_epilepsy_document': patient_held_individualised_epilepsy_document,
        'care_planning_has_been_updated_when_necessary': care_planning_has_been_updated_when_necessary,
        'comprehensive_care_planning_content': comprehensive_care_planning_content,
        'parental_prolonged_seizures_care_plan': parental_prolonged_seizures_care_plan,
        'water_safety': water_safety,
        'first_aid': first_aid,
        'general_participation_and_risk': general_participation_and_risk,
        'service_contact_details': service_contact_details,
        'sudep': sudep,
        'school_individual_healthcare_plan': school_individual_healthcare_plan,
    }

    KPI.objects.filter(
        pk=registration_instance.kpi.pk).update(**kpis)


def kpis_for_abstraction_level(hospital_id=None, abstraction_level: Literal['hospital', 'trust', 'icb', 'nhs_region', 'open_uk', 'country', 'national'] = "national", kpi_name="all"):
    """
    Single function to rationalize all functions calculatirng KPIs
    Accepts hospital_id if not national view requested
    Accepts flag for hospital, trust, icb, nhs_region, open_uk, national, england_wales
    Accepts flag for kpi_name if only individual kpi_name requested
    """

    # choose all kpis or just one
    if kpi_name == "all":

        # initialize KPIs
        kpis = {
            "paediatrician_with_expertise_in_epilepsies": 0,
            "epilepsy_specialist_nurse": 0,
            "tertiary_input": 0,
            "epilepsy_surgery_referral": 0,
            "ecg": 0,
            "mri": 0,
            "assessment_of_mental_health_issues": 0,
            "mental_health_support": 0,
            "sodium_valproate": 0,
            "comprehensive_care_planning_agreement": 0,
            "patient_held_individualised_epilepsy_document": 0,
            "patient_carer_parent_agreement_to_the_care_planning": 0,
            "care_planning_has_been_updated_when_necessary": 0,
            "comprehensive_care_planning_content": 0,
            "parental_prolonged_seizures_care_plan": 0,
            "water_safety": 0,
            "first_aid": 0,
            "general_participation_and_risk": 0,
            "service_contact_details": 0,
            "sudep": 0,
            "school_individual_healthcare_plan": 0,
            "total_number_of_cases": 0,
        }

    else:

        kpis = {
            kpi_name: 0,
            "total_number_of_cases": 0
        }

    # select all hospitals to filter based on requested level of abstraction
    hospital_list = []

    if abstraction_level == 'national':
        hospital_list = HospitalTrust.objects.all()
    else:
        hospital_organisation = HospitalTrust.objects.get(pk=hospital_id)

        if abstraction_level == 'hospital':
            hospital_list = HospitalTrust.objects.filter(
                pk=hospital_id).all()  # returns single hospital in a list
        elif abstraction_level == 'trust':
            hospital_list = HospitalTrust.objects.filter(
                ParentODSCode=hospital_organisation.ParentODSCode).all()
        elif abstraction_level == 'icb':
            hospital_list = HospitalTrust.objects.filter(
                ICBODSCode=hospital_organisation.ICBODSCode).all()
        elif abstraction_level == 'nhs_region':
            hospital_list = HospitalTrust.objects.filter(
                NHSEnglandRegionCode=hospital_organisation.NHSEnglandRegionCode).all()
        elif abstraction_level == 'open_uk':
            hospital_list = HospitalTrust.objects.filter(
                OPENUKNetworkCode=hospital_organisation.OPENUKNetworkCode).all()
        elif abstraction_level == 'country':
            hospital_list = HospitalTrust.objects.filter(
                CountryONSCode=hospital_organisation.CountryONSCode).all()
        else:
            raise ValueError('No hospital name supplied')

    for hospital in hospital_list:
        # loop through all hospitals in curated list
        hospital_kpis = KPI.objects.filter(
            hospital_organisation=hospital
        ).all()
        if hospital_kpis.count() > 0:
            for hospital_kpi in hospital_kpis:
                # loop through all kpis for that hospital and add to total

                if kpi_name == "all":
                    # if all KPIs requested
                    kpis["paediatrician_with_expertise_in_epilepsies"] += hospital_kpi.paediatrician_with_expertise_in_epilepsies
                    kpis["epilepsy_specialist_nurse"] += hospital_kpi.epilepsy_specialist_nurse
                    kpis["tertiary_input"] += hospital_kpi.tertiary_input
                    kpis["epilepsy_surgery_referral"] += hospital_kpi.epilepsy_surgery_referral
                    kpis["ecg"] += hospital_kpi.ecg
                    kpis["mri"] += hospital_kpi.mri
                    kpis["assessment_of_mental_health_issues"] += hospital_kpi.assessment_of_mental_health_issues
                    kpis["mental_health_support"] += hospital_kpi.mental_health_support
                    kpis["sodium_valproate"] += hospital_kpi.sodium_valproate
                    kpis["comprehensive_care_planning_agreement"] += hospital_kpi.comprehensive_care_planning_agreement
                    kpis["patient_held_individualised_epilepsy_document"] += hospital_kpi.patient_held_individualised_epilepsy_document
                    kpis["patient_carer_parent_agreement_to_the_care_planning"] += hospital_kpi.patient_carer_parent_agreement_to_the_care_planning
                    kpis["care_planning_has_been_updated_when_necessary"] += hospital_kpi.care_planning_has_been_updated_when_necessary
                    kpis["comprehensive_care_planning_content"] += hospital_kpi.comprehensive_care_planning_content
                    kpis["parental_prolonged_seizures_care_plan"] += hospital_kpi.parental_prolonged_seizures_care_plan
                    kpis["water_safety"] += hospital_kpi.water_safety
                    kpis["first_aid"] += hospital_kpi.first_aid
                    kpis["general_participation_and_risk"] += hospital_kpi.general_participation_and_risk
                    kpis["service_contact_details"] += hospital_kpi.service_contact_details
                    kpis["sudep"] += hospital_kpi.sudep
                    kpis["school_individual_healthcare_plan"] += hospital_kpi.school_individual_healthcare_plan
                    kpis["total_number_of_cases"] += 1
                else:
                    # if only an individual kpi requested
                    kpis[kpi_name] += getattr(hospital_kpi, kpi_name, 0)
                    kpis["total_number_of_cases"] += 1
    return kpis
