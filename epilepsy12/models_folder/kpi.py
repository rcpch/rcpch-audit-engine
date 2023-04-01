from django.db import models
from django.utils.translation import gettext_lazy as _
from .help_text_mixin import HelpTextMixin


class KPI(models.Model, HelpTextMixin):
    """
    Key performance indicator fields.

    The 12 key performance indicators, as specified by RCPCH, are:

    1. Paediatrician with expertise in epilepsies - % of children and young people with epilepsy, with input by a 'consultant paediatrician with expertise in epilepsies' within 2 weeks of initial referral

    2. Epilepsy Specialist Nurse - % of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care

    3. Tertiary input	 - % of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care

        3b. Epilepsy surgery referral	 - % of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral

    4. ECG  - % of children and young people with convulsive seizures and epilepsy, with an ECG at first year

    5. MRI	 - % of children and young people with defined indications for an MRI, who had who had timely MRI within 6 weeks of request

    6. Assessment of mental health issues  - %  of children with epilepsy where there is documented evidence that they have been asked about mental health either through clinical screening, or a questionnaire/measure

    7. Mental health support - %  of children with epilepsy and a mental health problem who have evidence of mental health support"

    8. Sodium Valproate - % of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

    9. (a) Comprehensive Care Planning agreement  - % of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary

            9a. Patient held individualised epilepsy document/copy of clinic letter that includes care planning information - % of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information

            9b. Patient/carer/parent agreement to the care planning - % of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate

            9c. Care planning has been updated when necessary - % of children and young people with epilepsy after 12 months where there is evidence that the care plan has been updated where necessary

    9. (b) Comprehensive Care Planning content - % of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning

            9a. Parental prolonged seizures care plan

            9b. Water safety

            9c. First aid

            9d. General participation and risk

            9e. Service contact details

            9f. SUDEP

    10. School Individual Healthcare Plan - % of children and young people with epilepsy aged 5 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.              

    """

    """
    1. Percentage of children and young people with epilepsy, with input by a 'consultant paediatrician with expertise in epilepsies' within 2 weeks of initial referral
    
    Calculation Method
    Numerator = Number of children and young people  [diagnosed with epilepsy] at first year AND (who had [input from a paediatrician with expertise in epilepsy] OR a [input from a paediatric neurologist] within 2 weeks of initial referral. (initial referral to mean first paediatric assessment)
    Denominator = Number of and young people [diagnosed with epilepsy] at first year
    """
    paediatrician_with_expertise_in_epilepsies = models.IntegerField(
        help_text={
            'label': '1. Paediatrician with expertise in epilepsies',
            'reference': "Percentage of children and young people with epilepsy, with input by a 'consultant paediatrician with expertise in epilepsies' within 2 weeks of initial referral"
        },
        default=None,
        null=True
    )

    """
    2. Percentage of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care.
    
    Calculation Method
    Numerator= Number of children and young people [diagnosed with epilepsy] AND who had [input from or referral to an Epilepsy Specialist Nurse] by first year
    Denominator = Number ofchildren and young people [diagnosed with epilepsy] at first year
    """
    epilepsy_specialist_nurse = models.IntegerField(
        help_text={
            'label': '2. Epilepsy Specialist Nurse',
            'reference': "Percentage of children and young people with epilepsy, with input by epilepsy specialist nurse within the first year of care."
        },
        default=None,
        null=True
    )

    """
    3. Percentage of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care.
    
    Calculation Method
    Numerator = Number of children ([less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year) OR (Number of children less than 4 years old at first assessment with epilepsy AND myoclonic seizures)  OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] ) AND had [evidence of referral or involvement of a paediatric neurologist] OR [evidence of referral or involvement of CESS]
    Denominator = Number of children [less than 3 years old at first assessment] AND [diagnosed with epilepsy] OR (number of children and young people diagnosed with epilepsy who had [3 or more maintenance AEDS] at first year )OR (number of children and young people diagnosed with epilepsy  who met [CESS criteria] OR (Number of children less than 4 years old at first assessment with epilepsy AND  [myoclonic seizures])
    """
    tertiary_input = models.IntegerField(
        help_text={
            'label': '3. Tertiary input',
            'reference': "Percentage of children and young people meeting defined criteria for paediatric neurology referral, with input of tertiary care and/or CESS referral within the first year of care."
        },
        default=None,
        null=True
    )

    """
    3b. Percentage of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy AND met [CESS criteria] at first year AND had [evidence of referral or involvement of CESS]
    Denominator =Number of children and young people diagnosed with epilepsy AND met CESS criteria at first year
    """
    epilepsy_surgery_referral = models.IntegerField(
        help_text={
            'label': '3b. Epilepsy surgery referral',
            'reference': "Percentage of ongoing children and young people meeting defined epilepsy surgery referral criteria with evidence of epilepsy surgery referral."
        },
        default=None,
        null=True
    )

    """
    4. Percentage of children and young people with convulsive seizures and epilepsy, with an ECG at first year.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year AND who have [12 lead ECG obtained]
    Denominator = Number of children and young people diagnosed with epilepsy at first year AND with convulsive episodes at first year
    """
    ecg = models.IntegerField(
        help_text={
            'label': '4. ECG',
            'reference': "Percentage of children and young people with convulsive seizures and epilepsy, with an ECG at first year."
        },

        default=None,
        null=True
    )

    """
    5. Percentage of children and young people with defined indications for an MRI, who had who had timely MRI within 6 weeks of request
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND who are NOT JME or JAE or CAE or CECTS/Rolandic OR number of children aged under 2 years at first assessment with a diagnosis of epilepsy at first year AND who had an MRI within 6 weeks of request
    Denominator = Number of children and young people diagnosed with epilepsy at first year AND ((who are NOT JME or JAE or CAE or BECTS) OR (number of children aged under  2 years  at first assessment with a diagnosis of epilepsy at first year))
    """
    mri = models.IntegerField(
        help_text={
            'label': '5. MRI',
            'reference': "Percentage of children and young people with defined indications for an MRI, who had who had timely MRI within 6 weeks of request"
        },

        default=None,
        null=True
    )

    """
    6. Percentage of children with epilepsy where there is documented evidence that they have been asked about mental health either through clinical screening, or a questionnaire/measure.

    Calculation Method
    Numerator = Number of children and young people over 5 years diagnosed with epilepsy AND who had documented evidence of enquiry or screening for their mental health
    Denominator = = Number of children and young people over 5 years diagnosed with epilepsy
    """
    assessment_of_mental_health_issues = models.IntegerField(
        help_text={
            'label': '6. Assessment of mental health issues',
            'reference': "Percentage of children with epilepsy where there is documented evidence that they have been asked about mental health either through clinical screening, or a questionnaire/measure."
        },
        default=None,
        null=True
    )

    """
    7. Percentage of children with epilepsy and a mental health problem who have evidence of mental health support
    
    Calculation Method
    Numerator =  Number of children and young people diagnosed with epilepsy AND had a mental health issue identified AND had evidence of mental health support received
    Denominator= Number of children and young people diagnosed with epilepsy AND had a mental health issue identified
    """
    mental_health_support = models.IntegerField(

        help_text={
            'label': '7. Mental health support',
            'reference': "Percentage of children with epilepsy and a mental health problem who have evidence of mental health support"
        },
        default=None,
        null=True
    )

    """
    8. Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed

    Calculation Method
    Numerator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate AND annual risk acknowledgement forms completed AND pregnancy prevention programme in place
    Denominator = Number of females aged 12 and above diagnosed with epilepsy at first year AND on valproate
    """
    sodium_valproate = models.IntegerField(
        help_text={
            'label': '8. Sodium Valproate',
            'reference': "Percentage of all females 12 years and above currently on valproate treatment with annual risk acknowledgement form completed"
        },
        default=None,
        null=True
    )

    """
    9A. Percentage of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with an individualised epilepsy document or copy clinic letter that includes care planning information )AND evidence of agreement AND care plan is up to date including elements where appropriate as below 
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    comprehensive_care_planning_agreement = models.IntegerField(
        help_text={
            'label': '9A. Comprehensive care planning agreement',
            'reference': "Percentage of children and young people with epilepsy after 12 months where there is evidence of a comprehensive care plan that is agreed between the person, their family and/or carers and primary and secondary care providers, and the care plan has been updated where necessary."
        },
        default=None,
        null=True
    )

    """
    9a. Percentage of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND( with individualised epilepsy document or copy clinic letter that includes care planning information )
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    patient_held_individualised_epilepsy_document = models.IntegerField(

        help_text={
            'label': '9a. Patient-held individualised epilepsy document/copy of clinic letter that includes care planning information',
            'reference': "Percentage of children and young people with epilepsy after 12 months that had an individualised epilepsy document with individualised epilepsy document or a copy clinic letter that includes care planning information."
        },
        default=None,
        null=True
    )

    """
    9b. Percentage of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of agreement
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    patient_carer_parent_agreement_to_the_care_planning = models.IntegerField(
        help_text={
            'label': '9b. Patient/carer/parent agreement to the care planning',
            'reference': "Percentage of children and young people with epilepsy after 12 months where there was evidence of agreement between the person, their family and/or carers as appropriate."
        },
        default=None,
        null=True
    )

    """
    9c. Percentage of children and young people with epilepsy after 12 months where there is evidence that the care plan has been updated where necessary.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with care plan which is updated where necessary
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    care_planning_has_been_updated_when_necessary = models.IntegerField(
        help_text={
            'label': '9c. Care planning has been updated when necessary',
            'reference': "Percentage of children and young people with epilepsy after 12 months where there is evidence that the care plan has been updated where necessary."
        },
        default=None,
        null=True
    )

    """
    9B. Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning.
    
    Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND evidence of written prolonged seizures plan if prescribed rescue medication AND evidence of discussion regarding water safety AND first aid AND participation and risk AND service contact details AND SUDEP
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    comprehensive_care_planning_content = models.IntegerField(
        help_text={
            'label': '9B. Comprehensive care planning content',
            'reference': "Percentage of children diagnosed with epilepsy with documented evidence of communication regarding core elements of care planning."
        },
        default=None,
        null=True
    )

    """
    
    9a. Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication AND evidence of a written prolonged seizures plan 
    Denominator = Number of children and young people diagnosed with epilepsy at first year AND prescribed rescue medication
    """
    parental_prolonged_seizures_care_plan = models.IntegerField(
        help_text={
            'label': '9a. Parental prolonged seizures care plan',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    9b. Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding water safety
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    water_safety = models.IntegerField(
        help_text={
            'label': '9b. Water safety',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    
    9c. Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding first aid
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    first_aid = models.IntegerField(
        help_text={
            'label': '9c. First aid',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    
    9d. Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion regarding general participation and risk
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    general_participation_and_risk = models.IntegerField(
        help_text={
            'label': '9d. General participation and risk',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    
    9e. Calculation Method
    Numerator = Number of children and young people diagnosed with epilepsy at first year AND with evidence of discussion of been given service contact details
    Denominator = Number of children and young people diagnosed with epilepsy at first year
    """
    service_contact_details = models.IntegerField(
        help_text={
            'label': '9e. Service contact details',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    
    9f. Calculation Method
    Numerator = Number of children diagnosed with epilepsy AND had evidence of discussions regarding SUDEP AND evidence of a written prolonged seizures plan at first year
    Denominator = Number of children diagnosed with epilepsy at first year
    """
    sudep = models.IntegerField(
        help_text={
            'label': '9f. Sudden unexplained death in epilepsy',
            'reference': ""
        },
        default=None,
        null=True
    )

    """
    10. School Individual Healthcare Plan

    Percentage of children and young people with epilepsy aged 5 years and above with evidence of a school individual healthcare plan by 1 year after first paediatric assessment.	
    
    Calculation Method
    Numerator = Number of children and young people aged 5 years and above diagnosed with epilepsy at first year AND with evidence of EHCP
    Denominator =Number of children and young people aged 5 years and above diagnosed with epilepsy at first year
    """
    school_individual_healthcare_plan = models.IntegerField(
        help_text={
            'label': '10. School individualised health care plan',
            'reference': ""
        },
        default=None,
        null=True
    )

    organisation = models.ForeignKey(
        "epilepsy12.Organisation",
        on_delete=models.CASCADE
    )

    parent_trust = models.CharField(
        max_length=250
    )

    class Meta:
        verbose_name = _("KPI ")
        verbose_name_plural = _("KPIs")

    def __str__(self):
        return f'KPI for child in {self.organisation.OrganisationName}({self.parent_trust})'
