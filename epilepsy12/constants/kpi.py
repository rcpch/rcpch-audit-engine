INDIVIDUAL_KPI_MEASURES = (
    (
        "paediatrician_with_expertise_in_epilepsies",
        "Paediatrician with expertise in epilepsies",
    ),
    ("epilepsy_specialist_nurse", "Epilepsy specialist nurse"),
    ("tertiary_input", "Tertiary input"),
    ("epilepsy_surgery_referral", "Epilepsy surgery referral"),
    ("ecg", "ECG"),
    ("mri", "MRI"),
    ("assessment_of_mental_health_issues", "Assessment of mental health issues"),
    ("mental_health_support", "Mental health support"),
    ("sodium_valproate", "Sodium valproate"),
    ("comprehensive_care_planning_agreement", "Comprehensive care planning agreement"),
    (
        "patient_held_individualised_epilepsy_document",
        "Patient-held individualised epilepsy document",
    ),
    (
        "patient_carer_parent_agreement_to_the_care_planning",
        "Patient/Carer agreement to the care planning",
    ),
    (
        "care_planning_has_been_updated_when_necessary",
        "Care planning has been updated when necessary",
    ),
    ("comprehensive_care_planning_content", "Comprehensive care planning content"),
    ("parental_prolonged_seizures_care_plan", "Parental prolonged seizures care plan"),
    ("water_safety", "Water safety"),
    ("first_aid", "First aid"),
    ("general_participation_and_risk", "General participation and risk"),
    ("service_contact_details", "Service contact details"),
    ("sudep", "SUDEP (sudden unexplained death in epilepsy)"),
    ("school_individual_healthcare_plan", "School individual healthcare plan"),
)
KPI_SCORE = {
    "NOT_SCORED": None,
    "FAIL": 0,
    "PASS": 1,
    "INELIGIBLE": 2,
}

KPI_MAP = {
    "1": "paediatrician_with_expertise_in_epilepsies",
    "2": "epilepsy_specialist_nurse",
    "3": "tertiary_input",
    "3b": "epilepsy_surgery_referral",
    "4": "ecg",
    "5": "mri",
    "6": "assessment_of_mental_health_issues",
    "7": "mental_health_support",
    "8": "sodium_valproate",
    "9a": "comprehensive_care_planning_agreement",
    "9aa": "patient_held_individualised_epilepsy_document",
    "9ab": "patient_carer_parent_agreement_to_the_care_planning",
    "9ac": "care_planning_has_been_updated_when_necessary",
    "9b": "comprehensive_care_planning_content",
    "9ba": "parental_prolonged_seizures_care_plan",
    "9bb": "water_safety",
    "9bc": "first_aid",
    "9bd": "general_participation_and_risk",
    "9be": "service_contact_details",
    "9bf": "sudep",
    "10": "school_individual_healthcare_plan",
}
KPI_LABEL_MAP = {
    "1": "Paediatrician with expertise in epilepsies",
    "2": "Epilepsy specialist nurse",
    "3": "Tertiary input",
    "3b": "Epilepsy surgery referral",
    "4": "ECG",
    "5": "MRI",
    "6": "Assessment of mental health issues",
    "7": "Mental health support",
    "8": "Sodium valproate and topiramate",
    "9a": "Comprehensive care planning agreement",
    "9aa": "Patient-held individualised epilepsy document",
    "9ab": "Patient/Carer agreement to the care planning",
    "9ac": "Care planning has been updated when necessary",
    "9b": "Comprehensive care planning content",
    "9ba": "Parental prolonged seizures care plan",
    "9bb": "Water safety",
    "9bc": "First aid",
    "9bd": "General participation and risk",
    "9be": "Service contact details",
    "9bf": "SUDEP (sudden unexplained death in epilepsy)",
    "10": "School individual healthcare plan",
}

"""
1. Paediatrician with expertise in Epilepsy within 2 weeks - % of children and young people with epilepsy, with input by a 'consultant paediatrician with expertise in epilepsies' within 2 weeks of initial referral

    2. Access to Epilepsy Specialist Nurse - % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

    3. Tertiary Input	 - % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care

        3b. Epilepsy Surgery Referral	 - % of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral

    4. ECG  - % of children and young people with convulsive seizures and epilepsy, with an ECG at first year

    5. MRI within 6 weeks - % of children and young people with defined indications for an MRI, who had timely MRI within 6 weeks of request

    6. Assessment of Mental Health Issues  - %  of children and young people with epilepsy where there is documented evidence that they have been asked about mental health either through clinical screening, or a questionnaire/measure

    7. Mental Health Support - %  of children and young people with epilepsy and a mental health problem who have evidence of mental health support

    8. Medication and Reproduction Risks - % of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

    9. (a) Care Planning Agreement  - % of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary

            9a. Patient held individualised epilepsy document/copy of clinic letter that includes care planning information - % of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information

            9b. Patient/carer/parent agreement to the care planning - % of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate

            9c. Care planning has been updated when necessary - % of children and young people with epilepsy after 12 months where there is evidence that the care plan has been updated where necessary

    9. (b) Care Planning Components - % of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning

            9a. Parental prolonged seizures care plan
                Percentage of children and young people with epilepsy who have been prescribed rescue medication and have evidence of a written prolonged seizures plan.

            9b. Water safety
                Percentage of children and young people with epilepsy with evidence of discussion regarding water safety.

            9c. First aid
                Percentage of children and young people with epilepsy with evidence of discussion regarding first aid.

            9d. General participation and risk
                Percentage of children and young people with epilepsy with evidence of discussion regarding general participation and risk.

            9e. SUDEP
                Percentage of children and young people with epilepsy with evidence of discussion regarding SUDEP.

            9f. Service contact details
                Percentage of children and young people with epilepsy with evidence of being given service contact details.

    10. School Individual Health Care Plan - % of children and young people with epilepsy aged 4 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment..
"""
