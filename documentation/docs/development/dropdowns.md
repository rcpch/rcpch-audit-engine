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

Workflow to add a new cause:

1. Navigate to the SNOMED CT browser: https://browser.ihtsdotools.org/ and search for the cause and get the SCTID
2. Add the SCTID to the `extra_concept_ids` list in `migrations/0006_seed_epilepsy_causes.py` together with the appropriate name in the comments as a fallback Should include the SCTID, the term and the preferred term
3. if the cause is not in the SNOMED CT server, add it manually to the `extra_causes_without_concept_ids` list in `migrations/0006_seed_epilepsy_causes.py`. Should include the term and the preferred term, with the `conceptId` provided as `None`.
eg: `extra_causes_without_concept_ids = [...., {"preferredTerm": "Cause name", "term": "Cause name"}]`
4. REMEMBER: adding causes here will not add them to the database, and is only for reference should the database be reseeded
5. To add the causes to the database depends on whether the cause has an SCTID or not:
    - If the cause has an SCTID, on the command line in the epilepsy12 app, run the command:
    `python manage.py seed --mode=add_new_epilepsy_causes -sctids <list of SCTIDs>`
    [e.g. `python manage.py seed --mode=add_new_epilepsy_causes -sctids 764946008 52767006`]
    - if the cause does not have an SCTID, use the django shell:
  
        ```console
        python manage.py shell
        from epilepsy12.general_functions import add_epilepsy_causes_without_snomedct_ids
        causes = [{"preferredTerm": "Cause name", "term": "Cause name"}]
        add_epilepsy_causes_without_snomedct_ids(causes)
        ```

6. Check the database to ensure the causes have been added (a summary of the causes added will be printed to the console)

    ```console
    docker compose exec django python manage.py seed --mode=add_new_epilepsy_causes -sctids 764946008 52767006 ...
    ```

Note that the function expects a list, even if only one item is supplied.

> [!NOTE]
> Epilepsy Causes have as of #1224 been deprecated pending a better solution.



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
