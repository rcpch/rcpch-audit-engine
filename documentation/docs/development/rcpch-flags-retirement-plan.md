# Retiring `is_rcpch_audit_team_member` and `is_rcpch_staff`

This is the plan for replacing the two `Epilepsy12User` boolean flags with permissions attached to the **RCPCH Audit Team** role. Code checks those permissions with `has_perm`, not group membership.

> **Status: complete.** The flags were removed in Phase 3 (migration `0075_remove_rcpch_user_flags`). National access now comes only from the RCPCH Audit Team role's group permissions. This page records how the change was made.

## How the code works now

- **Two separate systems.** The `RCPCH_AUDIT_TEAM` role (4) puts a user in the `epilepsy12_audit_team_full_access` group (`common_view_functions/group_for_group.py`). The two booleans are set on their own, and about 70 non-test call sites check them directly.
- **They can disagree.** The model's comments say audit team members "can be clinicians". So a Lead Clinician with `is_rcpch_audit_team_member=True` gets national access without the role or group. **This is the main migration risk** (see Phase 0).
- **Permissions already exist for this.** `groups_seeder()` in `management/commands/create_groups.py` gives the audit team group its own `EPILEPSY12_AUDIT_TEAM_ACCESS_PERMISSIONS` list. That's where the new permissions go.
- **Superuser checks get simpler.** `has_perm()` is always True for an active superuser, so every `is_superuser or flag` becomes a single `has_perm(...)`.

## New permissions

Define each new permission in `constants/user_types.py`, add it to `PERMISSIONS` and to the `Meta.permissions` of the model it most relates to, and attach it only to the audit team group. Where a built-in model permission already fits (`view_banner`), use that instead.

| Permission | Replaces the flag checks in |
|---|---|
| `can_access_all_organisations` (view any organisation, user or child nationally, including the national view preference and the submission dashboard) | `decorator._user_may_view_this_organisation`, `user_may_view_organisational_audit`, `user_can_access_user`, `lookup_user_permissions_on_child` (`can_view`), `permissions.CanAccessOrganisation`, `organisation_views.py:120,381`, `case_views.py:1164`, `user_management_views.py:149,209,495`, `sanction_user_access.merged_parent_list_for_user` (Jersey rule), `audit_period_permissions._is_rcpch_user` (5 callers, all view checks), `case_table.html:117`; national view: `Epilepsy12User.save()` invariant, `organisation_views.py:938` toggle, `rcpch_choices` in `user_management_views.py:332` and `case_views.py:455`, `partials/cases/view_preference.html`; admin data banner and submission dashboard link: `nav.html:5,27`, and the dashboard view itself (`decorator.rcpch_full_access_only`) |
| `can_edit_case_outside_audit_period` (edit any child whatever its organisation, lock state or period) | `lookup_user_permissions_on_child` (`can_edit`), `registration_views.py:612` (earliest date = DOB), `registration_dates.html:18` (change a registration date), `case_table.html:136–150` |
| `can_manage_rcpch_audit_team_users` (create/edit RCPCH audit team users, edit emails) | `decorator.py:74` (`user_type == "rcpch-staff"`), `Epilepsy12UserAdminCreationForm.__init__` / `clean()`, `epilepsy12_user_list.html:31`, `admin_create_user.html:73` |
| `view_banner` (built-in; see banners targeted at any role, to check how they look) | `context_processors/banner.py:19` |
| `can_approve_audit_period_organisations` | `approve_audit_period_organisations.py:117` |

Line numbers are as of the commit this plan was written against.

**No new permission needed for two of them:**

- **KPI download and publishing:** `kpi_download` and `kpi_download_file` already sit behind `can_publish_epilepsy12_data`, so the flag check inside them is redundant and can go. `cohort_card.html:56` and the publish button in `selected_organisation_summary.html:30` use `perms.epilepsy12.can_publish_epilepsy12_data`.
- **16-character admin passwords:** `Epilepsy12UserUpdatePasswordForm` checks `role == RCPCH_AUDIT_TEAM or is_superuser`, not `has_perm`. The form also runs for password resets and first-time setup, when the account may still be inactive, and `has_perm` is always False for inactive users.

Where code needs to know *what a user is*, not *what they may do*, use `user.role == RCPCH_AUDIT_TEAM` rather than a group or permission check:

