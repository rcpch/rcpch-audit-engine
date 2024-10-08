import pandas as pd

from django.core.management.base import BaseCommand

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

    def handle(self, *args, **options):
        file = options["file"]
        data = pd.read_csv(file)

        print(f"!! {data}")