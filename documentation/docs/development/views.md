---
title: Epilepsy12 views
reviewers: Dr Simon Chapman
---

For design reasons explained [elsewhere](design-decisions.md), function-based views were preferred over class-based views. This means that each field in a given model is updated in isolation of others through individual ajax post requests direct from the template.

## Decorators

Decorators are used to protect the views.

- ```@login_required```: Nearly all routes are decorated by the django decorator and redirect to the login page
- ```@user_may_view_this_organisation()```: The is a custom decorator which only allows access to the logged in user whose employing organisation (as stored in the request.user object) matches that of the lead Epilepsy centre for the child. Superusers or RCPCH members may see all children nationally. Failure redirects to 403
- ```@user_may_view_this_child()```: This is a custom decorator which allows only the logged-in user access to view or edit data relating to a given child in their same organisation. Failure redirects to 403
- ```user_can_access_user```: This is a custom decorator which allows only the logged-in user access to view or edit data relating to a given user in their same organisation. Failure redirects to 403
- ```@permission_required("epilepsy12.change_episode", raise_exception=True)```

## View structure

View functions mirror the structure of the models. Each model has a corresponding view in the ```views``` folder in the root of the ```epilepsy12``` folder. The first function in each file is called to load the form template. If no instance of that model exists, an instance is created. Any dependencies for the template (such as lists for select dropdowns etc) are retrieved here and added to the context to be passed on to the template.

### View functions

Any function that updates, creates or deletes a model, early on in the function, calls ```validate_and_update_model``` in ```epilepsy12/common_view_functions/```. It accepts the following parameters:

- ```request```: request object passed in from calling view
- ```model_id```: id of the model to update
- ```model```: the Model itself
- ```field_name```: the name of the field to be updated as string
- ```page_element```: the type of page element selector, one of ```date_field```, ```hospitals_select```, ```multiple_choice_multiple_toggle_button```, ```select```, ```single_choice_multiple_toggle_button```, ```toggle_button```, ```snomed_select```
- ```comparison_date_field_name=None```: if the selector is a ```date_field```, additional parameters are required for validation
- ```is_earliest_date=None```: if the selector is a ```date_field```, additional parameters are required for validation
- ```earliest_allowable_date=None```: if the selector is a ```date_field```, additional parameters are required for validation

For the final 3 optional parameters, see the section on date validation in ```validators.py```

Any validations that identify errors are raised here with messages that are caught in the view. Otherwise the model is updated with the new value.

The name of the view function matches the name of the field of the model affected. It is passed also in the url.

#### Example

```python
@login_required
@user_may_view_this_child()
@permission_required("epilepsy12.change_episode", raise_exception=True)
def seizure_onset_date(request, episode_id):
    """
    HTMX post request from episode.html partial on date change
    """

    try:
        episode = Episode.objects.get(pk=episode_id)
        error_message = None
        validate_and_update_model(
            request=request,
            model=Episode,
            model_id=episode_id,
            field_name="seizure_onset_date",
            page_element="date_field",
            earliest_allowable_date=None,  # episodes may precede the first assessment date or cohort date
        )
    except ValueError as error:
        error_message = error

    keywords = Keyword.objects.all()
    episode = Episode.objects.get(pk=episode_id)

    context = {
        "episode": episode,
        "seizure_onset_date_confidence_selection": DATE_ACCURACY,
        "episode_definition_selection": EPISODE_DEFINITION,
        "keyword_selection": keywords,
        "epilepsy_or_nonepilepsy_status_choices": sorted(
            EPILEPSY_DIAGNOSIS_STATUS, key=itemgetter(1)
        ),
        "epileptic_seizure_onset_types": sorted(
            EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)
        ),
        "GENERALISED_SEIZURE_TYPE": sorted(GENERALISED_SEIZURE_TYPE, key=itemgetter(1)),
        "LATERALITY": LATERALITY,
        "FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS": FOCAL_EPILEPSY_MOTOR_MANIFESTATIONS,
        "FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS": FOCAL_EPILEPSY_NONMOTOR_MANIFESTATIONS,
        "FOCAL_EPILEPSY_EEG_MANIFESTATIONS": FOCAL_EPILEPSY_EEG_MANIFESTATIONS,
        "nonepilepsy_onset_types": NON_EPILEPSY_SEIZURE_ONSET,
        "nonepilepsy_types": sorted(NON_EPILEPSY_SEIZURE_TYPE, key=itemgetter(1)),
        "syncopes": sorted(NON_EPILEPTIC_SYNCOPES, key=itemgetter(1)),
        "behavioural": sorted(
            NON_EPILEPSY_BEHAVIOURAL_ARREST_SYMPTOMS, key=itemgetter(1)
        ),
        "sleep": sorted(NON_EPILEPSY_SLEEP_RELATED_SYMPTOMS, key=itemgetter(1)),
        "paroxysms": sorted(NON_EPILEPSY_PAROXYSMS, key=itemgetter(1)),
        "migraines": sorted(MIGRAINES, key=itemgetter(1)),
        "nonepilepsy_miscellaneous": sorted(EPIS_MISC, key=itemgetter(1)),
        "epilepsy_cause_selection": EPILEPSY_CAUSES,
    }

    response = recalculate_form_generate_response(
        model_instance=episode.multiaxial_diagnosis,
        request=request,
        template="epilepsy12/partials/multiaxial_diagnosis/episode.html",
        context=context,
        error_message=error_message,
    )

    return response
```

This function is called from the following path in ```urls.py```, as an HTMX POST request from the template, called in the change event of the custom page element ```date_field```.

```python
path(
        "episode/<int:episode_id>/seizure_onset_date",
        views.seizure_onset_date,
        name="seizure_onset_date",
    ),
```

```seizure_onset_date``` is a field in the ```Episode``` model. The request contains the ```episode_id``` and the new date in the header. It can be accessed by ```request.POST.get(request.htmx.trigger_name)```.

After the episode to be updated with the new date has been retrieved using the the```episode_id```, these parameters are passed into```validate_and_update_model``` where the date is retrieved, validated and the model updated. If there are any validation errors, these are raised here, and caught in the ```try...except``` block and stored in the ```error_message``` variable.

The ```context``` is updated in the ```recalculate_form_generate_response``` discussed elsewhere before being passed back to the template. This latter function also calculates the number of scored fields in the form and updates the totals in the ```steps.html``` partial by adding an HTMX custom trigger to the header.
