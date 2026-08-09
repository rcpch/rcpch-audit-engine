---
title: Public KPI reporting — feature scope
reviewers: Dr Simon Chapman
---

# Public KPI reporting — feature scope

!!! note "Document status"
    Draft for review. This document scopes a new public reporting feature that will replace the existing Power BI report. It describes the intended product, data, publication and technical boundaries; it is not an implementation specification.

## Executive summary

Epilepsy12 will provide a public, longitudinal KPI reporting area within the Django application. It will replace the existing Power BI report as the public source of published KPI results.

The report will:

- report KPI totals and percentages across published audit periods;
- support national, country and sub-national geographical levels down to Trust or Local Health Board level;
- use `AuditPeriod.slug` in all report URLs;
- include only organisations participating and active in the relevant audit period when calculating results;
- be separate from the authenticated, organisation-scoped dashboard;
- use manually generated, immutable publication snapshots rather than query live clinical records;
- resolve organisational and geographical reference data (including history and mergers) from the `rcpch-nhs-organisations` API `snapshot` endpoint, and boundaries from `rcpch-census-platform`, freezing both onto each publication snapshot;
- initially be published manually, with a design that can support monthly publication later; and
- use a dedicated public base template and navigation.

The first release will contain KPI results only. Organisation-level demographics, patient maps and travel data will remain in the authenticated organisation dashboard. National demographic summaries may be added in a later phase.

## Background

The authenticated organisation dashboard reports live KPI and demographic information for a selected organisation and its related geographies. The existing Power BI report separately publishes audit results to the public.

The replacement public report is not a public version of the organisation dashboard. It is an audit-wide reporting product whose primary purpose is to:

1. show how KPI performance changes between audit periods;
2. show results at different geographical levels; and
3. provide a stable, shareable and reproducible view of each published dataset.

The application already contains useful foundations:

- `AuditPeriod`, including a unique `slug` and authoritative audit dates;
- KPI scores associated with registrations;
- aggregation models for the existing levels of abstraction;
- KPI labels, definitions and help text;
- stable codes for organisations and geographical entities;
- a permission for publishing Epilepsy12 data; and
- an incomplete `open_access` publication workflow.

The organisational and geographical reference data currently held in this project (`Organisation`, `Trust`, `LocalHealthBoard`, `IntegratedCareBoard`, `NHSEnglandRegion`, `OPENUKNetwork` and their boundaries) is being superseded. The `rcpch-nhs-organisations` API now maintains organisations, their hierarchy and their history (including mergers and ODS code successions) as the source of truth, and `rcpch-census-platform` maintains boundaries. This project mirrors that data, kept in sync with the API.

These foundations should be reused where appropriate, but the public report must not depend directly on live clinical tables.

## Goals

### Product goals

- Replace the KPI data currently published through Power BI.
- Allow members of the public to compare published KPI performance longitudinally.
- Allow users to move between national, country and sub-national views.
- Present both the numerator/denominator totals and the resulting percentage.
- Give every published report a stable URL that can be shared or cited.
- Make the presentation responsive, accessible and understandable without reproducing the Power BI design.
- Make publication a controlled and auditable operation for the RCPCH audit team.
- Support silent corrections without changing public URLs.
- Prepare the publication process for an eventual monthly schedule.

### Technical goals

- Make `AuditPeriod` the authoritative period identifier throughout reporting.
- Produce an internally consistent, atomic snapshot for each publication.
- Keep anonymous requests isolated from patient-level and live clinical data.
- Reuse the established KPI scoring definitions rather than implementing a second set of KPI rules.
- Represent publication history explicitly so that corrections and future automation are safe.
- Keep the internal live dashboard and public published report as separate consumers of shared reporting calculations.

## Non-goals for the first release

The initial feature will not include:

- organisation-level public reports;
- organisation-level demographic summaries;
- patient locations, patient maps or travel-distance information;
- national age, sex or ethnicity summaries;
- a pixel-for-pixel recreation of the Power BI user interface;
- live or provisional results visible to anonymous users;
- automatic scheduled publication; or
- a general-purpose public API unless a separate requirement is agreed.

The authenticated organisation dashboard will continue to provide its existing organisation-specific demographics and mapping features.

## Reporting levels

The lowest public reporting level will be Trust or Local Health Board. Organisation-level results will not be published by this feature.