- `create_user` needs no organisation for this role (groups aren't assigned yet at that point).
- The "Edit RCPCH Epilepsy12 staff member" title (`user_management_views.py:594`).
- The user table badges.

## Phases

### Phase 0 – data audit (before any code change)

Run the read-only report (removed in Phase 3, once the flags were gone):

```bash
python manage.py audit_rcpch_user_flags
python manage.py audit_rcpch_user_flags --active-only
python manage.py audit_rcpch_user_flags --csv --output rcpch_flags_report.csv
```

It lists users with any of these findings:

- `flag_without_role`: a flag is set but the role is not RCPCH Audit Team. These users **lose** national access after the switch.
- `role_without_flag`: the role is RCPCH Audit Team but a flag is False. These users **gain** whatever that flag gates.
- `group_mismatch`: the user's groups are not exactly `group_for_role(role)`.

The team decides each one: change the role, or accept the change in access. Without this step, some users will lose access without warning.

The test seed users `*_CLINICAL_AUDIT_TEAM@nhs.net` (`tests/UserDataClasses.py`) are Lead Clinicians with both flags set, so they show up as `flag_without_role`. Revisit them in Phase 4.

### Phase 1 – add the permissions (additive, safe to deploy)

- Add the constants and `Meta.permissions` entries, then run `makemigrations` (permission-only migration, `0074_rcpch_audit_team_permissions`). Each permission sits on the model it most relates to:

    | Permission | Model |
    |---|---|
    | `can_access_all_organisations` | `Organisation` |
    | `can_edit_case_outside_audit_period` | `Case` |
    | `can_manage_rcpch_audit_team_users` | `Epilepsy12User` |
    | `can_approve_audit_period_organisations` | `AuditPeriodOrganisation` |

- Extend `EPILEPSY12_AUDIT_TEAM_ACCESS_PERMISSIONS` in `groups_seeder` with the four new permissions and the built-in `view_banner`, which no group held before.
- Extend `tests/general_functions_tests/test_groups_seeder.py`: the audit team group has all five (including `view_banner`), the other groups have none.

**Deploying.** `migrate` creates the permission rows; it doesn't attach them to the group. `s/start-prod` runs the seeder on every start, straight after `migrate`. Any environment that starts another way needs it run by hand:

```bash
python manage.py seed --mode=seed_groups_and_permissions
```

Until Phase 2, nothing checks these permissions, so the gap between deploying and running the seeder doesn't affect anyone.

**Groups.** The re-sync data migration originally planned here was dropped. [rcpch/rcpch-audit-engine#1496](https://github.com/rcpch/rcpch-audit-engine/pull/1496) lets audit team members and superusers change a user's role, which re-syncs that user's groups. Re-run `audit_rcpch_user_flags` and fix any remaining `group_mismatch` by setting the role again.

### Phase 2 – switch the checks

- Replace each call site in the table with `user.has_perm(PERM_...)` (full names are constants in `constants/user_types.py`), or `perms.epilepsy12.<codename>` in templates.
- `audit_period_permissions._is_rcpch_user` checks `can_access_all_organisations`. All five callers are view checks; editing stays constrained by `Case.editable()`.
- `Epilepsy12User.save()` checks `role == RCPCH_AUDIT_TEAM or is_superuser` for the national-view invariant. Django caches permissions on the user object, and a role change only updates groups after the save, so `has_perm` would be wrong there.
- `decorator.rcpch_full_access_only` (the submission dashboard) checks `can_access_all_organisations` instead of group membership, matching the nav link. Superusers now get access too.
- A database system check (`epilepsy12/checks.py`, `epilepsy12.E001`) errors if `epilepsy12_audit_team_full_access` lacks any permission in `RCPCH_AUDIT_TEAM_REQUIRED_PERMISSIONS`, so a missed seed shows up instead of locking the audit team out. Django runs database checks on `migrate` and `manage.py check --database default`, not on server start. The check skips a fresh database (no group yet) and permission rows that don't exist yet, because `migrate` runs it before applying migrations.
- Tests: the seeded `CLINICAL_AUDIT_TEAM` user now has the RCPCH Audit Team role, and test helpers that build users add them to their role's group, as real users are.

### Phase 3 – remove the fields

- Migration `0075_remove_rcpch_user_flags` drops both fields from `Epilepsy12User` and `HistoricalEpilepsy12User`. Their past values in the history table go with them.
- `create_user` requires an organisation unless `role == RCPCH_AUDIT_TEAM` (previously: unless `is_rcpch_staff`). `REQUIRED_FIELDS` and `create_superuser` no longer mention the flags.
- Removed the flags from:
    - the user form's `save()`, and the admin's list display, fieldsets and `save_model`, which used to sync them from role. The admin still re-syncs groups on a role change.
    - `Epilepsy12UserSerializer` and the user list CSV export;
    - `signals.py`. `role` is now in `EMAIL_TRIGGER_FIELDS`: promotion to the RCPCH Audit Team used to email admins only because the flags changed with it.
    - `create_dev_users`, `user_scripts` and `manual-setup.md`.
- The user table's two flag badges are now one "RCPCH Audit Team Member" badge, shown by the display-only template filter `has_rcpch_audit_team_role`.
- Deleted the `audit_rcpch_user_flags` command and its tests.

### Phase 4 – tests

Done alongside Phases 2 and 3:

- The factories and fixtures (`E12UserFactory`, `seed_users`, `UserDataClasses`) no longer set flags. The seeded `CLINICAL_AUDIT_TEAM` user has the RCPCH Audit Team role, and test helpers add users to their role's group.
- Tests that asserted flag values now assert role and group, and lookups by flag now filter on `role=RCPCH_AUDIT_TEAM`.
- `test_groups_seeder.py` checks the audit team group holds every RCPCH Audit Team permission and the other groups hold none.

## Existing bugs fixed along the way

- **Missing app label** (Phase 2): `add_employer_organisation` called `has_perm("can_allocate_user_to_organisation")` without the `epilepsy12.` prefix, so it was always False for non-superusers.
- **Typo:** `epilepsy12_user_list.html` checked `user.is_rcpch_team_member`, which doesn't exist. It now checks `can_manage_rcpch_audit_team_users`.

## Behaviour changes to sign off

- **Inactive superusers:** they lose implicit access, because `has_perm` returns False for inactive users. The current flag checks don't look at `is_active`.
- **Clinicians with the flag:** a clinician who had `is_rcpch_audit_team_member=True` but a trust role loses national access unless their role changes in Phase 0.

## Suggested PRs

1. Phases 0–1.
2. Phase 2.
3. Phases 3–4, after Phase 2 has run in production.
