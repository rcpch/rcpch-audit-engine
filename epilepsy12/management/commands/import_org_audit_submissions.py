import pandas as pd

from django.core.management.base import BaseCommand

from ...models import (
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
    Trust,
    LocalHealthBoard
)

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

            try:
                submission.trust = Trust.objects.get(ods_code=row["SiteCode"])
            except Trust.DoesNotExist:
                submission.local_health_board = LocalHealthBoard.objects.get(ods_code=row["SiteCode"])
            
            for column, value in row.to_dict().items():
                if column.startswith("S"):
                    if value == "Y":
                        value = True
                    elif value == "N":
                        value = False

                    setattr(submission, column, value)

            submission.save()
            
            break

            