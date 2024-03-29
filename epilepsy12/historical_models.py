from django.contrib.gis.db import models
from django.contrib.gis.db.models import base, indexes
from django.contrib.gis.db.models.deletion import CASCADE
from django.contrib.gis.db.models.fields import BooleanField, CharField, DateField, DateTimeField, IntegerField
from .constants import *


class Registration(base.Model):
    SiteName = models.CharField(max_length=100)
    CaseId = models.IntegerField(max_length=30)
    SiteCode = models.CharField(max_length=10)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    TransferToActionDateTime = models.DateField()
    TransferToActionUserName = models.CharField(max_length=256)
    TransferToDateTime = models.DateField()
    TransferToSiteCode = models.CharField(max_length=10)
    TransferToCaseId = models.CharField(max_length=30)
    TransferFromActionDateTime = models.DateField()
    TransferFromActionUserName = models.CharField(max_length=256)
    TransferFromDateTime = models.DateField()
    TransferFromSiteCode = models.CharField(max_length=10)
    TransferFromCaseId = models.CharField(max_length=30)
    OriginalSiteCode = models.CharField(max_length=10)
    Closed = models.BooleanField("Locked", default=False)
    S01SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    #
    S01NHSPatient = models.CharField(max_length=2, choices=OPT_OUT)
    S01NHSCHINumber = models.CharField(max_length=10)
    S01FirstName = models.CharField(max_length=100)
    S01SurName = models.CharField(max_length=100)
    S01Gender = models.CharField(max_length=3)
    S01DOB = models.DateField()
    S01DOBDateOnly = models.DateField()
    S01DOBTimeOnly = models.DateTimeField()
    S01FirstEEG = models.CharField(max_length=2, choices=OPT_OUT)
    S01FirstEEGDate = models.DateField()
    S01FirstEEGDateDateOnly = models.DateField()
    S01FirstEEGDateTimeOnly = models.DateTimeField()
    S01FirstEEGIndicated = models.CharField(max_length=2, choices=OPT_OUT)
    S01AssessmentForTheParoxysmalHere = models.CharField(
        max_length=2, choices=OPT_OUT)
    S01ReferringHospital = models.CharField(max_length=150)
    S01ReferringPerson = models.CharField(max_length=150)
    S01TrustVerify = models.CharField(
        max_length=3, choices=TRUST_VERIFICATION_STATUS)
    S01DiagnosticStatus = models.CharField(
        max_length=2, choices=DIAGNOSTIC_STATUS)
    S01EEGCaseId = models.CharField(max_length=30)
    S02ParoxysmalEpisode = models.CharField(max_length=2, choices=OPT_OUT)
    S02EEGAssessments = models.CharField(max_length=2, choices=OPT_OUT)
    S02FirstAssessmentsDate = models.DateField()
    S02FirstAssessmentsDateDateOnly = models.DateField()
    S02FirstAssessmentsDateTimeOnly = models.DateTimeField()
    S02HomePostcodeOut = models.CharField(max_length=4)
    S02HomePostcodeIn = models.CharField(max_length=3)
    # Helen/Colin
    # S02GPCode=models.CharField(max_length=10)
    # S02GPPostcodeOut=models.CharField(max_length=4)
    # S02GPPostcodeIn=models.CharField(max_length=3)
    S02TrustEmailSent = models.CharField(max_length=3)
    S02Cohort = models.IntegerField(2, choices=CHOICES)


