from django.core.validators import MaxValueValidator
from django.contrib.gis.db import models

from simple_history.models import HistoricalRecords
from multiselectfield import MultiSelectField

from .entities.trust import Trust
from .entities.local_health_board import LocalHealthBoard

from .help_text_mixin import HelpTextMixin
from .time_and_user_abstract_base_classes import TimeStampAbstractBaseClass, UserStampAbstractBaseClass

YES_NO_UNCERTAIN = {
    1: 'Yes',
    2: 'No',
    3: 'Uncertain'
}

def DecimalField(help_text=None):
    return models.DecimalField(null=True, blank=True, max_digits=7, decimal_places=3, help_text=help_text)

def YesNoField(help_text=None):
    return models.BooleanField(null=True, blank=True, help_text=help_text)

def TextField(help_text=None):
    return models.CharField(null=True, blank=True, help_text=help_text)

def PositiveIntegerField(help_text=None):
    return models.PositiveIntegerField(null=True, blank=True, help_text=help_text)

def ChoiceField(choices, help_text=None):
    return models.PositiveIntegerField(choices=choices, null=True, blank=True, help_text=help_text)

YesNoUncertainField = lambda: models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True, blank=True)


class OrganisationalAuditSubmissionPeriod(models.Model):
    year = models.PositiveIntegerField()
    is_open = models.BooleanField(default=False)

    def __str__(self):
        return f"Organisational Audit Submission Period {self.year}"


