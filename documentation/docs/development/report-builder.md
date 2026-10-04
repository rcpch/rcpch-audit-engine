---
title: Report Builder
reviewers: Dr Simon Chapman
---

## Report Builder

The Report Builder leverages facets to allow users to construct their own complex filter queries.

It is written with the 'django-filter` package though the facets are calculated within the filterset class.

### Current audit-period compatibility

The report builder currently keeps its existing route and all-period/current-hierarchy semantics. It does **not** use `AuditPeriod.slug` in the URL as part of the `AuditPeriodOrganisation` foundation work.

The foundation described in [Audit-period organisation membership and access](audit-period-organisation.md) should preserve the existing report-builder behaviour while the historical membership model, sync commands and permission vocabulary are added. In particular:

- the existing report-builder route remains unchanged;
- the legacy cohort filter remains available;
- hierarchy facets continue to use the current `Organisation` relationships until the report builder is deliberately refactored;
- tests should prove the existing route and representative facets still load after the foundation migrations; and
- links from report-builder results should continue to reach clinical views that derive their period from `Registration.audit_period`, not from a report-builder URL slug.

A future period-aware report-builder refactor may introduce a canonical route such as:

```text
/organisation/<organisation_id>/audit-periods/<audit_period_slug>/report-builder/
```

That future refactor should resolve the `AuditPeriod` from the slug before constructing the base queryset, filter cases through `Registration.audit_period`, and derive hierarchy facets from `AuditPeriodOrganisation`. It is intentionally separate from the foundation work.

### Structure

There is a `CaseFilter` filterset and a helper class, `CaseFilterMethods` for running all the queries. This is because some of the queries can then be used in the admin.

### Workflow for adding a new filter and facet

1. create a new field in `CaseFilter` and at it to the `Meta` class.
2. In the `CaseFilterMethods` class create `filter_by_{field}` and `get_{field}_counts` @staticmethod`s.
3. Add a call to the filter query in `apply_all_active_filters` in `CaseFilterMethods`.
4. Add a method to the `get_context_data` method in `CaseListView`: this should either pass the `get_{field}_counts` dictionary to the template to be deconstructed into individual keys with labels for the counts which are clickable and apply the key to the query get parameters, or it should pass a list of choices to be used in a select. The select choices have to be built in a loop as the django basic select will not otherwise include the facet counts.

for example:

```python
# Add ethnicity facets to dropdowns
    ethnicity_counts = CaseFilterMethods.get_ethnicity_counts(filtered_queryset)
    ethnicity_choices = [("", "All")]
    for ethnicity_code, label in ETHNICITIES:
        count = ethnicity_counts.get(ethnicity_code, 0)
        ethnicity_choices.append((f"{ethnicity_code}", f"{label} ({count})"))
    context["ethnicities"] = ethnicity_choices
```

vs

```python
context["registered_cases"] = CaseFilterMethods.get_registration_status_counts(
            filtered_queryset, "registered"
        )
        context["unregistered_cases"] = (
            CaseFilterMethods.get_registration_status_counts(
                filtered_queryset, "unregistered"
            )
        )
```

If you add the name of the field to the `special_filters` list in the `CaseListView` it must follow that pattern `filter_by_{field}` and `get_{field}_counts` and the filter must accept a parameter in the url.