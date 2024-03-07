---
title: Reporting
reviewers: Dr Simon Chapman
---

Reporting is the principle reason for the Epilepsy12 Audit - to provide patients, their families and the teams caring for them meaningful information about the standard of their care. A secondary aim of the audit is to provide clinicians and hospital manager teams with real time information, filtered to their organisation, on their performance against the indicators, as well as other descriptors of their clinic - for example demographic information and case mix. Whilst it is not a clinical tool, it is meant to be used and updated in a clinical setting, and allow multidisciplinary teams to view the dashboard together at intervals and reflect on their service.

## Filtering and aggregation

Each time a measure in the audit is scored for a given child, the KPIs are rescored for that child and stored in the KPI model.

For the purposes of reporting, a summary of all KPIs for a given cohort are needed at different 'levels of abstraction'. Users are interested not only in how the child's care has performed against the national standard, but also how all the children in their organisation and trust compare with the rest of their integrated care board, NHS England Region or local health board. The functions for first filtering all the children for a particular cohort and level of abstraction are found in ```/common_view_functions/report_queries.py```. The KPI scores for these children are then aggregated in ```/common_view_functions/aggregate_by.py```. 
