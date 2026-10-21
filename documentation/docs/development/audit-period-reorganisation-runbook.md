---
title: Audit-period reorganisation runbook
reviewers: Dr Simon Chapman
---

# Audit-period reorganisation runbook

This is the staff-facing procedure for applying an organisational
reorganisation (a trust merger, acquisition, dissolution, or ODS code
change) to the Epilepsy12 audit-period organisation membership layer.

It is the operational counterpart to the design in
[audit-period-organisation.md](./audit-period-organisation.md). The design
document explains *why* the model separates live current-state hierarchy
from period-aware frozen hierarchy; this runbook explains *how* the audit
team applies a reorganisation in production.

## When to use this runbook

Use this runbook when:

- the `rcpch-nhs-organisations` API has been updated to reflect a merger,
  acquisition, dissolution, or ODS code change that affects one or more
  organisations with Epilepsy12 registrations; **or**
- you are standing up the audit-period organisation membership layer for
  the first time in a new environment (staging or live); **or**
- you are re-syncing the in-flight cohort after a mid-cohort reorganisation
  has been reflected in the API.

## Prerequisites

- `RCPCH_NHS_ORGANISATIONS_API_KEY` is set in the environment.
- The Django management commands are available:
  `sync_nhs_organisations`, `sync_audit_period_organisations`,
  `approve_audit_period_organisations`.
- You have an audit-team user account (RCPCH audit team member, RCPCH staff,
  or superuser) for the approval step.
