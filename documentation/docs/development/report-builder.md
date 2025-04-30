---
title: Report Builder
reviewers: Dr Simon Chapman
---

## Report Builder

The Report Builder leverages facets to allow users to construct their own complex filter queries.

It is written with the 'django-filter` package though the facets are calculated within the filterset class.

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