The intended reporting dimensions are:

| Level | Scope | Notes |
|---|---|---|
| National | All participating countries and islands | Must include England, Wales, Jersey and the Isle of Man where they participate in the audit. |
| Country | One result per participating country or island | England, Wales, Jersey and the Isle of Man are separate country-level results. |
| NHS England Region | England | Applies only where a participating organisation has this relationship for the audit period. |
| Integrated Care Board | England | Applies only where a participating organisation has this relationship for the audit period. |
| OPEN UK network | Cross-cutting network geography | This is a comparison dimension rather than a strict parent in the administrative hierarchy. Inclusion of Channel Island organisations in network results must be explicitly agreed. |
| Trust | Primarily England and any other jurisdiction represented through a Trust | Lowest public English reporting level. |
| Local Health Board | Wales | Lowest public Welsh reporting level. |

The public reporting hierarchy should not assume that every level applies to every country. The user interface should present only valid levels and entities for the selected context.

### Change to current “National” semantics

The existing `NationalKPIAggregation` is described in code as England and Wales and the current aggregation filter explicitly excludes Jersey. The new public report's national result has different semantics: it includes all participating countries and islands, including Jersey and the Isle of Man.

This difference must be represented deliberately and covered by tests. Existing exports or internal reports that still require an England-and-Wales result must not silently change meaning as an accidental side effect.

The repository currently contains explicit Jersey support, but equivalent Isle of Man data was not identified during this scoping review. Country, organisation and parent-geography reference data for the Isle of Man will need to be verified or added before the Isle of Man can contribute to a publication.

## Audit periods and URLs

### `AuditPeriod` is authoritative

Public report views and aggregation services must resolve the period from `AuditPeriod.slug` and retain the resulting `AuditPeriod` instance throughout the request or publication operation.

Reporting queries should filter through `Registration.audit_period`, not reconstruct an integer cohort and then rely primarily on the legacy `Registration.cohort` field.

This allows the report to use the period's:

- stable slug;
- display name;
- cohort number, where it remains useful to users;
- recruitment dates;
- data collection dates;
- submission deadline; and
- future period-specific reporting configuration.

### Proposed URL structure

The final prefix can be agreed during implementation, but the route structure should follow this shape:

```text
/reports/epilepsy12/
/reports/epilepsy12/<audit_period_slug>/
/reports/epilepsy12/<audit_period_slug>/national/
/reports/epilepsy12/<audit_period_slug>/countries/<country_code>/
/reports/epilepsy12/<audit_period_slug>/nhs-regions/<region_code>/
/reports/epilepsy12/<audit_period_slug>/icbs/<icb_code>/
/reports/epilepsy12/<audit_period_slug>/open-uk-networks/<network_code>/
/reports/epilepsy12/<audit_period_slug>/trusts/<trust_code>/
/reports/epilepsy12/<audit_period_slug>/local-health-boards/<lhb_code>/
```

`/reports/epilepsy12/` may redirect to the latest published audit period. It must not select an unpublished period merely because that period is currently recruiting or submitting.

The period slug must always be present in canonical report URLs. Stable external codes should be used for geographical entities instead of database primary keys.

A selected KPI or display mode may be represented with query parameters where useful, for example:

```text
/reports/epilepsy12/cohort-7/trusts/RGT/?measure=epilepsy-specialist-nurse
```

This makes specific report states shareable without treating every visualisation choice as a distinct resource.

### Longitudinal behaviour

The audit period in the path is the report's anchor period. A longitudinal chart may include that period and other published periods available for the selected KPI and geography.

The interface should make the included periods explicit. It must not combine draft data with published data or infer a period from today's date.

Where an organisation has changed ODS code between periods (for example following a trust dissolution and redistribution), the longitudinal series should follow the physical hospital across the code change. The `rcpch-nhs-organisations` API `snapshot` endpoint walks the `OrganisationSuccession` chain automatically and returns the predecessor's geography for dates before the organisation's current ODS code existed, so this project does not need to implement chain-walking itself. The interface should not silently drop earlier periods or treat the predecessor and successor as unrelated entities.

## Source of truth for organisations and geography

Organisational and geographical reference data is maintained outside this project:

