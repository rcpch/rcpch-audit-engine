---
title: Organisations, Trusts and Levels of Abstraction
reviewers: Dr Simon Chapman
---

## Levels of Abstraction

The organisational structure of health care in England and Wales influences reporting and table structure.

### Organisations and Trusts

This is the lowest level of abstraction and represents either an acute or a community hospital/organisation responsible for epilepsy care of children and young people. There are often several organisations in a Trust. Each organisation, like each Trust, has its own ODS code, and from year to year there is movement between trusts as organisations change their allegiances between trusts when mergers are carried out.

Organisational and geographical reference data is maintained by the [`rcpch-nhs-organisations`](https://github.com/rcpch/rcpch-nhs-organisations) API, which is the source of truth for organisations, trusts, their hierarchy and their history (including mergers and ODS code successions). This project mirrors that data locally via a sync (`epilepsy12/general_functions/nhs_organisations_sync.py`), which upserts the local `Organisation`, `Trust` and other entity tables from the API's list endpoints. The sync is idempotent and runs inside a single transaction. The old direct NHS ODS (Spine) sync has been removed.

For historical geography — "which trust was this organisation under on date X?" — the API exposes a `GET /organisations/{ods_code}/snapshot/?date=YYYY-MM-DD` endpoint that walks the `OrganisationSuccession` chain to a predecessor if the organisation did not yet exist on that date. This is used by the public KPI publication flow (see [Public KPI reporting — feature scope](public-kpi-reporting-scope.md)).

### Integrated Care Boards

These were introduced in 2022 and superceded Clinical Commissioning Groups (CCGs) as the geographical commissioning areas within the NHS. The are 42 ICBs and trusts and their organisations fit neatly inside them like Russian dolls. Each ICB has its own ODS code. The ICB model is synced from the `rcpch-nhs-organisations` API. Note there are no ICBs in Wales.

### Local Health Boards

These exist only in Wales and are both equivalent to Trust and ICB in England. One LHB might have several organisations and commissioning also is distributed across the 7 LHBs. The model is synced from the `rcpch-nhs-organisations` API.

### OPENUK Networks

These are [networks](https://www.rcpch.ac.uk/resources/open-uk-organisation-paediatric-epilepsy-networks-uk) of NHS Health Boards and Trusts that provide care for children with epilepsies, organised regionally and overseen by a UK Working Group. Not all centres are members of an OPEN UK network. Each one has its own identifier, and the model is synced from the `rcpch-nhs-organisations` API's dedicated `/openuk_networks/` endpoint.

### NHS England Regions

There are 7 of these in England and each one has its own boundary code. ICBs fit neatly inside each one. The model is synced from the `rcpch-nhs-organisations` API.

### Local Authorities

Local authority codes for each organisation are not stored except for those organisations in London. Local authorities are administrative regions not related to health or the NHS. In London local authorities are usually referred to as London Boroughs. There is a boundary model for London Boroughs which is used only for mapping. These are not synced from the `rcpch-nhs-organisations` API.

### Jersey and the Channel Islands

Jersey joined Epilepsy12 in 2024. Jersey is in the Channel Islands and part of the UK but does not participate in the NHS. There are reciprocal agreements about some hospital treatment, but inpatient care is free only to people who have been resident for 6 months and have a Health Card.

***Organisational structure***
The E12 structure is that organisations have a Trust or Local Health Board as their parent. There is a hierarchy above this which varies between England and Wales. Organisations and Trusts in England might have the same name, but will always have separate ODS codes, which are often similar. Jersey General Hospital in St Helier is a Trust which provides medical care directly. To work around this, Jersey General Hospital has been created both as an Organisation and a Trust, each with the same ODS code, so that it is its own parent.

***Levels of Abstraction***
Jersey has been added as a separate country, so that it can report at the level of organisation, Open UK Network, trust and country, though the numbers for these 3 hierarchies will be the same.

## Maps

Django GIS and the additional Postgres support for geoJSON are both reasons why these tools were used for this project. The Organisation View presents a dashboard that includes a scatterplot of patients specific to that organisation, with mean, median, minimum and maximum distances for patients to travel to clinic. There are also maps with boundaries demarcating health geographies such as NHS England regions and Integrated Care Boards.

Boundary geometries are no longer persisted locally from the `rcpch-nhs-organisations` API. The mapping component (`@rcpch/imd-map`) now pulls boundary tiles directly from the `rcpch-census-platform` vector tile service. The local boundary models (`Country`, `IntegratedCareBoard`, `LocalHealthBoard`, `NHSEnglandRegion`) still carry `geom` fields for backward compatibility, but these are now nullable (migration `0065`) and are not populated by the sync. Existing geometry values from previous shapefile imports are left untouched.

The basic maps are provided by [MapBox](https://www.mapbox.com/) using their free tier, with the API key stored in credentials. An API key is required.

E12 currently looks up postcodes against an API which returns longitude and latitude, and these are stored in the model (using SRID 27700) and this is used to plot them on the scatter plots. This currently does not function for Jersey as longitude and latitude for post codes are currently not stored.