class Assessment(base.Model):
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    S01SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S01Assessment = models.IntegerField(choices=ASSESSMENT)
    S01OptOut = models.CharField(max_length=2, choices=OPT_OUT)
    # Helen/Colin
    # S01OptOutDate=models.DateField()
    # S01FollowUpEpisodes=models.CharField(max_length=2, choices=OPT_OUT)
    # S01FollowUpEpisodesStatus=models.IntegerField(choices=FOLLOW_UP_EPISODE_STATUS)
    # S01FollowUpEpisodesStatusDate=models.DateField()
    # S01FollowUpEpisodesReason=models.CharField(max_length=250)
    S01SiteCode = models.CharField(max_length=10)
    S01Gender = models.CharField(max_length=3)
    S01FirstAssessmentsDate = models.DateField()
    S01NeonatalSeizures = models.CharField(
        max_length=2, choices=OPT_OUT_UNCERTAIN)
    S01FebrileSeizure = models.CharField(
        max_length=2, choices=OPT_OUT_UNCERTAIN)
    S01AcuteSymptomaticSeizure = models.CharField(
        max_length=2, choices=OPT_OUT_UNCERTAIN)
    S01DiagnosticStatus = models.CharField(
        max_length=2, choices=DIAGNOSTIC_STATUS)
    S01DescribeTheEpisode = models.CharField(
        max_length=2, choices=EPISODE_DESCRIPTION)
    S01EPIS = models.CharField(max_length=2)
    S01Notes = models.CharField(max_length=250)
    S03SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # Helen/Colin
    # S03CurrentEpilepsyService
    # S03CurrentEpilepsyServiceDetails
    # S03SecondaryPaediatricConsultant
    # S03SecondaryPaediatricConsultantDetails
    # S03CurrentEsn
    # S03CurrentEsnDetails
    # S03StatusPaediatricNeurologyFollowUp=models.IntegerField(choices=INPUT_STATUS)
    # S03TrustsTertiaryPaediatricNeurologyEpilepsy
    # S03TrustsTertiaryPaediatricNeurologyEpilepsyDetails
    # S03CurrentPaediatricNeurologist
    # S03CurrentPaediatricNeurologistDetails
    # S03CurrentStatusOfEpilepsySurgeryService=models.CharField(max_length=2, choices=INPUT_STATUS)
    # S03CurrentManagingEpilepsySurgeryService
    # S03CurrentManagingEpilepsySurgeryServiceDetails
    S04SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S04ServiceChildReferredForFirstAssessment = models.CharField(
        max_length=2, choices=REFERRAL_SERVICES)
    # S04ServiceChildReferredForFirstAssessmentOther=models.CharField(max_length=250)
    S04DateOfReferralToPaediatrics = models.DateField()
    S04DateOfReferralToPaediatrics_NK = models.IntegerField(
        choices=CHECKED_STATUS)
    S04FirstPaediatricAssessmentAcuteOrNonAcute = models.CharField(
        max_length=2, choices=CHRONICITY)
    S04ADescriptionOfTheEpisodeOrEpisodes = models.CharField(
        max_length=2, choices=OPT_OUT)
    S04WhenTheFirstEpilepticEpisodeOccurredApxExcNK = models.CharField(
        max_length=3, choices=DATE_ACCURACY)
    S04WhenTheFirstEpilepticEpisodeOccurred = models.DateField()
    S04FrequencyOrNumberOfEpisodesSinceTheFirstEpisode = models.CharField(
        max_length=2, choices=OPT_OUT)
    S04AGeneralExamination = models.CharField(max_length=2, choices=OPT_OUT)
    S04ANeurologicalExamination = models.CharField(
        max_length=2, choices=OPT_OUT)
    S04DevelopmentalLearningOrSchoolingProblems = models.CharField(
        max_length=2, choices=OPT_OUT)
    S04BehaviouralOrEmotionalProblems = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S04Comments=models.CharField(max_length=250)
    S05SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S05SEIZ = models.IntegerField(0)
    S05ECLS = models.IntegerField(0)
    S05CAUS = models.IntegerField(0)
    S05NUDS = models.IntegerField(0)
    S05MHPB = models.IntegerField(0)
    S05WereAnyOfTheEpilepticSeizuresConvulsive = models.CharField(
        max_length=2, choices=OPT_OUT)
    S05ProlongedGeneralizedConvulsiveSeizures = models.CharField(
        max_length=3, choices=OPT_OUT_UNCERTAIN)
    S05ExperiencedProlongedFocalSeizures = models.CharField(
        max_length=3, choices=OPT_OUT_UNCERTAIN)
    S05IsThereAFamilyHistoryOfEpilepsy = models.CharField(
        max_length=3, choices=OPT_OUT_UNCERTAIN)
    # S05IsThereAFamilyHistoryOfEpilepsyNotes=models.CharField(max_length=250)
    S06SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # S06FirstEeg=models.IntegerField(2, choices=REFERRAL_STATUS)
    S06FirstEegDate = models.DateField()
    # S06FirstEegReasons=models.CharField(max_length=250)
    S0612LeadEcg = models.IntegerField(2, choices=REFERRAL_STATUS)
    # S0612LeadEcgDate=models.DateField()
    # S0612LeadEcgReasons=models.CharField(max_length=250)
    # S06IsThereEvidenceThatTheQtcCalculated=models.CharField(max_length=2, choices=OPT_OUT)
    S06CtHeadScan = models.IntegerField(2, choices=REFERRAL_STATUS)
    # S06CtHeadScanDate=models.DateField()
    # S06CtHeadScanReasons=models.CharField(max_length=250)
    # S06MriBrain=models.IntegerField(2, choices=REFERRAL_STATUS)
    S06MriBrainDate = models.DateField()
    # S06MriBrainReasons=models.CharField(max_length=250)
    # S06InvestigationSectionNotes=models.CharField(max_length=250)
    S07SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S07HasAnAedBeenGiven = models.CharField(max_length=2, choices=OPT_OUT)
    S07AED = models.IntegerField(default=0)
    S07RescueMedication = models.CharField(max_length=2, choices=OPT_OUT)
    S07RMED = models.IntegerField()
    S07DoesTheChildHaveAnyOfTheCESSReferralCriteria = models.CharField(
        max_length=2, choices=OPT_OUT)
    S07DoesTheChildHaveAnyOfTheCESSReferralCriteriaNotes = models.CharField(
        max_length=250)
    # S07FormChecked=models.IntegerField(choices=CHECKED_STATUS)
    S07AEDSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S07AEDGender = models.CharField(max_length=3)
    S07AEDType = models.IntegerField(choices=ANTI_EPILEPTIC_DRUG_TYPES)
    S07AEDOther = models.CharField(max_length=100)
    # S07AEDStartDate=models.DateField()
    # S07AEDStopDate=models.DateField()
    # S07AEDStopDate_NK=models.IntegerField(choices=CHECKED_STATUS)
    S07AEDRisk = models.CharField(max_length=2, choices=OPT_OUT)
    S07RMEDSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S07RMEDType = models.CharField(max_length=3, choices=BENZODIAZEPINE_TYPES)
    S07RMEDOther = models.CharField(max_length=100)
    # S07RMEDStartDate=models.DateField()
    # S07RMEDStopDate=models.DateField()
    # S07RMEDStopDate_NK=models.IntegerField(choices=CHECKED_STATUS)
    # S07RMEDNotes=models.CharField(max_length=250)
    S08SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S08IndividualisedPlanningOfCare = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08IndividualisedPlanningOfCareDetails=models.CharField(max_length=250)
    S08IndividualisedEpilepsyDocuments = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08IndividualisedEpilepsyDocumentsDetails=models.CharField(max_length=250)
    S08ParentCarerPatientAgreementToThePlanOfCare = models.CharField(
        max_length=2, choices=OPT_OUT)
    S08ParentCarerPatientAgreementToThePlanOfCareDetails = models.CharField(
        max_length=250)
    S08CarePlanUpdatedEvidence = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08CarePlanUpdatedEvidenceDetails=models.CharField(max_length=250)
    S08CareThatEncompassesServiceContact = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08Serv=models.IntegerField()
    S08CareThatEncompassesFirstAid = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08FAID=models.IntegerField()
    S08CareThatEncompassesAParentalProlongedSeizureCarePlan = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08PSCP=models.IntegerField()
    S08CareThatEncompassesGeneralParticipationAndRisk = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08Risk=models.IntegerField()
    S08CareThatEncompassesWaterSafety = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08Watr=models.IntegerField()
    S08CareThatEncompassesSUDEP = models.CharField(
        max_length=2, choices=OPT_OUT)
    # S08SUDP=models.IntegerField()
    # S08CareThatEncompassesRoadSafety=models.CharField(max_length=2, choices=OPT_OUT)
    # S08RdSf=models.IntegerField()
    # S08CareThatEncompassesHeights=models.CharField(max_length=2, choices=OPT_OUT)
    # S08Hght=models.IntegerField()
    # S08CareThatEncompassesSleep=models.CharField(max_length=2, choices=OPT_OUT)
    # S08Slep=models.IntegerField()
    # S08CareThatEncompassesPhotosensitivity=models.CharField(max_length=2, choices=OPT_OUT)
    # S08PtSe=models.IntegerField()
    # S08Info=models.IntegerField()
    # S08Teen=models.IntegerField()
    # S08Epil=models.IntegerField()
    # S08SeizureDiary=models.CharField(max_length=2, choices=OPT_OUT)
    # S08SzDi=models.IntegerField()
    S08IsThereEvidenceOfAIHP = models.IntegerField(choices=IHP_STATUS)
    # S08IsThereEvidenceOfAIHPDate=models.DateField()
    S08IsThereEvidenceOfAnEHCP = models.IntegerField(choices=EHCP_STATUS)
    # S08IsThereEvidenceOfAnEHCPDate=models.DateField()
    # S08Edu=models.IntegerField()
    S09SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S09WhenWasTheLastEpilepticSeizureApxExcNK = models.CharField(
        max_length=3, choices=DATE_ACCURACY)
    S09WhenWasTheLastEpilepticSeizure = models.DateField()
    # S09WhenWasTheLastEpilepticSeizureUpdated=models.DateField()
    S10SectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    S10ConsultantPaediatrician = models.IntegerField(
        choices=INPUT_REQUEST_STATUS)
    S10ConsultantPaediatricianInputDate = models.DateField()
    S10ConsultantPaediatricianInputAchieved = models.DateField()
    # S10ConsultantPaediatricianInputReasons=models.CharField(max_length=250)
    S10Esn = models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10EsnInputDate = models.DateField()
    S10EsnInputAchieved = models.DateField()
    # S10EsnInputReasons=models.CharField(max_length=250)
    S10PaediatricNeurologist = models.IntegerField(
        choices=INPUT_REQUEST_STATUS)
    S10PaediatricNeurologistInputDate = models.DateField()
    S10PaediatricNeurologistInputAchieved = models.DateField()
    # S10PaediatricNeurologistInputReasons=models.CharField(max_length=250)
    S10Cess = models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10CessInputDate = models.DateField()
    S10CessInputAchieved = models.DateField()
    # S10CessInputReasons=models.CharField(max_length=250)
    # S10KetognicDietician=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10KetognicDieticianInputDate=models.DateField()
    # S10KetognicDieticianInputAchieved=models.DateField()
    # S10KetognicDieticianInputReasons=models.CharField(max_length=250)
    # S10VnsService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10VnsServiceInputDate=models.DateField()
    # S10VnsServiceInputAchieved=models.DateField()
    # S10VnsServiceInputReasons=models.CharField(max_length=250)
    # S10GeneticService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10GeneticServiceInputDate=models.DateField()
    # S10GeneticServiceInputAchieved=models.DateField()
    # S10GeneticServiceInputReasons=models.CharField(max_length=250)
    # S10ClinicalPsychologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10ClinicalPsychologistInputDate=models.DateField()
    # S10ClinicalPsychologistInputAchieved=models.DateField()
    # S10ClinicalPsychologistInputReasons=models.CharField(max_length=250)
    # S10EducationalPsychologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10EducationalPsychologistInputDate=models.DateField()
    # S10EducationalPsychologistInputAchieved=models.DateField()
    # S10EducationalPsychologistInputReasons=models.CharField(max_length=250)
    # S10Psychiatrist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10PsychiatristInputDate=models.DateField()
    # S10PsychiatristInputAchieved=models.DateField()
    # S10PsychiatristInputReasons=models.CharField(max_length=250)
    # S10Neuropyschologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10NeuropyschologistInputDate=models.DateField()
    # S10NeuropyschologistInputAchieved=models.DateField()
    # S10NeuropyschologistInputReasons=models.CharField(max_length=250)
    # S10CounsellingService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10CounsellingServiceInputDate=models.DateField()
    # S10CounsellingServiceInputAchieved=models.DateField()
    # S10CounsellingServiceInputReasons=models.CharField(max_length=250)
    # S10OtherMentalHealthProfessional=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10OtherMentalHealthProfessionalInputDate=models.DateField()
    # S10OtherMentalHealthProfessionalInputAchieved=models.DateField()
    # S10OtherMentalHealthProfessionalInputReasons=models.CharField(max_length=250)
    # S10YouthWorker=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10YouthWorkerInputDate=models.DateField()
    # S10YouthWorkerInputAchieved=models.DateField()
    # S10YouthWorkerInputReasons=models.CharField(max_length=250)
    # S10OtherFreeField=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    # S10OtherFreeFieldInputDate=models.DateField()
    # S10OtherFreeFieldInputAchieved=models.DateField()
    # S10OtherFreeFieldInputReasons=models.CharField(max_length=250)
    # S10FormalDevelopmentalAssessment=models.CharField(max_length=2, choices=OPT_OUT)
    # S10FDA=models.IntegerField()
    # S10FormalCognitiveAssessment=models.CharField(max_length=2, choices=OPT_OUT)
    # S10FCA=models.IntegerField()
    # S10ReviewByAPaediatrician12Months=models.CharField(max_length=2, choices=OPT_OUT)
    # S10RBAP=models.IntegerField()
    S10DiagnosisOfEpilepsyWithdrawn = models.CharField(
        max_length=2, choices=OPT_OUT)
    S10DOEW = models.IntegerField()


