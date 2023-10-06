---
title: Introduction and application structure
reviewers: Dr Simon Chapman
---

The RCPCH Audit Engine is a generic framework for national clinical audits. Its first deployment is as a new platform for the RCPCH's established Epilepsy12 audit, but it is designed to be reusable for other audits in the future.

National clinical audits collect diagnosis and care process data on patient cohorts with a diagnosis in common, nationally, to benchmark the standard of care and feed back to care-giving organisations about their performance. They are a way to make sure that clinics are meeting centrally-set standards, and give clinics feedback on how they are doing. Most national audits such as Epilepsy12 are commissioned by NHS England.

## Project Design

The RCPCH Incubator development team used Django 4.0 as it is a Python-based web framework which is mature, accessible and well-documented. It is founded on the concept of a Project which can have many Applications within it. This meant that RCPCH could have an audit-engine project within which multiple audit applications might sit, sharing resources, for example relating to authorisation and authentication, or potentially constant values and so on. RCPCH administers several national audits on behalf of children and their families and the paediatric organisations that serve them, so Django offered the opportunity in future to bring together audits into a single platform.

The top level folder, therefore, is ```rcpch-audit-engine```, which contains the ```settings.py```, project ```urls.py``` as well as ```asgi.py``` and ```wsgi.py``` files.

Within the rcpch-audit-engine platform, currently epilepsy12 is the only application.

## Application Structure

An application folder sits within the ```rcpch-audit-engine``` folder and is named after the application name (```AppName```).

### The key files are

- ```apps.py```: This subclasses the Django ```AppConfig``` and it is here that the application name is set
- ```admin.py```: It is here that the custom user is set as ```Epilepsy12User```, personalizations to the admin interface are set, and rules for user creation including the ```createsuperuser``` function.
- ```decorator.py```: Decorators are python functions which wrap a function. They are used to protect routes by performing validation and authorization, redirecting as necessary to 404 and 403 screens.
- ```forms.py```: Forms in Django automate much of the complication of webforms. In the Epilepsy12 project, the power of Django forms has not been leveraged for reasons discussed further down. There are 2 types of Django form that have been retained. The first are the login/account creation/registration forms. Custom forms have been created to match the Epilepsy12 and RCPCH styles, but the form validation logic sits on top of Django. The other place Django forms have been used is in Case creation/updating within the Epilepsy12 application. There is a file for each form in the ```forms_folder``` at the top level within the Epilepsy12 application. These in turn are imported into ```forms.py```.
- ```models.py```: The structure of each Model Class can be found in the ```models``` folder, at the top level within the Epilepsy12 application. There is a file for each model class. These in turn are imported into ```models.py```.
- ```serializers.py```: This file is part of the ```django-rest-framework``` and is analagous to forms in the application. Serializers take in the models to generate the API definitions.
- ```signals.py``` contains receiver functions triggered when a user attempts to log in. This activity is tracked in the VisitActivity model.
- ```urls.py```: All routes, both for the application and the API, are defined here and imported into project-level ```urls.py``` of the same name in the ```rcpch-audit-engine``` folder above. The routes use the Django ```path()``` function which link defined paths and wildcards with functions in ```views.py```. Routes for the API use the ```django-rest-framework``` ```Router``` module.
- ```validators.py```: contains functions for date validation.

### The folders are:

- ```constants```: This contants multiple files each containing constant values used in the models and elsewhere. The follow the standard that uppercase is used to denote its immutable nature.
- ```coverage_tests```: Tests are found here and collected automatically by the Coverage package and executed on the command line with the command: ```coverage run```.
- ```forms_folder```: see ```forms.py``` above.
- ```general_functions```: this folder contains files for functions that can be called across the application. It contains functions particularly for external API calls (for example to the SNOMED server), but also houses the logic behind fuzzy matching for the description words in the DESSCRIBE tool.
- ```management```: Files here contain functions that are run from the command line with the prefix ```python manage.py```. These include functions that seed the database with dummy data in development.
- ```migrations```: This is a Django folder and should not be touched unless the user is a confident Django user. Any changes to the models are stored here and therefore the history in this folder reflects the history of the database design over time. It should always be checked into Git.
- ```models_folder```: see ```models.py``` above.
- ```shape_files```: contains files with the geojson data for drawing maps
- ```templatetags```: files in this folder contain helper functions used by Django templates.
- ```tests```: files and folders for the test suite
- ```views```: All views files can be found here. There is one for each model, with the exception of ```multiaxial_diagnosis_views.py``` which has functions for all its related models (```Episode```, ```Syndrome``` and ```Comorbidity```).

## Folders outside of the Applications

There are several other top level folders and files

### Files

- ```CITATION.cff```: This has been generated by [zenodo](https://zenodo.org) and allows the ```rcpch-audit-engine``` project to be cited in the academic literature
- ```docker-compose.yml```: see [manual setup](manual-setup.md)
- ```dockerfile```: see [manual setup](manual-setup.md)
- ```example.env```: Environment variables for security - these are an example only and in production should be hidden.
- ```LICENSE```: This is the AGPL-3.0 License.
- ```manage.py```: This is a django file and should not be touched.
- ```README.md```: This is a readme file but contains very little as redirects to this documentation site.
- ```requirements.txt```: This is a python file and contains a list of all the dependencies +/- versions. The RCPCH Incubator team are judicious with dependencies and these should only be used if the dependency is established, well-documented and meets an important need where building in-house would be impractical. The file references the ```requirements``` folder which contains dependencies organised into folders based on whether they are installed for development or production. The syntax for installation is: ```pip install -r requirements/common-requirements.txt```

### Folders

- ```s```: This is an RCPCH incubator standard. Shortcuts related to running the project or migrating or seeding the database are here. The commands follow the example: ```s/migrate```. Any custom functions are found in the ```manage``` folder.
- ```static```: contains all static files. The RCPCH Incubator recommend any css files be persisted here, rather than using CDNs to protect from situations where data signals are not available. This has a small latency cost, and involves regular review of dependencies to ensure they are up to date.
- ```tables```: This has no function and is listed for deprecation. It contains olds excel sheets of database models in the previous version of Epilepsy12
- ```templates```: All templates are found here.
