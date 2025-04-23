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