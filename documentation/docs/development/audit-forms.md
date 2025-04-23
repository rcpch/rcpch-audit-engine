---
title: Epilepsy12 audit forms
reviewers: Dr Simon Chapman
ignore_macros: true
---

The Epilepsy12 platform has a reactive user interface with RCPCH colours and design elements. Each audit form relates to an aspect of the child's epilepsy journey to be captured in the audit process. The elements are customised and a deliberate decision was to favour toggle buttons (either single or multichoice) that could be selected easily, were unambiguous and provided structured data easy for analysis.

There is an audit form for each model and each follows the same structure:

```audit_section.html``` divides the page into a left side-bar which contains a progress wheel reporting how many fields have been completed, and as series of steps which serve as navigation menu to the different forms that must all be completed prior to submission. They are numbered but do not have to be completed in order. A completed form renders as a pink tile in the steps. A selected tile renders as dark blue. The final tile links to a table of Key Performance Indicators for the care of that individual child.

In the main window, a square segment contains the audit form, and comprises a top-attached header segment with the child's identifiers. The main segment contains the ```audit_section_form``` block, which populates with the different forms from the ```templates/epilepsy12/forms``` folder. Finally the footer section contains user information guiding.

## Steps

The steps element described above is updated every time an item in the audit form is scored.

```python
<div
      hx-get='{% url "registration_active" case_id active_template %}'
      hx-trigger='registration_active from:body'
      hx-target='#registration_active'
      hx-swap="innerHTML"
      name="steps"
      class="rcpch_steps_wrapper"
    >
```

The steps are wrapped in this div which defines a custom ```htmx-trigger```, named ```registration_active```, called from the ```body``` element. This HTMX action can be called from any other element and triggers a GET request to the ```registration_active``` endpoint, found in ```views.py```.

```python
# HTMX generic partials
def registration_active(request, case_id, active_template):
    """
    Call back from GET request in steps partial template
    Triggered also on registration in the audit
    """
    registration = Registration.objects.get(case=case_id)
    audit_progress = registration.audit_progress
    site = Site.objects.filter(
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
        case=registration.case,
    ).get()
    organisation_id = site.organisation.pk

    # enable the steps if has just registered
    if audit_progress.registration_complete:
        if active_template == "none":
            active_template = "register"

    context = {
        "audit_progress": audit_progress,
        "active_template": active_template,
        "case_id": case_id,
        "organisation_id": organisation_id,
    }

    return render(
        request=request, template_name="epilepsy12/steps.html", context=context
    )
```

This function retrieves user progress from the ```AuditProgress``` model and passes this to the steps for it to render progress and rerender the ```steps.html``` partial with the updated data.

## Labels and References

The labels and associated references for each field in each model are stored in the `help_text` field of each model. This is done by overriding the `help_text` with a custom `HelpTextMixin`. Instead of returning a single string, it returns a python object with keys of `label` and `reference`. These are accessed in the templates to render the labels and tooltips.

In #1215 the E12 team sought to change the wording and KPI 8 scoring only for cohort 7 and above. To retain the wording for previous cohorts therefore a new `conditional_help_text` was introduced which conditionally renders if present, otherwise the default label and reference in the model instead are returned.

### Implementing conditional labels

1. in the model add a new method using the syntax `get_(measure)__conditional_help_text`
2. apply any conditional logic (for example comparison of cohort)
3. return a python object with the keys `label` and `reference`

```python
def get_is_a_pregnancy_prevention_programme_in_place_conditional_help_text(self):
        """
        Return conditional help text based on cohort - works in conjunction with HelpTextMixin

        Relates to KPI measure 8 amendment in issue #1215

        This measure has changed to allow a risk acknowledgement form and pregnancy prevention programme to be in place
        to be offered to all girls on valproate (any age) and all girls aged 12 and over on Topiramate.

        This measure is only calculated for cohorts 7 and above, so the old calculation is retained.

        In the user interface, the help text is updated to reflect the new measure, but only for cohorts 7 and above.
        """
        if (
            hasattr(self, "management")
            and self.management
            and hasattr(self.management, "registration")
            and self.management.registration.cohort > 6
        ):
            return {
                "label": "Is a Pregnancy Prevention Programme in place?",
                "reference": "For girls and young women who are prescribed sodium valproate or topiramate (if > 12y), it is recommended that pregnancy prevention is actively discussed and documented.",
            }
        return None  # Fall back to default help text
```