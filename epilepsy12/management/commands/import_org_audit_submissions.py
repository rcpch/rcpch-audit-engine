import pandas as pd

from django.core.management.base import BaseCommand

from ...models import (
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
    Trust,
    LocalHealthBoard
)

def include_column(column):
    # TODO: adapt multiselect columns
    if column.startswith("S01ESN") or \
        column.startswith("S06Professionals") or \
        column.startswith("S07ScreenForIssues") or \
        column.startswith("S07MentalHealthQuestionnaire") or \
        column.startswith("S07MentalHealthAgreedPathway") or \
        column.startswith("S07DoesThisCompromise") or \
        column.startswith("S07TrustAchieve") or \
        column.startswith("S08AgreedReferral"):
        return False

    return column.startswith("S0") or column.startswith("S1")

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
                if include_column(column):
                    value = None if pd.isnull(raw_value) else raw_value

                    print(f"!! {column} {raw_value} -> {value}:{type(value)}")
                    setattr(submission, column, value)

            submission.save()
            
            break

            