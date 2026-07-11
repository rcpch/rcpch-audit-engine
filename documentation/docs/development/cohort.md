---
title: Cohort
reviewers: Dr Simon Chapman
render_macros: true
---

## Cohorts

Cohorts are defined between 1st December year and 30th November in the subsequent year. Note, the final submission date
is the second Tuesday in January after the closing date 1 YEAR ON. So if the cohort closes on 30 Nov 22, the submission date is
the second Tuesday after 30/11/23, which is 9 Jan 24

Cohorts are defined as follows:

- **currently recruiting cohort**: this is the cohort that is currently recruiting patients
- **currently submitting cohort**: this is the cohort that is no longer recruiting patients but is still collecting data to complete a full year of care
- **grace cohort**: this cohort is also no longer recruiting patients but is still collecting data to complete a full year of care. This cohort is the one before the submitting cohort.

Time zone is not explicity supplied. Since this is a UK audit, time zone is assumed always to be UK.

### Examples of cohort numbers

- Cohort 4: 1 December 2020 - 30 November 2021: submission 10 January 2023
- Cohort 5: 1 December 2021 - 30 November 2022: submission 9 January 2024
- Cohort 6: 1 December 2022 - 30 November 2023: submission 14 January 2025
- Cohort 7: 1 December 2023 - 30 November 2024: submission 13 January 2026
- Cohort 8: 1 December 2024 - 30 November 2025: submission 12 January 2027

## Cohort-specific measures

This section is a policy review matrix. It focuses on which measures are intended to belong to which cohort, and which parts of the codebase still need a decision.

### Measure matrix

| Area | Measure / field | Current cohort policy in code | Review status |
|---|---|---|---|
| Multiaxial diagnosis | `syndrome_present` | Available in all cohorts | Keep |
| Multiaxial diagnosis | `epilepsy_cause_known` | Available in all cohorts | Keep |
| Multiaxial diagnosis | `epilepsy_cause_categories` | Available when cause is known, all cohorts | Keep |
| Multiaxial diagnosis | `epilepsy_cause` | Deprecated legacy FK, not part of scoring | Remove when migration is complete |
| Multiaxial diagnosis | `relevant_impairments_behavioural_educational` | Available in all cohorts | Keep |
| Multiaxial diagnosis | `autistic_spectrum_disorder` | Available in the form and currently not cohort-gated in scoring logic | Needs cohort decision |
| Multiaxial diagnosis | `mental_health_screen` | Available in the form and currently not cohort-gated in scoring logic | Needs cohort decision |
| Multiaxial diagnosis | `mental_health_issue_identified` | Available in the form and currently not cohort-gated in scoring logic | Needs cohort decision |
| Multiaxial diagnosis | `mental_health_issues` | Conditional on `mental_health_issue_identified`; not cohort-gated | Needs cohort decision |
| Multiaxial diagnosis | `global_developmental_delay_or_learning_difficulties` | Available in all cohorts | Keep |
| Multiaxial diagnosis | `global_developmental_delay_or_learning_difficulties_severity` | Conditional on `global_developmental_delay_or_learning_difficulties`; not cohort-gated | Keep |
| Investigations | `genome_sequencing_requested` | Cohort 8+ only | Keep |
| Investigations | `r14_test_status` / `r14_test_requested_date` / `r14_test_achieved_date` | Cohort 8+ only, conditional on genome sequencing request state | Keep |
| Investigations | `r27_test_status` / `r27_test_requested_date` / `r27_test_achieved_date` | Cohort 8+ only, conditional on genome sequencing request state | Keep |
| Investigations | `r59_test_status` / `r59_test_requested_date` / `r59_test_achieved_date` | Cohort 8+ only, conditional on genome sequencing request state | Keep |
| Management | `has_an_aed_been_given` | Available in all cohorts | Keep |
| Management | `has_rescue_medication_been_prescribed` | Available in all cohorts | Keep |
| Management | Care planning fields (`individualised_care_plan_*`) | Available in all cohorts, no cohort gate in code | Needs cohort decision |
| Medication risk | `has_a_valproate_annual_risk_acknowledgement_form_been_completed` | Cohort 6: valproate in females aged 12+; Cohort 7+: valproate, plus topiramate in females aged 12+ | Keep |
| Medication risk | `is_a_pregnancy_prevention_programme_needed` | Cohort 7+ eligibility only; tied to valproate/topiramate rules | Keep |
| Medication risk | `is_a_pregnancy_prevention_programme_in_place` | Cohort 7+ and only when PPP is indicated | Keep |

### Interpretation

- The codebase is already cohort-gated for genome sequencing and for KPI 8 medication/reproduction risk.
- The newer multiaxial diagnosis fields are currently present in the form and scoring constants, but they are not consistently cohort-gated everywhere. That is the main policy gap to resolve.
- Care planning is currently available to all cohorts; if that is not intended, it needs an explicit policy decision before changing the implementation.

### Review prompts

- Should `autistic_spectrum_disorder`, `mental_health_screen`, and `mental_health_issue_identified` be cohort 8+ only, or available in all cohorts?
- Should `mental_health_issues` be treated the same way as the parent mental health measure, or remain conditional only on `mental_health_issue_identified`?
- Should care planning stay available in all cohorts, or be gated from a specific cohort onward?
- Can `epilepsy_cause` be removed from docs and scoring references once the legacy path is fully retired?