- **Organisations, Trusts, Local Health Boards, ICBs, NHS England regions, OPEN UK networks and PDUs** — including their history, mergers and succession — are the responsibility of the `rcpch-nhs-organisations` API. That service maintains a temporal history layer and exposes a snapshot endpoint that this project consumes:

    ```text
    GET /organisations/{ods_code}/snapshot?date=YYYY-MM-DD
    ```

    The endpoint returns the full geography of an organisation as it was on the given date — name and address, plus the Trust / Local Health Board / ICB / NHS England region / OPEN UK network / PDU it belonged to on that date. If the organisation did not yet exist on that date (for example because its ODS code was introduced by a merger), the endpoint walks the `OrganisationSuccession` chain to the predecessor and returns the predecessor's geography. The internal mechanics of the temporal layer (`*Version`, `*Membership` and `*Succession` tables with `[valid_from, valid_to)` intervals) are owned by the API and are not duplicated here.

- **Geographical boundaries** (Trust, LHB, ICB, region, OPEN UK, London borough, LAD, LSOA geometries) are the responsibility of the `rcpch-census-platform` service.

This project retains its existing `Organisation`, `Trust`, `LocalHealthBoard`, `IntegratedCareBoard`, `NHSEnglandRegion` and `OPENUKNetwork` models as a **synchronised mirror** of the API rather than the source of truth. The local models remain FK targets for clinical data (`Site`, `KPI`, etc.) and serve the live dashboard; the API is the source of truth for organisational state, history and mergers. Mergers, reorganisations and ODS code changes are made in the API first and flow down into this project via sync; they are no longer authored here. The existing direct ODS sync in `epilepsy12/general_functions/ods_update.py` is retired in favour of the API sync.

The public report must not depend on the API being available at request time. Geography is resolved against the API `snapshot` endpoint (or the local mirror) at **publication time** and frozen onto the publication snapshot; anonymous public views read only the frozen snapshot.

## Active organisations for an audit period

The current `Organisation.active` boolean represents current operational status; it cannot reliably answer whether an organisation was participating and active in a historical audit period.

A period-aware source of truth is therefore required. The recommended approach is an explicit relationship such as an `AuditPeriodOrganisation` participation model, with one row per organisation and audit period. The exact model name is not prescribed by this scope.

The relationship should be able to record at least:

- the `AuditPeriod`;
- the `Organisation`;
- whether the organisation is included in reporting for that period; and
- audit fields explaining who changed the status and when.

It does **not** need to record geography. Period geography is resolved from the `rcpch-nhs-organisations` API `snapshot` endpoint at the audit period's reference date (see [Source of truth for organisations and geography](#source-of-truth-for-organisations-and-geography)) and frozen onto the publication snapshot. The participation model is concerned only with the RCPCH audit-team decision that the API cannot answer: whether the organisation was enrolled and in scope for the audit period.

At publication time, the release must snapshot the set of included organisations and their geographical memberships as resolved from the API `snapshot` endpoint at the period's reference date. This prevents later organisational changes from rewriting the meaning of an already published result.

### Proposed aggregation inclusion rule

A case may contribute to a published aggregation only when all applicable conditions are met:

1. its registration belongs to the selected `AuditPeriod`;
2. it satisfies the established KPI completion and eligibility rules;
3. the relevant site is the primary centre and actively involved in epilepsy care, consistent with the KPI methodology; and
4. the site's organisation is included as an active participant for that `AuditPeriod`.

The audit team must approve the precise operational meaning and source of “active for the audit period” before implementation. It should not be derived retrospectively from the current value of `Organisation.active` alone.

Although organisations determine which cases contribute to aggregates, organisation-level result rows will not be exposed in the public report.

## KPI data and longitudinal comparability

### Published values

For every KPI, audit period and reported geography, the publication should retain enough information to show and validate:

- passed count (numerator);
- total eligible count (denominator);
- percentage passed;
- ineligible count;
- incomplete or unscored count; and
- total cases included in the aggregation.

The primary public presentation will show the numerator, denominator and percentage. Ineligible, incomplete and total-included counts may be shown in detailed tables, downloads or methodology views as agreed during design.

Percentages should be derived consistently from the published counts. If a percentage is persisted for performance, publication validation must confirm that it matches the numerator and denominator.

Zero eligible cases, unavailable data and genuinely zero performance are distinct states and must not be displayed as if they are equivalent.

### KPI definitions can change between periods

