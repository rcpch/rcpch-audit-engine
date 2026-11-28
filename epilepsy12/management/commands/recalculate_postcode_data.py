"""
Management command to recalculate the postcode-derived fields on Cases in a
given cohort (or all cohorts):

- the Index of Multiple Deprivation (IMD) quintile, from the RCPCH Census Platform
- the location fields (``location_wgs84`` and ``location_bng``), from postcodes.io

By default only missing values are filled in, so the command can be rerun until
nothing is left (for example after a timeout or an API outage). Pass
``--rebuild`` to recalculate both fields for every case in scope.

Usage:
    # Fill in missing values for all cases across all cohorts:
    python manage.py recalculate_postcode_data --all

    # Fill in missing values for cases in cohort 6:
    python manage.py recalculate_postcode_data --cohort 6

    # Recalculate IMD and location for every case in cohort 6:
    python manage.py recalculate_postcode_data --cohort 6 --rebuild

    # Show how many cases would be processed, without calling any APIs:
    python manage.py recalculate_postcode_data --cohort 6 --dry-run

Or via the convenience script:
    s/recalculate-postcode-data                  # all cohorts, missing values only
    s/recalculate-postcode-data 6                # cohort 6, missing values only
    s/recalculate-postcode-data 6 --rebuild      # cohort 6, full rebuild

The same command is available to superusers in the Django admin, under
"Administrative tools".
"""

# Standard imports
import logging

# Django imports
from django.core.management.base import BaseCommand
from django.db.models import BooleanField, ExpressionWrapper, Q

# RCPCH imports
from epilepsy12.models import Case
from epilepsy12.constants import UNKNOWN_POSTCODES_NO_SPACES
from epilepsy12.general_functions.index_multiple_deprivation import (
    recalculate_imd_for_case,
)
from epilepsy12.general_functions.postcode import (
    location_lookup_possible,
    update_location_for_case,
)

logger = logging.getLogger(__name__)

MISSING_LOCATION = Q(location_wgs84__isnull=True) | Q(location_bng__isnull=True)
MISSING_IMD = Q(index_of_multiple_deprivation_quintile__isnull=True)


def _imd_lookup_possible(postcode, cohort) -> bool:
    """Matches the checks in recalculate_imd_for_case, without the API call."""
    if not postcode or cohort is None:
        return False
    normalised = str(postcode).replace(" ", "").replace("-", "").upper()
    return normalised not in UNKNOWN_POSTCODES_NO_SPACES


def _cohort_for_case(case):
    try:
        return case.registration.audit_period.cohort_number
    except Exception:
        # No registration, or a registration with no audit period yet.
        return None


class Command(BaseCommand):
    help = (
        "Fill in missing IMD quintiles and locations (or, with --rebuild, "
        "recalculate them all) for Cases in a given cohort (or all cohorts)."
    )

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "--cohort",
            type=int,
            metavar="N",
            help="Only process cases in this cohort number.",
        )
        group.add_argument(
            "--all",
            action="store_true",
            dest="all_cohorts",
            help="Process all cases regardless of cohort, including unregistered cases.",
        )
        parser.add_argument(
            "--rebuild",
            action="store_true",
            help=(
                "Recalculate IMD and location for every case, not just those "
                "missing them. Cases whose postcode cannot be looked up have "
                "their location cleared. A failed lookup keeps the existing value."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report how many cases would be processed without calling any APIs or saving anything.",
        )

    def handle(self, *args, **options):
        rebuild = options["rebuild"]
        cases = Case.objects.select_related("registration__audit_period")
        if options["all_cohorts"]:
            scope = "all cases"
        else:
            cohort = options["cohort"]
            cases = cases.filter(registration__audit_period__cohort_number=cohort)
            scope = f"cohort {cohort}"
        cases = cases.order_by("pk")
        mode = "full rebuild" if rebuild else "missing values only"

        total = cases.count()
        if total == 0:
            self.stdout.write(
                self.style.WARNING(f"No matching cases found for {scope}.")
            )
            return

        if options["dry_run"]:
            self._dry_run(cases, scope, mode, total, rebuild)
            return

        if not rebuild:
            cases = cases.filter(MISSING_IMD | MISSING_LOCATION)
        to_process = cases.count()

        self.stdout.write(
            f"Recalculating IMD and locations for {scope} ({mode}): "
            f"{to_process} of {total} case(s) to process…"
        )

        imd_counts = {"recalculated": 0, "failed": 0, "skipped": 0, "present": 0}
        location_counts = {
            "filled": 0,
            "failed": 0,
            "cleared": 0,
            "skipped": 0,
            "present": 0,
        }
        errors = 0

        for ix, case in enumerate(cases.iterator(), 1):
            prefix = f"  [{ix}/{to_process}] Case {case.pk}:"
            try:
                imd_status, imd_message = self._update_imd(case, rebuild)
                imd_counts[imd_status] += 1

                location_status = update_location_for_case(case, rebuild=rebuild)
                location_counts[location_status] += 1

                self.stdout.write(f"{prefix} {imd_message}; location {location_status}")
            except Exception as exc:
                errors += 1
                self.stderr.write(self.style.ERROR(f"{prefix} ERROR — {exc}"))
                logger.exception(
                    "recalculate_postcode_data failed for case %s", case.pk
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone ({scope}, {mode}, {to_process} of {total} cases processed). "
                f"IMD: {imd_counts['recalculated']} recalculated, "
                f"{imd_counts['failed']} lookups failed, "
                f"{imd_counts['skipped']} could not be looked up. "
                f"Locations: {location_counts['filled']} filled in, "
                f"{location_counts['failed']} lookups failed, "
                f"{location_counts['cleared']} cleared, "
                f"{location_counts['skipped']} could not be looked up. "
                f"{errors} errors."
            )
        )

    def _update_imd(self, case, rebuild):
        """Returns (status, message) for the case's IMD quintile."""
        before = case.index_of_multiple_deprivation_quintile
        if before is not None and not rebuild:
            return "present", f"IMD {before} (already set)"

        if not _imd_lookup_possible(case.postcode, _cohort_for_case(case)):
            return "skipped", "IMD skipped (no usable postcode or cohort)"

        recalculate_imd_for_case(case)
        after = case.index_of_multiple_deprivation_quintile
        if after is None:
            return "failed", f"IMD {before} → None (lookup failed)"
        return "recalculated", f"IMD {before} → {after}"

    def _dry_run(self, cases, scope, mode, total, rebuild):
        rows = cases.annotate(
            missing_location=ExpressionWrapper(
                MISSING_LOCATION, output_field=BooleanField()
            )
        ).values_list(
            "postcode",
            "index_of_multiple_deprivation_quintile",
            "registration__audit_period__cohort_number",
            "missing_location",
        )

        imd_lookups = 0
        location_lookups = 0
        imd_missing = 0
        location_missing = 0
        for postcode, quintile, cohort, missing_location in rows.iterator():
            if quintile is None:
                imd_missing += 1
            if missing_location:
                location_missing += 1
            if (rebuild or quintile is None) and _imd_lookup_possible(postcode, cohort):
                imd_lookups += 1
            if (rebuild or missing_location) and location_lookup_possible(postcode):
                location_lookups += 1

        self.stdout.write(
            f"[DRY RUN] {scope} ({mode}): {total} case(s). "
            f"{imd_missing} are missing IMD and {location_missing} are missing a location. "
            f"Would look up IMD for {imd_lookups} case(s) and location for "
            f"{location_lookups} case(s) (cases with no usable postcode, or no "
            f"cohort for IMD, cannot be looked up)."
        )