class AED(base.Model):
    OtherId = models.CharField(max_length=30, primary_key=True)
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    AEDSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    AEDGender = models.CharField(max_length=3)
    AEDType = models.IntegerField(choices=ANTI_EPILEPTIC_DRUG_TYPES)
    AEDOther = models.CharField(max_length=100)
    AEDStartDate = models.DateField()
    AEDStopDate = models.DateField()
    AEDStopDate_NK = models.IntegerField(choices=CHECKED_STATUS)
    AEDRisk = models.CharField(max_length=2, choices=OPT_OUT)

# class ClinicalReview(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     RBAPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     RBAPDate=models.DateField()
#     RBAPDetails=models.CharField(max_length=250)

# class Cognitive(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     FCASectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     FCADate=models.DateField()
#     FCADetails=models.CharField(max_length=250)

# class DevelopmentAssessment(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     FDASectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     FDADate=models.DateField()
#     FDADetails=models.CharField(max_length=250)

# Helen/Colin
# class Education(base.Model):
    # OtherId=models.CharField(max_length=30, primary_key=True)
    # UpdateId=models.CharField(max_length=30)
    # CaseId=models.CharField(max_length=30)
    # CreatedDateTime=models.DateField()
    # CreatedUserName=models.CharField(max_length=256)
    # UpdatedDateTime=models.DateField()
    # UpdatedUserName=models.CharField(max_length=256)
    # Locked=models.BooleanField("Locked", default=False)
    # LockedDateTime=models.DateField()
    # LockedUserName=models.CharField(max_length=256)
    # RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    # Closed=models.BooleanField("Locked", default=False)
    # EDUSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    # EDUSiteCode=models.CharField(max_length=10)
    # EDUType=models.IntegerField(choices=EDUCATION_TYPE)
    # EDUTypeOther=models.CharField(max_length=50)
    # EDUDate=models.DateField()
    # # EDUProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    # EDUProvidedByOther=models.CharField(max_length=100)
    # EDUDetails=models.CharField(max_length=250)