KPI definitions are audit-period aware; for example, the medication and reproduction risk measure changed after cohort 6. A longitudinal report must therefore publish or reference the definition and label applicable to each `AuditPeriod`.

A trend may connect periods only where the measure remains meaningfully comparable. Where a definition changes materially, the interface should mark the change rather than imply an uninterrupted like-for-like series.

### Data parity with Power BI

The replacement does not need to copy Power BI's visual design. It must reproduce and validate the KPI data currently provided there, subject to the revised national inclusion rule and any explicitly approved methodology changes.

Before launch, representative results should be reconciled against the existing Power BI output at every supported abstraction level and for multiple audit periods. Differences must be explained and signed off rather than assumed to be presentation differences.

## Publication model

### Why `open_access` is insufficient on its own

The existing aggregation rows have an `open_access` boolean. When `open_access=True`, new rows are created and consumers select the most recently updated row independently at each abstraction level.

That does not identify which rows belong to one coherent release. It can therefore produce a public response containing Trust, regional and national results generated by different publication actions.

A publication must be an explicit object that groups all of its results atomically.

### Recommended publication entity

Introduce a release entity, provisionally named `KPIReportPublication`, associated with exactly one `AuditPeriod`.

It should record:

- audit period;
- status, such as generating, draft, ready, published, failed or superseded;
- generation start and completion timestamps;
- source-data cutoff timestamp;
- publication timestamp;
- generating and publishing users;
- validation outcome;
- optional internal notes or release notes; and
- whether it is the currently active publication for its audit period.

Only one publication may be publicly active for an audit period at a time. Previous versions should be retained internally for audit, diagnosis and rollback even though corrections can silently replace the public version.

### Published results

The public snapshot should store results against the publication rather than exposing live `Case`, `Registration` or `KPI` rows.

A generic, reporting-oriented result shape is recommended:

- publication;
- abstraction level;
- stable geography code;
- snapshot geography name;
- KPI code;
- numerator/passed count;
- denominator/eligible count;
- ineligible count;
- incomplete count; and
- total included count.

A tall result table is likely to be easier to query longitudinally and extend than adding new columns to several wide aggregation models whenever KPI definitions change. This choice should be confirmed in the implementation design after measuring the size and query patterns of real publications.

A companion geography snapshot must retain the names, codes and parent relationships that applied at publication time. This snapshot is fetched from the `rcpch-nhs-organisations` API `snapshot` endpoint at the audit period's reference date (one `snapshot` call per included organisation) and frozen onto the publication; it is not re-derived from the local `Organisation` FKs, which may have been overwritten by a later merger. The reference date per `AuditPeriod` must be chosen and documented before publication begins (see [Decisions still required](#decisions-still-required)).

### How to reuse `open_access`

The existing concept can be repurposed, but the boolean should not remain the public report's sole integrity or access mechanism.

Recommended reuse:

- retain the existing publication permission;
- reuse and refactor the established KPI calculation functions;
- reuse historical `open_access=True` rows as a migration or reconciliation source where they are trustworthy; and
- keep `open_access` temporarily for compatibility with the existing dashboard while the old incomplete flow is retired.

The new public views should require an active `KPIReportPublication` and should never infer publication merely from `open_access=True`.

## Publication workflow

Publication is audit-period-wide, not organisation-scoped.

The current publish button on the organisation dashboard should not be the long-term entry point. Publication should have a dedicated RCPCH audit-team screen.

### Initial manual workflow

1. An authorised user selects an `AuditPeriod` by name/slug.
2. The system establishes the period's included organisations and snapshots their relevant geography memberships.
3. The system calculates KPI results once for every applicable public geography.
4. Results are attached to a new draft publication.
5. Automated validation checks run.
6. The user previews a summary of the publication and any warnings.
7. The user confirms publication with a CSRF-protected POST action.
8. In one atomic operation, the new publication becomes active and the previous active publication for that period becomes superseded.
9. Public caches for that audit period are invalidated.

If generation or validation fails, the current public publication remains unchanged.

### Silent corrections

A correction creates a new publication version for the same `AuditPeriod` and promotes it at the existing URLs. Public URLs do not change and do not need to display a correction history.

For governance and rollback, superseded versions should remain visible to authorised staff with their timestamps and publishing users.

### Future monthly publication

The same release service should later be invokable by a scheduler. Scheduling should automate generation, not weaken validation or atomic activation.