class OrganisationalAuditSubmission(TimeStampAbstractBaseClass, UserStampAbstractBaseClass, HelpTextMixin):
    submission_period = models.ForeignKey(OrganisationalAuditSubmissionPeriod, on_delete=models.CASCADE)

    # Either
    trust = models.ForeignKey(Trust, null=True, on_delete=models.SET_NULL)
    # or
    local_health_board = models.ForeignKey(LocalHealthBoard, null=True, on_delete=models.SET_NULL)

    history = HistoricalRecords()

    @property
    def _history_user(self):
        return self.updated_by

    @_history_user.setter
    def _history_user(self, value):
        self.updated_by = value

    # These field names mostly match the CSV export format from the old system for convenience

    # 1. Workforce

    S01WTEConsultants = DecimalField(help_text={
        "question_number": "1.1",
        "label": "How many whole time equivalent general paediatric consultants do you employ?",
        "reference": """
            <p>
                Includes general paediatric consultants with 'expertise in epilepsy' (community or hospital based).
            </p>
            <p>
                Audit Unit - The audit unit is defined by your audit unit profile. Most audit units will include one or more secondary tier paediatric services
                grouped together using pragmatic boundaries agreed by the paediatric audit unit lead, the project team and the tertiary link.
            </p>
            <p>
                WTE = whole time equivalent. E.g One full time post is 1 WTE; Someone working 3 days a week = 0.6 WTE. 2 people both working 3 days a week = 1.2 WTE
            </p>
        """
    })

    S01WTEConsultantsEpilepsy = DecimalField(help_text={
        "question_number": "1.2",
        "label": "Of these, how many have an ‘expertise in epilepsy’?",
        "reference": """
            <p>
                Answer using whole time equivalent again. Paediatric neurologists should not be included in your response.
            </p>
            <p>
                Paediatrician with expertise - Paediatric consultant (or associate specialist) defined by themselves, their employer and tertiary service/network as having: training and continuing education in epilepsies AND peer review of practice AND regular audit of diagnosis (e.g. participation in Epilepsy12).
            </p>
        """
    })

    S01EpilepsyClinicalLead = YesNoField(help_text={
        "question_number": "1.3",
        "label": "Do you have a defined paediatric epilepsy clinical lead?"
    })
    S01EpilepsyClinicalLeadTitle = TextField(help_text={
        "parent_question_number": "1.3",
        "label": "Title"
    })
    S01EpilepsyClinicalLeadFirstName = TextField(help_text={
        "parent_question_number": "1.3",
        "label": "First name"
    })
    S01EpilepsyClinicalLeadSurname = TextField(help_text={
        "parent_question_number": "1.3",
        "label": "Surname"
    })

    S01WTEEpilepsySpecialistNurses = DecimalField(help_text={
        "question_number": "1.4",
        "label": "How many WTE paediatric epilepsy specialist nurses do you employ?",
        "reference": "Paediatric ESN - A children’s nurse with a defined role and specific qualification and/or training in children’s epilepsies"
    })
    # TODO MRB: do they want this split out into separate columns as per the template CSV
    S01ESNFunctions = MultiSelectField(choices={
        1: 'ED visits',
        2: 'Home visits',
        3: 'School Individual Healthcare Plan (IHP) facilitation',
        4: 'Nurse led clinics',
        5: 'Nurse prescribing',
        6: 'Rescue medication training for parents',
        7: 'Rescue medication training for schools',
        8: 'School meetings',
        9: 'Ward visits',
        10: 'None of the above'
    }, null=True, blank=True, help_text={
        "parent_question_number": "1.4",
        "question_number": "1.4i",
        "label": "Which of the following Paediatric ESN functions is the epilepsy service currently able to support?",
    }) #1.4i

    # New! https://github.com/rcpch/rcpch-audit-engine/issues/876#issuecomment-2312271287
    S01JobPlannedHoursPerWeekLeadershipQIActivities = PositiveIntegerField(help_text={
        "question_number": "1.5",
        "label": "How many job planned hours are there per week (ESN and/or paediatrician) specified for epilepsy leadership and/or QI activities?"
    })


    # 2. Epilepsy Clinic configuration

    S02DefinedEpilepsyClinics = YesNoField(help_text={
        "question_number": "2.1",
        "label": "Does the Health Board/Trust have defined epilepsy clinics seeing patients at a secondary level?",
        "reference": "A secondary level 'epilepsy clinic' is a clinic run just for children with seizures or epilepsy that takes referrals direct from GPs or emergency department (decimal answers are allowed). An ‘Epilepsy Clinic’ is defined as a paediatric clinic where all the children and young people attending have epilepsy or possible epileptic seizures."
    })
    S02EpilepsyClinicsPerWeek = DecimalField(help_text={
        "parent_question_number": "2.1",
        "question_number": "2.1i",
        "label": "On average, how many consultant (or associate specialist) led secondary level ‘epilepsy clinics’ for children or young people take place within your Health Board/Trust per week?"
    })
    S02Consultant20Mins = YesNoField(help_text={
       "parent_question_number": "2.1",
       "question_number": "2.1ii",
       "label": "Within the epilepsy clinics, does the clinic booking time allow at least 20 minutes of time with a consultant with expertise in epilepsy and an ESN? (This might be 20 min with the doctor and nurse at the same time or 20 mins each in succession)"
    })

    S02TFC223 = ChoiceField(choices={
        1: 'Not applicable',
        2: 'Yes',
        3: 'No, not at all',
        4: 'No, in development'
    }, help_text={
        "question_number": "2.2",
        # TODO MRB: hide this question for Wales
        "label": "Does the Trust currently run TFC 223 Epilepsy Best Practice Criteria (BPC) clinics?",
        "reference": "For Trusts in England only"
    })


    # 3. Tertiary provision

    S03WTEPaediatricNeurologists = DecimalField(help_text={
        "question_number": "3.1",
        "label": "How many whole-time equivalent (WTE) paediatric neurologists who manage children with epilepsy do you employ?",
        "reference": """
            <p>
                Acutely and or non-acutely.
            </p>
            <p>
                This should not include visiting neurologists who are primarily employed by another trust 
            </p>
        """
    })
    S03PathwaysTertiaryPaedNeurology = YesNoField(help_text={
        "question_number": "3.2",
        "label": "Does you have agreed referral pathways to tertiary paediatric neurology services?"
    })
    S03PaedNeurologistsDirectReferrals = YesNoField(help_text={
        "question_number": "3.3",
        "label": "Can paediatric neurologists receive direct referrals from general practice or emergency services to assess children with possible epilepsy?"
    })
    S03SatellitePaediatricNeurologyClinics = YesNoField(help_text={
        "question_number": "3.4",
        "label": "Does the trust host satellite paediatric neurology clinics?",
        "reference": """
            <p>
                e.g. a paediatric neurologist visits a site within the trust to undertake paediatric neurology clinics
            </p>
            <p>
                A satellite clinic is where a neurologist supports a clinic outside their base hospital. This might be another hospital or clinic location in their trust or another hospital or clinic location in another trust. 
            </p>
        """
    })

    S03CommenceKetogenicDiet = YesNoUncertainField() # 3.5i
    S03ReviewKetogenicDiet = YesNoUncertainField() # 3.5ii
    S03VNSInsertion = YesNoUncertainField() # 3.5iii
    S03VNSReview = YesNoUncertainField() # 3.5iv

    
    # 4. Investigations

    S04LeadECG = YesNoUncertainField() # 4.1i
    S04AwakeMRI = YesNoUncertainField() # 4.1ii
    S04MriWithSedation = YesNoUncertainField() # 4.1iii
    S04MriWithGeneralAnaesthetic = YesNoUncertainField() # 4.1iv
    S04StandardEeg = YesNoUncertainField() # 4.1v
    S04SleepDeprivedEeg = YesNoUncertainField() # 4.1vi
    S04MelatoninInducedEeg = YesNoUncertainField() # 4.1vii
    S04SedatedEeg = YesNoUncertainField() # 4.1viii
    S042448HAmbulatoryEeg = YesNoUncertainField() # 4.1ix
    S04InpatientVideoTelemetry = YesNoUncertainField() # 4.1x
    S04OutpatientVideoTelemetry = YesNoUncertainField() # 4.1xi
    S04HomeVideoTelemetry = YesNoUncertainField() # 4.1xii
    S04PortableEEGOnWardAreaWithinTrust = YesNoUncertainField() # 4.1xiii
    # TODO MRB: do we need an entry for requesting and consenting of Whole Genome Sequencing?


    # 5. Service Contact

    S05ContactEpilepsyServiceForSpecialistAdvice = YesNoField() # 5.1
    S05AdviceAvailableAllWeekdays = YesNoField() # 5.1.1
    S05AdviceAvailableAllOutOfHours = YesNoField() # 5.1.2
    S05AdviceAvailable52WeeksPerYear = YesNoField() # 5.1.3

    S05TypicalTimeToAchieveSpecialistAdvice = ChoiceField({
        1: 'Same working day',
        2: 'By next working day',
        3: 'Within 3-4 working days',
        4: 'Within a working week'
    }) # 5.2

    S05WhoProvidesSpecialistAdvice = ChoiceField({
        1: 'ESN',
        2: 'Consultant Paediatrician with expertise in epilepsy',
        3: 'Paediatric neurologist',
        4: 'Trainee paediatric neurologist',
        5: 'Other'
    }) # 5.3
    S05WhoProvidesSpecialistAdviceOther = TextField() # 5.3
    S05evidenceclearpointofcontact = YesNoField() # 5.4


    # 6. Young People and Transition

    S06AgreeedReferralPathwaysAdultServices = YesNoField() # 6.1

    S06OutpatientClinicYoungPeopleEpilepsies = YesNoField() # 6.2
    S06WhatAgeDoesThisClinicAcceptYoungPeople = PositiveIntegerField() # 6.2i

    S06ServiceForEpilepsyBopthAdultAndPaed = YesNoField() # 6.3
    S06IsThisUsually = ChoiceField({
        1: 'A single joint appointment',
        2: 'A series of several joint appointments',
        3: 'A flexible appraoch including mixture of joint or individual reviews',
        4: 'Other'
    }) # 6.3i
    S06IsThisUsuallyOther = TextField() # 6.3i
    S06PercentageOfYoungPeopleTransferred = models.PositiveIntegerField(null=True, blank=True, validators=[
        MaxValueValidator(100)
    ]) # 6.3ii

    S06ProfessionalsRoutinelyInvolvedInTransitionAdultESN = ChoiceField({
        1: 'Adult ESN',
        2: 'Adult Learning difficulty ESN',
        3: 'Adult Neurologist',
        4: 'Youth Worker',
        5: 'Other'
    }) # 6.4
    S06ProfessionalsRoutinelyInvolvedInTransitionAdultESNOther = TextField() # 6.4

    S06StructuredResourcesToSupportTransition = YesNoField() # 6.5


    # 7. Mental health

    # TODO MRB: in the CSV it references ADHD, ASD, Mental Health and None but in the docs it's Yes/No
    S07ScreenForIssuesMentalHealth = YesNoField() # 7.1
    S07MentalHealthQuestionnaire = ChoiceField({
        1: 'BDI - Beck Depression Inventory',
        2: "Connor's Questionnaire",
        3: 'Emotional Thermometers Tool',
        4: 'GAD - Generalised Anxiety Disorder',
        5: 'GAD 2 - Generalised Anxiety Disorder 2',
        6: 'GAD 7 - Generalised Anxiety Disorder 7',
        7: 'HADS - Hospital Anxiety and Depression Scale',
        8: 'MFQ - Mood and Feelings Questionnaire (Child, Parent, Adult versions)',
        9: 'NDDI-E Neurological Disorders Depression Inventory for Epilepsy',
        10: 'PHQ - Patient Health Questionnaire, PHQ 2, PHQ 9',
        11: 'SDQ (Strengths and Difficulties Questionnaire)',
        12: 'Other'
    }) # 7.1i
    S07MentalHealthQuestionnaireOther = TextField() # 7.1i

    S07MentalHealthAgreedPathway =ChoiceField({
        1: 'Anxiety',
        2: 'Depression',
        3: 'Mood Disorders',
        4: 'Non-epileptic attack disorders',
        5: 'Other'
    }) # 7.2
    S07MentalHealthAgreedPathwayOther = TextField() # 7.2

    S07MentalHealthProvisionEpilepsyClinics = YesNoField() # 7.3
    S07DoesThisCompromise = ChoiceField({
        1: 'Epilepsy Clinics where mental health professionals can provide direct co-located clinical care',
        2: 'MDT meetings where epilepsy and mental health professionals discuss individual patients',
        3: 'Other'
    }) # 7.3i
    S07DoesThisCompromiseOther = TextField() # 7.3.1
    S07CurrentTrustActionPlanCoLocatedMentalHealth = YesNoField() # 7.3.2

    S07TrustAchieve = ChoiceField({
        1: 'Clinical psychology assessment',
        2: 'Educational psychology assessment',
        3: 'Formal developmental assessment',
        4: 'Neurospsychology assessment',
        5: 'Psychiatric assessment',
        6: 'Cannot achieve any of the above'
    }) # 7.4


    # 8. Neurodevelopmental support

    # TODO MRB: this is not in the CSV?
    S08ScreenForNeurodevelopmentalConditions = YesNoField() # 8.1
    S08AgreedReferralCriteriaChildrenNeurodevelopmental = ChoiceField({
        1: 'ADHD',
        2: 'ASD',
        3: 'Behavioural difficulties',
        4: 'Developmental Coordination Disorder',
        5: 'Intellectual disability/Global developmental delay',
        6: 'Learning disabilities',
        8: 'None of the above',
        7: 'Other'
    })  # 8.1
    S08AgreedReferralCriteriaChildrenNeurodevelopmentalOther = TextField() # 8.1


    # 9. Care Planning

    S09ComprehensiveCarePlanningChildrenEpilepsy = YesNoField() # 9.1


    # 10. Patient Database/Register

    S10TrustMaintainADatabaseOfChildrenWithEpilepsy = ChoiceField({
        1: 'Yes, for all children',
        2: 'Yes, for some children',
        3: 'No'
    }) # 10.1
