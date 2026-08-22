"""
Management command to sync organisation and geography models from the
RCPCH NHS Organisations API.

Usage:
    python manage.py sync_nhs_organisations           # sync all entities
    python manage.py sync_nhs_organisations --dry-run  # report what would change, write nothing
    python manage.py sync_nhs_organisations --only trusts  # sync only the specified entity
    python manage.py sync_nhs_organisations --confirm  # proceed despite registration/case impact

The command calls ``sync_current_state()`` which upserts Trust, LocalHealthBoard,
IntegratedCareBoard, NHSEnglandRegion, Country, OPENUKNetwork and Organisation
rows from the API's list endpoints, wiring up the foreign keys on Organisation.

Before the live sync commits, a pre-sync safety check runs the dry-run diff
internally and enforces two rules:

1. **Ordering constraint** — if the sync would move any organisation's
   trust/LHB or flip any trust/LHB ``active`` flag, and any in-flight audit
   period (recruiting / data collection / grace) has no approved
   ``AuditPeriodOrganisation`` rows, the sync is blocked. Historical
   memberships must be frozen before live rows are mutated.
2. **Impact confirmation** — if the sync would affect any registrations or
   cases, ``--confirm`` is required. Without it, the sync aborts and prints
   the exposure summary.

This replaces the old direct NHS ODS (Spine) sync that was in
``epilepsy12/general_functions/ods_update.py`` (now removed).
"""

import logging

from django.core.management.base import BaseCommand

