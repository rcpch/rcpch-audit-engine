# Retiring `is_rcpch_audit_team_member` and `is_rcpch_staff`

This is the plan for replacing the two `Epilepsy12User` boolean flags with permissions attached to the **RCPCH Audit Team** role. Code checks those permissions with `has_perm`, not group membership.

## How the code works now

- **Two separate systems.** The `RCPCH_AUDIT_TEAM` role (4) puts a user in the `epilepsy12_audit_team_full_access` group (`common_view_functions/group_for_group.py`). The two booleans are set on their own, and about 70 non-test call sites check them directly.
- **They can disagree.** The model's comments say audit team members "can be clinicians". So a Lead Clinician with `is_rcpch_audit_team_member=True` gets national access without the role or group. **This is the main migration risk** (see Phase 0).
- **Permissions already exist for this.** `groups_seeder()` in `management/commands/create_groups.py` gives the audit team group its own `EPILEPSY12_AUDIT_TEAM_ACCESS_PERMISSIONS` list. That's where the new permissions go.
- **Superuser checks get simpler.** `has_perm()` is always True for an active superuser, so every `is_superuser or flag` becomes a single `has_perm(...)`.

## New permissions

Define each in `constants/user_types.py`, add it to `PERMISSIONS` and to `Epilepsy12User.Meta.permissions`, and attach it only to the audit team group.

| Permission | Replaces the flag checks in |
|---|---|
| `can_access_all_organisations` (view any organisation, user or child nationally) | `decorator._user_may_view_this_organisation`, `user_may_view_organisational_audit`, `user_can_access_user`, `lookup_user_permissions_on_child` (`can_view`), `permissions.CanAccessOrganisation`, `organisation_views.py:120,381`, `case_views.py:1164`, `user_management_views.py:149,209,495`, `sanction_user_access.merged_parent_list_for_user` (Jersey rule), `case_table.html:117` |
| `can_edit_case_outside_audit_period` (edit any child whatever its organisation, lock state or period) | `lookup_user_permissions_on_child` (`can_edit`), `audit_period_permissions._is_rcpch_user` (5 callers), `registration_views.py:612` (earliest date = DOB), `case_table.html:136–150` |
| `can_select_national_view_preference` | `Epilepsy12User.save()` invariant, `organisation_views.py:938` toggle, `rcpch_choices` in `user_management_views.py:332` and `case_views.py:455`, `partials/cases/view_preference.html` |
| `can_manage_rcpch_audit_team_users` (create/edit RCPCH audit team users, edit emails) | `decorator.py:74` (`user_type == "rcpch-staff"`), `Epilepsy12UserAdminCreationForm.__init__` / `clean()`, `epilepsy12_user_list.html:31`, `admin_create_user.html:73` |
| `can_view_admin_tools` (admin banner, submission dashboard link, all banners) | `nav.html:5,27`, `context_processors/banner.py:19` |
| `can_approve_audit_period_organisations` | `approve_audit_period_organisations.py:117` |

Line numbers are as of the commit this plan was written against.

**No new permission needed for two of them:**

- **KPI download:** `kpi_download` and `kpi_download_file` already sit behind `can_publish_epilepsy12_data`, so the flag check inside them is redundant and can go. `cohort_card.html:56` becomes `perms.epilepsy12.can_publish_epilepsy12_data`.
- **16-character admin passwords:** `Epilepsy12UserUpdatePasswordForm` should use `has_perm("epilepsy12.can_access_all_organisations")`.

Where code needs to know *what a user is*, not *what they may do*, use `user.role == RCPCH_AUDIT_TEAM` rather than a group or permission check:

- `create_user` needs no organisation for this role (groups aren't assigned yet at that point).
- The "Edit RCPCH Epilepsy12 staff member" title (`user_management_views.py:594`).
- The user table badges.

## Phases

### Phase 0 – data audit (before any code change)

Run the read-only report:

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

- Add the constants and `Meta.permissions` entries, then run `makemigrations` (permission-only migration).
- Extend `EPILEPSY12_AUDIT_TEAM_ACCESS_PERMISSIONS` in `groups_seeder`.
- Add a data migration that calls the seeder, or attaches the new permissions to the existing group. Production only gets them if `seed --mode=seed_groups_and_permissions` runs, so don't rely on that.
- Add a data migration to re-sync every user's groups from their role (fixes any `group_mismatch` found in Phase 0).
- Extend `tests/general_functions_tests/test_groups_seeder.py`.

### Phase 2 – switch the checks

- Replace each call site in the table with `user.has_perm("epilepsy12.<codename>")`, or `perms.epilepsy12.<codename>` in templates.
- Turn `audit_period_permissions._is_rcpch_user` into a permission check, splitting it into view and edit where the callers differ.
- In `Epilepsy12User.save()`, Django caches permissions on the user object, so don't use `has_perm` there. Move the national-view invariant into the toggle view and form, or have `save()` check `role == RCPCH_AUDIT_TEAM or is_superuser`.
- **Optional, in scope:** `decorator.rcpch_full_access_only` currently checks group membership. It could become a permission check too.

### Phase 3 – remove the fields

- Drop both fields from the model and run `makemigrations`. Simple History also changes `HistoricalEpilepsy12User`.
- Update `REQUIRED_FIELDS` (it currently lists `is_rcpch_audit_team_member`) and remove the flags from `create_superuser`'s `setdefault`s.
- Remove the flags from:
    - the form fields and `clean_is_*` methods;
    - `admin.py` (list display and fieldsets);
    - `Epilepsy12UserSerializer`;
    - the user export dict at `user_management_views.py:1003`;
    - `signals.py` (`EMAIL_TRIGGER_FIELDS`, `LOGGED_FIELDS`, `ADMIN_FLAGS`, the role-change notification list). Role changes already trigger both notifications.
- Remove the toggle from `admin_create_user.html` and the badges from `epilepsy12_user_table.html`.
- Update `create_dev_users`, `user_scripts`, `documentation/docs/development/manual-setup.md` and `tests/misc_py_shell_code.py`.
- Delete the `audit_rcpch_user_flags` command and its tests.

### Phase 4 – tests

- Update the factories (`E12UserFactory`, `seed_users`, `UserDataClasses`), which set the flags directly.
- Update about 15 test modules: the `permissions_tests/*`, `test_audit_period_permissions`, `test_case_list_filters`, `test_merged_parent_list`, `test_epilepsy12user_sync`, `test_inactivity_deactivation`, `test_approve_audit_period_organisations_command`.
- Add a test per new permission: audit team has it, the other groups don't.
- Run the full suite.

## Existing bugs to fix along the way

- **Missing app label:** `user_management_views.py:675` calls `has_perm("can_allocate_user_to_organisation")` without the `epilepsy12.` prefix. It's always False for non-superusers.
- **Typo:** `epilepsy12_user_list.html:31` checks `user.is_rcpch_team_member`, which doesn't exist.

## Behaviour changes to sign off

- **Inactive superusers:** they lose implicit access, because `has_perm` returns False for inactive users. The current flag checks don't look at `is_active`.
- **Clinicians with the flag:** a clinician who had `is_rcpch_audit_team_member=True` but a trust role loses national access unless their role changes in Phase 0.

## Suggested PRs

1. Phases 0–1.
2. Phase 2.
3. Phases 3–4, after Phase 2 has run in production.
