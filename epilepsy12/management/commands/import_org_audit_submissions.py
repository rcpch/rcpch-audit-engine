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
                    converter = CONVERTERS[column]

                    if not pd.isnull(raw_value) and converter:
                        value = converter(raw_value)
                    else:
                        value = raw_value

                    if value is None:
                        raise ValueError(f"Could not convert {column} {raw_value}")

                    print(f"!! {column} {raw_value} -> {value}")
                    setattr(submission, column, value)

            submission.save()
            
            break

            