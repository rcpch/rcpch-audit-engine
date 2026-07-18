"""
Management command to recalculate the Index of Multiple Deprivation (IMD) quintile
for all Cases in a given cohort (or all cohorts).

Usage:
    # All cases across all cohorts:
    python manage.py recalculate_imd --all

    # All cases in cohort 6:
    python manage.py recalculate_imd --cohort 6

Or via the convenience script:
    s/recalculate-imd        # all cohorts
    s/recalculate-imd 6      # cohort 6 only
"""

# Standard imports
import logging

# Django imports
from django.core.management.base import BaseCommand, CommandError

# RCPCH imports
from epilepsy12.models import Case
from epilepsy12.general_functions.index_multiple_deprivation import (
    recalculate_imd_for_case,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Recalculate IMD quintile for all Cases in a given cohort (or all cohorts)."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--cohort",
            type=int,
            metavar="N",
            help="Recalculate only for cases in this cohort number.",
        )
        group.add_argument(
            "--all",
            action="store_true",
            dest="all_cohorts",
            help="Recalculate for all cases regardless of cohort.",
        )

    def handle(self, *args, **options):
        if options["all_cohorts"]:
            cases = Case.objects.select_related("registration").all()
            self.stdout.write("Recalculating IMD for all cases…")
        else:
            cohort = options["cohort"]
            cases = Case.objects.select_related("registration").filter(
                registration__audit_period__cohort_number=cohort
            )
            self.stdout.write(f"Recalculating IMD for cohort {cohort}…")

        total = cases.count()
        if total == 0:
            self.stdout.write(self.style.WARNING("No matching cases found."))
            return

        success = 0
        skipped = 0
        errors = 0

        for ix, case in enumerate(cases, 1):
            try:
                before = case.index_of_multiple_deprivation_quintile
                recalculate_imd_for_case(case)
                after = case.index_of_multiple_deprivation_quintile

                if after is None and not case.postcode:
                    skipped += 1
                    self.stdout.write(
                        f"  [{ix}/{total}] Case {case.pk}: skipped (no postcode)"
                    )
                else:
                    success += 1
                    self.stdout.write(
                        f"  [{ix}/{total}] Case {case.pk}: {before} → {after}"
                    )
            except Exception as exc:
                errors += 1
                self.stderr.write(
                    self.style.ERROR(f"  [{ix}/{total}] Case {case.pk}: ERROR — {exc}")
                )
                logger.exception("recalculate_imd failed for case %s", case.pk)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {success} updated, {skipped} skipped, {errors} errors (total {total})."
            )
        )
