from django.core.validators import MaxValueValidator
from django.contrib.gis.db import models

from simple_history.models import HistoricalRecords
import multiselectfield

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

# TODO MRB: re-use the existing yes/no constants
def YesNoUncertainField(help_text=None):
    return models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True, blank=True, help_text=help_text)

def MultiSelectField(choices, help_text=None):
    return multiselectfield.MultiSelectField(choices=choices, null=True, blank=True, help_text=help_text)

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

    S01WTEConsultants = DecimalField() # 1.1

    S01WTEConsultantsEpilepsy = DecimalField() # 1.2

    S01EpilepsyClinicalLead = YesNoField() # 1.3
    S01EpilepsyClinicalLeadTitle = TextField()
    S01EpilepsyClinicalLeadFirstName = TextField()
    S01EpilepsyClinicalLeadSurname = TextField()

    S01WTEEpilepsySpecialistNurses = DecimalField() # 1.4
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
    }) #1.4i

    # New! https://github.com/rcpch/rcpch-audit-engine/issues/876#issuecomment-2312271287
    S01JobPlannedHoursPerWeekLeadershipQIActivities = PositiveIntegerField() # 1.5


    # 2. Epilepsy Clinic configuration

    S02DefinedEpilepsyClinics = YesNoField() # 2.1
    S02EpilepsyClinicsPerWeek = DecimalField() # 2.1i
    S02Consultant20Mins = YesNoField() # 2.1ii

    S02TFC223 = ChoiceField(choices={
        1: 'Not applicable',
        2: 'Yes',
        3: 'No, not at all',
        4: 'No, in development'
    }) # 2.2


    # 3. Tertiary provision

    S03WTEPaediatricNeurologists = DecimalField() # 3.1

    S03PathwaysTertiaryPaedNeurology = YesNoField() # 3.2

    S03PaedNeurologistsDirectReferrals = YesNoField() # 3.3

    S03SatellitePaediatricNeurologyClinics = YesNoField() # 3.4

    # 3.5 itself has no representation in the model, we construct it from the help text alone
    S03CommenceKetogenicDiet = YesNoUncertainField() # 3.5i
    S03ReviewKetogenicDiet = YesNoUncertainField() # 3.5ii
    S03VNSInsertion = YesNoUncertainField() # 3.5iii
    S03VNSReview = YesNoUncertainField() # 3.5iv

    
    # 4. Investigations

    # 4.1 itself has no representation in the model, we construct it from the help text alone
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
    S04WholeGenomeSequencing = YesNoUncertainField() # 4.1xiv


    # 5. Service Contact

    S05ContactEpilepsyServiceForSpecialistAdvice = YesNoField(help_text={
        "section": "5. Service Contact",
        "question_number": "5.1",
        "label": "Can patients contact the Epilepsy service for specialist advice?",
        "reference": "e.g. from a paediatrician with expertise, paediatric neurologist or ESN) between scheduled reviews?"
    })
    S05AdviceAvailableAllWeekdays = YesNoField(help_text={
        "section": "5. Service Contact",
        "question_number": "5.1.1",
        "parent_question_number": "5.1",
        "label": "Is this available all weekdays?"
    })
    S05AdviceAvailableAllOutOfHours = YesNoField(help_text={
        "section": "5. Service Contact",
        "question_number": "5.1.2",
        "parent_question_number": "5.1",
        "label": "Is this available out of hours?"
    })
    S05AdviceAvailable52WeeksPerYear = YesNoField(help_text={
        "section": "5. Service Contact",
        "question_number": "5.1.3",
        "parent_question_number": "5.1",
        "label": "Is this available 52 weeks per year?"
    })

    S05TypicalTimeToAchieveSpecialistAdvice = ChoiceField(choices={
        1: 'Same working day',
        2: 'By next working day',
        3: 'Within 3-4 working days',
        4: 'Within a working week'
    }, help_text={
        "section": "5. Service Contact",
        "question_number": "5.2",
        "label": "What would your service describe as a typical time for a parent or young person to achieve specialist advice?"
    })

    S05WhoProvidesSpecialistAdvice = ChoiceField(choices={
        1: 'ESN',
        2: 'Consultant Paediatrician with expertise in epilepsy',
        3: 'Paediatric neurologist',
        4: 'Trainee paediatric neurologist',
        5: 'Other'
    }, help_text={
        "section": "5. Service Contact",
        "question_number": "5.3",
        "label": "Who typically provides the initial ‘specialist advice’?"   
    })
    S05WhoProvidesSpecialistAdviceOther = TextField(help_text={
        "section": "5. Service Contact",
        "parent_question_number": "5.3",
        "parent_question_value": 5,
        "label": "Other"
    })

    S05evidenceclearpointofcontact = YesNoField(help_text={
        "section": "5. Service Contact",
        "question_number": "5.4",
        "label": "Do you have evidence of a clear point of contact for non‐paediatric professionals seeking paediatric epilepsy support?",
        "reference": "(e.g. school, social care, CAMHS, adult services)"
    })


    # 6. Young People and Transition

    S06AgreedReferralPathwaysAdultServices = YesNoField(help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.1",
        "label": "Do you have agreed referral pathways to adult services?"
    })

    S06OutpatientClinicYoungPeopleEpilepsies = YesNoField(help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.2",
        "label": "Do you have a specific outpatient clinic for 'young people' with epilepsies that supports transition?"
    })
    S06WhatAgeDoesThisClinicAcceptYoungPeople = PositiveIntegerField(help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.2i",
        "parent_question_number": "6.2",
        "label": "From what age does this clinic typically accept young people?"
    })

    S06ServiceForEpilepsyBothAdultAndPaed = YesNoField(help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.3",
        "label": "Do you have an outpatient service for epilepsy where there is a presence of both adult and paediatric professionals??"
    })
    S06IsThisUsually = ChoiceField(choices={
        1: 'A single joint appointment',
        2: 'A series of several joint appointments',
        3: 'A flexible approach including mixture of joint or individual reviews',
        4: 'Other'
    }, help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.3i",
        "parent_question_number": "6.3",
        "label": "Is this usually:"
    })
    S06IsThisUsuallyOther = TextField(help_text={
        "section": "6. Young People and Transition",
        "parent_question_number": "6.3i",
        "parent_question_value": 4,
        "label": "Other"
    })
    S06PercentageOfYoungPeopleTransferred = models.PositiveIntegerField(null=True, blank=True, validators=[
        MaxValueValidator(100)
    ], help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.3ii",
        "parent_question_number": "6.3",
        "label": "What percentage of young people transferred to adult services are transitioned through this process?",
        "reference": "Please provide an estimate"
    })

    S06ProfessionalsRoutinelyInvolvedInTransitionAdultESN = MultiSelectField(choices={
        1: 'Adult ESN',
        2: 'Adult Learning difficulty ESN',
        3: 'Adult Neurologist',
        4: 'Youth Worker',
        5: 'Other'
    }, help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.4",
        "label": "Which adult professionals are routinely involved in transition or transfer to adult services?"
    })
    S06ProfessionalsRoutinelyInvolvedInTransitionAdultESNOther = TextField(help_text={
        "section": "6. Young People and Transition",
        "parent_question_number": "6.4",
        "parent_question_value": 5,
        "label": "Other"
    })

    S06StructuredResourcesToSupportTransition = YesNoField(help_text={
        "section": "6. Young People and Transition",
        "question_number": "6.5",
        "label": "Do you use structured resources to support transition?",
        "reference": "e.g. Ready Steady Go"
    })


    # 7. Mental health

    # TODO MRB: in the CSV it references ADHD, ASD, Mental Health and None but in the docs it's Yes/No
    S07ScreenForIssuesMentalHealth = YesNoField(help_text={
        "section": "7. Mental health",
        "question_number": "7.1",
        "label": "In the paediatric epilepsy service do you routinely formally screen for mental health disorders?"
    })
    S07MentalHealthQuestionnaire = MultiSelectField(choices={
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
    }, help_text={
        "section": "7. Mental health",
        "question_number": "7.1i",
        "parent_question_number": "7.1",
        "label": "Which questionnaires do you use?",
    })
    S07MentalHealthQuestionnaireOther = TextField(help_text={
        "section": "7. Mental health",
        "parent_question_number": "7.1i",
        "parent_question_value": 12,
        "label": "Other"
    })

    S07MentalHealthAgreedPathway = MultiSelectField(choices={
        1: 'Anxiety',
        # TODO MRB: not in the word doc but in the source CSV
        2: 'Depression',
        3: 'Mood Disorders',
        4: 'Non-epileptic attack disorders',
        5: 'Other'
    }, help_text={
        "section": "7. Mental health",
        "question_number": "7.2",
        "label": "Do you have agreed referral pathways for children with any of the following mental health concerns?",
    })
    S07MentalHealthAgreedPathwayOther = TextField(help_text={
        "section": "7. Mental health",
        "parent_question_number": "7.2",
        "parent_question_value": 5,
        "label": "Other"
    })

    S07MentalHealthProvisionEpilepsyClinics = YesNoField(help_text={
        "section": "7. Mental health",
        "question_number": "7.3",
        "label": "Do you facilitate mental health provision within epilepsy clinics?"
    })
    S07DoesThisComprise = ChoiceField(choices={
        1: 'Epilepsy Clinics where mental health professionals can provide direct co-located clinical care',
        2: 'MDT meetings where epilepsy and mental health professionals discuss individual patients',
        3: 'Other'
    }, help_text={
        "section": "7. Mental health",
        "question_number": "7.3.1",
        "parent_question_number": "7.3",
        "label": "Does this comprise:"
    })
    S07DoesThisCompriseOther = TextField(help_text={
        "section": "7. Mental health",
        "parent_question_number": "7.3.1",
        "parent_question_value": 3,
        "label": "Other"
    })

    S07CurrentTrustActionPlanCoLocatedMentalHealth = YesNoField(help_text={
        "section": "7. Mental health",
        "question_number": "7.3.2",
        "parent_question_number": "7.3",
        # If no to question 7.3
        "parent_question_value": False,
        "label": "Is there a current action plan describing steps towards co-located mental health provision within epilepsy clinics?",
    })

    S07TrustAchieve = MultiSelectField(choices={
        1: 'Clinical psychology assessment',
        2: 'Educational psychology assessment',
        3: 'Formal developmental assessment',
        4: 'Neurospsychology assessment',
        5: 'Psychiatric assessment',
        6: 'Cannot achieve any of the above'
    }, help_text={
        "section": "7. Mental health",
        "question_number": "7.4",
        "label": "Can you refer to any of the following where required, either within or outside of your audit unit?"
    })


    # 8. Neurodevelopmental support

    # TODO MRB: this is not in the CSV?
    S08ScreenForNeurodevelopmentalConditions = YesNoField(help_text={
        "section": "8. Neurodevelopmental support",
        "question_number": "8.1",
        "label": "Do you routinely formalling screen for neurodevelopmental conditions?"
    })

    S08AgreedReferralCriteriaChildrenNeurodevelopmental = MultiSelectField(choices={
        1: 'ADHD',
        2: 'ASD',
        3: 'Behavioural difficulties',
        4: 'Developmental Coordination Disorder',
        5: 'Intellectual disability/Global developmental delay',
        6: 'Learning disabilities',
        8: 'None of the above',
        7: 'Other'
    }, help_text={
        "section": "8. Neurodevelopmental support",
        "question_number": "8.2",
        "label": "Do you have agreed referral criteria for children with any of the following neurodevelopmental conditions?"
    })
    S08AgreedReferralCriteriaChildrenNeurodevelopmentalOther = TextField(help_text={
        "section": "8. Neurodevelopmental support",
        "label": "Other",
        "parent_question_number": "8.2",
        "parent_question_value": 7
    })


    # 9. Care Planning

    S09ComprehensiveCarePlanningChildrenEpilepsy = YesNoField(help_text={
        "section": "9. Care Planning",
        "question_number": "9.1",
        "label": "Do you undertake comprehensive care planning for children with epilepsy?"
    })


    # 10. Patient Database/Register

    S10TrustMaintainADatabaseOfChildrenWithEpilepsy = ChoiceField(choices={
        1: 'Yes, for all children',
        2: 'Yes, for some children',
        3: 'No'
    }, help_text={
        "section": "10. Patient Database/Register",
        "question_number": "10.1",
        "label": "Does you maintain a database or register of children with epilepsies?",
        "reference": "Other than the epilepsy12 audit itself"
    })
