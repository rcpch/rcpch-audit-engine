# agents.md — RCPCH Audit Engine: Agent Orientation

> This file is intended as a growing reference for AI agents and developers working on this codebase. It will be expanded over time to cover each major area of the project.

---

## Project Overview

**rcpch-audit-engine** is the backend and web application for **Epilepsy12**, a national clinical audit run by the Royal College of Paediatrics and Child Health (RCPCH). It collects, validates, and reports on epilepsy care for children across England and Wales.

- **Framework**: Django (Python)
- **Database**: PostgreSQL with the PostGIS extension (spatial queries)
- **Deployment target**: Azure Container Apps
- **Container registry**: Azure Container Registry (ACR)
- **Reverse proxy**: Caddy (handles HTTPS)
- **Task queue**: Celery (celerybeat for scheduled tasks)
- **Primary app**: `epilepsy12/` — all audit domain logic lives here
- **Documentation**: MkDocs site, served via a separate Docker Compose service and built into the image at deploy time
- **Full docs**: https://e12.rcpch.ac.uk/docs

The main Django project config is in `rcpch-audit-engine/` (the inner directory), including `settings.py`, `urls.py`, `logging_settings.py`, and `build_info.py`.

---

## The `s/` Scripts Directory

All developer and CI operations are driven by short shell scripts in `s/`. These exist to reduce typing, reduce errors, and ensure consistency. Scripts are plain bash; make them executable with `chmod +x s/<script>` if needed.

| Script | Purpose |
|---|---|
| `s/up` | `docker compose up` — starts all services (caddy, django, postgis, mkdocs) |
| `s/down` | `docker compose down` — stops services, does **not** destroy volumes or images |
| `s/rebuild` | Destroys containers and images then calls `s/up` (runs `s/remove-containers-and-images` then `s/up`) |
| `s/remove-containers-and-images` | Removes local containers and images without touching volumes |
| `s/DELETE-LOCAL-DATA` | **Destructive** — prompts for confirmation, then runs `docker compose down -v --rmi local` removing volumes too. Never run on live/production. |
| `s/start-dev` | Django entrypoint for development: `collectstatic`, `migrate`, seed groups/permissions, create dev users, then `runserver` |
| `s/start-prod` | Django entrypoint for production |
| `s/start-test` | Django entrypoint used during test runs: `collectstatic` then sleeps (keeps container alive for pytest) |
| `s/seed` | Seeds 200 cases and registrations into a running django container via `manage.py seed` |
| `s/test` | Runs `pytest -v` in the running django container by default (`--container` / `--in-container`); use `--local` / `--host` / `--outside-container` for host mode, or `--spin-up` / `--up` / `--with-up` to start an isolated test compose project, run tests, and tear it down |
| `s/pr-check` | Used in CI on PRs: spins up compose with `start-test`, runs `not slow` then `slow` test markers, tears down |
| `s/ci` | Full deployment pipeline script (see CI section below) |
| `s/logs` | Tails all compose service logs with timestamps |
| `s/psql` | Opens a psql shell inside the postgis container |
| `s/django-shell` | Opens a Django shell inside the django container |
| `s/create-superuser` | Creates a Django superuser inside the running container |
| `s/get-build-info` | Writes git metadata (hash, branch, etc.) to `build_info.json` for the build info page |
| `s/push-envs-github-secret` | Pushes environment secrets to GitHub Actions secrets |
| `s/trust-caddy-ca` | Trusts Caddy's local CA certificate for local HTTPS development |
| `s/restart` | Restarts compose services |

The `DJANGO_START_COMMAND` environment variable controls which start script the django container runs. It defaults to `s/start-dev`; CI overrides it to `s/start-test` when running tests.

---

## CI / Deployment Pipeline

### GitHub Actions Workflows

| Workflow file | Trigger | Purpose |
|---|---|---|
| `run-docker-compose-test-on-pr.yml` | PR to any branch | Runs the full pytest suite via `s/pr-check` |
| `deploy.yml` | Push to `live` branch | Full build, test, and deploy to Azure via `s/ci` |
| `staging_e12-staging-web-app-service.yml` | (see file) | Staging App Service deployment |
| `auto-add-issues-to-project.yml` | Issue events | Automatically adds issues to the GitHub Project board |