class ElectroClinicalSyndrome(base.Model):
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    ECLSSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # ECLSDateOfDiagnosisApproxExactNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    # ECLSDateOfDiagnosis=models.DateField()
    ECLSElectroclinicalSyndrome = models.IntegerField(
        choices=ELECTROCLINICAL_SYNDROMES)
    ECLSElectroclinicalSyndromeOther = models.CharField(max_length=250)

# class EpilepsyDetails(base.Model):
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     EPILSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     EPILSiteCode=models.CharField(max_length=10)
#     EPILType=models.IntegerField(choices=EPIL_TYPE_CHOICES)
#     EPILTypeOther=models.CharField(max_length=50)
#     EPILDate=models.DateField()
#     # EPILProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     EPILProvidedByOther=models.CharField(max_length=100)
#     EPILDetails=models.CharField(max_length=250)

# class FirstAid(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     FAIDSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     FAIDSiteCode=models.CharField(max_length=10)
#     FAIDDate=models.DateField()
#     # FAIDProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     FAIDProvidedByOther=models.CharField(max_length=100)
#     FAIDDetails=models.CharField(max_length=250)

# class GeneralRisk(base.Model):
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     RISKSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     RISKSiteCode=models.CharField(max_length=10)
#     RISKPDate=models.DateField()
#     # RISKProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     RISKProvidedByOther=models.CharField(max_length=100)
#     RISKDetails=models.CharField(max_length=250)

