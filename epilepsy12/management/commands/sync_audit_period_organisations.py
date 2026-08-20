"""
Management command to populate ``AuditPeriodOrganisation`` rows from the
``rcpch-nhs-organisations`` API snapshot endpoint.

Usage:
    python manage.py sync_audit_period_organisations           # sync all periods
    python manage.py sync_audit_period_organisations --cohort 7  # sync one period
    python manage.py sync_audit_period_organisations --dry-run  # report expected changes, write nothing
    python manage.py sync_audit_period_organisations --reconcile  # run reconciliation after sync

The sync is idempotent: re-running it for the same period upserts the same
rows. Already-approved rows are not overwritten.
"""

import logging

from django.core.management.base import BaseCommand

from epilepsy12.general_functions.audit_period_sync import (
    sync_audit_period,
    sync_all_audit_periods,
    link_organisation_identities,
)
from epilepsy12.general_functions.audit_period_reconciliation import reconcile_period

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Populate AuditPeriodOrganisation rows from the RCPCH NHS Organisations "
        "API snapshot endpoint. For each audit period and each participating "
        "organisation, calls the snapshot endpoint at the period's "
        "data_collection_end_date and upserts a membership row with the "
        "hierarchy FKs and snapshot name fields. Idempotent; does not "
        "overwrite approved rows."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--cohort",
            type=int,
            help="Sync only the specified cohort number. If omitted, all "
            "audit periods are synced.",
        )
        parser.add_argument(
            "--ods-code",
            type=str,
            action="append",
            help="Sync only the specified ODS code(s). Can be passed multiple "
            "times (e.g. --ods-code RGT01 --ods-code RP401). If omitted, all "
            "organisations with registrations in the period are synced.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what the sync would do without writing anything. "
            "Signposts the changes expected; use --reconcile after a live "
            "sync to confirm the sync was successful.",
        )
        parser.add_argument(
            "--reconcile",
            action="store_true",
            help="Run reconciliation after the sync to confirm hierarchy "
            "changes, registration attribution, and sibling organisations.",
        )
        parser.add_argument(
            "--link-identities",
            action="store_true",
            help="Link OrganisationIdentity rows for organisations without one. "
            "Runs after the per-cohort sync and the current-state sync "
            "(sync_nhs_organisations). For each active organisation without an "
            "identity, calls the API snapshot at a historical date to find its "
            "predecessor ODS code and links both rows to the same "
            "OrganisationIdentity. This bridges ODS code changes from mergers "
            "and dissolutions.",
        )

    def handle(self, *args, **options):
        cohort = options.get("cohort")
        ods_codes = options.get("ods_code")
        dry_run = options["dry_run"]
        reconcile = options["reconcile"]

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run mode: no changes will be written to the database.\n"
                    "Reporting what the sync would do..."
                )
            )
            # The dry-run reports what would change by inspecting the current
            # state of the API against the local DB. For now, we report the
            # periods that would be synced and the organisations that would
            # be processed.
            from epilepsy12.models import AuditPeriod, Registration

            periods = AuditPeriod.objects.all().order_by("cohort_number")
            if cohort:
                periods = periods.filter(cohort_number=cohort)

            for period in periods:
                participating_org_ids = (
                    Registration.objects.filter(audit_period=period)
                    .values_list("case__epilepsy12_sites__organisation", flat=True)
                    .distinct()
                )
                org_count = len(set(participating_org_ids))
                if ods_codes:
                    from epilepsy12.models import Organisation
                    org_count = Organisation.objects.filter(
                        id__in=participating_org_ids,
                        ods_code__in=ods_codes,
                    ).count()
                self.stdout.write(
                    f"  Cohort {period.cohort_number}: would sync {org_count} "
                    f"organisations at reference date "
                    f"{period.data_collection_end_date.isoformat()}"
                )

            self.stdout.write(
                self.style.SUCCESS("Dry-run complete. No changes written.")
            )
            return

        # Live sync
        if cohort:
            from epilepsy12.models import AuditPeriod

            try:
                period = AuditPeriod.objects.get(cohort_number=cohort)
            except AuditPeriod.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"AuditPeriod with cohort {cohort} not found.")
                )
                return

            self.stdout.write(
                f"Syncing cohort {cohort} at reference date "
                f"{period.data_collection_end_date.isoformat()}..."
            )
            result = sync_audit_period(period, ods_codes=ods_codes)
            self._report_result(result)
        else:
            self.stdout.write("Syncing all audit periods...")
            results = sync_all_audit_periods(ods_codes=ods_codes)
            for result in results:
                self._report_result(result)

        if reconcile:
            self.stdout.write("")
            self.stdout.write("Running reconciliation...")

            from epilepsy12.models import AuditPeriod

            periods = AuditPeriod.objects.all().order_by("cohort_number")
            if cohort:
                periods = periods.filter(cohort_number=cohort)

            for period in periods:
                self._report_reconciliation(period)

        if options["link_identities"]:
            self.stdout.write("")
            self.stdout.write("Linking OrganisationIdentity rows...")
            result = link_organisation_identities()
            self.stdout.write(
                f"  {result['linked']} linked, "
                f"{result['already_linked']} already linked, "
                f"{result['no_predecessor']} no predecessor (genuinely new)"
            )
            if result["errors"]:
                self.stdout.write(
                    self.style.ERROR(f"    {len(result['errors'])} errors:")
                )
                for ods_code, error in result["errors"][:20]:
                    self.stdout.write(f"      {ods_code}: {error}")
                if len(result["errors"]) > 20:
                    self.stdout.write(
                        f"      ... and {len(result['errors']) - 20} more"
                    )

        self.stdout.write(self.style.SUCCESS("Sync complete."))

    def _report_result(self, result: dict):
        self.stdout.write(
            f"  Cohort {result['period']} (reference date {result['reference_date']}): "
            f"{result['created']} created, {result['updated']} updated, "
            f"{result['skipped_approved']} skipped (approved)"
        )
        if result.get("snapshot") or result.get("detail_fallback"):
            self.stdout.write(
                f"    Source: {result.get('snapshot', 0)} from snapshot, "
                f"{result.get('detail_fallback', 0)} from detail fallback "
                f"(current state — re-sync once API has temporal history)"
            )
        if result["errors"]:
            self.stdout.write(
                self.style.ERROR(f"    {len(result['errors'])} errors:")
            )
            for ods_code, error in result["errors"][:20]:
                self.stdout.write(f"      {ods_code}: {error}")
            if len(result["errors"]) > 20:
                self.stdout.write(f"      ... and {len(result['errors']) - 20} more")
        if result["predecessors"]:
            self.stdout.write(
                self.style.WARNING(
                    f"    {len(result['predecessors'])} organisations with "
                    f"predecessor ODS codes (succession chain walked):"
                )
            )
            for ods_code, predecessor in result["predecessors"][:20]:
                self.stdout.write(f"      {ods_code} -> {predecessor}")
            if len(result["predecessors"]) > 20:
                self.stdout.write(
                    f"      ... and {len(result['predecessors']) - 20} more"
                )

    def _report_reconciliation(self, period):
        report = reconcile_period(period)

        self.stdout.write(f"  Cohort {report['period']} reconciliation:")

        # Hierarchy changes
        changes = report["hierarchy_changes"]
        if changes:
            self.stdout.write(
                self.style.WARNING(
                    f"    {len(changes)} hierarchy changes:"
                )
            )
            for change in changes[:20]:
                prev = change["previous_trust"] or change["previous_lhb"]
                curr = change["current_trust"] or change["current_lhb"]
                self.stdout.write(
                    f"      {change['ods_code']} ({change['organisation_name']}): "
                    f"{prev} -> {curr}"
                )
            if len(changes) > 20:
                self.stdout.write(f"      ... and {len(changes) - 20} more")
        else:
            self.stdout.write("    No hierarchy changes from previous period.")

        # Registration attribution
        attr = report["registration_attribution"]
        if attr["orphaned_registrations"]:
            self.stdout.write(
                self.style.ERROR(
                    f"    {len(attr['orphaned_registrations'])} organisations "
                    f"with registrations but no membership row:"
                )
            )
            for org in attr["orphaned_registrations"][:20]:
                self.stdout.write(
                    f"      {org['ods_code']} ({org['name']}): "
                    f"{org['registration_count']} registrations"
                )
        if attr["orphaned_memberships"]:
            self.stdout.write(
                self.style.WARNING(
                    f"    {len(attr['orphaned_memberships'])} membership rows "
                    f"with no registrations:"
                )
            )
            for org in attr["orphaned_memberships"][:20]:
                self.stdout.write(
                    f"      {org['ods_code']} ({org['name']})"
                )

        # Sibling organisations
        siblings = report["sibling_organisations"]
        self.stdout.write(
            f"    {len(siblings)} organisations with sibling verification."
        )