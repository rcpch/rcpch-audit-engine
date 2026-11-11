"""
Management command to report users whose RCPCH flags, role and groups disagree.

Phase 0 of retiring ``is_rcpch_audit_team_member`` and ``is_rcpch_staff`` in
favour of permissions attached to the RCPCH Audit Team role. Once the flags are
gone, a user's national access comes only from ``role == RCPCH_AUDIT_TEAM`` (via
its group's permissions), so every user listed here needs a decision before the
switch: change their role, or accept the change in access.

This command is read-only. It never writes to the database.

Findings:
    flag_without_role   A flag is True but role is not RCPCH Audit Team.
                        The user will LOSE national access.
    role_without_flag   Role is RCPCH Audit Team but a flag is False.
                        The user will GAIN whatever that flag currently gates.
    group_mismatch      The user's groups are not exactly the group their role
                        maps to (``group_for_role``). Their permissions will be
                        wrong until groups are re-synced from role.

Usage:
    python manage.py audit_rcpch_user_flags
    python manage.py audit_rcpch_user_flags --active-only
    python manage.py audit_rcpch_user_flags --csv
    python manage.py audit_rcpch_user_flags --csv --output flags_report.csv
"""

import csv

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db.models import Prefetch

from epilepsy12.common_view_functions.group_for_group import group_for_role
from epilepsy12.constants.user_types import RCPCH_AUDIT_TEAM
from epilepsy12.models import Epilepsy12User, OrganisationEmployer

FLAG_WITHOUT_ROLE = "flag_without_role"
ROLE_WITHOUT_FLAG = "role_without_flag"
GROUP_MISMATCH = "group_mismatch"

FINDING_DESCRIPTIONS = {
    FLAG_WITHOUT_ROLE: "RCPCH flag set but role is not RCPCH Audit Team (will LOSE national access)",
    ROLE_WITHOUT_FLAG: "Role is RCPCH Audit Team but a flag is not set (will GAIN flag-gated access)",
    GROUP_MISMATCH: "Groups do not match the group for the user's role",
}

CSV_COLUMNS = [
    "id",
    "email",
    "full_name",
    "is_active",
    "is_superuser",
    "role",
    "is_rcpch_audit_team_member",
    "is_rcpch_staff",
    "groups",
    "expected_group",
    "primary_organisation",
    "findings",
]


def _expected_group_name(role):
    """Name of the group ``group_for_role`` assigns, or a marker if it is missing."""
    try:
        return group_for_role(role).name
    except Group.DoesNotExist:
        return None


def findings_for_user(user, expected_group_name):
    """Return the list of finding codes that apply to ``user``."""
    findings = []
    has_any_flag = user.is_rcpch_audit_team_member or user.is_rcpch_staff
    has_both_flags = user.is_rcpch_audit_team_member and user.is_rcpch_staff
    is_audit_team_role = user.role == RCPCH_AUDIT_TEAM

    if has_any_flag and not is_audit_team_role:
        findings.append(FLAG_WITHOUT_ROLE)
    if is_audit_team_role and not has_both_flags:
        findings.append(ROLE_WITHOUT_FLAG)

    group_names = {group.name for group in user.groups.all()}
    if expected_group_name is None or group_names != {expected_group_name}:
        findings.append(GROUP_MISMATCH)

    return findings


def _primary_organisation(user):
    for employment in user.employer_organisations.all():
        if employment.is_primary and employment.is_active:
            return str(employment.employer_organisation)
    return ""


class Command(BaseCommand):
    help = (
        "Read-only report of users whose is_rcpch_audit_team_member / "
        "is_rcpch_staff flags, role and groups disagree."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--active-only",
            action="store_true",
            help="Only report active users (default: all users, with is_active shown).",
        )
        parser.add_argument(
            "--csv",
            action="store_true",
            help="Write one CSV row per affected user instead of the text report.",
        )
        parser.add_argument(
            "--output",
            help="With --csv, write to this file instead of stdout.",
        )

    def handle(self, *args, **options):
        users = (
            Epilepsy12User.objects.order_by("email")
            .prefetch_related(
                "groups",
                Prefetch(
                    "employer_organisations",
                    queryset=OrganisationEmployer.objects.select_related(
                        "employer_organisation"
                    ),
                ),
            )
        )
        if options["active_only"]:
            users = users.filter(is_active=True)

        expected_groups = {}
        rows = []
        for user in users:
            if user.role not in expected_groups:
                expected_groups[user.role] = _expected_group_name(user.role)
            expected_group = expected_groups[user.role]

            findings = findings_for_user(user, expected_group)
            if not findings:
                continue

            rows.append(
                {
                    "id": user.pk,
                    "email": user.email,
                    "full_name": user.get_full_name(),
                    "is_active": user.is_active,
                    "is_superuser": user.is_superuser,
                    "role": user.get_role_display() if user.role else "",
                    "is_rcpch_audit_team_member": user.is_rcpch_audit_team_member,
                    "is_rcpch_staff": user.is_rcpch_staff,
                    "groups": ";".join(sorted(g.name for g in user.groups.all())),
                    "expected_group": expected_group or "(group missing from database)",
                    "primary_organisation": _primary_organisation(user),
                    "findings": ";".join(findings),
                }
            )

        if options["csv"]:
            self._write_csv(rows, options.get("output"))
        else:
            self._write_report(rows)

    def _write_csv(self, rows, output_path):
        if output_path:
            with open(output_path, "w", newline="") as handle:
                self._csv_rows(handle, rows)
            self.stderr.write(f"Wrote {len(rows)} row(s) to {output_path}")
        else:
            self._csv_rows(self.stdout, rows)

    @staticmethod
    def _csv_rows(handle, rows):
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    def _write_report(self, rows):
        if not rows:
            self.stdout.write(self.style.SUCCESS("No mismatches found."))
            return

        for code, description in FINDING_DESCRIPTIONS.items():
            affected = [row for row in rows if code in row["findings"].split(";")]
            self.stdout.write("")
            self.stdout.write(
                self.style.MIGRATE_HEADING(f"{description}: {len(affected)}")
            )
            for row in affected:
                status = "active" if row["is_active"] else "inactive"
                superuser = ", superuser" if row["is_superuser"] else ""
                self.stdout.write(
                    f"  [{row['id']}] {row['email']} ({status}{superuser})\n"
                    f"      role={row['role'] or '-'}"
                    f"  audit_team_flag={row['is_rcpch_audit_team_member']}"
                    f"  staff_flag={row['is_rcpch_staff']}\n"
                    f"      groups={row['groups'] or '-'}"
                    f"  expected={row['expected_group']}\n"
                    f"      organisation={row['primary_organisation'] or '-'}"
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(f"{len(rows)} user(s) need a decision before Phase 1.")
        )
