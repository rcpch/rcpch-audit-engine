---
title: Postcodes
reviewers: Dr Simon Chapman
---

This should be read in conjunction with sections on mapping and index of multiple deprivation. 

Postcodes for patients are stored in RCPCH-Audit-Engine securely as part of the national agreement for the RCPCH Epilepsy12 clinical audit. Opt out can be requested by patients and all data with the exception of the platform unique identifier (not the NHS number or Unique Reference Number) which is retained to generate an accurate denominator.

Postcodes are used primarily to calculate indices of multiple deprivation, but are also used to provide a scatterplot for clinicians of patients in a given organisation to report maximum/minimum/mean and median distances patients have to travel for care.

Postcodes are passed to `api.rcpch.ac.uk/postcodes`. This is an RCPCH managed instance of the `postcodes.io` and requires an api key. It reports information against postcode which include LSOA (see Indices of Multiple Deprivation) as well as longitude and latitude. These latter data points are used for scatter plots.

Jersey is currently not supported as there is no open source solution for mapping currently though this is tracked in a [github issue](https://github.com/rcpch/rcpch-audit-engine/issues/1107)

## Postcode and IMD

To calculate an IMD we need the year for England as new data was published in 2025.

If the patient is in cohort 8, this will by default use 2025 data. Earlier cohorts will use 2019.

To fill in or recalculate the postcode-derived fields (the IMD quintile, and the location fields `location_wgs84` and `location_bng`) use the convenience script:

```console
s/recalculate-postcode-data                 # all cases, missing values only
s/recalculate-postcode-data 6               # cohort 6, missing values only
s/recalculate-postcode-data 6 --rebuild     # cohort 6, full rebuild
```

By default only missing values are filled in, for example where postcodes.io or the Census Platform was unavailable when the case was saved. Cases that already have both values are not looked up again, so it can be rerun until nothing is left. `--rebuild` recalculates both fields for every case in scope, for example after a change to the IMD dataset. In a rebuild a failed lookup keeps the existing value, and a case whose postcode cannot be looked up (unknown or Jersey) has its location cleared, as saving the case does.

Add `--dry-run` to the underlying command (`python manage.py recalculate_postcode_data --cohort 6 --dry-run`) to see how many lookups would be made without calling any APIs.

Superusers can also run it from the Django admin: **Administrative tools → Recalculate IMD and locations**. Pick a cohort and whether to fill in missing values or rebuild, preview the counts, then confirm. The admin page runs the command within the web request, so a large cohort can time out; if it does, rerun it with "Only fill in missing" until nothing is left.