# class Heights(base.Model):
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     HGHTSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     HGHTSiteCode=models.CharField(max_length=10)
#     HGHTDate=models.DateField()
#     # HGHTProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     HGHTProvidedByOther=models.CharField(max_length=100)
#     HGHTDetails=models.CharField(max_length=250)


class MentalHealth(base.Model):
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    MHPBSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # MHPBDateNeurodevelopmentalProblemApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    # MHPBDateNeurodevelopmentalProblem=models.DateField()
    MHPBMentalHealthProblem = models.CharField(
        max_length=3, choices=NEUROPSYCHIATRIC)
    MHPBMentalHealthProblemOther = models.CharField(max_length=250)
    MHPBMentalHealthProblemEmotional = models.CharField(
        max_length=3, choices=DEVELOPMENTAL_BEHAVIOURAL)


class Neurodevelopmental(base.Model):
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    NUDSSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # NUDSDateNeurodevelopmentalProblemApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    # NUDSDateNeurodevelopmentalProblem=models.DateField()
    NUDSNeurodevelopmentalProblem = models.CharField(
        max_length=3, choices=NEURODEVELOPMENTAL)
    NUDSNeurodevelopmentalProblemOther = models.CharField(max_length=250)
    NUDSNeurodevelopmentalProblemSeverity = models.CharField(
        max_length=3, choices=DISORDER_SEVERITY)


