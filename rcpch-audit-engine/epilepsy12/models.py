from django.db import models
from django.db.models.fields import CharField, DateField, IntegerField

from .constants import *
class BaseData(models.Model):
    UpdateId= models.CharField(max_length=30)
    CaseId=models.CharField(max_length=30, primary_key=True)
    SiteCode=models.CharField(max_length=10)
    ImportId=models.CharField(max_length=30)
    ImportIdentifier=models.CharField(max_length=50)
    CreatedDateTime=models.DateField()
    CreatedUserName=models.CharField(max_length=256)
    UpdatedDateTime=models.DateField()
    UpdatedUserName=models.CharField(max_length=256)
    Locked=models.BooleanField("Locked", default=False)
    LockedDateTime=models.DateField()
    LockedUserName=models.CharField(max_length=256)
    RecordStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    TransferToActionDateTime=models.DateField()
    TransferToActionUserName=models.CharField(max_length=256)
    TransferToDateTime=models.DateField()
    TransferToSiteCode=models.CharField(max_length=10)
    TransferToCaseId=models.IntegerField()
    TransferFromActionDateTime=models.DateField()
    TransferFromActionUserName=models.CharField(max_length=256)
    TransferFromDateTime=models.DateField()
    TransferFromSiteCode=models.CharField(max_length=10)
    TransferFromCaseId=models.IntegerField()
    OriginalSiteCode=models.CharField(max_length=10)
    Closed=models.BooleanField("Locked", default=False)