- The API's temporal history layer is backfilled for the periods you intend
  to sync. See the [pre-floor mergers](#pre-floor-mergers) section below
  for the limitation when it is not.

## The two sync commands

There are two sync commands. They have distinct, non-overlapping
responsibilities and must not be conflated:

| Command | Owns | Writes to | Trust it changes |
|---|---|---|---|
| `sync_audit_period_organisations` | Period-aware membership rows | `AuditPeriodOrganisation` | Period memberships (`AuditPeriodOrganisation.trust`) |
| `sync_nhs_organisations` | Live current-state rows | `Organisation`, `Trust`, `ICB`, `LHB`, etc. | **Live `Organisation.trust`** |

The per-cohort sync freezes the hierarchy as it was at each audit period's
reference date. The current-state sync moves the live `Organisation.trust`
FK to match the API's current state. The separation is what makes the
design safe: once cohort 7's trust assignment is frozen into
`AuditPeriodOrganisation`, a later current-state sync can move
`Organisation.trust` to the new trust without affecting cohort 7's KPIs —
because publication reads the frozen membership, not the live FK.

## Cutover sequence (first run)

This is the step-by-step sequence for the **first time** you stand up the
period-aware organisation membership layer in a new environment. It orders
all five commands with what each does, why the order matters, and what to
check before moving on.

### Step 0 — Baseline review

```bash
python manage.py sync_nhs_organisations --dry-run
```

Preview what the current-state sync will do. Review the output for:

- **Organisation trust/LHB moves** and whether they carry
  registrations/cases exposure — these are the high-impact changes.
- **Trust/LHB `active` flips** (mostly dissolved/merged trusts going
  `active=False`).
- **Cases orphaned from no-cohort UI** — the dry-run reports, for each
  organisation going `active=False` with cases but no active successor
  linked via `OrganisationIdentity`, the number of cases that would not
  appear in the no-cohort trust dropdown after cutover. These cases remain
  in the database and are reachable via cohort-selected views and direct
  organisation URLs, but they disappear from the no-cohort dropdown until
  `--link-identities` is run.

Pass `--full` to see every entry without truncation:

```bash
python manage.py sync_nhs_organisations --dry-run --full
```

Keep the dry-run output for the record.

### Step 1 — Freeze historical memberships

```bash
python manage.py sync_audit_period_organisations
```

Populate `AuditPeriodOrganisation` rows for every audit period by calling
the API's snapshot endpoint at each period's reference date
(`data_collection_end_date`). This freezes, per period, which Trust/LHB/
ICB/region/network/country each participating organisation belonged to.
Rows are created **unapproved** (`approved_at` is null). This command never
touches live `Organisation.*` fields.

### Step 2 — Review and approve the memberships

```bash
python manage.py approve_audit_period_organisations
```

Walk each unapproved row and decide whether the frozen period hierarchy is
correct. The command shows the period hierarchy and the exposure
(registrations and distinct cases attached to the organisation) so you can
judge impact before committing.

At minimum you must approve memberships in the **in-flight cohorts**
(currently recruiting / in data collection / in grace) to unblock the next
step — the current-state sync's ordering constraint blocks on any in-flight
period having zero approved memberships.

Flags:

- `--cohort N` — scope to a single cohort.
- `--ods-code CODE` — scope to specific organisations (can be passed
  multiple times).
- `--dry-run` — review exposure without prompting or writing.
- `--auto-approve` — approve every unapproved row (review with `--dry-run`
  first).

See [Pre-floor mergers](#pre-floor-mergers) for cases where the
snapshot-sourced hierarchy is wrong and must be declined with a note.

### Step 3 — Apply the live current state

```bash
python manage.py sync_nhs_organisations --confirm
```

This is the command that mutates the **live** `Organisation.trust` /
`Organisation.local_health_board` / etc. and flips `active` flags to match
the API's current state.

If the command prints `Sync blocked by the ordering constraint: ...`,
return to Step 2 and approve the in-flight cohorts before re-running.

### Step 4 — Link OrganisationIdentity

```bash
python manage.py sync_audit_period_organisations --link-identities
```

Bridge ODS code changes from mergers/dissolutions by linking successor
`Organisation` rows to their predecessors via `OrganisationIdentity`. This
must run **after** Step 3 because the current-state sync creates the new
ODS code rows that this step links.

This step is what makes cases on an inactive predecessor organisation
visible through the active successor in the no-cohort UI. Without it, the
dry-run's "cases orphaned from no-cohort UI" warning would materialise:
cases would remain in the database but not appear in the trust dropdown.

### Step 5 — Confirm the changes

```bash
python manage.py sync_audit_period_organisations --reconcile
```

Produce a read-only verification report covering hierarchy changes between
periods, registration attribution, and sibling organisations. This is the
counterpart to Step 3 — it confirms the sync was applied as expected.

### Summary of commands

| # | Command | Writes to | Trust it changes | Net effect |
|---|---|---|---|---|
| 0 | `sync_nhs_organisations --dry-run` | nothing | — | Preview + orphan check |
| 1 | `sync_audit_period_organisations` | `AuditPeriodOrganisation` | period memberships | Freeze historical/period hierarchy (unapproved) |
| 2 | `approve_audit_period_organisations` | `AuditPeriodOrganisation.approved_at/by` | period memberships (locks) | Approve & freeze; unblocks Step 3 |
| 3 | `sync_nhs_organisations --confirm` | live `Organisation`, `Trust`, etc. | **live `Organisation.trust`** | Move/reparent live organisations to current state |
| 4 | `sync_audit_period_organisations --link-identities` | `Organisation.identity` / `OrganisationIdentity` | — | Link ODS code successors to predecessors |
| 5 | `sync_audit_period_organisations --reconcile` | nothing | — | Verify the whole cutover |

## Succession walking

The `rcpch-nhs-organisations` API's snapshot endpoint walks the
`OrganisationSuccession` chain to resolve the entity that was in force on
the queried date. When the queried ODS code was inactive by the reference
date (because a merger or dissolution occurred before then), the snapshot
walks **forward** to the active successor and returns the successor's
state — its ODS code, trust, ICB, region, network, and country — with
`predecessor_ods_code` set to the queried code. When the queried code did
not yet exist on the reference date, the snapshot walks **backward** to the
predecessor.

This means the per-cohort sync does not need to reconstruct succession
locally: the API does it. For each cohort, the snapshot returns the
organisation and trust that were in force at that cohort's reference date,
and the sync freezes them into the `AuditPeriodOrganisation` membership.

### Worked example: Ormskirk & District General Hospital (`RVY02`)

Southport & Ormskirk Hospital NHS Trust (`RVY`) was dissolved on
2023-07-01; Ormskirk hospital then came under Mersey & West Lancashire
Teaching Hospitals NHS Trust (`RBN`) as `RBN52`.

| Cohort | Reference date | Snapshot for `RVY02` returns | Membership frozen as |
|---|---|---|---|
| 4 (2022-11-30) | before merger | `ods_code=RVY02`, `trust=RVY`, `successor=RBN52` | `trust=RVY` ✓ |
| 7 (2025-11-30) | after merger | `ods_code=RBN52`, `trust=RBN`, `predecessor=RVY02` | `trust=RBN` ✓ |
| 8 (2026-12-31) | after merger | `ods_code=RBN52`, `trust=RBN`, `predecessor=RVY02` | `trust=RBN` ✓ |

The sync also links `RVY02` and `RBN52` via `OrganisationIdentity` using
the `predecessor_ods_code` / `successor_ods_code` fields, so cases
registered against the predecessor ODS code remain visible through the
active successor after cutover.

### Genuine dissolution (no successor)

When the snapshot returns an inactive trust with no successor
(`predecessor_ods_code` and `successor_ods_code` both null for the
resolved entity), the organisation is genuinely defunct. The sync freezes
the inactive trust into the membership — this is correct, because there is
no active successor to attribute the cases to.

### The `source` field

Each `AuditPeriodOrganisation` row records its provenance via the `source`
field:

- `"snapshot"` — the row came from the API's snapshot endpoint at the
  period's reference date.
- `"detail_fallback"` — the snapshot returned 404 (no temporal history for
  this date), and the sync fell back to the detail endpoint (current
  state).
- `"manual"` — the row was created or corrected by hand.

Rows with `source="detail_fallback"` should be re-synced once the API
backfills temporal history for the relevant period.

## Period-correct dropdown behaviour

After cutover, the operational dashboard and case list update their
dropdowns based on the organisational relationships at the time of the
selected cohort:

- **Cohort 4 selected** (before the Ormskirk merger) — the dashboard shows
  `RVY` (Southport & Ormskirk) from the frozen membership. The
  period-context alert fires when the period-correct parent differs from
  the current parent (`RBN`).

- **Cohort 7 or 8 selected** (after the Ormskirk merger) — the dashboard
  shows `RBN` (Mersey & West Lancs) from the frozen membership. No alert
  fires if `RBN` is also the current parent.

- **No cohort selected ("all children")** — the dashboard uses the
  current live parent. No period alert fires.

The alert is contextual: it appears only when the period-correct parent
and the current parent diverge, and it does not block or hide anything.
It is the UX guard that makes period-correct dropdowns safe to ship.

## In-flight cohort re-sync

The currently in-flight cohort (recruiting, in data collection, or in
grace) is not yet historical. Its organisational hierarchy can still change
while the cohort is open. Re-run the per-cohort sync periodically for the
in-flight cohort:

```bash
python manage.py sync_audit_period_organisations --cohort <N>
```

The sync is idempotent:

- approved rows are never overwritten (an approved historical membership
  is stable);
- unapproved rows for the in-flight cohort are updated to the latest
  snapshot, which is the desired behaviour while the cohort is still open
  and the audit team have not yet approved the membership;
- once the cohort closes and the audit team approve the membership, the
  row is frozen.

Approving an in-flight membership freezes it against later
re-organisations for the remainder of the open cohort. Keep an in-flight
cohort's memberships unapproved until you are confident the hierarchy is
final, run the re-sync to pick up the latest snapshot, and only then
approve. If you approve too early and a mid-cohort reorganisation occurs,
clear `approved_at` on the affected row(s) before re-syncing.

## Reference-date policy

The per-cohort sync uses `AuditPeriod.data_collection_end_date` as the
reference date for the snapshot call. This is the currently implemented
default.

An open decision for the audit team: should the reference date be
`data_collection_end_date`, `recruitment_end_date`, or
`recruitment_start_date`? The choice determines which cohort first picks
up a new trust after a merger:

| Policy | Reference date | A merger during cohort N's data collection takes effect from |
|---|---|---|
| A | `recruitment_start_date` | cohort N+1 (first cohort whose recruitment opens after the merger) |
| B | `recruitment_end_date` | cohort N (the cohort in recruitment at merger time) |
| C (current) | `data_collection_end_date` | cohort N (the cohort in data collection at merger time) |

The reference date does not affect pre-floor mergers (the snapshot returns
the same trust regardless of reference date). It only matters for mergers
that land **inside** the API's temporal window.

This decision should be confirmed by the audit team before the sync runs.
If a different reference date is needed per period, an explicit
`hierarchy_reference_date` field can be added to `AuditPeriod`.

## Rollback

- Steps 1–5 are safe to re-run. Step 2 only ever touches unapproved rows,
  so a re-run re-presents only what is still unapproved.
- Once Step 3 has run, re-running it is idempotent — it detects that live
  rows already match the API and reports no further high-impact changes.
- Rolling back a live trust move is not automatic. To undo a specific
  move you would need to re-run a later current-state sync with the API
  reflecting the previous state, or correct the `Organisation.trust`
  manually — there is no built-in undo in these commands.

## Country invariant

England uses `Trust` as the reporting parent; Wales uses `LocalHealthBoard`.
The two are mutually exclusive for a given organisation. The per-cohort
sync and the current-state sync both preserve this invariant: an English
organisation's `local_health_board` must not be populated, and a Welsh
organisation's `trust` must not be populated. Reconciliation reports
Trust/LHB changes between periods but does not conflate the two.