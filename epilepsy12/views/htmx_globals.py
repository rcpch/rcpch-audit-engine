# python
import csv

# django
from django.apps import apps
from django.shortcuts import render
from django.http import HttpResponse

# e12
from epilepsy12.models import (
    Registration,
    Site,
    Case,
    FirstPaediatricAssessment,
    EpilepsyContext,
    MultiaxialDiagnosis,
)
from epilepsy12.decorator import rcpch_full_access_only, login_and_otp_required


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


@login_and_otp_required()
@rcpch_full_access_only()
def download_select(request):
    """
    POST request from frida_button.html
    """
    model = request.POST.get("model")

    context = {
        "selected_model": model,
        "model_list": (
            "allregisteredcases",
            "registration",
            "firstpaediatricassessment",
            "epilepsycontext",
            "multiaxialdiagnosis",
            "assessment",
            "investigations",
            "management",
            "site",
            "case",
            "epilepsy12user",
            "organisation",
            "comorbidity",
            "episode",
            "syndrome",
            "keyword",
        ),
        "is_selected": True,
    }

    return render(
        request, template_name="epilepsy12/partials/frida_button.html", context=context
    )


@login_and_otp_required()
@rcpch_full_access_only()
def download(request, model_name):
    """
    POST request to download table as csv
    """

    field_list = []

    if model_name == "allregisteredcases":
        one_to_one_tables = [
            "registration",
            "case",
            "firstpaediatricassessment",
            "epilepsycontext",
            "multiaxialdiagnosis",
            "assessment",
            "investigations",
            "management",
        ]

        for index, one_to_one_table in enumerate(one_to_one_tables):
            model_class = apps.get_model(
                app_label="epilepsy12", model_name=one_to_one_table
            )
            fields = model_class._meta.get_fields()

            for field in fields:
                if field.name in [
                    "id",
                    "episode",
                    "syndrome",
                    "antiepilepsymedicine",
                    "comorbidity",
                ]:
                    pass
                else:
                    if one_to_one_table == "registration":
                        relative_field_name = field.name
                    else:
                        relative_field_name = f"{one_to_one_table}__{field.name}"
                        if field.name == "organisations":
                            relative_field_name += "__name"
                    field_list.append(relative_field_name)
        model_class = Registration
    else:
        model_class = apps.get_model(app_label="epilepsy12", model_name=model_name)

        fields = model_class._meta.get_fields()
        for field in fields:
            field_list.append(field.name)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="all_registered_cases.csv"'

    writer = csv.writer(response)

    all_fields = model_class.objects.all().values(*field_list)

    for index, p in enumerate(all_fields):
        if index == 0:
            # csv headings - format the name to be readable from the key and add to the header
            headers = p.keys()

            header_list = []
            for header in headers:
                # loop through the headings and remove the model name which prefixes the field by __
                split_header = header.split("__")
                header_list.append(split_header[-1])
            writer.writerow(header_list)
        else:
            # discard the keys and store only the values in each row. If the value represents a choice,
            # get the choice key from the value
            # this is a bit tedious but because a queryset is not an instance of the model, we have to create
            # one in order to use the get_field_display() model instance method to look up the key name.
            # This function has been abstracted out to the return_choice_for_instance_and_value function below
            if p.get("case__sex") is not None:
                field_value = p.get("case__sex")
                choice = return_choice_for_instance_and_value(Case, "sex", field_value)
                p["case__sex"] = choice

            if p.get("case__ethnicity") is not None:
                field_value = p.get("case__ethnicity")
                choice = return_choice_for_instance_and_value(
                    Case, "ethnicity", field_value
                )
                p["case__ethnicity"] = choice

            if (
                p.get(
                    "firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting"
                )
                is not None
            ):
                field_value = p.get(
                    "firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting"
                )
                choice = return_choice_for_instance_and_value(
                    FirstPaediatricAssessment,
                    "first_paediatric_assessment_in_acute_or_nonacute_setting",
                    field_value,
                )
                p[
                    "firstpaediatricassessment__first_paediatric_assessment_in_acute_or_nonacute_setting"
                ] = choice

            if p.get("epilepsycontext__previous_febrile_seizure") is not None:
                field_value = p.get("epilepsycontext__previous_febrile_seizure")
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, "previous_febrile_seizure", field_value
                )
                p["epilepsycontext__previous_febrile_seizure"] = choice

            if p.get("epilepsycontext__previous_acute_symptomatic_seizure") is not None:
                field_value = p.get(
                    "epilepsycontext__previous_acute_symptomatic_seizure"
                )
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, "previous_acute_symptomatic_seizure", field_value
                )
                p["epilepsycontext__previous_acute_symptomatic_seizure"] = choice

            if (
                p.get("epilepsycontext__is_there_a_family_history_of_epilepsy")
                is not None
            ):
                field_value = p.get(
                    "epilepsycontext__is_there_a_family_history_of_epilepsy"
                )
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext,
                    "is_there_a_family_history_of_epilepsy",
                    field_value,
                )
                p["epilepsycontext__is_there_a_family_history_of_epilepsy"] = choice

            if p.get("epilepsycontext__previous_neonatal_seizures") is not None:
                field_value = p.get("epilepsycontext__previous_neonatal_seizures")
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, "previous_neonatal_seizures", field_value
                )
                p["epilepsycontext__previous_neonatal_seizures"] = choice

            if (
                p.get(
                    "epilepsycontext__experienced_prolonged_generalized_convulsive_seizures"
                )
                is not None
            ):
                field_value = p.get(
                    "epilepsycontext__experienced_prolonged_generalized_convulsive_seizures"
                )
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext,
                    "experienced_prolonged_generalized_convulsive_seizures",
                    field_value,
                )
                p[
                    "epilepsycontext__experienced_prolonged_generalized_convulsive_seizures"
                ] = choice

            if (
                p.get("epilepsycontext__experienced_prolonged_focal_seizures")
                is not None
            ):
                field_value = p.get(
                    "epilepsycontext__experienced_prolonged_focal_seizures"
                )
                choice = return_choice_for_instance_and_value(
                    EpilepsyContext, "experienced_prolonged_focal_seizures", field_value
                )
                p["epilepsycontext__experienced_prolonged_focal_seizures"] = choice

            if p.get("multiaxialdiagnosis__mental_health_issues") is not None:
                field_value = p.get("multiaxialdiagnosis__mental_health_issues")
                choice = return_choice_for_instance_and_value(
                    MultiaxialDiagnosis, "mental_health_issues", [field_value]
                )
                p["multiaxialdiagnosis__mental_health_issues"] = choice

            # write the formated data to a new row in the csv
            writer.writerow(p.values())

    return response


def return_choice_for_instance_and_value(model, field, choice_value):
    """
    Helper function when cleaning the data for downloadable csv files of the different models,
    accessed via the Frida button.
    """
    query_object = {field: choice_value}
    temp_instance = model(**query_object)
    choice = getattr(temp_instance, "get_{}_display".format(field))()
    return choice
