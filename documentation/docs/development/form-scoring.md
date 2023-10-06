---
title: Scoring the audit forms
reviewers: Dr Simon Chapman
---

This is the process of tracking user progress through scoring all the elements of the child's journey through the epilepsy12 audit. Progress is tracked in the ```AuditProgress``` model which has the following fields:

- ```registration_complete```
- ```registration_total_expected_fields```
- ```registration_total_completed_fields```
- ```first_paediatric_assessment_complete```
- ```first_paediatric_assessment_total_expected_fields```
- ```first_paediatric_assessment_total_completed_fields```
- ```assessment_complete```
- ```assessment_total_expected_fields```
- ```assessment_total_completed_fields```
- ```epilepsy_context_complete```
- ```epilepsy_context_total_expected_fields```
- ```epilepsy_context_total_completed_fields```
- ```multiaxial_diagnosis_complete```
- ```multiaxial_diagnosis_total_expected_fields```
- ```multiaxial_diagnosis_total_completed_fields```
- ```investigations_complete```
- ```investigations_total_expected_fields```
- ```investigations_total_completed_fields```
- ```management_complete```
- ```management_total_expected_fields```
- ```management_total_completed_fields```

For each form, a boolean flag tracks if the form is complete, how many fields in the form have been completed so far as an integer, and how many are expected, also as an integer. This is because the denominator is dynamic - the minimum number of fields expected to be scored to complete the form changes based on the user choices. For example, in ```MultiaxialDiagnosis```, if the user selects 'yes' to 'Is there an identifiable epilepsy syndrome?', they are invited to add a syndrome and the date of diagnosis: this increases the number of expected fields therefore by 2.

The final step, is to update the ```AuditProgress``` with these results and call the ```calculate_kpis()``` function.

## ```total_expected_fields``` vs ```total_completed_fields```

The logic calculating user progress can be summarise by these two fields and is found in ```common_view_functions/recalculate_form_generate_response.py```.

### ```total_completed_fields```

This is calculated from two functions:

- ```completed_fields()```
- ```number_of_completed_fields_in_related_models()```

Both functions accept a registration instance, from which all models can be accessed.

This function loops through all fields in a given model instance counting up all the fields that are not None (since all fields are None until scored). Several fields in each model have to be excluded, since they are not storing information about the audit. These include fields such as the primary key. This stripping of fields occurs in ```fields_to_avoid()```.

Some other fields are not included - ```epilepsy_cause_categories``` and ```description``` in multiaxial diagnosis are not included. The boolean fields describing features present or absent in a focal epilepsy are exlcuded - only focality (left or right) count to the total.

```number_of_completed_fields_in_related_models``` performs this same process for all fields in related models. For example, a single multiaxial description of a child's epilepsy comprises multiple episodes, all of which are different. 

This function steps through the audit questions one by one, calculating the minimum number of fields that can be expected to be completed, based on the selections the user has already made. As with the other functions it accepts an instance of the ```Registration``` model that relates to the child in question. It draws on two other helper functions:

- ```scoreable_fields_for_model_class_name()```
- ```count_episode_fields()```

These both do the same for related models if they exist. The ```Episode``` model is particularly complicated as it details all the different epilepsy types each of which have different decision trees that contribute to the scores.