A later workflow may either:

- generate a monthly draft for manual approval; or
- generate and publish automatically after agreed validation gates.

This policy can be decided separately. The initial implementation should avoid embedding publication logic solely inside an HTTP view so it can be called safely by either a staff action or a future scheduled task.

## Validation before publication

A draft publication should not become active until automated checks have completed. At minimum, validate that:

- the `AuditPeriod` exists and has a slug;
- at least one organisation is included for the period;
- every result belongs to the selected audit period and publication;
- required national and country results are present;
- all expected public geographies represented by participating organisations have result rows;
- no organisation-level result is exposed by the public dataset;
- numerators do not exceed denominators;
- no stored counts are negative;
- calculated percentages match published counts;
- duplicate geography/KPI rows do not exist within the publication;
- the national result includes all and only participating countries and islands;
- rows from a different publication cannot be mixed into the release; and
- no patient identifiers or patient-level values are present.

Validation should produce a staff-readable summary including result counts, included organisations, included countries and any missing geography relationships.

## Public user experience

The public area will use a dedicated base template rather than `templates/base.html`. It should not include authenticated navigation, automatic logout behaviour or internal organisation autocomplete assumptions.

The public base should provide:

- RCPCH/Epilepsy12 identity;
- public report navigation;
- accessibility and methodology links;
- publication and data-coverage information;
- responsive chart and table assets; and
- no controls that imply access to live patient data.

### Suggested report structure

#### Report landing page

- latest published audit period;
- audit-period selector containing only periods with a public publication;
- explanation of what the report contains;
- links to national results, geographical exploration, methodology and downloads; and
- publication date and source-data cutoff.

#### KPI overview

- one row or card per KPI;
- selected audit period's national result;
- numerator, denominator and percentage;
- clear unavailable/zero-denominator states; and
- links to a KPI detail view.

#### KPI detail

- KPI definition applicable to the selected period;
- longitudinal line or point chart across published periods;
- accessible tabular equivalent with numerator, denominator and percentage;
- geography-level selector;
- geography/entity selector; and
- a clear marker where the KPI definition changed.

#### Geographical comparison

- comparison of entities at the same level for the selected audit period and KPI;
- sortable accessible table as the canonical representation;
- optional bar, dot or funnel-style visualisation; and
- links from a country or region to applicable lower levels.

The exact visual design should be developed using current RCPCH branding and accessibility standards rather than inherited from Power BI.

### Downloads

A CSV download is desirable for parity, accessibility and independent analysis. Any download must be generated from the same publication snapshot as the page, not by rerunning live queries.

Download URLs should also include the `AuditPeriod.slug`. A combined longitudinal download can be added if it is needed for initial Power BI parity.

## Disclosure and privacy boundary

The public feature will expose aggregated KPI totals and percentages only. It will not expose organisation-level demographics, patient locations or patient-level records.

The lowest result level is Trust or Local Health Board. A formal decision is still required on whether small numerators or denominators at those levels need suppression or rounding. The data model should be capable of representing a suppressed value and suppression reason even if the initial approved policy permits all totals to be displayed.

Anonymous public requests must query only active publication snapshots and safe geographical reference data. They must not execute reporting queries against live `Case`, `Registration`, `Site` or `KPI` records.

## Future national demographics

National age, sex and ethnicity summaries are explicitly outside the first KPI release.

When demographics are added, age must be calculated at a fixed audit event rather than from the current date. The likely reference is age at registration or first paediatric assessment, using dates associated with the registration and its `AuditPeriod`. The clinical/reporting team must choose and document the exact reference event before demographic aggregation is implemented.

Published demographic groups will require the same period-aware participation rules, atomic publication process and disclosure review as KPI results.

## Caching and performance

Public report pages are strong candidates for caching because publication snapshots do not change between releases.

The implementation may cache:

- complete report responses;
- serialised chart payloads;
- lists of published audit periods and geographies; and
- downloadable files.

Cache keys must include the active publication identifier, not only the audit-period slug, so silent corrections take effect immediately after invalidation.

Aggregation performance should be measured using production-scale data. The initial manual process may run synchronously if it completes reliably within operational limits. A background-task dependency should be introduced only if measurements or the future scheduling implementation justify it.

