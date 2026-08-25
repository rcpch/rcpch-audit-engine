"""
Management command to review and approve ``AuditPeriodOrganisation`` membership
rows for an audit period.

The per-cohort sync (``sync_audit_period_organisations``) populates membership
rows for each participating organisation but leaves them **unapproved**
(``approved_at`` is null). Approved rows are the frozen, period-aware source of
truth: the period-aware permission and reporting services only read approved
rows, and the current-state sync's ordering constraint blocks mutating live
``Organisation`` hierarchy rows until the in-flight periods' memberships are
approved.

This command lets the audit team walk through each unapproved membership row
for a period, see the exposure (registrations and cases that would be grouped
under the period hierarchy), and either approve it or decline it (recording a
note). It never edits the hierarchy FKs — if a sync-sourced assignment is
wrong, decline it with a note so it can be corrected separately.

Usage:
    python manage.py approve_audit_period_organisations            # all cohorts
    python manage.py approve_audit_period_organisations --cohort 8  # one cohort
    python manage.py approve_audit_period_organisations --cohort 8 --dry-run
    python manage.py approve_audit_period_organisations --cohort 8 --user a@rcpch.ac.uk
    python manage.py approve_audit_period_organisations --cohort 8 --auto-approve
    python manage.py approve_audit_period_organisations --cohort 8 --ods-code RJZ01

Prompts, one row at a time:
    y     approve
    n     decline (leave unapproved, record a note)
    d     show details (registrations/cases, hierarchy, siblings)
    s     skip (leave for later, no note)
    q     quit
"""