from epilepsy12.general_functions.nhs_organisations_sync import (
    sync_countries,
    sync_current_state,
    sync_integrated_care_boards,
    sync_local_health_boards,
    sync_nhs_england_regions,
    sync_openuk_networks,
    sync_organisations,
    sync_trusts,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Sync all organisation and geography models from the RCPCH NHS Organisations "
        "API. Upserts Trust, LocalHealthBoard, IntegratedCareBoard, NHSEnglandRegion, "
        "Country, OPENUKNetwork and Organisation rows from the API's list endpoints, "
        "wiring up the foreign keys on Organisation. Parent entities are synced first "
        "so their rows exist before organisations reference them. The entire operation "
        "runs inside a single transaction."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Compare the API's current state against the local DB and report "
            "what would change (new, changed, unchanged, local-only) without "
            "writing anything. Reports field-level differences for changed entities.",
        )
        parser.add_argument(
            "--only",
            type=str,
            choices=[
                "trusts",
                "local_health_boards",
                "integrated_care_boards",
                "nhs_england_regions",
                "countries",
                "openuk_networks",
                "organisations",
            ],
            help="Sync only the specified entity type. If omitted, all entities are "
            "synced (parent entities first, then organisations with FKs wired up). "
            "Note: when syncing only 'organisations', parent entities must already "
            "exist in the local DB — they will be resolved by ODS code / boundary "
            "identifier on demand.",
        )
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Confirm that you have reviewed the exposure report and accept "
            "the impact on registrations and cases. Required when the sync would "
            "move an organisation between trusts/LHBs or flip a trust/LHB active "
            "flag and any registrations or cases are attached to the affected "
            "organisations. Without --confirm, the sync aborts and prints the "
            "exposure summary. Run --dry-run first to see the exposure.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        only = options.get("only")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "Dry-run mode: no changes will be written to the database.\n"
                    "Comparing API state against local DB..."
                )
            )
            from epilepsy12.general_functions.nhs_organisations_sync import dry_run_diff

            try:
                diffs = dry_run_diff(only=only)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"API error during dry-run: {e}"))
                raise

            total_new = 0
            total_changed = 0
            total_unchanged = 0
            total_local_only = 0

            for entity_name, diff in diffs.items():
                label = entity_name.replace("_", " ").title()
                new = diff["new"]
                changed = diff["changed"]
                unchanged = diff["unchanged"]
                local_only = diff["local_only"]

                total_new += len(new)
                total_changed += len(changed)
                total_unchanged += unchanged
                total_local_only += len(local_only)

                self.stdout.write(f"\n  {label}:")
                self.stdout.write(
                    f"    {unchanged} unchanged, {len(new)} new, {len(changed)} changed, {len(local_only)} local-only"
                )

                if new:
                    self.stdout.write(self.style.SUCCESS(f"    New (would be created):"))
                    for identifier, name in new[:20]:
                        self.stdout.write(f"      + {identifier}: {name}")
                    if len(new) > 20:
                        self.stdout.write(f"      ... and {len(new) - 20} more")

                if changed:
                    self.stdout.write(self.style.WARNING(f"    Changed (would be updated):"))
                    for entry in changed[:20]:
                        identifier, name, field_diffs = entry[0], entry[1], entry[2]
                        exposure = entry[3] if len(entry) > 3 else None
                        self.stdout.write(f"      ~ {identifier}: {name}")
                        for field, (old_val, new_val) in field_diffs.items():
                            self.stdout.write(
                                f"          {field}: {old_val!r} → {new_val!r}"
                            )
                        if exposure:
                            self.stdout.write(
                                f"          Exposure: {exposure['registrations_all_periods']} reg "
                                f"({exposure['registrations_in_flight']} in-flight), "
                                f"{exposure['cases_all_periods']} cases"
                                + (
                                    f" across {exposure['organisations']} organisations"
                                    if "organisations" in exposure
                                    else ""
                                )
                            )
                    if len(changed) > 20:
                        self.stdout.write(f"      ... and {len(changed) - 20} more")

                if local_only:
                    self.stdout.write(
                        self.style.HTTP_INFO(f"    Local-only (not in API, would not be touched):")
                    )
                    for identifier, name in local_only[:10]:
                        self.stdout.write(f"      - {identifier}: {name}")
                    if len(local_only) > 10:
                        self.stdout.write(f"      ... and {len(local_only) - 10} more")

            self.stdout.write("")
            self.stdout.write(
                f"  Total: {total_unchanged} unchanged, {total_new} new, "
                f"{total_changed} changed, {total_local_only} local-only"
            )

            # Aggregate exposure across all changed entities that carry it.
            total_registrations = 0
            total_registrations_in_flight = 0
            total_cases = 0
            for entity_name, diff in diffs.items():
                for entry in diff.get("changed", []):
                    if len(entry) > 3 and entry[3]:
                        exposure = entry[3]
                        total_registrations += exposure.get("registrations_all_periods", 0)
                        total_registrations_in_flight += exposure.get("registrations_in_flight", 0)
                        total_cases += exposure.get("cases_all_periods", 0)
            if total_registrations or total_cases:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Exposure across all changed entities: "
                        f"{total_registrations} registrations "
                        f"({total_registrations_in_flight} in-flight), "
                        f"{total_cases} distinct cases would be affected"
                    )
                )

            self.stdout.write(
                self.style.SUCCESS("Dry-run complete. No changes written.")
            )
            return

        # Live sync
        # Run the pre-sync safety check before mutating anything. This
        # enforces the ordering constraint (historical memberships must be
        # frozen before live rows are moved) and requires --confirm when the
        # sync would affect registrations or cases.
        from epilepsy12.general_functions.nhs_organisations_sync import pre_sync_safety_check

        try:
            safety = pre_sync_safety_check(only=only)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"API error during pre-sync safety check: {e}"))
            raise

        if safety["blocked"]:
            self.stdout.write(
                self.style.ERROR("Sync blocked by the ordering constraint:")
            )
            self.stdout.write(self.style.ERROR(f"  {safety['block_reason']}"))
            self.stdout.write(
                "  Run `python manage.py sync_audit_period_organisations` first, "
                "then re-run this command."
            )
            return

        if safety["requires_confirm"] and not options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    "This sync would affect registrations or cases. "
                    "Run with --dry-run to see the full exposure report, "
                    "or pass --confirm to proceed."
                )
            )
            self.stdout.write("")
            self.stdout.write(
                f"  Affected registrations: {safety['total_registrations']} "
                f"({safety['total_registrations_in_flight']} in-flight)"
            )
            self.stdout.write(f"  Affected cases: {safety['total_cases']}")
            if safety["high_impact_changes"]:
                self.stdout.write("")
                self.stdout.write("  High-impact changes:")
                for entity, identifier, description in safety["high_impact_changes"][:20]:
                    self.stdout.write(f"    {entity}: {identifier} — {description}")
                if len(safety["high_impact_changes"]) > 20:
                    self.stdout.write(
                        f"    ... and {len(safety['high_impact_changes']) - 20} more"
                    )
            return

        if safety["requires_confirm"] and options["confirm"]:
            self.stdout.write(
                self.style.WARNING(
                    f"Proceeding with confirmed impact: "
                    f"{safety['total_registrations']} registrations "
                    f"({safety['total_registrations_in_flight']} in-flight), "
                    f"{safety['total_cases']} cases."
                )
            )

        # Live sync
        if only:
            self.stdout.write(f"Syncing only: {only}")
            if only == "trusts":
                result = sync_trusts()
                self.stdout.write(f"  Synced {len(result)} trusts")
            elif only == "local_health_boards":
                result = sync_local_health_boards()
                self.stdout.write(f"  Synced {len(result)} local health boards")
            elif only == "integrated_care_boards":
                result = sync_integrated_care_boards()
                self.stdout.write(f"  Synced {len(result)} integrated care boards")
            elif only == "nhs_england_regions":
                result = sync_nhs_england_regions()
                self.stdout.write(f"  Synced {len(result)} NHS England regions")
            elif only == "countries":
                result = sync_countries()
                self.stdout.write(f"  Synced {len(result)} countries")
            elif only == "openuk_networks":
                result = sync_openuk_networks()
                self.stdout.write(f"  Synced {len(result)} OPEN UK networks")
            elif only == "organisations":
                count = sync_organisations()
                self.stdout.write(f"  Synced {count} organisations")
        else:
            self.stdout.write(
                "Syncing all entities from RCPCH NHS Organisations API..."
            )
            result = sync_current_state()
            for entity, count in result.items():
                self.stdout.write(
                    f"  {entity.replace('_', ' ').title()}: {count}"
                )

        self.stdout.write(self.style.SUCCESS("Sync complete."))
