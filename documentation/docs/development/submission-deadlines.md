---
title: Submission Deadlines
reviewers: Dr Simon Chapman
render_macros: true
---

Cohorts recruit from January to December and collect data for a full year of care, before submission the following January. More detail on the dates can be found [here](cohort.md).

Cohorts are tracked in the `AuditPeriod` model which sets default values for the start and end dates of the audit period. These can be overridden on a per-organisation basis in the `AuditPeriodExtension` model.

## Per-organisation submission deadline extensions

The audit-wide `submission_deadline` on `AuditPeriod` can be extended for a single organisation via `AuditPeriodExtension`. Previously this was only editable in Django admin; this feature exposes it in the UI for Epilepsy12 admin staff.

### Workflow

1. Organisation lead clinician contacts the audit team by email requesting an extension.
2. Epilepsy12 admin logs in and navigates to the organisation dashboard (`organisation/<id>/summary`), which shows cohort date cards.
3. Admin clicks **Extend submission deadline** on the relevant cohort card, enters a new date and reason, and confirms.
4. The extension is saved (one row per organisation per audit period; re-extending edits the same row) and an email is sent to the organisation's lead clinician(s) and the generic audit team address confirming the extension.

### Decisions

- **Permissions**: new custom permission `can_extend_submission_deadline`, hung on `AuditPeriodExtension.Meta.permissions`, granted to the `epilepsy12_audit_team_full_access` group.
- **Card display**: the card keeps showing the original audit-wide deadline, with a badge showing "Extended to …" where an extension exists for the viewed organisation.
- **Email recipients**: lead clinician(s) of the organisation (active users with `role=AUDIT_CENTRE_LEAD_CLINICIAN` employed by the organisation) plus the generic audit team address (`settings.SITE_CONTACT_EMAIL`).
- **Eligible cohorts**: only the currently submitting cohort and the grace cohort (periods where data submission is still open), not completed periods.
- **One row per org/period**: enforced by the existing `one_extension_per_organisation_per_audit_period` unique constraint; the view uses `update_or_create`. Changes are captured by simple-history.
- **Reason is coded, not free text**: `AuditPeriodExtension.reason` changes from `TextField` to `PositiveSmallIntegerField(choices=...)`. Reasons are defined as class-level constants + a tuple of tuples on the model (the `VisitActivity.ACTIVITY` pattern), so the list can be extended/edited later without a migration — only the initial field-type change needs one.
- **URL design**: `organisation/<int:organisation_id>/audit_period/<int:cohort>/extension`, named `audit_period_extension`. Cohort number (not PK, not slug) is used in the URL — stable and human-meaningful. The `AuditPeriod.slug` field stays unexposed for now; it can be formalised later for reporting URLs if needed.

### Implementation checklist

- [ ] **1. Permission: constant + migration**
  - Add `CAN_EXTEND_SUBMISSION_DEADLINE` to `epilepsy12/constants/user_types.py` and include in `PERMISSIONS`.
  - Add to `AuditPeriodExtension.Meta.permissions` in `epilepsy12/models_folder/audit_period.py`.
  - *Commit: "Add can_extend_submission_deadline permission"*

- [ ] **2. Change `reason` to coded choices + single migration for steps 1–2**
  - Define reason constants and `EXTENSION_REASONS` tuple on `AuditPeriodExtension` (e.g. staffing shortage, EPR/system issues, clinical capacity, data quality queries, other).
  - Replace `reason = models.TextField(...)` with `models.PositiveSmallIntegerField(choices=EXTENSION_REASONS, ...)`. Field was introduced in migration `0062`; existing rows (if any) need a data decision — default to "other".
  - Generate one migration covering the new permission and the field change.
  - Model test: reason stores a coded value; `get_reason_display()` returns the label.
  - *Commit: "Change extension reason to coded choices"*

- [ ] **3. Grant permission to audit team group**
  - Wire into `epilepsy12/management/commands/create_groups.py` (content type for `AuditPeriodExtension`, assign to `epilepsy12_audit_team_full_access`).
  - *Commit: "Grant extension permission to audit team group"*

- [ ] **4. Model/manager support for the card**
  - Add `audit_period_id` and (org-aware) extension info to `AuditPeriod.as_cohort_card_dict()`, or add a small helper returning the org's extension for the summary view to merge in.
  - Helper on `AuditPeriod` or manager to identify extension-eligible periods (submitting or grace, not complete).
  - Tests in `epilepsy12/tests/model_tests/test_audit_period.py`: card dict exposes extension when present for the org; eligibility helper excludes completed periods.
  - *Commit: "Expose extension state on cohort card data"*

- [ ] **5. URL**
  - Add path to `organisation_patterns` in `epilepsy12/urls.py`: `organisation/<int:organisation_id>/audit_period/<int:cohort>/extension`, name `audit_period_extension`.

- [ ] **6. View: GET form partial + POST grant**
  - New view in `epilepsy12/views/organisation_views.py`, decorated with `@login_and_otp_required()`, `@user_may_view_this_organisation()`, `@permission_required("epilepsy12.can_extend_submission_deadline", raise_exception=True)`.
  - GET: render `extension_form.html` partial with organisation, audit period, current deadline, existing extension (prefilled), and the reason choices.
  - POST: validate date (must be after audit-wide deadline; period must be eligible) and reason (must be a valid choice), `update_or_create` the `AuditPeriodExtension`, set user stamps, send email, re-render the cohort card with success state.
  - View tests (new file, e.g. `epilepsy12/tests/view_tests/test_audit_period_extension.py`): permission denied for non-audit-team users; audit team can GET the form; POST creates an extension; POST again updates the same row (no duplicate); invalid date rejected; completed cohort rejected.
  - *Commit: "Add extension view and URL"*

- [ ] **7. Email**
  - New `construct_extension_granted_email()` helper in `epilepsy12/general_functions/` (following `construct_transfer_email.py`) rendering a new template `templates/registration/extension_granted_email.html`; include the organisation, cohort, new deadline and the reason's display label.
  - Recipients: lead clinician(s) of the organisation (fallback to `SITE_CONTACT_EMAIL` if none) plus `SITE_CONTACT_EMAIL`.
  - Tests: email sent to expected recipients on POST (use Django's `mail.outbox`); fallback recipient when no lead clinician.
  - *Commit: "Send extension granted email"*

- [ ] **8. Templates**
  - `cohort_card.html`: add "Extend submission deadline" button gated on `perms.epilepsy12.can_extend_submission_deadline`; render "Extended to …" badge when extension data present.
  - New partial `templates/epilepsy12/partials/organisation/extension_form.html` (date input + reason select from the coded choices, `hx-post` with CSRF header, inline error re-render; success swaps back the updated card).
  - *Commit: "Extension UI on cohort card"*

- [ ] **9. Full test run + docs**
  - `s/test` full suite green.
  - Tick off this checklist; note any deviations.

### Test command

```bash
s/test --local epilepsy12/tests/model_tests/test_audit_period.py
s/test --local epilepsy12/tests/view_tests/test_audit_period_extension.py
s/test  # full suite
```
