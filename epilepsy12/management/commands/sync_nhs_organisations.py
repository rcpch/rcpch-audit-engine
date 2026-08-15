"""
Management command to sync organisation and geography models from the
RCPCH NHS Organisations API.

Usage:
    python manage.py sync_nhs_organisations           # sync all entities
    python manage.py sync_nhs_organisations --dry-run  # report what would change, write nothing
    python manage.py sync_nhs_organisations --only trusts  # sync only the specified entity

The command calls ``sync_current_state()`` which upserts Trust, LocalHealthBoard,
IntegratedCareBoard, NHSEnglandRegion, Country, OPENUKNetwork and Organisation
rows from the API's list endpoints, wiring up the foreign keys on Organisation.

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
                    for identifier, name, field_diffs in changed[:20]:
                        self.stdout.write(f"      ~ {identifier}: {name}")
                        for field, (old_val, new_val) in field_diffs.items():
                            self.stdout.write(
                                f"          {field}: {old_val!r} → {new_val!r}"
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
            self.stdout.write(
                self.style.SUCCESS("Dry-run complete. No changes written.")
            )
            return

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
