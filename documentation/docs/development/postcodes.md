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

To recalculate all postcodes in a given cohort use the convenience script:

```console
s/recalculate-imd        # all cohorts
s/recalculate-imd 6      # cohort 6 only
```

As well as recalculating the IMD quintile for every case, this fills in the location fields (`location_wgs84` and `location_bng`) for any case missing them, for example because postcodes.io was unavailable when the case was saved. Cases that already have a location are not looked up again.

Add `--dry-run` to the underlying command (`python manage.py recalculate_imd --cohort 6 --dry-run`) to see how many cases would be processed without calling any APIs.

Superusers can also run it from the Django admin: **Administrative tools → Recalculate IMD and locations**. Pick a cohort, preview the counts, then confirm. The admin page runs the command within the web request, so a large cohort can take several minutes.
