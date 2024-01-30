---
title: Dropdowns
reviewers: Dr Simon Chapman
---

## Lists

Lists that feed either the toggle buttons or the select dropdowns are either found in the `constants` folder, or are seeded to the database in the `migrations`.

**Organisation** lists are seeded from `constants` as are the levels of abstraction associated with them (trust, ICB etc.) 

The **Epilepsy causes** and **comorbidities**, by contrast are a SNOMED refset seeded from the RCPCH SNOMED server in migration 0006 and 0009 into EpilepsyCause and ComorbidityList respectively.

**Syndromes** are from lists in the `constants` folder.

**Epilepsy medicines** (both rescue and not) are found in the `constants` folder but look up the full SNOMED concept from the RCPCH SNOMED server before saving in the Medicine table.

**Semiology Keywords**, used to categorize words in the free text descriptions of a seizure event, are taken from a list in the `constants` folder.

The tables that supply the dropdowns are seeded in the migrations which is a recommended way in the [Django documentation](https://docs.djangoproject.com/en/5.0/topics/migrations/#data-migrations) to add data, known as data migrations.

Since go-live, E12 have wished on the basis of user feedback, from time to time to add new items to these lists. The process for adding new items should be:

### EpilepsyCause

1. Epilepsy12 team to supply the SNOMED CT ID (SCTID) of the concept
2. The development team add the SCTID to the list `extra_concept_ids` in migration 0006 for future seeding from scratch, mostly for development reasons
3. In the python shell to run the seed function:

```console
python manage.py --mode=add_new_epilepsy_causes -sctids 764946008 52767006
```

Note that the function expects a list, even if only one item is supplied.

<!-- There will need to be further documentation added here for new organisations and trust, as well as new comorbidities, and possibly medications and so on. For now, this is the workflow for EpilepsyCauses -->

### Organisations

Just updating the `RCPCH_ORGANISATIONS` constant will not in itself update the database, but is a necessary step in the process. The workflow needs to be:

#### Deleting an organisation

1. check there are no children associated with this organisation. If there are, it must not be deleted
2. Delete the organisation in the admin. This will delete any relationships it also has with associated trusts/health boards etc as well KPIAggregation models

#### Updating an organisation

This can be done reasonably straightforwardly in the admin. Note that the ODS Code is a unique identifier and if the update includes an update to this, you are in effect creating a new organisation, rather than editing an existing one. Better therefore to create a new organisation and delete the old. This becomes more complicated if there are children associated with this organisation.

#### Adding a new organisation

This can be done in the admin. The ODS Code must be unique. The name and ODS code should ideally be mandatory fields but are not currently prescribed as such in the model. Note that you must also allocate the Trust/Health Board, ICB, NHS England Region, London Borough and Country.
Add the same details to the `RCPCH_ORGANISATIONS` constant. This is necessary later when seeding the KPI Aggregation models
in the shell:

```console
from epilepsy12.common_view_functions import _seed_all_aggregation_models
_seed_all_aggregation_models()
```
