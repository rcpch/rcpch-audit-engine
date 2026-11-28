"""
Management command to recalculate the postcode-derived fields on Cases in a
given cohort (or all cohorts):

- the Index of Multiple Deprivation (IMD) quintile, recalculated for every case
- the location fields (``location_wgs84`` and ``location_bng``), looked up only
  for cases that are missing them

Usage:
    # All cases across all cohorts:
    python manage.py recalculate_imd --all

    # All cases in cohort 6:
    python manage.py recalculate_imd --cohort 6

    # Show how many cases would be processed, without calling any APIs:
    python manage.py recalculate_imd --cohort 6 --dry-run

Or via the convenience script:
    s/recalculate-imd        # all cohorts
    s/recalculate-imd 6      # cohort 6 only

The same command is available to superusers in the Django admin, under
"Administrative tools".
"""

# Standard imports
import logging

# Django imports
from django.core.management.base import BaseCommand
from django.db.models import Q

# RCPCH imports
from epilepsy12.models import Case
from epilepsy12.constants import UNKNOWN_POSTCODES_NO_SPACES
from epilepsy12.general_functions.index_multiple_deprivation import (
    recalculate_imd_for_case,
)
from epilepsy12.general_functions.postcode import fill_missing_location_for_case

logger = logging.getLogger(__name__)


def _location_lookup_possible(postcode) -> bool:
    """Matches the checks in fill_missing_location_for_case, without the API call."""
    if not postcode:
        return False
    normalised = str(postcode).replace(" ", "").replace("-", "").upper()
    return normalised not in UNKNOWN_POSTCODES_NO_SPACES and not normalised.startswith(
        "JE"
    )


class Command(BaseCommand):
    help = (
        "Recalculate IMD quintile, and fill in missing location fields, for all "
        "Cases in a given cohort (or all cohorts)."
    )

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
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many cases would be processed without calling any APIs or saving anything.",
        )

    def handle(self, *args, **options):
        cases = Case.objects.select_related("registration__audit_period")
        if options["all_cohorts"]:
            scope = "all cases"
        else:
            cohort = options["cohort"]
            cases = cases.filter(registration__audit_period__cohort_number=cohort)
            scope = f"cohort {cohort}"
        cases = cases.order_by("pk")

        total = cases.count()
        if total == 0:
            self.stdout.write(
                self.style.WARNING(f"No matching cases found for {scope}.")
            )
            return

        if options["dry_run"]:
            self._dry_run(cases, scope, total)
            return

        self.stdout.write(
            f"Recalculating IMD and filling in missing locations for {scope}…"
        )

        imd_updated = 0
        imd_skipped = 0
        locations_filled = 0
        locations_failed = 0
        errors = 0

        for ix, case in enumerate(cases.iterator(), 1):
            prefix = f"  [{ix}/{total}] Case {case.pk}:"
            try:
                before = case.index_of_multiple_deprivation_quintile
                recalculate_imd_for_case(case)
                after = case.index_of_multiple_deprivation_quintile

                if after is None and not case.postcode:
                    imd_skipped += 1
                    imd_message = "IMD skipped (no postcode)"
                else:
                    imd_updated += 1
                    imd_message = f"IMD {before} → {after}"

                location_status = fill_missing_location_for_case(case)
                if location_status == "filled":
                    locations_filled += 1
                    imd_message += "; location filled in"
                elif location_status == "failed":
                    locations_failed += 1
                    imd_message += "; location lookup failed"

                self.stdout.write(f"{prefix} {imd_message}")
            except Exception as exc:
                errors += 1
                self.stderr.write(self.style.ERROR(f"{prefix} ERROR — {exc}"))
                logger.exception("recalculate_imd failed for case %s", case.pk)

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({scope}, {total} cases). "
                f"IMD: {imd_updated} recalculated, {imd_skipped} skipped. "
                f"Locations: {locations_filled} filled in, {locations_failed} lookups failed. "
                f"{errors} errors."
            )
        )

    def _dry_run(self, cases, scope, total):
        missing_location_postcodes = cases.filter(
            Q(location_wgs84__isnull=True) | Q(location_bng__isnull=True)
        ).values_list("postcode", flat=True)
        missing = 0
        fillable = 0
        for postcode in missing_location_postcodes.iterator():
            missing += 1
            if _location_lookup_possible(postcode):
                fillable += 1

        self.stdout.write(
            f"[DRY RUN] {scope}: {total} case(s) would have IMD recalculated. "
            f"{missing} case(s) are missing a location, of which {fillable} "
            f"would be looked up (the rest have no usable postcode)."
        )
