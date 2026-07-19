---
title: Submission Deadlines
reviewers: Dr Simon Chapman
render_macros: true
---

Cohorts recruit from January to December and collect data for a full year of care, before submission the following January. More detail on the dates can be found [here](cohort.md).

Cohorts are tracked in the `AuditPeriod` model which sets the dates for each audit period: recruitment start and end, data collection end, and the audit-wide `submission_deadline`.

## Per-organisation overrides

The audit-wide `submission_deadline` applies to every organisation. Individual organisations can be granted a different deadline for a single audit period via the `AuditPeriodExtension` model. One row exists per (audit period, organisation), enforced by a unique constraint — "extending further" edits the same row in place, and every change is captured by simple-history.

An extension row can move the deadline in either direction:

- **Later** — a granted extension, requested by the organisation's lead clinician (e.g. because of staffing shortages or EPR problems).
- **Earlier** — the audit team closes submission for that organisation immediately, typically because the organisation has confirmed it has finished entering data. The extension date is set to today (inclusive: submission is still possible today).

Deadline resolution lives on `AuditPeriod.submission_deadline_for_organisation()`: if the organisation holds an extension row it always wins, whether later or earlier; otherwise the audit-wide deadline applies. All countdowns on the dashboard (`days_until_submission_deadline_for_organisation()`) resolve through this method, so an extension or early close is reflected everywhere automatically.

`AuditPeriod.effective_latest_submission_date` (used by `is_complete`) takes the *latest* of the audit-wide deadline and any extensions — an early-close row never exceeds the audit-wide deadline, so it cannot make a period complete while other organisations can still submit.

### Reasons

Extensions carry a coded `reason` (`PositiveSmallIntegerField` with choices), not free text. The choices live in `epilepsy12/constants/audit_period_extension_reasons.py` and can be added to or reworded without a migration — only the initial field type change needed one. Reason is optional, and always `None` for early closes.

## Granting, closing and removing

All three operations are methods on `AuditPeriod`, keeping the validation (which is all period business logic) next to the deadline-resolution code:

| Method | Effect | Validation |
|---|---|---|
| `extend_submission_deadline(organisation, days, user, reason)` | Sets the extension to the organisation's current *effective* deadline plus `days` — so a second extension stacks on the first | Period must be submitting or in grace; result must be after the audit-wide deadline; reason must be a valid choice |
| `close_submission_for_organisation(organisation, user)` | Sets the extension to today; reason cleared | Period must be submitting or in grace |
| `remove_submission_extension(organisation, user)` | Deletes the row, reverting to the audit-wide deadline | Refused once the audit-wide deadline has passed (the row is then the historical record of what the organisation submitted against) |

All three stamp `created_by`/`updated_by` from the acting user (`UserStampAbstractBaseClass`).

Eligibility — "submitting or grace" — is the window from `data_collection_start_date` through the audit-wide `submission_deadline`. The cohort card exposes this as `is_extension_eligible` (evaluated against the card's `today`, not the `is_collecting_data`/`is_in_grace_period` properties, which are pinned to `timezone.now()`).

## The UI

Epilepsy12 audit team members manage extensions from the organisation dashboard (`organisation/<id>/summary`), which shows three cohort cards:

1. **Grace cohort** (December to the second Tuesday of January) or the **most recently closed cohort** the rest of the year — so the first card always shows a cohort with dates. The fallback is `AuditPeriod.objects.most_recently_closed()`; `within_grace_period` keeps its strict meaning for views deciding which cohort is imminently submitting.
2. **Currently submitting cohort**.
3. **Currently recruiting cohort**.

Cards are built by `AuditPeriod.as_cohort_card_dict(today, organisation)`, which includes the audit-wide deadline, the organisation's extension date (if any), an `is_closed_early` flag distinguishing early closes from true extensions, and `is_extension_eligible`. `cohort_summary(organisation=...)` threads the viewed organisation through all three cards; callers that don't render per-organisation cards omit it and get audit-wide dates.

Users holding the `can_extend_submission_deadline` permission (granted to the `epilepsy12_audit_team_full_access` group) see action buttons on eligible cards:

- **Extend deadline** / **Extend further** (when an extension already exists) — swaps the card for a form partial. The admin enters a number of days (stacked on the current effective deadline) and an optional reason.
- **Close submission** (only when an extension exists) — closes today, with a SweetAlert confirmation.
- **Remove extension** (only when an extension exists) — reverts to the audit-wide deadline, with a SweetAlert confirmation.

The endpoint is `organisation/<organisation_id>/audit_period/<cohort>/extension` (`audit_period_extension`), one URL handling GET (form partial, or plain card for the cancel button) and POST (`action` of `extend`/`close`/`remove`). The form partial and cohort card share the same root element id (`cohort_card_<cohort>`) so every response swaps the same target — this matters because three cards render on one page and every id must be cohort-suffixed.

The card badge shows "Extended to …" in pink when the extension is later than the audit-wide deadline, "Closed early: …" when earlier or equal.

## Emails

Every successful action emails the organisation's lead clinician(s) (active users with `role=AUDIT_CENTRE_LEAD_CLINICIAN` employed by the organisation) and the generic audit team address (`settings.SITE_CONTACT_EMAIL`). If the organisation has no lead clinician, the email goes only to the audit team address with "NO LEAD CLINICIAN" in the subject — the same fallback as the lead-site transfer emails.

The email is constructed by `construct_extension_granted_email()` in `epilepsy12/general_functions/construct_extension_email.py`, rendering `templates/registration/extension_granted_email.html` with wording per action: granted (new deadline, audit-wide date and reason), closed (no further submissions after today), withdrawn (deadline reverts).

## Permissions

`can_extend_submission_deadline` is declared in `epilepsy12/constants/user_types.py`, hung on `AuditPeriodExtension.Meta.permissions`, and assigned to the `epilepsy12_audit_team_full_access` group by the `create_groups` seeder. The seeder (`groups_seeder()`) is idempotent: it creates missing groups and adds missing permissions to existing ones, and is run unconditionally by the test suite's `seed_groups_fixture` so reused test databases pick up newly added permissions.

## Testing

- `epilepsy12/tests/model_tests/test_audit_period.py` — card dict shape and org-awareness, extension eligibility windows, close-early resolution, `clean()` floors, close/remove methods, cohort summary fallback.
- `epilepsy12/tests/view_tests/test_audit_period_extension.py` — permission gating (audit team vs lead clinician), GET form, POST extend creates/updates one row, invalid days/reason, ineligible cohort, close/remove actions, 404 for unknown cohort, and email outbox assertions including the no-lead-clinician fallback.

Note the view tests are date-sensitive: extend and close require today to be inside an eligible cohort window, so they use whichever cohort is currently submitting rather than hard-coding cohort numbers.