class NonEpileptic(base.Model):
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    EPISSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    EPISType = models.IntegerField(choices=EPIS_TYPE)
    EPISSyncope = models.CharField(
        max_length=3, choices=NON_EPILEPTIC_SYNCOPES)
    EPISBehavioral = models.CharField(
        max_length=3, choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    EPISSleep = models.CharField(
        max_length=3, choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    EPISParoxysmal = models.CharField(
        max_length=3, choices=NON_EPILEPSY_PAROXYSMS)
    EPISMigraine = models.CharField(max_length=3, choices=MIGRAINES)
    EPISMiscellaneous = models.CharField(max_length=3, choices=EPIS_MISC)
    EPISOther = models.CharField(max_length=250)

# class Photosensitivity(base.Model):
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     PTSESectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     PTSESiteCode=models.CharField(max_length=10)
#     PTSEDate=models.DateField()
#     # PTSEProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     PTSEProvidedByOther=models.CharField(max_length=100)
#     PTSEDetails=models.CharField(max_length=250)


class RescueMeds(base.Model):
    OtherId = models.CharField(max_length=30, primary_key=True)
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    RMEDSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    RMEDType = models.CharField(max_length=3, choices=BENZODIAZEPINE_TYPES)
    RMEDOther = models.CharField(max_length=100)
    RMEDStartDate = models.DateField()
    RMEDStopDate = models.DateField()
    RMEDStopDate_NK = models.IntegerField(choices=CHECKED_STATUS)
    RMEDNotes = models.CharField(max_length=250)

# class RoadSafety(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     RDSFSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     RDSFSiteCode=models.CharField(max_length=10)
#     RDSFDate=models.DateField()
#     # RDSFProvidedBy=,"Q. 2","10","","","varchar(10)","Drop down list","uspx_ServiceContractList = FullDetails"
#     RDSFProvidedByOther=models.CharField(max_length=100)
#     RDSFDetails=models.CharField(max_length=250)

# class SeizureCare(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     PSCPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     PSCPSiteCode=models.CharField(max_length=10)
#     PSCPDate=models.DateField()
#     # PSCPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     PSCPProvidedByOther=models.CharField(max_length=100)
#     PSCPDetails=models.CharField(max_length=250)


class SeizureCause(base.Model):
    OtherId = models.CharField(max_length=30, primary_key=True)
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    CAUSSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # CAUSDateCauseApxExcNK=models.CharField(max_length=3,choices=DATE_ACCURACY)
    # CAUSDateCause=models.DateField()
    CAUSMain = models.CharField(max_length=3, choices=EPILEPSY_CAUSES)
    CAUSSubStructural = models.CharField(
        max_length=3, choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES)
    CAUSSubGenetic = models.CharField(
        max_length=3, choices=EPILEPSY_GENETIC_CAUSE_TYPES)
    CAUSSubGeneticChromoAbno = models.CharField(max_length=200)
    CAUSSubGeneticGeneAbno = models.CharField(
        max_length=3, choices=EPILEPSY_GENE_DEFECTS)
    CAUSSubGeneticGeneAbnoOther = models.CharField(max_length=250)
    CAUSSubInfectious = models.CharField(max_length=250)
    CAUSSubMetabolic = models.CharField(max_length=3, choices=METABOLIC_CAUSES)
    CAUSSubMetabolicOther = models.CharField(max_length=250)
    CAUSSubImmune = models.CharField(max_length=3, choices=IMMUNE_CAUSES)
    CAUSSubImmuneAntibody = models.CharField(
        max_length=3, choices=AUTOANTIBODIES)
    CAUSSubImmuneAntibodyOther = models.CharField(max_length=250)

# class SeizureDiary(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     SZDISectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     SZDISiteCode=models.CharField(max_length=10)
#     SZDIDate=models.DateField()
#     # SZDIProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     SZDIProvidedByOther=models.CharField(max_length=100)
#     SZDIDetails=models.CharField(max_length=250)

# class ServiceDetails(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     SERVSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     SERVSiteCode=models.CharField(max_length=10)
#     SERVDate=models.DateField()
#     # SERVProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     SERVProvidedByOther=models.CharField(max_length=100)
#     SERVDetails=models.CharField(max_length=250)

# class SleepIssues(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     SLEPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     SLEPSiteCode=models.CharField(max_length=10)
#     SLEPDate=models.DateField()
#     # SLEPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     SLEPProvidedByOther=models.CharField(max_length=100)
#     SLEPDetails=models.CharField(max_length=250)


class SeizureType(base.Model):
    OtherId = models.CharField(max_length=30, primary_key=True)
    UpdateId = models.CharField(max_length=30)
    CaseId = models.CharField(max_length=30)
    CreatedDateTime = models.DateField()
    CreatedUserName = models.CharField(max_length=256)
    UpdatedDateTime = models.DateField()
    UpdatedUserName = models.CharField(max_length=256)
    Locked = models.BooleanField("Locked", default=False)
    LockedDateTime = models.DateField()
    LockedUserName = models.CharField(max_length=256)
    RecordStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    Closed = models.BooleanField("Locked", default=False)
    SEIZSectionStatus = models.CharField(
        max_length=2, choices=SECTION_STATUS_CHOICES)
    # SEIZDateOfOnsetApproxExactNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    # SEIZDateOfOnset=models.DateField()
    # SEIZDescriptionOfEvent=models.CharField(max_length=250)
    SEIZEpilepticOrNonEpilepticOrUncertain = models.CharField(
        max_length=3, choices=EPILEPSY_DIAGNOSIS_STATUS)
    SEIZEpilepticSeizureType = models.CharField(
        max_length=3, choices=EPILEPSY_SEIZURE_TYPE)
    SEIZNonEpilepticSeizureType = models.CharField(
        max_length=3, choices=NON_EPILEPSY_SEIZURE_TYPE)
    SEIZEpilepticSeizureTypeFOImpAware = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOAutomatisms = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOAtonic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOClonic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOLeft = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFORight = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOEpilepticSpasms = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOHyperkinetic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOMyoclonic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOTonic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOAutonomic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOBehaviourArrest = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOCognitive = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOEmotional = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOSensory = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOCentroTemporal = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOTemporal = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOFrontal = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOParietal = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOOccipital = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOGelastic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOFocaltoBilateralTonicClonic = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOOther = models.IntegerField(
        choices=CHECKED_STATUS)
    SEIZEpilepticSeizureTypeFOOtherDetails = models.CharField(max_length=250)
    SEIZEpilepticSeizureTypeGeneralisedOnset = models.CharField(
        max_length=3, choices=GENERALISED_SEIZURE_TYPE)
    SEIZEpilepticSeizureTypeGeneralisedOnsetOtherDetails = models.CharField(
        max_length=250)
    SEIZNonEpilepticSeizureTypeUnknownOnset = models.CharField(
        max_length=3, choices=NON_EPILEPSY_SEIZURE_ONSET)
    SEIZNonEpilepticSeizureTypeUnknownOnsetOtherDetails = models.CharField(
        max_length=250)
    SEIZNonEpilepticSeizureTypeSyncope = models.CharField(
        max_length=3, choices=NON_EPILEPTIC_SYNCOPES)
    SEIZNonEpilepticSeizureTypeBehavioral = models.CharField(
        max_length=3, choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    SEIZNonEpilepticSeizureTypeSleep = models.CharField(
        max_length=3, choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    SEIZNonEpilepticSeizureTypeParoxysmal = models.CharField(
        max_length=3, choices=NON_EPILEPSY_PAROXYSMS)
    SEIZNonEpilepticSeizureTypeMigraine = models.CharField(
        max_length=3, choices=MIGRAINES)
    SEIZNonEpilepticSeizureTypeMiscellaneous = models.CharField(
        max_length=3, choices=EPIS_MISC)
    SEIZNonEpilepticSeizureTypeOther = models.CharField(max_length=250)

# class SUDEP(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     SUDPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     SUDPSiteCode=models.CharField(max_length=10)
#     SUDPDate=models.DateField()
#     # SUDPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     SUDPProvidedByOther=models.CharField(max_length=100)
#     SUDPDetails=models.CharField(max_length=250)

# class Transition(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     TEENSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     TEENSiteCode=models.CharField(max_length=10)
#     TEENType=models.IntegerField(choices=TRANSITION_TOPICS)
#     TEENTypeOther=models.CharField(max_length=50)
#     TEENDate=models.DateField()
#     # TEENProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     TEENProvidedByOther=models.CharField(max_length=100)
#     TEENDetails=models.CharField(max_length=250)

# class Treatments(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     INFOSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     INFOSiteCode=models.CharField(max_length=10)
#     INFOType=models.CharField(max_length=3,choices=INFORMATION_TYPES)
#     INFOTypeOther=models.CharField(max_length=50)
#     INFODate=models.DateField()
#     # INFOProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     INFOProvidedByOther=models.CharField(max_length=100)
#     INFODetails=models.CharField(max_length=250)

# class WaterSafety(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     WATRSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     WATRSiteCode=models.CharField(max_length=10)
#     WATRDate=models.DateField()
#     # WATRProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     WATRProvidedByOther=models.CharField(max_length=100)
#     WATRDetails=models.CharField(max_length=250)

# class Withdrawal(base.Model):
#     OtherId=models.CharField(max_length=30, primary_key=True)
#     UpdateId=models.CharField(max_length=30)
#     CaseId=models.CharField(max_length=30)
#     CreatedDateTime=models.DateField()
#     CreatedUserName=models.CharField(max_length=256)
#     UpdatedDateTime=models.DateField()
#     UpdatedUserName=models.CharField(max_length=256)
#     Locked=models.BooleanField("Locked", default=False)
#     LockedDateTime=models.DateField()
#     LockedUserName=models.CharField(max_length=256)
#     RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     Closed=models.BooleanField("Locked", default=False)
#     DOEWSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
#     DOEWDate=models.DateField()
#     DOEWDetails=models.CharField(max_length=250)
