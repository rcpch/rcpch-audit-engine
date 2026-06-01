# Standard imports
import logging
from datetime import datetime

# Django imports
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Q
from django.utils import timezone

# RCPCH imports
from epilepsy12.models import Case

logger = logging.getLogger(__name__)


def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise CommandError(f"Invalid date '{value}'. Expected format: YYYY-MM-DD.")


class Command(BaseCommand):
    help = "Remove unregistered cases created before a given date"

    def add_arguments(self, parser):
        parser.add_argument(
            "--before",
            type=_parse_date,
            required=True,
            metavar="YYYY-MM-DD",
            help="Remove unregistered cases created before this date (format: YYYY-MM-DD).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show which cases would be deleted without actually deleting them.",
        )

    def handle(self, *args, **options):
        before_date = options["before"]
        dry_run = options["dry_run"]

        # Normalise to an aware datetime at start-of-day
        cutoff = timezone.make_aware(datetime.combine(before_date, datetime.min.time()))

        # Unregistered: no registration at all, or registration with no first_paediatric_assessment_date
        cases = Case.objects.filter(created_at__lt=cutoff).filter(
            Q(registration__isnull=True)
            | Q(registration__first_paediatric_assessment_date__isnull=True)
        )

        count = cases.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No unregistered cases created before {before_date} found."
                )
            )
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f"[DRY RUN] {count} case(s) would be deleted:"))
            org_counts = (
                cases.values("organisations__name")
                .annotate(n=Count("id", distinct=True))
                .order_by("organisations__name")
            )
            for row in org_counts:
                org_name = row["organisations__name"] or "(no organisation)"
                self.stdout.write(f"  {row['n']:>4}  {org_name}")
            self.stdout.write(self.style.WARNING("No changes made (--dry-run)."))
            return

        org_counts = (
            cases.values("organisations__name")
            .annotate(n=Count("id", distinct=True))
            .order_by("organisations__name")
        )
        self.stdout.write(f"Found {count} unregistered case(s) created before {before_date}:")
        for row in org_counts:
            org_name = row["organisations__name"] or "(no organisation)"
            self.stdout.write(f"  {row['n']:>4}  {org_name}")
        confirm = input("Delete these cases? [y/N] ").strip().lower()
        if confirm != "y":
            self.stdout.write("Aborted. No cases deleted.")
            return

        deleted = 0
        for case in cases.prefetch_related("organisations"):
            org_names = ", ".join(
                case.organisations.values_list("name", flat=True)
            ) or "(no organisation)"
            case.delete()
            deleted += 1
            self.stdout.write(f"  Deleted case {deleted}/{count} — {org_names}")

        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} case(s)."))

