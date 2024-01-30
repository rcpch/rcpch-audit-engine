---
title: Dropdowns
reviewers: Dr Simon Chapman
---

## Lists

Lists that feed either the toggle buttons or the select dropdowns are either found in the `constants` folder, or are seeded to the database in the `migrations`.

Organisation lists are seeded from `constants` as are the levels of abstraction associated with them (trust, ICB etc.) The Epilepsy causes and comorbidities, by contrast are a SNOMED refset seeded from the RCPCH SNOMED server in migration 0006 and 0009 into EpilepsyCause and ComorbidityList resp. Syndromes and medications are from lists in the `constants` folder.

Since go-live, E12 have wished on the basis of user feedback, wanted to add new items to these lists. The process for adding new items should be:

### EpilepsyCause

1. Epilepsy12 team to supply the SNOMED CT ID (SCTID) of the concept
2. The development team add the SCTID to the list `extra_concept_ids` in migration 0006 for future seeding from scratch, mostly for development reasons
3. In the python shell to run the seed function:

```console
python manage.py --mode=add_new_epilepsy_causes -sctids 764946008 52767006
```

Note that the function expects a list, even if only one item is supplied.

<!-- There will need to be further documentation added here for new organisations and trust, as well as new comorbidities, and possibly medications and so on. For now, this is the workflow for EpilepsyCauses -->