import logging

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from epilepsy12.models import (
    AuditPeriod,
    AuditPeriodOrganisation,
    Registration,
    Case,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Review and approve AuditPeriodOrganisation membership rows for an "
        "audit period. Reports exposure (registrations/cases) per row and "
        "iteratively approves or declines each organisation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--cohort",
            type=int,
            help="Only review memberships for the specified cohort number. "
            "If omitted, all cohorts with unapproved memberships are reviewed.",
        )
        parser.add_argument(
            "--ods-code",
            type=str,
            action="append",
            help="Only review memberships for the specified ODS code(s). "
            "Can be passed multiple times.",
        )
        parser.add_argument(
            "--user",
            type=str,
            metavar="EMAIL",
            help="Email of the audit-team user to record as approver "
            "(approved_by). If omitted, prompts for a user.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report the exposure for each unapproved membership without "
            "prompting or writing anything.",
        )
        parser.add_argument(
            "--auto-approve",
            action="store_true",
            help="Approve every unapproved row without prompting. Use "
            "--dry-run first to review the exposure.",
        )

    def _resolve_approver(self, email):
        from epilepsy12.models import Epilepsy12User

        if email:
            try:
                user = Epilepsy12User.objects.get(email=email)
            except Epilepsy12User.DoesNotExist:
                raise CommandError(f"No user found with email {email!r}.")
        else:
            user = None
            while user is None:
                self.stdout.write(
                    "Which user is approving? (email of an RCPCH audit-team "
                    "member / superuser)"
                )
                email = input("Email (blank to leave approved_by empty): ").strip()
                if not email:
                    return None
                try:
                    user = Epilepsy12User.objects.get(email=email)
                except Epilepsy12User.DoesNotExist:
                    self.stderr.write(self.style.ERROR(f"  No user with email {email!r}."))
                    user = None

        if not (
            user.is_superuser
            or user.is_rcpch_audit_team_member
            or user.is_rcpch_staff
        ):
            raise CommandError(
                f"{user.email} is not an RCPCH audit-team member, RCPCH staff, "
                "or superuser. Approval should be recorded by an audit-team user."
            )
        return user

    def _count_exposure(self, membership):
        """Count registrations and distinct cases attached to the membership's
        organisation across all periods."""
        registrations = Registration.objects.filter(
            case__epilepsy12_sites__organisation=membership.organisation,
        ).count()
        cases = (
            Case.objects.filter(
                epilepsy12_sites__organisation=membership.organisation,
            )
            .distinct()
            .count()
        )
        return registrations, cases

    # The identifier attribute differs per hierarchy entity type.
    _IDENTIFIER_FIELDS = {
        "country": "boundary_identifier",
        "trust": "ods_code",
        "local_health_board": "ods_code",
        "integrated_care_board": "ods_code",
        "nhs_england_region": "region_code",
        "openuk_network": "boundary_identifier",
    }

    def _format_hierarchy(self, membership):
        def label(name_field, fk_field):
            snapshot = getattr(membership, name_field, "") or ""
            fk = getattr(membership, fk_field, None)
            identifier_field = self._IDENTIFIER_FIELDS[fk_field]
            fk_identifier = getattr(fk, identifier_field, None) if fk is not None else None
            fk_label = (
                f"{fk_identifier} ({fk.name})" if fk is not None else "None"
            )
            return snapshot or fk_label

        country = label("country_name_snapshot", "country")
        trust = label("trust_name_snapshot", "trust")
        lhb = label("local_health_board_name_snapshot", "local_health_board")
        icb = label("integrated_care_board_name_snapshot", "integrated_care_board")
        region = label("nhs_england_region_name_snapshot", "nhs_england_region")
        network = label("openuk_network_name_snapshot", "openuk_network")

        if membership.trust is not None:
            parent = f"Trust: {trust}"
        elif membership.local_health_board is not None:
            parent = f"LHB: {lhb}"
        else:
            parent = "Parent: (none)"
        return f"{parent}; ICB: {icb}; Region: {region}; Network: {network}; Country: {country}"

    def _render_row(self, membership, regs, cases, status="unapproved"):
        org = membership.organisation
        status_label = {
            "approved": self.style.SUCCESS("APPROVED"),
            "declined": self.style.WARNING("DECLINED"),
            "unapproved": self.style.WARNING("unapproved"),
            "skipped": self.style.NOTICE("skipped"),
        }.get(status, status)
        return (
            f"  [{status_label}] {org.ods_code} ({org.name})\n"
            f"      {self._format_hierarchy(membership)}\n"
            f"      Registrations (all periods): {regs}; "
            f"Distinct cases (all periods): {cases}\n"
            f"      included_in_reporting={membership.included_in_reporting}, "
            f"source={membership.source}"
        )

    def handle(self, *args, **options):
        cohort = options["cohort"]
        ods_codes = options["ods_code"]
        dry_run = options["dry_run"]
        auto_approve = options["auto_approve"]

        periods = AuditPeriod.objects.all().order_by("cohort_number")
        if cohort:
            periods = periods.filter(cohort_number=cohort)

        memberships = (
            AuditPeriodOrganisation.objects.filter(
                audit_period__in=periods,
                approved_at__isnull=True,
            )
            .select_related(
                "audit_period",
                "organisation",
                "country",
                "trust",
                "local_health_board",
                "integrated_care_board",
                "nhs_england_region",
                "openuk_network",
            )
            .order_by("audit_period__cohort_number", "organisation__name")
        )
        if ods_codes:
            memberships = memberships.filter(organisation__ods_code__in=ods_codes)

        total = memberships.count()
        if total == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "No unapproved AuditPeriodOrganisation rows to review."
                )
            )
            return

        self.stdout.write(
            f"Found {total} unapproved membership row(s) across "
            f"{len(set(memberships.values_list('audit_period__cohort_number', flat=True)))} "
            f"cohort(s)."
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING("Dry-run: reporting exposure only, nothing written.")
            )
            for membership in memberships:
                regs, cases = self._count_exposure(membership)
                self.stdout.write(
                    self._render_row(membership, regs, cases)
                )
            self.stdout.write(self.style.WARNING("Dry-run complete. No changes written."))
            return

        if auto_approve:
            self.stdout.write(
                self.style.WARNING(
                    "--auto-approve set: approving every unapproved row without prompting."
                )
            )
            approver = self._resolve_approver(options["user"])
            now = timezone.now()
            approved = 0
            for membership in memberships:
                membership.approved_at = now
                membership.approved_by = approver
                membership.save()
                approved += 1
            self.stdout.write(
                self.style.SUCCESS(f"Approved {approved} membership row(s).")
            )
            return

        # Interactive mode
        approver = self._resolve_approver(options["user"])
        now = timezone.now()

        approved = 0
        declined = 0
        skipped = 0
        for index, membership in enumerate(memberships, start=1):
            regs, cases = self._count_exposure(membership)
            self.stdout.write(
                f"\n[{index}/{total}] Cohort {membership.audit_period.cohort_number}:"
            )
            self.stdout.write(self._render_row(membership, regs, cases))

            while True:
                self.stdout.write("")
                prompt = (
                    "  Approve? [y]es / [n]o (decline) / [d]etails / "
                    "[s]kip / [q]uit: "
                )
                answer = input(prompt).strip().lower()
                if answer == "y":
                    membership.approved_at = now
                    membership.approved_by = approver
                    membership.save()
                    approved += 1
                    self.stdout.write(self.style.SUCCESS("  Approved."))
                    break
                elif answer == "n":
                    note = input(
                        "  Reason for declining (recorded in notes; leave blank "
                        "to skip note): "
                    ).strip()
                    if note:
                        membership.notes = (
                            f"{membership.notes}\n[declined] {note}".strip()
                        )
                        membership.save()
                        declined += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Declined (left unapproved). Note recorded."
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "  No note given; leaving row untouched. Choose [s]kip "
                                "to leave for later without a note."
                            )
                        )
                        continue
                    break
                elif answer == "d":
                    self._show_details(membership)
                elif answer == "s":
                    skipped += 1
                    self.stdout.write(self.style.NOTICE("  Skipped (left for later)."))
                    break
                elif answer == "q":
                    self.stdout.write(
                        self.style.NOTICE(
                            f"\nQuit. Approved: {approved}, declined: {declined}, "
                            f"skipped: {skipped}."
                        )
                    )
                    return
                else:
                    self.stdout.write(
                        self.style.ERROR("  Please answer y, n, d, s or q.")
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nReview complete. Approved: {approved}, declined: {declined}, "
                f"skipped: {skipped}."
            )
        )

    def _show_details(self, membership):
        org = membership.organisation
        self.stdout.write("    --- Details ---")
        self.stdout.write(f"    Organisation: {org.ods_code} {org.name}")
        self.stdout.write(f"    Current trust: {org.trust}")
        self.stdout.write(f"    Current LHB: {org.local_health_board}")
        self.stdout.write(
            f"    Period hierarchy: {self._format_hierarchy(membership)}"
        )

        # Sites / registered cases in this period
        period = membership.audit_period
        reg_in_period = (
            Registration.objects.filter(
                audit_period=period,
                case__epilepsy12_sites__organisation=org,
            ).count()
        )
        self.stdout.write(
            f"    Registrations in this cohort ({period.cohort_number}): {reg_in_period}"
        )

        # Sibling organisations under the same period parent
        if membership.trust is not None:
            siblings = AuditPeriodOrganisation.objects.filter(
                audit_period=period,
                trust=membership.trust,
            ).exclude(pk=membership.pk)
            parent_label = f"Trust {membership.trust.ods_code}"
        elif membership.local_health_board is not None:
            siblings = AuditPeriodOrganisation.objects.filter(
                audit_period=period,
                local_health_board=membership.local_health_board,
            ).exclude(pk=membership.pk)
            parent_label = f"LHB {membership.local_health_board.ods_code}"
        else:
            siblings = AuditPeriodOrganisation.objects.none()
            parent_label = "(no parent)"

        sibling_list = list(
            siblings.values_list("organisation__ods_code", "organisation__name")[:15]
        )
        if sibling_list:
            self.stdout.write(
                f"    Sibling organisations under {parent_label} in this cohort:"
            )
            for code, name in sibling_list:
                self.stdout.write(f"      - {code} ({name})")
        else:
            self.stdout.write(
                f"    No sibling organisations under {parent_label} in this cohort."
            )
