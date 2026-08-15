---
title: Organisational versioning — design note
reviewers: Dr Simon Chapman
---

# Organisational versioning — design note

!!! note "Document status"
    Draft for review. This document explores how to represent the changing
    organisational landscape (trust mergers, ICB reorganisations, ODS code
    changes) between audit periods in the E12 local models, without requiring
    batch user-migration operations or case migrations.

## Problem

The `rcpch-nhs-organisations` API now maintains a temporal history layer
that records every state change from installation day forward: trust
mergers, renames, closures, ODS code changes, ICB reorganisations. The
API's `snapshot` endpoint returns an organisation's full geography as it
was on a given date, walking the succession chain to a predecessor when
the organisation did not yet exist on that date.

E12 needs to answer two different questions against this data:

1. **Operational** — "which hospital does this clinician work at, and
   which sibling organisations can they see?" This is always against
   current state.
2. **Reporting** — "which trust was this organisation under in cohort 7?"
   This is per-audit-period, not current state.

Today the local models (`Organisation`, `Trust`, `IntegratedCareBoard`,
`LocalHealthBoard`) represent current state only. When a trust merges,
the sync would mark the predecessor `active=False` — but the cases, KPIs,
sites, and user permissions are still attached to organisations under
that trust. The live dashboard breaks: cases disappear from trust-level
views, aggregations drop them, and users lose access.

## Design goals

- The correct organisational geography is available per audit period for
  reporting (KPI aggregation, audit progress, public KPI report).
- The operational code (case creation, user permissions, organisation
  selectors) continues to work without batch migrations when a trust
  merges.
- A clinician retains access to their own organisation's historic cases
  after a merger, but loses access to sibling organisations under the
  old trust.
- No case migration is needed — cases stay on the organisation row they
  were created against.
- No batch user-migration is needed when a new cohort starts or a trust
  merges mid-cohort.

## Proposed approach

### `audit_period` on the base models

Each of `Organisation`, `Trust`, `IntegratedCareBoard`, and
`LocalHealthBoard` gains an `audit_period` foreign key. The natural key
becomes `(ods_code, audit_period)` (or `(boundary_identifier,
audit_period)` for ICB/LHB/Country). One row per entity per audit
period, carrying the name, address, active flag, and parent FKs as they
were during that audit period.

```
Organisation
  ods_code: CharField
  audit_period: ForeignKey(AuditPeriod)
  name, address1, address2, telephone, postcode, ...
  trust: ForeignKey(Trust)          # the trust as of this audit period
  local_health_board: ForeignKey(LocalHealthBoard)
  integrated_care_board: ForeignKey(IntegratedCareBoard)
  nhs_england_region: ForeignKey(NHSEnglandRegion)
  openuk_network: ForeignKey(OPENUKNetwork)
  country: ForeignKey(Country)
  unique_together = (ods_code, audit_period)

Trust
  ods_code: CharField
  audit_period: ForeignKey(AuditPeriod)
  name, address_line_1, town, postcode, ...
  unique_together = (ods_code, audit_period)

# Same pattern for IntegratedCareBoard, LocalHealthBoard
```

The sync populates these by calling the API's `snapshot` endpoint for
each participating organisation at the audit period's reference date.
One row per (organisation, audit period), carrying the correct parent
geography for that period.

### How reporting works

```python
# All organisations for cohort 7, with their correct trust for that cohort
Organisation.objects.filter(audit_period=cohort_7)

# All trusts active in cohort 7
Trust.objects.filter(audit_period=cohort_7, active=True)

# KPI aggregation for a trust in cohort 7
Trust.objects.filter(audit_period=cohort_7, ods_code="RJZ")
```

No date arithmetic, no interval logic, no API calls at request time. The
correct geography for each cohort is a simple FK filter.

### Examples of organisational change

The table below shows how the four main types of organisational change
are represented in the per-cohort model. Each example uses real ODS
codes and merger dates from the `rcpch-nhs-organisations` API's
documentation.