Publication-time geography snapshot ingestion makes one `rcpch-nhs-organisations` API `snapshot` call per included organisation. For a full audit this is a few hundred sequential HTTP calls and should be measured early; if it is too slow it can be parallelised or run against the local mirror rather than the live API. Either way the frozen snapshot, not the API, serves public page views.

## Relationship with the internal dashboard

The internal and public dashboards have different data guarantees:

| Internal organisation dashboard | Public KPI report |
|---|---|
| Authenticated and permission-scoped | Anonymous |
| Organisation-centred | Audit-wide and geography-centred |
| Live/provisional calculations | Published snapshots only |
| Includes organisation demographics and maps | KPI results only in the first release |
| May display organisation results | Lowest level is Trust/LHB |
| Operational refresh actions | Controlled audit-period publication |

They should share tested KPI inclusion and aggregation services where their methodologies are identical. They should not share view-level access logic or templates in a way that risks exposing live data.

## Testing strategy

### Calculation tests

- Every KPI publishes the expected numerator and denominator.
- Eligibility, ineligibility and incomplete states match existing KPI definitions.
- Results are filtered through `Registration.audit_period`.
- Only period-active organisations contribute.
- National results include England, Wales, Jersey and the Isle of Man when those countries participate.
- Country and lower-level results contain only their contributing cases.
- Trust and LHB results are the lowest generated public levels.
- Organisation result rows are not generated for public consumption.
- KPI definition changes between periods are represented correctly.
- Geography assigned to each organisation at publication time matches the API `snapshot` response at the period's reference date, not the current local FK.

### Publication tests

- A complete release is activated atomically.
- A failed generation leaves the previous publication active.
- Only one active publication exists for an audit period.
- A correction supersedes the previous publication without changing public URLs.
- Rows from separate publications cannot be mixed.
- Publishing requires the existing or successor publication permission.
- State-changing publication requests are POST-only and CSRF-protected.

### Public view tests

- Published pages are accessible without authentication.
- Unpublished and invalid audit-period slugs return an appropriate 404 response.
- Canonical URLs contain the `AuditPeriod.slug`.
- Database primary keys are not used as public geography identifiers.
- Only geographies present in the active publication can be requested.
- Public views do not query patient-level tables.
- Pages and downloads use the same publication version.
- Zero denominator, unavailable and zero percent are rendered distinctly.

### Reconciliation tests

- Selected publications reconcile with Power BI at national, country, regional and Trust/LHB levels.
- Expected differences caused by the new Channel Islands national definition are documented.
- CSV totals reconcile with the corresponding visible report.
- The geography snapshot frozen onto each publication reconciles with the `rcpch-nhs-organisations` API `snapshot` response at the period's reference date.
- The local mirror tables (`Organisation`, `Trust`, etc.) reconcile with the API after sync.

### Accessibility tests

- All charts have equivalent data tables.
- Report controls are keyboard accessible and labelled.
- Colour is not the sole means of conveying performance.
- Tables remain usable on narrow screens and with screen readers.

## Proposed delivery phases

### Phase 0 — Methodology and data inventory

