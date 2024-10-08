import pandas as pd

from django.core.management.base import BaseCommand

from ...models import (
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
    Trust,
    LocalHealthBoard
)

def yes_no(value):
    match value:
        case "Y": return True
        case "N": return False

def yes_no_uncertain(value):
    match value:
        case "Y": return 1
        case "N": return 2
        case "U": return 3

def tfc_223(value):
    match value:
        case "NA": return 1
        case "Y": return 2
        case "N": return 3
        case "NID": return 4

CONVERTERS = {
    "S01WTEConsultants": None,
    "S01WTEConsultantsEpilepsy": None,
    "S01EpilepsyClinicalLead": yes_no,
    "S01EpilepsyClinicalLeadTitle": None,
    "S01EpilepsyClinicalLeadFirstName": None,
    "S01EpilepsyClinicalLeadSurname": None,
    "S01WTEEpilepsySpecialistNurses": None,
    "S02DefinedEpilepsyClinics": yes_no,
    "S02EpilepsyClinicsPerWeek": None,
    "S02Consultant20Mins": yes_no,
    "S02TFC223": tfc_223,
    "S03WTEPaediatricNeurologists": None,
    "S03PathwaysTertiaryPaedNeurology": yes_no,
    # TODO MRB: do we need an N/A option in the model?
    "S03PaedNeurologistsDirectReferrals": yes_no,
    "S03SatellitePaediatricNeurologyClinics": yes_no,
    "S03CommenceKetogenicDiet": yes_no_uncertain,
    "S03ReviewKetogenicDiet": yes_no_uncertain,
    "S03VNSInsertion": yes_no_uncertain,
    "S03VNSReview": yes_no_uncertain,
    "S04LeadECG": yes_no_uncertain,
    "S04AwakeMRI": yes_no_uncertain,
    "S04MriWithSedation": yes_no_uncertain,
    "S04MriWithGeneralAnaesthetic": yes_no_uncertain,
    "S04StandardEeg": yes_no_uncertain,
    "S04SleepDeprivedEeg": yes_no_uncertain,
    "S04MelatoninInducedEeg": yes_no_uncertain,
    "S04SedatedEeg": yes_no_uncertain,
    "S042448HAmbulatoryEeg": yes_no_uncertain,
    "S04InpatientVideoTelemetry": yes_no_uncertain,
    "S04OutpatientVideoTelemetry": yes_no_uncertain,
    "S04HomeVideoTelemetry": yes_no_uncertain,
    "S04PortableEEGOnWardAreaWithinTrust": yes_no_uncertain,
    "S05ContactEpilepsyServiceForSpecialistAdvice": yes_no,
    "S05AdviceAvailableAllWeekdays": yes_no,
    "S05AdviceAvailableOutOfHours": yes_no,
    "S05AdviceAvailable52WeeksPerYear": yes_no

}

class Command(BaseCommand):
    help = "Import organisational audit submissions from CSV export"

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            required=True,
            help="CSV file of submissions to import",
        )
        parser.add_argument(
            "-s",
            "--submission-period",
            type=int,
            required=True,
            help="ID of submission period to import into",
        )

    def handle(self, *args, **options):
        file = options["file"]
        data = pd.read_csv(file)

        submission_period = OrganisationalAuditSubmissionPeriod.objects.get(
            id=options["submission_period"]
        )

        for _, row in data.iterrows():
            ods_code = row["SiteCode"]

            submission = OrganisationalAuditSubmission()
            submission.submission_period = submission_period

            try:
                submission.trust = Trust.objects.get(ods_code=row["SiteCode"])
            except Trust.DoesNotExist:
                submission.local_health_board = LocalHealthBoard.objects.get(ods_code=row["SiteCode"])
            
            for column, raw_value in row.to_dict().items():
                if column in CONVERTERS:
                    value = None

                    if not pd.isnull(raw_value):
                        converter = CONVERTERS[column]
                        value = converter(raw_value) if converter else raw_value

                        if value is None:
                            raise ValueError(f"Could not convert {column} {raw_value}")

                    print(f"!! {column} {raw_value} -> {value}")
                    setattr(submission, column, value)

            # submission.save()
            
            break

            