| Type | What happens | Example | Cohort before | Cohort after | OrganisationEntity | Cases |
|---|---|---|---|---|---|---|
| **Merger** (full) | Two trusts dissolve; a new trust is created with a new ODS code. Child organisations are reassigned to the new trust. | Ipswich Hospital (RGQ) + Colchester (RDE) → East Suffolk and North Essex (RJL), 2018 | Orgs under RGQ and RDE in cohort 5 | Same orgs under RJL in cohort 6 | One entity per hospital, unchanged. Org rows point to RJL trust in cohort 6. | Cases stay on the same Organisation rows; trust FK changes to RJL in the new cohort's row. |
| **Acquisition** | One trust acquires another. The acquiring trust keeps its ODS code; the acquired trust is dissolved. Child organisations are reassigned. | Royal Free London (RAL) acquired Barnet & Chase Farm (RVL), 2014. Barnet Hospital kept its org code (RGT01-style) but parent changed from RVL to RAL. | Org under RVL in cohort 4 | Same org, same ODS code, under RAL in cohort 5 | One entity per hospital, unchanged. Org rows point to RAL trust in cohort 5. | Cases stay on the same Organisation rows; trust FK changes to RAL. |
| **Split** (dissolution with split) | A trust is dissolved and its child organisations are split between different successor trusts. Child organisations get new ODS codes. | South London Healthcare (RYQ) dissolved 2013. PRUH (RYQ30) → King's (RJZ) as RJZ30. QEH Woolwich (RYQ01) → Lewisham & Greenwich (RJ2) as RJ201. | PRUH as RYQ30 under RYQ in cohort 4 | PRUH as RJZ30 under RJZ in cohort 5 | One entity per hospital. PRUH entity links RYQ30 (cohort 4) and RJZ30 (cohort 5) via `successor_of`. | Cases stay on the Organisation row they were created against (RYQ30/cohort 4 or RJZ30/cohort 5). |
| **Rename** | A trust changes its name but keeps its ODS code. No child organisations move. | University Hospitals Bristol and Weston (RA7) renamed to Bristol NHS Foundation Trust (still RA7), 2024. | Trust RA7, name "UNIVERSITY HOSPITALS BRISTOL AND WESTON NHS FT" in cohort 7 | Trust RA7, name "BRISTOL NHS FOUNDATION TRUST" in cohort 8 | No entity change. Trust row for cohort 8 carries the new name. | Cases stay on the same Organisation rows; only the trust name changes in the new cohort's row. |

In all four cases:

- **No case migration is needed.** Cases stay on the `Organisation` row
  they were created against. That row carries the correct geography
  (trust, ICB, etc.) for its cohort.
- **No user migration is needed.** User memberships point to
  `OrganisationEntity`, which is stable. The user's sibling access
  changes automatically because it's resolved against the current
  cohort's trust.
- **The entity model handles ODS code changes.** In the split case,
  PRUH has two ODS codes (RYQ30, RJZ30) across cohorts, but one
  `OrganisationEntity` row. The `successor_of` link connects them.

### How the PRUH edge case works

Princess Royal University Hospital changed its ODS code from `RYQ30`
(under South London Healthcare NHS Trust, `RYQ`) to `RJZ30` (under King's
College Hospital NHS Foundation Trust, `RJZ`) when South London
Healthcare was dissolved in 2013.

With per-cohort rows:

```
Organisation(ods_code=RYQ30, audit_period=cohort_5, trust=RYQ/cohort_5)
Organisation(ods_code=RJZ30, audit_period=cohort_6, trust=RJZ/cohort_6)
Organisation(ods_code=RJZ30, audit_period=cohort_7, trust=RJZ/cohort_7)
```

Cases entered in cohort 5 are on `RYQ30/cohort_5`. Cases entered in
cohort 6 are on `RJZ30/cohort_6`. No case migration needed — the cases
stay on the organisation row they were created against, and that row
carries the correct geography for its cohort.

### How user access works — the intermediate model

The problem with `audit_period` on `Organisation` is that user
memberships (`Epilepsy12User` ↔ `Organisation` via the
`OrganisationEmployer` through table) would need to move to a new
`Organisation` row every time a new cohort starts or a trust merges
mid-cohort. This is a batch operation, and it's fragile — if it fails
partway through, users lose access.

To avoid this, introduce an intermediate model that is **stable across
cohorts** — one row per physical hospital, never changing when cohorts
rotate or trusts merge:

```
OrganisationEntity
  # The stable identity of a hospital, independent of cohort or ODS code.
  # One row per physical hospital, ever.
  current_ods_code: CharField  # the latest ODS code (for display/lookup)
  name: CharField              # current name (for display)
  successor_of: ForeignKey(self, null=True)  # links to predecessor entity
```

The existing models become per-cohort snapshots that point at the stable
entity:

```
Organisation  (per-cohort snapshot)
  entity: ForeignKey(OrganisationEntity)  # the stable hospital identity
  ods_code: CharField                     # the ODS code as of this cohort
  audit_period: ForeignKey(AuditPeriod)
  name, address, trust, icb, lhb, ...     # geography as of this cohort
  unique_together = (entity, audit_period)
```

User memberships point at `OrganisationEntity`, not at `Organisation`:

```
OrganisationEmployer  (existing through table, modified)
  epilepsy12_user: ForeignKey(Epilepsy12User)
  organisation_entity: ForeignKey(OrganisationEntity)  # was: organisation
  is_active: BooleanField
  is_rcpch_audit_team_member: BooleanField
```

When a trust merges mid-cohort:

1. The sync creates new `Organisation` rows for the new cohort (or
   updates the current cohort's rows if the merger happens mid-cohort).
2. The `OrganisationEntity` row is updated to point at the latest
   `Organisation` row (new ODS code, new trust).
3. **User memberships do not move** — they stay on the same
   `OrganisationEntity` row. The user automatically sees the new
   cohort's geography because the entity resolves to the latest
   `Organisation` row.
4. The user's sibling access is determined by the current cohort's trust
   — all `Organisation` rows in the current cohort whose `trust` matches
   the user's entity's current trust.

When a new cohort starts:

1. The sync creates new `Organisation` rows for the new audit period.
2. `OrganisationEntity` rows are updated to point at the latest
   `Organisation` rows.
3. **User memberships do not move** — no batch operation needed.

### How the PRUH edge case works with the intermediate model

```
OrganisationEntity(id=1, current_ods_code=RJZ30, name="Princess Royal University Hospital")

Organisation(entity=1, ods_code=RYQ30, audit_period=cohort_5, trust=RYQ/cohort_5)
Organisation(entity=1, ods_code=RJZ30, audit_period=cohort_6, trust=RJZ/cohort_6)
Organisation(entity=1, ods_code=RJZ30, audit_period=cohort_7, trust=RJZ/cohort_7)
```

The clinician's `OrganisationEmployer` points to `OrganisationEntity(id=1)`.
This never changes. When the clinician views cohort 5 data, the system
resolves `Organisation.objects.get(entity=1, audit_period=cohort_5)` →
`RYQ30` under `RYQ`. When viewing cohort 7 data, it resolves to `RJZ30`
under `RJZ`.

The clinician's sibling access is always against the current cohort:
all `Organisation` rows in the current cohort whose `trust` matches the
trust of the clinician's entity's current `Organisation` row. After the
merger, the clinician sees King's siblings (RJZ01 etc.), not South
London Healthcare siblings (QEH Woolwich, Lewisham).

The clinician retains access to their own organisation's historic cases
because `Site.organisation` can be resolved via the entity: all
`Organisation` rows for `entity=1` across all cohorts give the clinician
access to PRUH's data in every cohort.

### What changes in the operational code

| Code area | Change |
|---|---|
| Case creation | `Site.organisation` points to the current cohort's `Organisation` row. Lookup: `Organisation.objects.get(entity=entity, audit_period=current_cohort)`. |
| User permissions | `OrganisationEmployer.organisation` → `OrganisationEmployer.organisation_entity`. Sibling access: filter `Organisation` by current cohort + current trust. |
| Organisation selector | Dropdown shows `OrganisationEntity` rows (stable), resolved to current cohort's `Organisation` for display. |
| User access control (`sanction_user_access.py`) | Filter by entity's current trust, not by `Organisation.trust` directly. |
| KPI aggregation (`aggregate_by.py`) | Filter `Organisation`/`Trust` by `audit_period`. Direct FKs give correct geography. |
| Templates (`organisation.trust.name`) | Resolve via current cohort's `Organisation` row, or via a helper. |

### What does NOT change

- `Site`, `KPI`, `OrganisationalAuditSubmission` — these keep their FK
  to `Organisation` (the per-cohort row). Cases stay on the row they
  were created against.
- `AuditPeriod` — unchanged.
- `Country`, `OPENUKNetwork`, `NHSEnglandRegion` — these rarely change
  and are not versioned per cohort. They remain as current-state models.
  If a country or region ever needs versioning, the same pattern can be
  applied.

### Sync workflow

1. **Current-state sync** (existing, from the API's list endpoints) —
   upserts the latest cohort's `Organisation`, `Trust`, `ICB`, `LHB`
   rows. Also updates `OrganisationEntity.current_ods_code` and
   `OrganisationEntity.name` to the latest values.

2. **Per-cohort version sync** (new, from the API's `snapshot` endpoint)
   — for each audit period and each participating organisation, calls
   `GET /organisations/{ods_code}/snapshot/?date={reference_date}` and
   upserts the `Organisation`/`Trust`/`ICB`/`LHB` rows for that cohort.
   This is a batch operation run via a management command, not at
   request time.

3. **Succession sync** (new, from the API's succession data) — upserts
   `OrganisationEntity.successor_of` links so the system knows
   `RYQ30` and `RJZ30` are the same hospital.

### Database size

| Model | Rows per cohort | × 10 cohorts | Total |
|---|---|---|---|
| Organisation | ~350 | × 10 | 3,500 |
| Trust | ~250 | × 10 | 2,500 |
| ICB | ~42 | × 10 | 420 |
| LHB | ~7 | × 10 | 70 |
| OrganisationEntity | ~350 (one row per hospital, ever) | — | 350 |
| **Total** | | | **~6,850** |

This is tiny — no performance concern.

## Open questions

1. **What is the audit period's reference date for the snapshot call?**
   Candidate: `submission_deadline` or `data_collection_end_date`. This
   determines which trust/ICB is used for the whole cohort if a merger
   happens mid-cohort.

2. **Does `Site.organisation` need to change to `Site.organisation_entity`?**
   If `Site` keeps its FK to the per-cohort `Organisation` row, cases
   stay on the correct cohort's row automatically. But when a clinician
   views a historic cohort, the system needs to resolve the entity from
   the `Organisation` row. This is a simple FK traversal
   (`organisation.entity`) and doesn't require changing `Site`.

3. **Should `OrganisationEntity` carry the `OrganisationEmployer` link,
   or should `OrganisationEmployer` keep its FK to `Organisation` and
   be updated when cohorts rotate?**
   The entity approach avoids batch migrations. The direct approach is
   simpler but requires a migration step when a new cohort starts. The
   entity approach is recommended.

4. **What happens to the existing `OrganisationEmployer` data when this
   migration is applied?**
   Each existing `OrganisationEmployer.organisation` FK is resolved to
   an `OrganisationEntity` (one row per ODS code, created in the
   migration). The `OrganisationEmployer.organisation` FK is replaced
   with `OrganisationEmployer.organisation_entity`. This is a one-time
   data migration, not a recurring batch operation.

5. **Should the current-state `Organisation.trust` FK be kept for
   operational convenience, or removed in favour of the per-cohort
   rows only?**
   Keeping it means the operational code (organisation selector, user
   access) can use the current cohort's `Organisation` row directly.
   Removing it means all trust lookups go through the per-cohort rows.
   Keeping it is simpler for the operational code; the reporting code
   uses the per-cohort rows regardless.

6. **How are `NHSEnglandRegion` and `Country` handled?**
   These rarely change and are not versioned per cohort in this design.
   If an NHS England region or country ever needs versioning (e.g. a
   region boundary change), the same `audit_period` pattern can be
   applied later.

## Relationship to the public KPI reporting scope

This design replaces the "freeze geography onto the publication
snapshot" approach described in the public KPI reporting scope document.
Instead of calling the API `snapshot` endpoint at publication time and
freezing the result onto the publication, the per-cohort version rows
are the frozen snapshot — populated during sync, not at publication
time. Both the live dashboard and the public KPI report read the same
version rows.

The `organisation_geography_as_of()` function in the API client remains
useful for ad-hoc historical queries (e.g. "what was this org's
geography on this specific date?"), but the reporting infrastructure
uses the per-cohort rows, not live API calls.
