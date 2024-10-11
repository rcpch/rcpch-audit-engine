import pandas as pd

from django.core.management.base import BaseCommand
from ...epilepsy12.organisational_audit import import_submissions_from_csv

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

        import_submissions_from_csv(submission_period, data)
            