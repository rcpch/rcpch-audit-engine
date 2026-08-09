"""
Management command to sync organisation and geography models from the
RCPCH NHS Organisations API.

Usage:
    python manage.py sync_nhs_organisations           # sync all entities
    python manage.py sync_nhs_organisations --dry-run  # report counts from the API, write nothing
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
            help="Report counts from the API without writing to the database. "
            "Useful for verifying API connectivity before a live sync.",
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
                    "Fetching counts from the API to verify connectivity..."
                )
            )
            from epilepsy12.general_functions import nhs_organisations

            try:
                if only is None or only == "trusts":
                    trusts = nhs_organisations.list_trusts()
                    self.stdout.write(f"  Trusts: {len(trusts)} from API")
                if only is None or only == "local_health_boards":
                    lhbs = nhs_organisations.list_local_health_boards()
                    self.stdout.write(f"  Local Health Boards: {len(lhbs)} from API")
                if only is None or only == "integrated_care_boards":
                    icbs = nhs_organisations.list_integrated_care_boards()
                    self.stdout.write(f"  Integrated Care Boards: {len(icbs)} from API")
                if only is None or only == "nhs_england_regions":
                    regions = nhs_organisations.list_nhs_england_regions()
                    self.stdout.write(f"  NHS England Regions: {len(regions)} from API")
                if only is None or only == "countries":
                    countries = nhs_organisations.list_countries()
                    self.stdout.write(f"  Countries: {len(countries)} from API")
                if only is None or only == "openuk_networks":
                    networks = nhs_organisations.list_openuk_networks()
                    self.stdout.write(f"  OPEN UK Networks: {len(networks)} from API")
                if only is None or only == "organisations":
                    orgs = nhs_organisations.list_organisations()
                    self.stdout.write(f"  Organisations: {len(orgs)} from API")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"API error during dry-run: {e}"))
                raise
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