### The `s/ci` Deployment Script (called by `deploy.yml`)

This is the authoritative deploy sequence executed on every push to `live`:

1. **Login to Azure ACR** — `az acr login`
2. **Download `.env` from Azure File Share** — production secrets are stored in Azure Storage, not in the repo
3. **Burn in build info** — `s/get-build-info` writes git metadata to `build_info.json`
4. **Build the Docker image** — `docker compose build`
5. **Build the MkDocs documentation** — runs inside the image; docs are embedded into the static files
6. **Rebuild the image** — a second build to embed the freshly built docs
7. **Tag and push to ACR** — tagged with the Git SHA: `<registry>.azurecr.io/e12-django:<SHA>`
8. **Run tests** — `s/test -m 'not slow'` then `s/test -m 'slow'` against a local Postgres container
9. **Deploy to staging** — `az containerapp revision copy` creates a new revision on the staging Container App
10. **Deploy to production** — same command targets the live Container App

> Note: the image is pushed to ACR **before** tests run, so that an emergency deploy is possible from a known-good SHA even if tests are mid-flight.

### Authentication to Azure

The GitHub Actions workflow uses OIDC (`id-token: write` permission) with Azure federated credentials — no long-lived secrets for the Azure login itself. Remaining secrets (registry name, resource group, app names, storage account, etc.) are stored as GitHub Actions secrets and injected as environment variables into `s/ci`.

---

## Docker Compose Services

| Service | Image / Build | Role |
|---|---|---|
| `caddy` | `caddy` (official) | Reverse proxy, TLS termination, serves static docs |
| `django` | `e12-django:built` (local build) | Main Django application |
| `postgis` | `postgis/postgis:15-3.3` | PostgreSQL + PostGIS |
| `mkdocs` | `e12-django:built` | Builds and optionally serves the MkDocs documentation |

All services share environment from `envs/.env` (not committed to git). Two named volumes are used: `caddy-data` and `postgis-data`.

---

## IMD Calculation — Design Notes

### Background

The **Index of Multiple Deprivation (IMD)** quintile is stored on `Case.index_of_multiple_deprivation_quintile`. The correct IMD year to use depends on the patient's **cohort**:

- Cohort < 8 → 2019 IMD (England 2019 / Wales 2019, based on 2011 LSOA boundaries)
- Cohort ≥ 8 → 2025 IMD (England 2025, based on 2021 LSOA boundaries; Wales still 2019)

The cohort is stored on `Registration` and is derived from `Registration.first_paediatric_assessment_date`. The RCPCH Census Platform API was updated to **v2**, which now accepts a `year` parameter (`2019` or `2025`) in the IMD endpoint.

### The problem with putting IMD in `Case.save()`

`Case` and `Registration` have a 1-to-1 relation, but they can be created in either order. If IMD is calculated inside `Case.save()`, the Registration (and therefore the cohort) may not exist yet on first save, making it impossible to know the correct year. Workarounds inside `save()` grow complexity and can cause `ValueError` when filtering on an unsaved instance.

### Current design: signal-driven utility

IMD is calculated in a **single utility function** and triggered by **`post_save` signals** on both models:

```
epilepsy12/general_functions/index_multiple_deprivation.py
  └── recalculate_imd_for_case(case)
        - no-op if postcode missing or unknown
        - no-op if Registration or cohort not yet available
        - derives imd_year from registration.cohort
        - calls imd_for_postcode(postcode, year=imd_year) once
        - persists via queryset .update() to avoid re-triggering Case.save()
```

```
epilepsy12/signals.py
  ├── pre_save / post_save on Case
  │     → fires recalculate_imd_for_case when postcode changes
  └── pre_save / post_save on Registration
        → fires recalculate_imd_for_case when first_paediatric_assessment_date changes
```

`Case.save()` itself only normalises the postcode (strip spaces/dashes, uppercase) and updates geolocation coordinates (`location_wgs84`, `location_bng`). It sets `index_of_multiple_deprivation_quintile = None` when postcode switches to an unknown/placeholder value.

### Bulk recalculation

To recalculate IMD for existing records (e.g. after a cohort boundary change or API update):

```bash
s/recalculate-imd          # all cohorts
s/recalculate-imd 6        # cohort 6 only
```

This wraps `manage.py recalculate_imd --all` / `--cohort N` (`epilepsy12/management/commands/recalculate_imd.py`).