class S01(models.Model):
    S01SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S01Assessment=models.IntegerField(choices=ASSESSMENT)
    S01OptOut=models.CharField(max_length=2, choices=OPT_OUT)
    S01OptOutDate=models.DateField()
    S01FollowUpEpisodes=models.CharField(max_length=2, choices=OPT_OUT)
    S01FollowUpEpisodesStatus=models.IntegerField(choices=FOLLOW_UP_EPISODE_STATUS)
    S01FollowUpEpisodesStatusDate=models.DateField()
    S01FollowUpEpisodesReason=models.CharField(max_length=250)
    S01SiteCode=models.CharField(max_length=10)
    S01Gender=models.CharField(max_length=3)
    S01DOB=models.DateField()
    S01FirstAssessmentsDate=models.DateField()
    S01NeonatalSeizures=models.CharField(max_length=2,choices=OPT_OUT_UNCERTAIN)
    S01FebrileSeizure=models.CharField(max_length=2,choices=OPT_OUT_UNCERTAIN)
    S01AcuteSymptomaticSeizure=models.CharField(max_length=2,choices=OPT_OUT_UNCERTAIN)
    S01DiagnosticStatus=models.CharField(max_length=2,choices=DIAGNOSTIC_STATUS)
    S01DescribeTheEpisode=models.CharField(max_length=2,choices=EPISODE_DESCRIPTION)
    S01EPIS=models.CharField(max_length=2)
    EPISSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    EPISType=models.IntegerField(choices=EPIS_TYPE)
    EPISSyncope=models.CharField(max_length=3, choices=NON_EPILEPTIC_SYNCOPES)
    EPISBehavioral=models.CharField(max_length=3, choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    EPISSleep=models.CharField(max_length=3, choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    EPISParoxysmal=models.CharField(max_length=3, choices=NON_EPILEPSY_PAROXYSMS)
    EPISMigraine=models.CharField(max_length=3, choices=MIGRAINES)
    EPISMiscellaneous=models.CharField(max_length=3, choices=EPIS_MISC)
    EPISOther=models.CharField(max_length=250)
    S01Notes=models.CharField(max_length=250)
    S01NHSPatient=models.CharField(max_length=2, choices=OPT_OUT)
    S01NHSCHINumber=models.CharField(max_length=10)
    S01FirstName=models.CharField(max_length=100)
    S01Surname=models.CharField(max_length=100)
    S01Gender=models.CharField(max_length=3, choices=SEX_TYPE)
    S01DOB=models.DateField()
    S01FirstEEG=models.CharField(max_length=2, choices=OPT_OUT)
    S01FirstEEGDate=models.DateField()
    S01FirstEEGIndicated=models.CharField(max_length=2, choices=OPT_OUT)
    S01AssessmentForTheParoxysmalHere=models.CharField(max_length=2, choices=OPT_OUT)
    S01ReferringHospital=models.CharField(max_length=150)
    S01ReferringPerson=models.CharField(max_length=150)
    S01TrustVerify=models.CharField(max_length=3, choices=TRUST_VERIFICATION_STATUS)
    S01DiagnosisStatus=models.CharField(max_length=3, choices=EPILEPSY_DIAGNOSIS_STATUS)
    S01EEGCaseId=models.CharField(max_length=30)

class S02(models.Model):
    CHOICES = choices=((i,i) for i in range(11))
    S02SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S02ParoxysmalEpisode=models.CharField(max_length=2, choices=OPT_OUT)
    S02EEGAssessments=models.CharField(max_length=2, choices=OPT_OUT)
    S02FirstAssessmentsDate=models.DateField()
    S02Cohort=models.IntegerField(2, choices=CHOICES)
    S02HomePostcodeOut=models.CharField(max_length=4)
    S02HomePostcodeIn=models.CharField(max_length=3)
    S02GPCode=models.CharField(max_length=10)
    S02GPPostcodeOut=models.CharField(max_length=4)
    S02GPPostcodeIn=models.CharField(max_length=3)
    S02TrustEmailSent=models.CharField(max_length=3)

class S03(models.Model):
    S03SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S03HomePostcodeOut=models.CharField(max_length=4)
    S03HomePostcodeIn=models.CharField(max_length=3)
    S03CurrentGeneralPracticeCode=models.CharField(max_length=10)
    S03GPPostcodeOut=models.CharField(max_length=4)
    S03GPPostcodeIn=models.CharField(max_length=3)
    # S03CurrentEpilepsyService="Q. 3.3","10","","","varchar(10)","Combo box","uspx_LeadEpTeamCurrentEpilepsyService = FullDetails"
    # S03SecondaryPaediatricConsultant="Q. 3.4","10","","","varchar(10)","Combo box","uspx_LeadEpTeamSecondaryPaediatricConsultant = FullDetails"
    # S03CurrentEsn="Q. 3.5","10","","","varchar(10)","Combo box","uspx_LeadEpTeamCurrentEsn = FullDetails"
    S03StatusPaediatricNeurologyFollowUp=models.IntegerField(choices=INPUT_STATUS)
    # S03TrustsTertiaryPaediatricNeurologyEpilepsy="Q. 3.6i","10","","","varchar(10)","Combo box","uspx_LeadEpTeamServiceTrustsTertiaryPaediatricNeurologyEpilepsy = FullDetails"
    # S03CurrentPaediatricNeurologist="Q. 3.6ii","10","","","varchar(10)","Combo box","uspx_LeadEpTeamCurrentPaediatricNeurologist = FullDetails"
    S03CurrentStatusOfEpilepsySurgeryService=models.CharField(max_length=2, choices=INPUT_STATUS)
    # S03CurrentManagingEpilepsySurgeryService="Q. 3.7i","20","","","varchar(20)","Combo box","uspx_AffiliatedCESS_List = AffiliatedCESSName"
    S03SiteCode=models.CharField(max_length=10)
    S03FormChecked=models.IntegerField(choices=CHECKED_STATUS)

class S04(models.Model):
    S04SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S04ServiceChildReferredForFirstAssessment=models.CharField(max_length=2, choices=REFERRAL_SERVICES)
    S04ServiceChildReferredForFirstAssessmentOther=models.CharField(max_length=250)
    S04DateOfReferralToPaediatrics=models.DateField()
    S04DateOfReferralToPaediatrics_NK=models.IntegerField(choices=CHECKED_STATUS)
    S04FirstPaediatricAssessmentAcuteOrNonAcute=models.CharField(max_length=2, choices=CHRONICITY)
    S04ADescriptionOfTheEpisodeOrEpisodes=models.CharField(max_length=2, choices=OPT_OUT)
    S04WhenTheFirstEpilepticEpisodeOccurredApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S04WhenTheFirstEpilepticEpisodeOccurred=models.DateField()
    S04FrequencyOrNumberOfEpisodesSinceTheFirstEpisode=models.CharField(max_length=2, choices=OPT_OUT)
    S04AGeneralExamination=models.CharField(max_length=2, choices=OPT_OUT)
    S04ANeurologicalExamination=models.CharField(max_length=2, choices=OPT_OUT)
    S04DevelopmentalLearningOrSchoolingProblems=models.CharField(max_length=2, choices=OPT_OUT)
    S04BehaviouralOrEmotionalProblems=models.CharField(max_length=2, choices=OPT_OUT)
    S04Comments=models.CharField(max_length=250)
    S04FormChecked=models.IntegerField(choices=CHECKED_STATUS)

class S05(models.Model):
    S05SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05SEIZ=models.IntegerField(0)
    S05ECLS=models.IntegerField(0)
    S05CAUS=models.IntegerField(0)
    S05NUDS=models.IntegerField(0)
    S05MHPB=models.IntegerField(0)
    S05WereAnyOfTheEpilepticSeizuresConvulsive=models.CharField(max_length=2, choices=OPT_OUT)
    S05ProlongedGeneralizedConvulsiveSeizures=models.CharField(max_length=3, choices=OPT_OUT_UNCERTAIN)
    S05ExperiencedProlongedFocalSeizures=models.CharField(max_length=3, choices=OPT_OUT_UNCERTAIN)
    S05IsThereAFamilyHistoryOfEpilepsy=models.CharField(max_length=3, choices=OPT_OUT_UNCERTAIN)
    S05IsThereAFamilyHistoryOfEpilepsyNotes=models.CharField(max_length=250)
    S05FormChecked=models.IntegerField(choices=CHECKED_STATUS)
    S05CAUSSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05CAUSDateCauseApxExcNK=models.CharField(max_length=3,choices=DATE_ACCURACY)
    S05CAUSDateCause=models.DateField()
    S05CAUSMain=models.CharField(max_length=3, choices=EPILEPSY_CAUSES)
    S05CAUSSubStructural=models.CharField(max_length=3, choices=EPILEPSY_STRUCTURAL_CAUSE_TYPES)
    S05CAUSSubGenetic=models.CharField(max_length=3, choices=EPILEPSY_GENETIC_CAUSE_TYPES)
    S05CAUSSubGeneticChromoAbno=models.CharField(max_length=200)
    S05CAUSSubGeneticGeneAbno=models.CharField(max_length=3, choices=EPILEPSY_GENE_DEFECTS)
    S05CAUSSubGeneticGeneAbnoOther=models.CharField(max_length=250)
    S05CAUSSubInfectious=models.CharField(max_length=250)
    S05CAUSSubMetabolic=models.CharField(max_length=3, choices=METABOLIC_CAUSES)
    S05CAUSSubMetabolicOther=models.CharField(max_length=250)
    S05CAUSSubImmune=models.CharField(max_length=3, choices=IMMUNE_CAUSES)
    S05CAUSSubImmuneAntibody=models.CharField(max_length=3,choices=AUTOANTIBODIES)
    S05CAUSSubImmuneAntibodyOther=models.CharField(max_length=250)
    S05ECLSSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05ECLSDateOfDiagnosisApproxExactNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S05ECLSDateOfDiagnosis=models.DateField()
    S05ECLSElectroclinicalSyndrome=models.IntegerField(choices=ELECTROCLINICAL_SYNDROMES)
    S05ECLSElectroclinicalSyndromeOther=models.CharField(max_length=250)
    S05MHPBSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05MHPBDateNeurodevelopmentalProblemApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S05MHPBDateNeurodevelopmentalProblem=models.DateField()
    S05MHPBMentalHealthProblem=models.CharField(max_length=3,choices=NEUROPSYCHIATRIC)
    S05MHPBMentalHealthProblemOther=models.CharField(max_length=250)
    S05MHPBMentalHealthProblemEmotional=models.CharField(max_length=3, choices=DEVELOPMENTAL_BEHAVIOURAL)
    S05NUDSSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05NUDSDateNeurodevelopmentalProblemApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S05NUDSDateNeurodevelopmentalProblem=models.DateField()
    S05NUDSNeurodevelopmentalProblem=models.CharField(max_length=3, choices=NEURODEVELOPMENTAL)
    S05NUDSNeurodevelopmentalProblemOther=models.CharField(max_length=250)
    S05NUDSNeurodevelopmentalProblemSeverity=models.CharField(max_length=3,choices=DISORDER_SEVERITY)
    S05SEIZSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S05SEIZDateOfOnsetApproxExactNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S05SEIZDateOfOnset=models.DateField()
    S05SEIZDescriptionOfEvent=models.CharField(max_length=250)
    S05SEIZEpilepticOrNonEpilepticOrUncertain=models.CharField(max_length=3,choices=EPILEPSY_DIAGNOSIS_STATUS)
    S05SEIZEpilepticSeizureType=models.CharField(max_length=3,choices=EPILEPSY_SEIZURE_TYPE)
    S05SEIZNonEpilepticSeizureType=models.CharField(max_length=3,choices=NON_EPILEPSY_SEIZURE_TYPE)
    S05SEIZEpilepticSeizureTypeFOImpAware=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOAutomatisms=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOAtonic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOClonic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOLeft=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFORight=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOEpilepticSpasms=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOHyperkinetic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOMyoclonic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOTonic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOAutonomic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOBehaviourArrest=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOCognitive=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOEmotional=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOSensory=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOCentroTemporal=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOTemporal=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOFrontal=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOParietal=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOOccipital=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOGelastic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOFocaltoBilateralTonicClonic=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOOther=models.IntegerField(choices=CHECKED_STATUS)
    S05SEIZEpilepticSeizureTypeFOOtherDetails=models.CharField(max_length=250)
    S05SEIZEpilepticSeizureTypeGeneralisedOnset=models.CharField(max_length=3, choices=GENERALISED_SEIZURE_TYPE)
    S05SEIZEpilepticSeizureTypeGeneralisedOnsetOtherDetails=models.CharField(max_length=250)
    S05SEIZNonEpilepticSeizureTypeUnknownOnset=models.CharField(max_length=3, choices=NON_EPILEPSY_SEIZURE_ONSET)
    S05SEIZNonEpilepticSeizureTypeUnknownOnsetOtherDetails=models.CharField(max_length=250)
    S05SEIZNonEpilepticSeizureTypeSyncope=models.CharField(max_length=3,choices=NON_EPILEPTIC_SYNCOPES)
    S05SEIZNonEpilepticSeizureTypeBehavioral=models.CharField(max_length=3, choices=NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS)
    S05SEIZNonEpilepticSeizureTypeSleep=models.CharField(max_length=3,choices=NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS)
    S05SEIZNonEpilepticSeizureTypeParoxysmal=models.CharField(max_length=3,choices=NON_EPILEPSY_PAROXYSMS)
    S05SEIZNonEpilepticSeizureTypeMigraine=models.CharField(max_length=3,choices=MIGRAINES)
    S05SEIZNonEpilepticSeizureTypeMiscellaneous=models.CharField(max_length=3,choices=EPIS_MISC)
    S05SEIZNonEpilepticSeizureTypeOther=models.CharField(max_length=250)

class S06(models.Model):
    S06SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S06FirstEeg=models.IntegerField(2, choices=REFERRAL_STATUS)
    S06FirstEegDate=models.DateField()
    S06FirstEegReasons=models.CharField(max_length=250)
    S0612LeadEcg=models.IntegerField(2, choices=REFERRAL_STATUS)
    S0612LeadEcgDate=models.DateField()
    S0612LeadEcgReasons=models.CharField(max_length=250)
    S06IsThereEvidenceThatTheQtcCalculated=models.CharField(max_length=2, choices=OPT_OUT)
    S06CtHeadScan=models.IntegerField(2, choices=REFERRAL_STATUS)
    S06CtHeadScanDate=models.DateField()
    S06CtHeadScanReasons=models.CharField(max_length=250)
    S06MriBrain=models.IntegerField(2, choices=REFERRAL_STATUS)
    S06MriBrainDate=models.DateField()
    S06MriBrainReasons=models.CharField(max_length=250)
    S06InvestigationSectionNotes=models.CharField(max_length=250)
    S06FormChecked=models.IntegerField(choices=CHECKED_STATUS)

class S07(models.Model):
    S07SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S07HasAnAedBeenGiven=models.CharField(max_length=2, choices=OPT_OUT)
    S07AED=models.IntegerField(default=0)
    S07RescueMedication=models.CharField(max_length=2, choices=OPT_OUT)
    S07RMED=models.IntegerField()
    S07DoesTheChildHaveAnyOfTheCESSReferralCriteria=models.CharField(max_length=2, choices=OPT_OUT)
    S07DoesTheChildHaveAnyOfTheCESSReferralCriteriaNotes=models.CharField(max_length=250)
    S07FormChecked=models.IntegerField(choices=CHECKED_STATUS)
    S07AEDSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S07AEDGender=models.CharField(max_length=3)
    S07AEDType=models.IntegerField(choices=ANTI_EPILEPTIC_DRUG_TYPES)
    S07AEDOther=models.CharField(max_length=100)
    S07AEDStartDate=models.DateField()
    S07AEDStopDate=models.DateField()
    S07AEDStopDate_NK=models.IntegerField(choices=CHECKED_STATUS)
    S07AEDRisk=models.CharField(max_length=2, choices=OPT_OUT)
    S07RMEDSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S07RMEDType=models.CharField(max_length=3,choices=BENZODIAZEPINE_TYPES)
    S07RMEDOther=models.CharField(max_length=100)
    S07RMEDStartDate=models.DateField()
    S07RMEDStopDate=models.DateField()
    S07RMEDStopDate_NK=models.IntegerField(choices=CHECKED_STATUS)
    S07RMEDNotes=models.CharField(max_length=250)
class S08(models.Model):
    S08SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08IndividualisedPlanningOfCare=models.CharField(max_length=2, choices=OPT_OUT)
    S08IndividualisedPlanningOfCareDetails=models.CharField(max_length=250)
    S08IndividualisedEpilepsyDocuments=models.CharField(max_length=2, choices=OPT_OUT)
    S08IndividualisedEpilepsyDocumentsDetails=models.CharField(max_length=250)
    S08ParentCarerPatientAgreementToThePlanOfCare=models.CharField(max_length=2, choices=OPT_OUT)
    S08ParentCarerPatientAgreementToThePlanOfCareDetails=models.CharField(max_length=250)
    S08CarePlanUpdatedEvidence=models.CharField(max_length=2, choices=OPT_OUT)
    S08CarePlanUpdatedEvidenceDetails=models.CharField(max_length=250)
    S08CareThatEncompassesServiceContact=models.CharField(max_length=2, choices=OPT_OUT)
    S08Serv=models.IntegerField()
    S08CareThatEncompassesFirstAid=models.CharField(max_length=2, choices=OPT_OUT)
    S08FAID=models.IntegerField()
    S08CareThatEncompassesAParentalProlongedSeizureCarePlan=models.CharField(max_length=2, choices=OPT_OUT)
    S08PSCP=models.IntegerField()
    S08CareThatEncompassesGeneralParticipationAndRisk=models.CharField(max_length=2, choices=OPT_OUT)
    S08Risk=models.IntegerField()
    S08CareThatEncompassesWaterSafety=models.CharField(max_length=2, choices=OPT_OUT)
    S08Watr=models.IntegerField()
    S08CareThatEncompassesSUDEP=models.CharField(max_length=2, choices=OPT_OUT)
    S08SUDP=models.IntegerField()
    S08CareThatEncompassesRoadSafety=models.CharField(max_length=2, choices=OPT_OUT)
    S08RdSf=models.IntegerField()
    S08CareThatEncompassesHeights=models.CharField(max_length=2, choices=OPT_OUT)
    S08Hght=models.IntegerField()
    S08CareThatEncompassesSleep=models.CharField(max_length=2, choices=OPT_OUT)
    S08Slep=models.IntegerField()
    S08CareThatEncompassesPhotosensitivity=models.CharField(max_length=2, choices=OPT_OUT)
    S08PtSe=models.IntegerField()
    S08Info=models.IntegerField()
    S08Teen=models.IntegerField()
    S08Epil=models.IntegerField()
    S08SeizureDiary=models.CharField(max_length=2, choices=OPT_OUT)
    S08SzDi=models.IntegerField()
    S08IsThereEvidenceOfAIHP=models.IntegerField(choices=IHP_STATUS)
    S08IsThereEvidenceOfAIHPDate=models.DateField()
    S08IsThereEvidenceOfAnEHCP=models.IntegerField(choices=EHCP_STATUS)
    S08IsThereEvidenceOfAnEHCPDate=models.DateField()
    S08Edu=models.IntegerField()
    S08SiteCode=models.CharField(max_length=10)
    S08FormChecked=models.IntegerField(choices=CHECKED_STATUS)
    S08EDUSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08EDUSiteCode=models.CharField(max_length=10)
    S08EDUType=models.IntegerField(choices=EDUCATION_TYPE)
    S08EDUTypeOther=models.CharField(max_length=50)
    S08EDUDate=models.DateField()
    # S08EDUProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08EDUProvidedByOther=models.CharField(max_length=100)
    S08EDUDetails=models.CharField(max_length=250)
    S08EPILSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08EPILSiteCode=models.CharField(max_length=10)
    S08EPILType=models.IntegerField(choices=EPIL_TYPE_CHOICES)
    S08EPILTypeOther=models.CharField(max_length=50)
    S08EPILDate=models.DateField()
    # S08EPILProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08EPILProvidedByOther=models.CharField(max_length=100)
    S08EPILDetails=models.CharField(max_length=250)
    S08FAIDSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08FAIDSiteCode=models.CharField(max_length=10)
    S08FAIDDate=models.DateField()
    # S08FAIDProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08FAIDProvidedByOther=models.CharField(max_length=100)
    S08FAIDDetails=models.CharField(max_length=250)
    S08HGHTSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08HGHTSiteCode=models.CharField(max_length=10)
    S08HGHTDate=models.DateField()
    # S08HGHTProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08HGHTProvidedByOther=models.CharField(max_length=100)
    S08HGHTDetails=models.CharField(max_length=250)
    S08INFOSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08INFOSiteCode=models.CharField(max_length=10)
    S08INFOType=models.CharField(max_length=3,choices=INFORMATION_TYPES)
    S08INFOTypeOther=models.CharField(max_length=50)
    S08INFODate=models.DateField()
    # S08INFOProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08INFOProvidedByOther=models.CharField(max_length=100)
    S08INFODetails=models.CharField(max_length=250)
    S08PSCPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08PSCPSiteCode=models.CharField(max_length=10)
    S08PSCPDate=models.DateField()
    # S08PSCPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08PSCPProvidedByOther=models.CharField(max_length=100)
    S08PSCPDetails=models.CharField(max_length=250)
    S08PTSESectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08PTSESiteCode=models.CharField(max_length=10)
    S08PTSEDate=models.DateField()
    # S08PTSEProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08PTSEProvidedByOther=models.CharField(max_length=100)
    S08PTSEDetails=models.CharField(max_length=250)
    S08RDSFSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08RDSFSiteCode=models.CharField(max_length=10)
    S08RDSFDate=models.DateField()
    # S08RDSFProvidedBy=,"Q. 2","10","","","varchar(10)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08RDSFProvidedByOther=models.CharField(max_length=100)
    S08RDSFDetails=models.CharField(max_length=250)
    S08RISKSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08RISKSiteCode=models.CharField(max_length=10)
    S08RISKPDate=models.DateField()
    # S08RISKProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08RISKProvidedByOther=models.CharField(max_length=100)
    S08RISKDetails=models.CharField(max_length=250)
    S08SERVSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08SERVSiteCode=models.CharField(max_length=10)
    S08SERVDate=models.DateField()
    # S08SERVProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08SERVProvidedByOther=models.CharField(max_length=100)
    S08SERVDetails=models.CharField(max_length=250)
    S08SLEPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08SLEPSiteCode=models.CharField(max_length=10)
    S08SLEPDate=models.DateField()
    # S08SLEPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08SLEPProvidedByOther=models.CharField(max_length=100)
    S08SLEPDetails=models.CharField(max_length=250)
    S08SUDPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08SUDPSiteCode=models.CharField(max_length=10)
    S08SUDPDate=models.DateField()
    # S08SUDPProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08SUDPProvidedByOther=models.CharField(max_length=100)
    S08SUDPDetails=models.CharField(max_length=250)
    S08SZDISectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08SZDISiteCode=models.CharField(max_length=10)
    S08SZDIDate=models.DateField()
    # S08SZDIProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08SZDIProvidedByOther=models.CharField(max_length=100)
    S08SZDIDetails=models.CharField(max_length=250)
    S08TEENSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08TEENSiteCode=models.CharField(max_length=10)
    S08TEENType=models.IntegerField(choices=TRANSITION_TOPICS)
    S08TEENTypeOther=models.CharField(max_length=50)
    S08TEENDate=models.DateField()
    # S08TEENProvidedBy=,"Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08TEENProvidedByOther=models.CharField(max_length=100)
    S08TEENDetails=models.CharField(max_length=250)
    S08WATRSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S08WATRSiteCode=models.CharField(max_length=10)
    S08WATRDate=models.DateField()
    # S08WATRProvidedBy=,"Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
    S08WATRProvidedByOther=models.CharField(max_length=100)
    S08WATRDetails=models.CharField(max_length=250)
    
class S09(models.Model):
    S09SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S09WhenWasTheLastEpilepticSeizureApxExcNK=models.CharField(max_length=3, choices=DATE_ACCURACY)
    S09WhenWasTheLastEpilepticSeizure=models.DateField()
    S09WhenWasTheLastEpilepticSeizureUpdated=models.DateField()
    S09FormChecked=models.IntegerField(choices=CHECKED_STATUS)

class S10(models.Model):
    S10SectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S10ConsultantPaediatrician=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10ConsultantPaediatricianInputDate=models.DateField()
    S10ConsultantPaediatricianInputAchieved=models.DateField()
    S10ConsultantPaediatricianInputReasons=models.CharField(max_length=250)
    S10Esn=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10EsnInputDate=models.DateField()
    S10EsnInputAchieved=models.DateField()
    S10EsnInputReasons=models.CharField(max_length=250)
    S10PaediatricNeurologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10PaediatricNeurologistInputDate=models.DateField()
    S10PaediatricNeurologistInputAchieved=models.DateField()
    S10PaediatricNeurologistInputReasons=models.CharField(max_length=250)
    S10Cess=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10CessInputDate=models.DateField()
    S10CessInputAchieved=models.DateField()
    S10CessInputReasons=models.CharField(max_length=250)
    S10KetognicDietician=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10KetognicDieticianInputDate=models.DateField()
    S10KetognicDieticianInputAchieved=models.DateField()
    S10KetognicDieticianInputReasons=models.CharField(max_length=250)
    S10VnsService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10VnsServiceInputDate=models.DateField()
    S10VnsServiceInputAchieved=models.DateField()
    S10VnsServiceInputReasons=models.CharField(max_length=250)
    S10GeneticService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10GeneticServiceInputDate=models.DateField()
    S10GeneticServiceInputAchieved=models.DateField()
    S10GeneticServiceInputReasons=models.CharField(max_length=250)
    S10ClinicalPsychologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10ClinicalPsychologistInputDate=models.DateField()
    S10ClinicalPsychologistInputAchieved=models.DateField()
    S10ClinicalPsychologistInputReasons=models.CharField(max_length=250)
    S10EducationalPsychologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10EducationalPsychologistInputDate=models.DateField()
    S10EducationalPsychologistInputAchieved=models.DateField()
    S10EducationalPsychologistInputReasons=models.CharField(max_length=250)
    S10Psychiatrist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10PsychiatristInputDate=models.DateField()
    S10PsychiatristInputAchieved=models.DateField()
    S10PsychiatristInputReasons=models.CharField(max_length=250)
    S10Neuropyschologist=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10NeuropyschologistInputDate=models.DateField()
    S10NeuropyschologistInputAchieved=models.DateField()
    S10NeuropyschologistInputReasons=models.CharField(max_length=250)
    S10CounsellingService=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10CounsellingServiceInputDate=models.DateField()
    S10CounsellingServiceInputAchieved=models.DateField()
    S10CounsellingServiceInputReasons=models.CharField(max_length=250)
    S10OtherMentalHealthProfessional=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10OtherMentalHealthProfessionalInputDate=models.DateField()
    S10OtherMentalHealthProfessionalInputAchieved=models.DateField()
    S10OtherMentalHealthProfessionalInputReasons=models.CharField(max_length=250)
    S10YouthWorker=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10YouthWorkerInputDate=models.DateField()
    S10YouthWorkerInputAchieved=models.DateField()
    S10YouthWorkerInputReasons=models.CharField(max_length=250)
    S10OtherFreeField=models.IntegerField(choices=INPUT_REQUEST_STATUS)
    S10OtherFreeFieldInputDate=models.DateField()
    S10OtherFreeFieldInputAchieved=models.DateField()
    S10OtherFreeFieldInputReasons=models.CharField(max_length=250)
    S10FormalDevelopmentalAssessment=models.CharField(max_length=2, choices=OPT_OUT)
    S10FDA=models.IntegerField()
    S10FormalCognitiveAssessment=models.CharField(max_length=2, choices=OPT_OUT)
    S10FCA=models.IntegerField()
    S10ReviewByAPaediatrician12Months=models.CharField(max_length=2, choices=OPT_OUT)
    S10RBAP=models.IntegerField()
    S10DiagnosisOfEpilepsyWithdrawn=models.CharField(max_length=2, choices=OPT_OUT)
    S10DOEW=models.IntegerField()
    S10FormChecked=models.IntegerField(choices=CHECKED_STATUS)
    S10DOEWSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S10DOEWDate=models.DateField()
    S10DOEWDetails=models.CharField(max_length=250)
    S10FCASectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S10FCADate=models.DateField()
    S10FCADetails=models.CharField(max_length=250)
    S10FDASectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S10FDADate=models.DateField()
    S10FDADetails=models.CharField(max_length=250)
    S10RBAPSectionStatus=models.CharField(max_length=2, choices=SECTION_STATUS_CHOICES)
    S10RBAPDate=models.DateField()
    S10RBAPDetails=models.CharField(max_length=250)

# class EPIS(models):
#     "EPISSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "EPISType","Q. A","","","","varchar(3)","Radio button list","1 = Syncope And Anoxic Seizures; 2 = Behavioral Psychological And Psychiatric Disorders; 3 = Sleep Related Conditions; 4 = Paroxysmal Movement Disorders; 5 = Migraine Associated Disorders; 6 = Miscellaneous Events; 7 = Other"
#     "EPISSyncope","Q. B","","","","varchar(3)","Radio button list","a = Vasovagal syncope; b = Reflex anoxic seizures; c = Breath-holding attacks; d = Hyperventilation syncope; e = Compulsive valsalva; f = Neurological syncope; g = Imposed upper airways obstruction; h = Orthostatic intolerance; i = Long QT and cardiac syncope; j = Hyper-cyanotic spells"
#     "EPISBehavioral","Q. C","","","","varchar(3)","Radio button list","a = Daydreaming /inattention; b = Infantile gratification; c = Eidetic imagery; d = Tantrums and rage reactions; e = Out of body experiences; f = Panic attacks; g = Dissociative states; h = Non-epileptic seizures; i = Hallucinations in psychiatric disorders; j = Fabricated / factitious illness"
#     "EPISSleep","Q. D","","","","varchar(3)","Radio button list","a = Sleep related rhythmic movement disorders; b = Hypnogogic jerks; c = Parasomnias; d = REM sleep disorders; e = Benign neonatal sleep myoclonus; f = Periodic leg movements; g = Narcolepsy-cataplexy"
#     "EPISParoxysmal","Q. E","","","","varchar(3)","Radio button list","a = Tics; b = Stereotypies; c = Paroxysmal kinesigenic dyskinesia; d = Paroxysmal nonkinesigenic dyskinesia; e = Paroxysmal exercise induced dyskinesia; f = Benign paroxysmal tonic upgaze; g = Episodic ataxias; h = Alternating hemiplegia; i = Hyperekplexia; j = Opsoclonus-myoclonus syndrome"
#     "EPISMigraine","Q. F","","","","varchar(3)","Radio button list","a = Migraine with visual aura; b = Familial hemiplegic migraine; c = Benign paroxysmal torticollis; d = Benign paroxysmal vertigo; e = Cyclical vomiting"
#     "EPISMiscellaneous","Q. G","","","","varchar(3)","Radio button list","a = Benign myoclonus of infancy and shuddering attacks; b = Jitteriness; c = Sandifer syndrome; d = Non-epileptic head drops; e = Spasmus nutans; f = Raised intracranial pressure; g = Paroxysmal extreme pain disorder; h = Spinal myoclonus"
#     "EPISOther","Q. H","250","","","varchar(250)","Textbox",""

# class CAUS(models):
#     "CAUSSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "CAUSDateCauseApxExcNK","Q. 1","","","","varchar(3)","Radio button list","Apx = Approximate date; Exc = Exact date; NK = Not known"
#     "CAUSDateCause","Q. 1i","","","","datetime","Date",""
#     "CAUSMain","Q. 2","","","","varchar(3)","Radio button list","Str = Structural; Gen = Genetic; Inf = Infectious; Met = Metabolic; Imm = Immune; NK = Not known"
#     "CAUSSubStructural","Q. 3","","","","varchar(3)","Radio button list","TbS = Tuberous Sclerosis; StW = Sturge Weber; FCD = Focal cortical dysplasia; HyH = Hypothalamic Hamartoma; LGT = Low grade tumour; TuO = Tumour (other); MCD = Malformations of Cortical Development; Vas = Vascular (eg arterial ischaemic stroke venous ischaemia cerebral haemorrhage); TBI = Traumatic brain injury; NR = Not required"
#     "CAUSSubGenetic","Q. 3","","","","varchar(3)","Radio button list","DrS = Dravet syndrome; GTD = Glucose Transporter Defect; AnS = Angelman Syndrome; ReS = Rett Syndrome; ChA = Chromosomal abnormality; GeA = Gene abnormality"
#     "CAUSSubGeneticChromoAbno","Q. 3i","200","","","varchar(200)","Textbox",""
#     "CAUSSubGeneticGeneAbno","Q. 3i","","","","varchar(3)","Radio button list","UBE = UBE3A; GLU = GLUT1; SLC = SLC2A1; MEC = MECP2; SCN = SCN1A; STX = STXBP1; CDK = CDKL5; KCN = KCNQ2; SCN = SCN2A; KCN = KCNT1; ARX = ARX; FOX = FOXG1; PCD = PCDH19; GRI = GRIN2A; Oth = Other"
#     "CAUSSubGeneticGeneAbnoOther","Q. 3ii","250","","","varchar(250)","Textbox",""
#     "CAUSSubInfectious","Q. 3","250","","","varchar(250)","Textbox",""
#     "CAUSSubMetabolic","Q. 3","","","","varchar(3)","Radio button list","Mit = Mitochondrial disorder; Neu = Neuronal Ceroid Lipofuscinosis (Batten Disease); PPM = Disorder of pyridoxine/pyridoxal phosphate metabolism; BiM = Disorder of biotin metabolism; CrM = Disorder of creatine metabolism; AmA = Disorder of amino acid; UrA = Disorder of urea cycle; PyP = Disorder of pyrimidine and purine; Cho = Disorder of cholesterol; Oth = Other neurometabolic disorder"
#     "CAUSSubMetabolicOther","Q. 3i","250","","","varchar(250)","Textbox",""
#     "CAUSSubImmune","Q. 3","","","","varchar(3)","Radio button list","RaE = Rasmussen Encephalitis; AnM = Antibody mediated"
#     "CAUSSubImmuneAntibody","Q. 3i","","","","varchar(3)","Radio button list","VGK = VGKC; NMD = NMDAR; GAD = GAD; TPO = TPO; MOG = MOG; Oth = Other"
#     "CAUSSubImmuneAntibodyOther","Q. 3ii","250","","","varchar(250)","Textbox",""

# class ECLS(models):
#     "ECLSSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "ECLSDateOfDiagnosisApproxExactNK","Q. 1","","","","varchar(3)","Radio button list","Apx = Approximate date; Exc = Exact date; NK = Not known"
#     "ECLSDateOfDiagnosis","Q. 1i","","","","datetime","Date",""
#     "ECLSElectroclinicalSyndrome","Q. 2","3","","","varchar(3)","Combo box","46 = Autosomal dominant nocturnal frontal lobe epilepsy (ADNFLE); 48 = Autosomal dominant partial epilepsy with auditory features; 30 = Bathing epilepsy; 4 = (Benign) childhood epilepsy with centrotemporal spikes (BECTS) (benign rolandic epilepsy); 16 = Benign familial neonatal seizures; 38 = Benign infantile seizures; 37 = (Benign) Myoclonic epilepsy in infancy; 21 = Benign neonatal seizures Benign non-familial neonatal seizures; 13 = Childhood absence epilepsy (CAE); 27 = Childhood epilepsy with occipital paroxysms; 14 = Dravet syndrome (severe myoclonic epilepsy of/in infancy or SMEI); 34 = Early myoclonic encephalopathy; 44 = Epilepsy with generalized tonic-clonic seizures only (Epilepsy with generalised tonic clonic seizures on awakening); 41 = Epilepsy with myoclonic absences; 5 = Epilepsy with myoclonic astatic seizures (Doose syndrome) (Myoclonic astatic epilepsy); 24 = Eyelid myoclonia with absences; 47 = Familial temporal lobe epilepsies; 32 = Familial focal epilepsy with variable foci; 10 = Frontal lobe epilepsy; 23 = Gelastic seizures due to hypothalamic hamartoma; 33 = Generalized Epilepsies with Febrile seizures plus (FS+); 28 = Hemiconvulsion-hemiplegia syndrome; 29 = Hot water epilepsy; 17 = Idiopathic focal epilepsy of childhood; 12 = Juvenile absence epilepsy (JAE); 11 = Juvenile myoclonic epilepsy (JME); 40 = Late onset childhood occipital epilepsy (Gastaut type) (idiopathic childhood occipital epilepsy); 42 = Lennox-Gastaut syndrome; 43 = Landau-Kleffner syndrome; 36 = Migrating partial (focal) seizures of infancy; 39 = Myoclonic encephalopathy in non-progressive disorders {myoclonic status in non-progressive encephalopathies}; 7 = Occipital lobe epilepsy; 35 = Ohtahara syndrome; 6 = Panayiotopoulos syndrome (Early onset (benign) childhood occipital epilepsy); 8 = Parietal lobe epilepsy; 25 = Perioral myoclonia with absences; 26 = Phantom absences; 19 = Primary reading epilepsy; 45 = Progressive myoclonus (myoclonic) epilepsies (PME); 22 = Rasmussen's encephalitis (chronic progressive epilepsia partialis continua) (Kozhevnikov syndrome); 31 = Reflex epilepsies; 20 = Startle epilepsy; 9 = Temporal lobe epilepsy; 18 = Visual sensitive epilepsies; 15 = West syndrome; 3 = 'Unclassified syndrome'; 1 = No epilepsy syndrome stated; O = Other"
#     "ECLSElectroclinicalSyndromeOther",models.CharField(max_length=250)

# class MHPB(models):
#     "MHPBSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "MHPBDateNeurodevelopmentalProblemApxExcNK","Q. 1","","","","varchar(3)","Radio button list","Apx = Approximate date; Exc = Exact date; NK = Not known"
#     "MHPBDateNeurodevelopmentalProblem","Q. 1i","","","","datetime","Date",""
#     "MHPBMentalHealthProblem","Q. 2","3","","","varchar(3)","Drop down list","MoD = Mood disorder; AxD = Anxiety disorder; EmB = Emotional/ behavioural; SHm = Self harm; Oth = Other"
#     "MHPBMentalHealthProblemOther",models.CharField(max_length=250)
#     "MHPBMentalHealthProblemEmotional","Q. 2i","3","","","varchar(3)","Drop down list","CnD = Conduct disorder; ODD = Oppositional Defiant Disorder (ODD)"

# class NUDS(models):
#     "NUDSSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "NUDSDateNeurodevelopmentalProblemApxExcNK","Q. 1","","","","varchar(3)","Radio button list","Apx = Approximate date; Exc = Exact date; NK = Not known"
#     "NUDSDateNeurodevelopmentalProblem","Q. 1i","","","","datetime","Date",""
#     "NUDSNeurodevelopmentalProblem","Q. 2","3","","","varchar(3)","Drop down list","ASD = Autistic spectrum disorder; CeP = Cerebral palsy; NDC = Neurodegenerative disease or condition; ChD = An identified chromosomal disorder with a neurological or developmental component; ADH = Attention deficit hyperactivity disorder; Int = intellectual disability/global development delay/'learning disability'; Dsp = dyspraxia; Dsl = dyslexia; SDo = speech disorder; Oth = other learning difficulty"
#     "NUDSNeurodevelopmentalProblemOther",models.CharField(max_length=250)
#     "NUDSNeurodevelopmentalProblemSeverity","Q. 2i","3","","","varchar(3)","Drop down list","Mil = Mild; Mod = Moderate; Sev = Severe; Pro = Profound"

# class SEIZ(models):
#     "SEIZSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "SEIZDateOfOnsetApproxExactNK","Q. 1","","","","varchar(3)","Radio button list","Apx = Approximate date; Exc = Exact date; NK = Not known"
#     "SEIZDateOfOnset","Q. 1i","","","","datetime","Date",""
#     "SEIZDescriptionOfEvent","Q. 2","250","","","varchar(250)","Textbox",""
#     "SEIZEpilepticOrNonEpilepticOrUncertain","Q. 3","","","","varchar(3)","Radio button list","Ep = Epileptic; NEp = Non-epileptic; Unc = Uncertain"
#     "SEIZEpilepticSeizureType","Q. 31","","","","varchar(3)","Radio button list","FO = Focal onset; GO = Generalised onset; UO = Unknown onset; UC = Unclassified"
#     "SEIZNonEpilepticSeizureType","Q. 32","","","","varchar(3)","Radio button list","SAS = Syncope And Anoxic Seizures; BPP = Behavioral Psychological And Psychiatric Disorders; SRC = Sleep Related Conditions; PMD = Paroxysmal Movement Disorders; MAD = Migraine Associated Disorders; ME = Miscellaneous Events; Oth = Other"
#     "SEIZEpilepticSeizureTypeFOImpAware","Q. 311i","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOAutomatisms",models.IntegerField(choices=CHECKED_STATUS)
#     "SEIZEpilepticSeizureTypeFOAtonic","Q. 311iii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOClonic","Q. 311iv","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOLeft","Q. 311v","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFORight","Q. 311vi","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOEpilepticSpasms","Q. 311vii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOHyperkinetic",models.IntegerField(choices=CHECKED_STATUS)
#     "SEIZEpilepticSeizureTypeFOMyoclonic",models.IntegerField(choices=CHECKED_STATUS)
#     "SEIZEpilepticSeizureTypeFOTonic","Q. 311x","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOAutonomic","Q. 311xi","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOBehaviourArrest","Q. 311xii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOCognitive",models.IntegerField(choices=CHECKED_STATUS)
#     "SEIZEpilepticSeizureTypeFOEmotional",models.IntegerField(choices=CHECKED_STATUS)
#     "SEIZEpilepticSeizureTypeFOSensory","Q. 311xv","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOCentroTemporal","Q. 311xvi","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOTemporal","Q. 311xvii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOFrontal","Q. 311xviii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOParietal","Q. 311xix","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOOccipital","Q. 311xx","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOGelastic","Q. 311xxi","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOFocaltoBilateralTonicClonic","Q. 311xxii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOOther","Q. 311xxiii","3","","","varchar(3)","Checkbox","1 = Checked; 2 = Unchecked"
#     "SEIZEpilepticSeizureTypeFOOtherDetails","Q. 311xxiiii","250","","","varchar(250)","Textbox",""
#     "SEIZEpilepticSeizureTypeGeneralisedOnset","Q. 312","","","","varchar(3)","Radio button list","TCl = Tonic-clonic; Clo = Clonic; Ton = Tonic; MyC = Myoclonic; MTC = Myoclonic-tonic-clonic; MAt = Myoclonic-atonic; Ato = Atonic; EpS = Epileptic spasms; TAb = Typical absence; Aab = Atypical absence; MAb = Myoclonic absence; AEM = Absence with eyelid myoclonia; Oth = Other"
#     "SEIZEpilepticSeizureTypeGeneralisedOnsetOtherDetails","Q. 312i","250","","","varchar(250)","Textbox",""
#     "SEIZNonEpilepticSeizureTypeUnknownOnset","Q. 313","","","","varchar(3)","Radio button list","TCl = Tonic-clonic; EpS = Epileptic spasms; BAr = Behaviour arrest; Oth = Other"
#     "SEIZNonEpilepticSeizureTypeUnknownOnsetOtherDetails","Q. 313i","250","","","varchar(250)","Textbox",""
#     "SEIZNonEpilepticSeizureTypeSyncope","Q. 32i","","","","varchar(3)","Radio button list","a = Vasovagal syncope; b = Reflex anoxic seizures; c = Breath-holding attacks; d = Hyperventilation syncope; e = Compulsive valsalva; f = Neurological syncope; g = Imposed upper airways obstruction; h = Orthostatic intolerance; i = Long QT and cardiac syncope; j = Hyper-cyanotic spells"
#     "SEIZNonEpilepticSeizureTypeBehavioral","Q. 32ii","","","","varchar(3)","Radio button list","a = Daydreaming /inattention; b = Infantile gratification; c = Eidetic imagery; d = Tantrums and rage reactions; e = Out of body experiences; f = Panic attacks; g = Dissociative states; h = Non-epileptic seizures; i = Hallucinations in psychiatric disorders; j = Fabricated / factitious illness"
#     "SEIZNonEpilepticSeizureTypeSleep","Q. 32iii","","","","varchar(3)","Radio button list","a = Sleep related rhythmic movement disorders; b = Hypnogogic jerks; c = Parasomnias; d = REM sleep disorders; e = Benign neonatal sleep myoclonus; f = Periodic leg movements; g = Narcolepsy-cataplexy"
#     "SEIZNonEpilepticSeizureTypeParoxysmal","Q. 32iv","","","","varchar(3)","Radio button list","a = Tics; b = Stereotypies; c = Paroxysmal kinesigenic dyskinesia; d = Paroxysmal nonkinesigenic dyskinesia; e = Paroxysmal exercise induced dyskinesia; f = Benign paroxysmal tonic upgaze; g = Episodic ataxias; h = Alternating hemiplegia; i = Hyperekplexia; j = Opsoclonus-myoclonus syndrome"
#     "SEIZNonEpilepticSeizureTypeMigraine","Q. 32v","","","","varchar(3)","Radio button list","a = Migraine with visual aura; b = Familial hemiplegic migraine; c = Benign paroxysmal torticollis; d = Benign paroxysmal vertigo; e = Cyclical vomiting"
#     "SEIZNonEpilepticSeizureTypeMiscellaneous","Q. 32vi","","","","varchar(3)","Radio button list","a = Benign myoclonus of infancy and shuddering attacks; b = Jitteriness; c = Sandifer syndrome; d = Non-epileptic head drops; e = Spasmus nutans; f = Raised intracranial pressure; g = Paroxysmal extreme pain disorder; h = Spinal myoclonus"
#     "SEIZNonEpilepticSeizureTypeOther","Q. 32vii","250","","","varchar(250)","Textbox",""

# class AED(models):
#     "AEDSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "AEDGender","Q. 1","3","","","varchar(3)","{n/a}",""
#     "AEDType","Q. 1","3","","","varchar(3)","Drop down list","1 = Acetazolamide; 2 = ACTH; 3 = Carbamazepine; 4 = Clobazam; 5 = Clonazepam; 6 = Eslicarbazepine acetate; 7 = Ethosuximide; 8 = Gabapentin; 9 = Lacosamide; 10 = Lamotrigine; 11 = Levetiracetam; 12 = Methylprednisolone; 13 = Nitrazepam; 14 = Oxcarbazepine; 15 = Perampanel; 16 = Piracetam; 17 = Phenobarbital; 18 = Phenytoin; 19 = Pregabalin; 20 = Prednisolone; 21 = Primidone; 22 = Rufinamide; 23 = Sodium valproate; 24 = Stiripentol; 25 = Sulthiame; 26 = Tiagabine; 27 = Topiramate; 28 = Vigabatrin; 29 = Zonisamide; O = Other"
#     "AEDOther","Q. 1i","100","","","varchar(100)","Textbox",""
#     "AEDStartDate","Q. 2","","","","datetime","Date",""
#     "AEDStopDate","Q. 3","","","","datetime","Date",""
#     "AEDStopDate_NK"," - ","","","","bit","Checkbox","1 = Checked; 0 = Unchecked"
#     "AEDRisk","Q. 4","","","","varchar(3)","Radio button list","Y = Yes; N = No"


# class RMED(models):
#     "RMEDSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "RMEDType","Q. 1","3","","","varchar(3)","Drop down list","BMZ = Buccal midazolam; RDZ = Rectal diazepam; Oth = Other"
#     "RMEDOther","Q. 1i","100","","","varchar(100)","Textbox",""
#     "RMEDStartDate","Q. 2","","","","datetime","Date",""
#     "RMEDStopDate","Q. 3","","","","datetime","Date",""
#     "RMEDStopDate_NK"," - ","","","","bit","Checkbox","1 = Checked; 0 = Unchecked"
#     "RMEDNotes","Q. 4","250","","","varchar(250)","Textbox",""

# class EDU(models):
#     "EDUSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "EDUSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "EDUType","Q. 1","3","","","varchar(3)","Drop down list","1 = Consent to share health information with school; 2 = Teacher generic epilepsy awareness; 3 = IEP (individual education plan); 4 = Exam Provision; 5 = School rescue medication plan; 6 = School rescue medication training; 999 = Other"
#     "EDUTypeOther","Q. 1i","50","","","varchar(50)","Textbox",""
#     "EDUDate","Q. 2","","","","datetime","Date",""
#     "EDUProvidedBy","Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "EDUProvidedByOther","Q. 3i","100","","","varchar(100)","Textbox",""
#     "EDUDetails","Q. 4","250","","","varchar(250)","Textbox",""

# class EPIL(models):
#     "EPILSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "EPILSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "EPILType","Q. 1","3","","","varchar(3)","Drop down list","1 = Seizure diary; 2 = Seizure types; 3 = Syndrome type; 4 = Prognosis; 5 = Co-morbidities; 6 = National Support Groups; 999 = Other"
#     "EPILTypeOther","Q. 1i","50","","","varchar(50)","Textbox",""
#     "EPILDate","Q. 2","","","","datetime","Date",""
#     "EPILProvidedBy","Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "EPILProvidedByOther","Q. 3i","100","","","varchar(100)","Textbox",""
#     "EPILDetails","Q. 4","250","","","varchar(250)","Textbox",""

# class FAID(models):
#     "FAIDSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "FAIDSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "FAIDDate","Q. 1","","","","datetime","Date",""
#     "FAIDProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "FAIDProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "FAIDDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class HGHT(models):
#     "HGHTSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "HGHTSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "HGHTDate","Q. 1","","","","datetime","Date",""
#     "HGHTProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "HGHTProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "HGHTDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class INFO(models):
#     "INFOSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "INFOSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "INFOType","Q. 1","3","","","varchar(3)","Drop down list","1 = Treatment goals; 2 = Drug information leaflet; 3 = Sodium Valproate Risks and benefits; 4 = VNS option; 5 = Surgery option; 6 = Ketogenic option; 999 = Other"
#     "INFOTypeOther","Q. 1i","50","","","varchar(50)","Textbox",""
#     "INFODate","Q. 2","","","","datetime","Date",""
#     "INFOProvidedBy","Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "INFOProvidedByOther","Q. 3i","100","","","varchar(100)","Textbox",""
#     "INFODetails","Q. 4","250","","","varchar(250)","Textbox",""

# class PSCP(models):
#     "PSCPSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "PSCPSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "PSCPDate","Q. 1","","","","datetime","Date",""
#     "PSCPProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "PSCPProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "PSCPDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class PTSE(models):
#     "PTSESectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "PTSESiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "PTSEDate","Q. 1","","","","datetime","Date",""
#     "PTSEProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "PTSEProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "PTSEDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class RDSF(models):
#     "RDSFSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "RDSFSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "RDSFDate","Q. 1","","","","datetime","Date",""
#     "RDSFProvidedBy","Q. 2","10","","","varchar(10)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "RDSFProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "RDSFDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class RISK(models):
#     "RISKSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "RISKSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "RISKPDate","Q. 1","","","","datetime","Date",""
#     "RISKProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "RISKProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "RISKDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class SERV(models):
#     "SERVSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "SERVSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "SERVDate","Q. 1","","","","datetime","Date",""
#     "SERVProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "SERVProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "SERVDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class SLEPS(models):
#     "SLEPSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "SLEPSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "SLEPDate","Q. 1","","","","datetime","Date",""
#     "SLEPProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "SLEPProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "SLEPDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class SUDP(models):
#     "SUDPSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "SUDPSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "SUDPDate","Q. 1","","","","datetime","Date",""
#     "SUDPProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "SUDPProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "SUDPDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class SZDI(models):
#     "SZDISectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "SZDISiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "SZDIDate","Q. 1","","","","datetime","Date",""
#     "SZDIProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "SZDIProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "SZDIDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class TEEN(models):
#     "TEENSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "TEENSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "TEENType","Q. 1","3","","","varchar(3)","Drop down list","1 = Driving; 2 = Contraception; 3 = Pregnancy; 4 = Adherence; 5 = Sleep hygiene; 6 = Alcohol; 7 = Recreational Drugs; 8 = Career; 9 = Bus pass; 10 = Seen on own; 11 = Self management; 12 = Goal setting; 13 = Ready; 14 = Steady; 15 = Go; 16 = Hello; 999 = Other"
#     "TEENTypeOther","Q. 1i","50","","","varchar(50)","Textbox",""
#     "TEENDate","Q. 2","","","","datetime","Date",""
#     "TEENProvidedBy","Q. 3","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "TEENProvidedByOther","Q. 3i","100","","","varchar(100)","Textbox",""
#     "TEENDetails","Q. 4","250","","","varchar(250)","Textbox",""

# class WATR(models):
#     "WATRSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "WATRSiteCode"," - ","10","","","varchar(10)","{n/a}",""
#     "WATRDate","Q. 1","","","","datetime","Date",""
#     "WATRProvidedBy","Q. 2","20","","","varchar(20)","Drop down list","uspx_ServiceContractList = FullDetails"
#     "WATRProvidedByOther","Q. 2i","100","","","varchar(100)","Textbox",""
#     "WATRDetails","Q. 3","250","","","varchar(250)","Textbox",""

# class DOEW(models):
#     "DOEWSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "DOEWDate","Q. 1","","","","datetime","Date",""
#     "DOEWDetails","Q. 2","250","","","varchar(250)","Textbox",""
# class FCA(models):
#     "FCASectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "FCADate","Q. 1","","","","datetime","Date",""
#     "FCADetails","Q. 2","250","","","varchar(250)","Textbox",""

# class FDA(models):
#     "FDASectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "FDADate","Q. 1","","","","datetime","Date",""
#     "FDADetails","Q. 2","250","","","varchar(250)","Textbox",""

# class RBAP(models):
#     "RBAPSectionStatus"," - ","","","","int","{n/a}","-1 = Not set; 0 = Not saved; 5 = Disabled; 10 = Complete; 20 = Incomplete; 30 = Errors; 60 = TransferredIn; 70 = TransferredOut"
#     "RBAPDate","Q. 1","","","","datetime","Date",""
#     "RBAPDetails","Q. 2","250","","","varchar(250)","Textbox",""