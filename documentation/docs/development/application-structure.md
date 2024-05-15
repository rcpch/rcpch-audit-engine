---
title: Introduction and application structure
reviewers: Dr Simon Chapman, Dr Marcus Baw
---

The RCPCH Audit Engine is a generic framework for national clinical audits. Its first deployment is as a new platform for the RCPCH's established Epilepsy12 audit, but it is designed to be reusable for other audits in the future.

National clinical audits collect diagnosis and care process data on patient cohorts with a diagnosis in common, nationally, to benchmark the standard of care and feed back to care-giving organisations about their performance. They are a way to make sure that clinics are meeting centrally-set standards, and give clinics feedback on how they are doing. Most national audits such as Epilepsy12 are commissioned at national level.

## Project Design

The RCPCH development team used Django, a Python-based web framework which is mature, accessible and well-documented. It is founded on the concept of a Project which can have many Applications within it. This meant that we could have an `rcpch-audit-engine` project, within which *multiple* audit applications might sit, sharing resources, for example relating to authorisation and authentication, or potentially constant values and so on. RCPCH administers several national audits on behalf of children and their families and the paediatric organisations that serve them, so Django offered the opportunity in future to bring together audits into a single platform.

The top level folder, therefore, is `rcpch-audit-engine`, which contains the `settings.py`, project `urls.py` as well as `asgi.py` and `wsgi.py` files.

Within the rcpch-audit-engine Project, currently `epilepsy12` is the only Application.