### Key constants

| Setting | Location |
|---|---|
| `RCPCH_CENSUS_PLATFORM_URL` | `settings.py` / `.env` |
| `RCPCH_CENSUS_PLATFORM_TOKEN` | `settings.py` / `.env` |
| `UNKNOWN_POSTCODES_NO_SPACES` | `epilepsy12/constants/postcodes.py` |

---

## Organisation Dashboard — Cases Map (`@rcpch/imd-map`)

The organisation dashboard (`epilepsy12/views/organisation_views.py` → `selected_organisation_summary`) renders a choropleth deprivation map showing case locations against IMD tiles. This is implemented using the [`@rcpch/imd-map`](https://github.com/rcpch/rcpch-mapping-component) browser library, **not** a server-side mapping tool.

### Architecture

The backend prepares a plain JSON payload; the browser library does all tile streaming and WebGL rendering.

```
View (organisation_views.py)
  └── builds organisation_cases_imd_payload:
        { initialNation, initialEra, patients: [{id, lat, lon, ...}], leadCentre: {lat, lon, label} }
        → passed to template via Django json_script (XSS-safe)

Template (selected_organisation_summary.html)
  └── CDN: @rcpch/imd-map UMD bundle (includes MapLibre GL)
  └── <div id="organisation_cases_map"> — mount point
  └── <script> IIFE:
        RcpchImdMap.createImdMap({ container, tilesBaseUrl, initialNation, initialEra, ... })
        map.setPatients(payload.patients)
        map.setLeadCentre(payload.leadCentre)
        map.fitToData()
        stored on window._organisationCasesImdMap for HTMX-safe destroy/recreate
```

### Nation and era rules

The library selects the correct IMD tile era based on `initialNation` + `initialEra` passed from the view:

- England, cohort ≥ 8 → `initialEra: "2021"` (2021 LSOA boundaries, 2025 IMD)
- England, cohort < 8 → `initialEra: "2011"` (2011 LSOA boundaries, 2019 IMD)
- Wales / Scotland / N. Ireland → always `"2011"` (library enforces this regardless of era passed)

`initialNation` is derived from `selected_organisation.country.boundary_identifier` via a lookup dict in the view.

### Boundary overlays

NHS Region, ICB, and LHB boundary overlays are rendered by the library itself via `enableHealthOverlays: true`. The view **no longer** builds or serialises boundary GeoJSON — the old `_build_boundary_overlay()` function and `return_tile_for_region` / `generate_case_counts_for_each_region_in_each_abstraction_level` calls have been removed.

### Tile server

`tilesBaseUrl` is read from `settings.RCPCH_DEPRIVATION_TILES_URL` (env var `RCPCH_DEPRIVATION_TILES_URL`) and passed directly from view context to the template JS. The library also reads `window.RCPCH_DEPRIVATION_TILES_URL` as a fallback.

### Key files

| File | Role |
|---|---|
| `epilepsy12/views/organisation_views.py` | Builds `organisation_cases_imd_payload` context key |
| `templates/epilepsy12/partials/selected_organisation_summary.html` | Map mount point + init script |
| `rcpch-audit-engine/settings.py` | `RCPCH_DEPRIVATION_TILES_URL` setting |

### What was removed

The old hand-rolled `static/js/maps/organisation_cases_map.js` (which exposed `window.RCPCHMaps.initialiseOrganisationCasesMap`) has been deleted. Do not attempt to restore it or reference `window.RCPCHMaps` — use `window.RcpchImdMap.createImdMap` instead.

---

## Areas to Expand

The following sections will be added over time:

- `epilepsy12/` app structure (models, views, forms, KPIs, migrations)
- `epilepsy12/models_folder/` — domain model breakdown
- `epilepsy12/views/` — view organisation and HTMX patterns
- `epilepsy12/constants/` — audit constants and clinical coding
- `epilepsy12/management/commands/` — custom management commands including `seed`
- `epilepsy12/tests/` — test structure and pytest markers
- `epilepsy12/common_view_functions/` — shared view logic
- KPI calculation logic (`kpi.py`, `organisational_audit.py`)
- Permissions and decorator patterns
- Celery / celerybeat scheduled tasks
- REST API (serializers, DRF)
- Template and HTMX patterns