- Inventory the KPI datasets and filters currently represented in Power BI.
- Confirm active-organisation **participation** rules for each historical audit period (the RCPCH audit-team decision; geography is the API's responsibility).
- Confirm OPEN UK inclusion rules for Jersey and the Isle of Man, and confirm the `rcpch-nhs-organisations` API holds the corresponding OPEN UK network memberships for the relevant organisations and audit periods (verifiable via the `snapshot` endpoint at each period's reference date).
- Confirm the `rcpch-nhs-organisations` API has backfilled temporal geography for every E12-participating organisation across every audit period to be published. **This is a hard gate:** Phase 1 must not start until coverage is confirmed. Verification is by calling the `snapshot` endpoint at each period's reference date for every participating organisation and confirming a non-404 response with the expected geography.
- Confirm Isle of Man reference data exists in the API (organisations, country, parent geography) and is returned by the `snapshot` endpoint for the relevant audit periods. The Isle of Man may not be in the ODS feed; verify how it is represented.
- Choose and document the per-`AuditPeriod` geography reference date used for snapshot calls (likely `submission_deadline` or `data_collection_end_date`).
- Confirm the small-number disclosure policy.
- Identify KPI definition changes that affect longitudinal comparability.
- Produce reconciliation fixtures for representative Power BI results.

### Phase 1 — Publication foundation

- Add period-aware organisation **participation** (participation only; no geography on this model).
- Add explicit publication and published-result storage.
- Add publication-time geography snapshot ingestion: for each included organisation, fetch its `snapshot` from the `rcpch-nhs-organisations` API `snapshot` endpoint at the period's reference date and freeze the result onto the publication.
- Replace the local direct ODS sync (`epilepsy12/general_functions/ods_update.py`) with synchronisation from the `rcpch-nhs-organisations` API, so that mergers and reorganisations made in the API flow down into the local `Organisation` / `Trust` / `IntegratedCareBoard` / `NHSEnglandRegion` / `OPENUKNetwork` / `LocalHealthBoard` mirror tables. The local models remain for now as a mirror, not the source of truth.
- Refactor shared KPI aggregation into a service callable outside an HTTP view.
- Generate all public abstraction levels for one `AuditPeriod`.
- Add validation, preview, activation and supersession.
- Retire or redirect the organisation-dashboard publish action.
- Keep the existing public version live if a new generation fails.

### Phase 2 — Public longitudinal KPI report

- Add dedicated public base template and routing.
- Add published audit-period navigation using slugs.
- Add national KPI overview.
- Add country, network, region, ICB, Trust and LHB exploration where applicable.
- Add KPI longitudinal charts and accessible tables, using the `OrganisationSuccession` chain walked by the API `snapshot` endpoint to align a hospital's results across ODS code changes between periods.
- Add publication metadata, methodology and CSV downloads.
- Reconcile results with Power BI before launch.

### Phase 3 — Operational hardening and monthly publication

- Profile and optimise generation and public query performance.
- Add caching and cache invalidation tied to publication activation.
- Add scheduled monthly draft generation or publication.
- Add monitoring and failure notifications.
- Document correction and rollback procedures for audit staff.

### Phase 4 — National demographics

- Agree fixed age reference event.
- Define national sex, age and ethnicity groupings.
- Agree disclosure rules.
- Add demographic aggregations to the same publication lifecycle.

## MVP acceptance criteria

The first public release is complete when:

1. a permitted audit-team user can generate and publish a complete KPI snapshot for a selected `AuditPeriod`;
2. publication is atomic and a failed replacement cannot alter the current public report;
3. the canonical public URLs use `AuditPeriod.slug`;
4. anonymous users can view numerator, denominator and percentage for every published KPI;
5. users can view longitudinal results across published audit periods;
6. users can explore applicable levels from national and country down to Trust/LHB;
7. national results include all participating England, Wales, Jersey and Isle of Man data;
8. only organisations active for the relevant audit period contribute to calculations;
9. no organisation-level public results, demographics, maps or patient-level data are exposed;
10. a correction can replace the active publication at the same public URL;
11. report tables remain usable without charts or JavaScript; and
12. agreed sample results reconcile with Power BI or have a documented, approved reason for differing.

## Decisions still required

The following decisions remain before implementation can be considered fully specified:

1. What system or staff workflow defines that an organisation is active and participating in a particular `AuditPeriod`? (Participation only — geography is resolved from the API.)
2. Should Jersey and the Isle of Man contribute to their assigned OPEN UK network results, or only to country and national results?
3. What small-number suppression or rounding rules apply at Trust/LHB level?
4. Which Power BI KPI downloads and filter combinations are required for launch parity?
5. Should `/reports/epilepsy12/` redirect to the latest publication or present an audit-period index?
6. Which KPI definition changes should break a trend line rather than be shown with an annotation?
7. Is initial publication generation fast enough to remain synchronous, or does it need a background worker?
8. What is the per-`AuditPeriod` geography reference date used for API `snapshot` calls? (Candidate: `submission_deadline` or `data_collection_end_date`.)
9. Does the local mirror sync from the API run on a schedule, on demand at publication time, or both? What is the target latency between a merger being recorded in the API and the local mirror reflecting it?
10. Confirm the boundary geometries required for the public report are available from `rcpch-census-platform` for every geography level and audit period to be published.

These decisions do not alter the central architecture: public results are versioned snapshots tied to an `AuditPeriod`, generated across the whole audit and activated atomically. Organisational and geographical reference data is sourced from the `rcpch-nhs-organisations` and `rcpch-census-platform` services; this project mirrors it, kept in sync with the API.
