import pandas as pd

from django.core.management.base import BaseCommand

from ...models import (
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
    Trust,
    LocalHealthBoard
)

def adapt_multiselect_field(row, choices_to_column):
    return [key for key, value in choices_to_column.items() if row[value] == 1]

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
            
            #######################
            # Single value fields #
            #######################

            for column, raw_value in row.to_dict().items():
                # Multiselect fields handled below
                if column.startswith("S01ESN") or \
                    column.startswith("S06Professionals") or \
                    column.startswith("S07ScreenForIssues") or \
                    column.startswith("S07MentalHealthQuestionnaire") or \
                    column.startswith("S07MentalHealthAgreedPathway") or \
                    column.startswith("S07DoesThisCompromise") or \
                    column.startswith("S07TrustAchieve") or \
                    column.startswith("S08AgreedReferral") or \
                    not column.startswith("S0") or \
                    not column.startswith("S01"):
                        continue
                
                value = None if pd.isnull(raw_value) else raw_value
                setattr(submission, column, value)

            ######################
            # Multiselect fields #
            ######################      

            submission.S01ESNFunctions = adapt_multiselect_field(row, {
                1: 'S01ESNEDVisit',
                2: 'S01ESNHomeVisit',
                3: 'S01ESNIndividualHealthcare',
                4: 'S01ESNNurseLedClinic',
                5: 'S01ESNNursePrescribing',
                6: 'S01ESNRescueMedicationParent',
                7: 'S01ESNRescueMedicationSchool',
                8: 'S01ESNSchoolMeetings',
                9: 'S01ESNWardVisits',
                10: 'S01ESNNoneOfTheAbove'
            })

            submission.S06ProfessionalsRoutinelyInvolvedInTransitionAdultESN = adapt_multiselect_field(row, {
                1: 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultESN',
                2: 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultLDESN',
                3: 'S06ProfessionalsRoutinelyInvolvedInTransitionAdultNeuro',
                4: 'S06ProfessionalsRoutinelyInvolvedInTransitionYouthWorker',
                5: 'S06ProfessionalsRoutinelyInvolvedInTransitionOther'
                # The other free text field is handled as a normal single value field earlier
            })

            print(submission.S01ESNFunctions)

            submission.save()
            
            break

            