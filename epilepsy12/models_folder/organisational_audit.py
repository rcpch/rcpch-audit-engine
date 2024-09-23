from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField

YES_NO_UNCERTAIN = {
    1: 'Yes',
    2: 'No',
    3: 'Uncertain'
}

class OrganisationalAuditSubmissionPeriod(models.Model):
    year = models.PositiveIntegerField()
    is_open = models.BooleanField(default=False)

ReasonableDecimalField = lambda: models.DecimalField(null=True, max_digits=7, decimal_places=3)

class OrganisationalAuditSubmission(models.Model):
    # These field names mostly match the CSV export format from the old system for convenience

    # 1. Workforce

    S01WTEConsultants = ReasonableDecimalField() # 1.1
    S01WTEConsultantsEpilepsy = ReasonableDecimalField() # 1.2

    S01EpilepsyClinicalLead = models.BooleanField(null=True) # 1.3
    S01EpilepsyClinicalLeadTitle = models.CharField(null=True) # 1.3i
    S01EpilepsyClinicalLeadFirstName = models.CharField(null=True)
    S01EpilepsyClinicalLeadSurname = models.CharField(null=True)

    S01WTEEpilepsySpecialistNurses = ReasonableDecimalField() # 1.4
    # TODO MRB: do they want this split out into separate columns as per the template CSV
    S01ESNFunctions = ArrayField(models.PositiveIntegerField(null=True, choices={
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
    })) #1.4i


    # 2. Epilepsy Clinic configuration

    S02DefinedEpilepsyClinics = models.BooleanField(null=True) # 2.1
    S02EpilepsyClinicsPerWeek = ReasonableDecimalField() # 2.1i
    S02Consultant20Mins = models.BooleanField(null=True) # 2.1ii
    S02TFC223 = models.PositiveIntegerField(choices={
        1: 'Not applicable',
        2: 'Yes',
        3: 'No, not at all',
        4: 'No, in development'
    }) # 2.2


    # 3. Tertiary provision

    S03WTEPaediatricNeurologists = ReasonableDecimalField() # 3.1
    S03PathwaysTertiaryPaedNeurology = models.BooleanField(null=True) # 3.2
    S03PaedNeurologistsDirectReferrals = models.BooleanField(null=True) # 3.3
    S03SatellitePaediatricNeurologyClinics = models.BooleanField(null=True) # 3.4

    S03CommenceKetogenicDiet = models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 3.5i
    S03ReviewKetogenicDiet = models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 3.5ii
    S03VNSInsertion = models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 3.5iii
    S03VNSReview = models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 3.5iv

    
    # 4. Investigations

    S04LeadECG = models.PositiveIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1i
    S04AwakeMRI = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1ii
    S04MriWithSedation = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1iii
    S04MriWithGeneralAnaesthetic = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1iv
    S04StandardEeg = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1v
    S04SleepDeprivedEeg = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1vi
    S04MelatoninInducedEeg = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1vii
    S04SedatedEeg = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1viii
    S042448HAmbulatoryEeg = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1ix
    S04InpatientVideoTelemetry = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1x
    S04OutpatientVideoTelemetry = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1xi
    S04HomeVideoTelemetry = models.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1xii
    S04PortableEEGOnWardAreaWithinTrust = moels.PositiveSmallIntegerField(choices=YES_NO_UNCERTAIN, null=True) # 4.1xiii
    # TODO MRB: do we need an entry for requesting and consenting of Whole Genome Sequencing?


    # 5. Service Contact

    S05ContactEpilepsyServiceForSpecialistAdvice = models.BooleanField(null=True) # 5.1
    S05AdviceAvailableAllWeekdays = models.BooleanField(null=True) # 5.1.1
    S05AdviceAvailableAllOutOfHours = models.BooleanField(null=True) # 5.1.2
    S05AdviceAvailable52WeeksPerYear = models.BooleanField(null=True) # 5.1.3

    S05TypicalTimeToAchieveSpecialistAdvice = models.PositiveIntegerField(null=True, choices={
        1: 'Same working day',
        2: 'By next working day',
        3: 'Within 3-4 working days',
        4: 'Within a working week'
    }) # 5.2

    S05WhoProvidesSpecialistAdvice = models.PositiveIntegerField(null=True, choices={
        1: 'ESN',
        2: 'Consultant Paediatrician with expertise in epilepsy',
        3: 'Paediatric neurologist',
        4: 'Trainee paediatric neurologist',
        5: 'Other'
    }) # 5.3
    S05WhoProvidesSpecialistAdviceOther = models.CharField(null=True) # 5.3

    S05evidenceclearpointofcontact = models.BooleanField(null=True) # 5.4
