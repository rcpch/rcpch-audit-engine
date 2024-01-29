import re
import math

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.simple_tag
def percent_complete(registration):
    total = 0
    if registration.audit_progress.first_paediatric_assessment_complete:
        total += 12
    if registration.audit_progress.epilepsy_context_complete:
        total += 6
    if registration.audit_progress.multiaxial_diagnosis_complete:
        total += 6
    if registration.audit_progress.assessment_complete:
        total += 16
    if registration.audit_progress.investigations_complete:
        total += 4
    if registration.audit_progress.management_complete:
        total += 4
    return total


@register.simple_tag
def date_string(date):
    return date.strftime("%d %B %Y")


@register.simple_tag
def characters_left(description):
    length = 2000 - len(description)
    colour = "black"
    if length < 100:
        colour = "red"
    safe_text = f'<span style="color:{colour}">{length}</span>'
    return mark_safe(safe_text)


@register.simple_tag
def percentage_of_total(numerator, denominator):
    if numerator and denominator:
        if int(denominator) > 0:
            return round(int(numerator) / int(denominator) * 100)


@register.simple_tag
def kpi_for_kpi_name(aggregated_kpi, kpi_name, color=False):
    # guard clause check if color should be returned
    if color:
        return aggregated_kpi["color"]
    if aggregated_kpi["aggregated_kpis"][kpi_name] is None:
        return -1
    else:
        pct = (
            100
            * aggregated_kpi["aggregated_kpis"][kpi_name]
            / aggregated_kpi["aggregated_kpis"]["total_number_of_cases"]
        )
        return pct


@register.simple_tag
def kpi_average_for_kpi_name(aggregated_kpi, kpi_name):
    if aggregated_kpi["aggregated_kpis"][kpi_name] is None:
        return 0
    else:
        return aggregated_kpi["aggregated_kpis"][f"{kpi_name}_average"]


@register.simple_tag
def formatlabel(label):
    if label is None:
        return "Unclassified"
    else:
        nhs_icb_string = re.search(r"(NHS\s)(.+)(\sINTEGRATED CARE BOARD)", label)
        if nhs_icb_string:
            # \u002D fixes hyphen render for 'Stoke-on-trent'
            return nhs_icb_string.group(2).replace(r"\u002D", "-").title()
        return label


@register.filter
def custom_filter(text, color):
    safe_text = '<span style="color:{color}">{text}</span>'.format(
        color=color, text=text
    )
    return mark_safe(safe_text)


@register.simple_tag
def permission_text(add_permission, change_permission, delete_permission, model_name):
    return_string = "You do not have permission to"
    if add_permission:
        if change_permission and not delete_permission:
            return_string += f" delete {model_name}."
        elif not change_permission and delete_permission:
            return_string += f" edit {model_name}."
        elif not change_permission and not delete_permission:
            return_string += f" edit or delete {model_name}."
        else:
            return_string = ""
    else:
        if change_permission and not delete_permission:
            return_string += f" add or delete {model_name}."
        elif not change_permission and not delete_permission:
            return_string += f" add, edit or delete {model_name}."
        elif change_permission and delete_permission:
            return_string += f" add {model_name}."
        else:
            return_string = ""

    return return_string


@register.simple_tag
def matches_model_field(field_name, model):
    if field_name:
        value = getattr(model, field_name)
        if value:
            return True
        else:
            return False


@register.simple_tag
def wait_days_and_weeks(day_number):
    if day_number is None:
        return ""
    if day_number < 7:
        return f"{day_number} days"
    else:
        weeks = math.floor(day_number / 7)
        remaining_days = day_number - (weeks * 7)
        if remaining_days > 0:
            return f"{weeks} weeks, {remaining_days} days"
        else:
            return f"{weeks} weeks"


@register.filter
def is_in(url_name, args):
    """
    receives the request.resolver_match.url_name
    and compares with the template name (can be a list in a string separated by commas),
    returning true if a match is present
    """
    if args is None:
        return None
    arg_list = [arg.strip() for arg in args.split(",")]
    if url_name in arg_list:
        return True
    else:
        return False


@register.simple_tag
def match_two_values(val1, val2):
    """
    Matches two values
    """
    return val1 == val2


@register.simple_tag
def value_for_field_name(model, field_name, in_parentheses):
    """
    Returns the field value for a given field name in a model
    If in_parentheses is true, return the value in parentheses.
    """
    return_val = getattr(model, field_name, None)
    if in_parentheses:
        return_string = f"\n({return_val})"
    else:
        return_string = f"{return_val}"

    if return_val is not None:
        return return_string
    return ""


@register.filter
def record_complete(model):
    # helper largely for medicines table to report if complete or not

    minimum_requirement_met = False
    if hasattr(model, "medicine_entity"):
        if model.medicine_entity is not None:
            minimum_requirement_met = (
                model.antiepilepsy_medicine_start_date is not None
                and model.antiepilepsy_medicine_risk_discussed is not None
                and model.medicine_entity.medicine_name is not None
            )
            if (
                model.management.registration.case.sex == 2
                and model.medicine_entity.medicine_name == "Sodium valproate"
                and model.management.registration.case.age_days() >= 365 * 12
            ):
                return minimum_requirement_met and (
                    model.is_a_pregnancy_prevention_programme_needed is not None
                    and model.has_a_valproate_annual_risk_acknowledgement_form_been_completed
                    is not None
                    and model.is_a_pregnancy_prevention_programme_in_place is not None
                )

    return minimum_requirement_met


@register.filter
def to_class_name(value):
    if value.__class__.__name__ == "Registration":
        return "Verification/Registration"
    elif value.__class__.__name__ == "FirstPaediatricAssessment":
        return "First Paediatric Assessment"
    elif value.__class__.__name__ == "EpilepsyContext":
        return "Epilepsy Context"
    elif value.__class__.__name__ == "MultiaxialDiagnosis":
        return "Multiaxial Diagnosis"
    elif value.__class__.__name__ == "Assessment":
        return "Milestones"
    elif value.__class__.__name__ == "Investigations":
        return "Investigations"
    elif value.__class__.__name__ == "Management":
        return "Management"
    elif value.__class__.__name__ == "Site":
        return "Site"
    elif value.__class__.__name__ == "Episode":
        return "Episode"
    elif value.__class__.__name__ == "Syndrome":
        return "Syndrome"
    elif value.__class__.__name__ == "Comorbidity":
        return "Comorbidity"
    elif value.__class__.__name__ == "Epilepsy12User":
        return "Epilepsy12 User"
    elif value.__class__.__name__ == "Antiepilepsy Medicine":
        return "Antiepilepsy Medicine"
    else:
        return "Error"


@register.filter
def return_case(value):
    if value.__class__.__name__ == "Registration":
        return value.case
    elif value.__class__.__name__ == "FirstPaediatricAssessment":
        return value.registration.case
    elif value.__class__.__name__ == "EpilepsyContext":
        return value.registration.case
    elif value.__class__.__name__ == "MultiaxialDiagnosis":
        return value.registration.case
    elif value.__class__.__name__ == "Assessment":
        return value.registration.case
    elif value.__class__.__name__ == "Investigations":
        return value.registration.case
    elif value.__class__.__name__ == "Management":
        return value.registration.case
    elif value.__class__.__name__ == "Site":
        return value.case
    elif value.__class__.__name__ == "Episode":
        return value.multiaxial_diagnosis.registration.case
    elif value.__class__.__name__ == "Syndrome":
        return value.multiaxial_diagnosis.registration.case
    elif value.__class__.__name__ == "Comorbidity":
        return value.multiaxial_diagnosis.registration.case
    elif value.__class__.__name__ == "Epilepsy12User":
        return "Epilepsy12 User"
    elif value.__class__.__name__ == "Antiepilepsy Medicine":
        return value.management.registration.case
    else:
        return "Error"


@register.filter("has_group")
def has_group(user, group_names_string):
    # thanks to Lucas Simon for this efficiency
    # https://stackoverflow.com/questions/1052531/get-user-group-in-a-template
    """
    Check if user has permission
    """
    result = [x.strip() for x in group_names_string.split(",")]
    groups = user.groups.all().values_list("name", flat=True)
    match = False
    for group in groups:
        if group in result:
            match = True
    return match


@register.simple_tag
def none_masked(field):
    if field is None:
        return "##########"
    else:
        return field


@register.simple_tag
def none_percentage(field):
    if field is None:
        return "No data"
    else:
        return f"{field} %"


@register.filter(name="icon_for_score")
def icon_for_score(score):
    if score is None:
        return
    if score < 1:
        return mark_safe(
            """<i
                    class='rcpch_light_blue exclamation triangle icon'
                    data-title="Not achieved"
                    data-content="This measure has not been achieved for this child."
                    data-position="top right"
                    _="init js $('.rcpch_light_blue.exclamation.triangle.icon').popup(); end"
                ></i>
            """
        )
    elif score > 1:
        return mark_safe(
            """<i
                    class='rcpch_light_grey ban icon'
                    data-title="Not applicable"
                    data-content="This measure does not apply to this child."
                    data-position="top right"
                    _="init js $('.rcpch_light_grey.ban.icon').popup(); end"
                ></i>"""
        )
    elif score == 1:
        return mark_safe(
            """<i
                class='check circle outline rcpch_pink icon'
                data-title="Achieved"
                data-content="This child's care has met the Epilepsy12 standard for this measure."
                data-position="top right"
                _="init js $('.check.circle.outline.rcpch_pink.icon').popup(); end"
                ></i>
                """
        )
    else:
        return mark_safe(
            """<i
                class='rcpch dot circle icon'
                data-title="Unscored"
                data-content="This measure has not yet been scored."
                data-position="top right"
                _="init js $('.rcpch.dot.circle.icon').popup(); end"
                ></i>
                """
        )


@register.simple_tag
def get_region_name(region_data: tuple[str, dict]):
    return region_data[0]


@register.simple_tag
def get_kpi_pct_passed(region_data: tuple[str, dict]):
    data = region_data[1]

    # Find the KPI_NAME_passed key
    passed_key = [name for name in data.keys() if name.endswith("_passed")][0]
    total_eligible_key = [
        name for name in data.keys() if name.endswith("_total_eligible")
    ][0]

    return f"{100 * data[passed_key] / data[total_eligible_key]:.2f}"


@register.simple_tag
def get_pct_passed_and_total_eligible(aggregation_model, kpi: str):
    if not aggregation_model or (not aggregation_model.aggregation_performed()):
        return -1

    total_eligible_count = getattr(aggregation_model, f"{kpi}_total_eligible")

    if total_eligible_count == 0:
        return 0

    passed_count = getattr(aggregation_model, f"{kpi}_passed")

    pct_passed = round(100 * passed_count / total_eligible_count)

    return f"{pct_passed}% ({total_eligible_count})"


@register.simple_tag
def get_total_counts_passed(aggregation_model, kpi: str):
    if not aggregation_model.aggregation_performed():
        return mark_safe(
            "Aggregation not yet performed. This is most likely because there are no eligible data upon which to aggregate."
        )

    passed_count = getattr(aggregation_model, f"{kpi}_passed")

    total_eligible_count = getattr(aggregation_model, f"{kpi}_total_eligible")

    ineligible_count = getattr(aggregation_model, f"{kpi}_ineligible")
    incomplete_count = getattr(aggregation_model, f"{kpi}_incomplete")

    return mark_safe(
        f"""{passed_count} passed out of {total_eligible_count} total eligible children.

        Ineligible: {ineligible_count} children.
        Incomplete: {incomplete_count} children
        """
    )


@register.simple_tag
def get_help_label_text_for_kpi(kpi_name: str, kpi_instance):
    help_label_attribute_name = f"get_{kpi_name}_help_label_text"
    help_label_text_method = getattr(kpi_instance, help_label_attribute_name)
    return help_label_text_method()


@register.simple_tag
def get_help_reference_text_for_kpi(kpi_name: str, kpi_instance):
    help_reference_attribute_name = f"get_{kpi_name}_help_reference_text"
    help_reference_text_method = getattr(kpi_instance, help_reference_attribute_name)
    return help_reference_text_method()


@register.simple_tag
def render_title_kpi_name(kpi_name: str):
    return kpi_name.replace("_", " ")


@register.simple_tag
def get_pct_passed_for_kpi_from_agg_model(aggregation_model, kpi_name: str):
    if (aggregation_model is None) or (not aggregation_model.aggregation_performed()):
        return None

    pct_passed = aggregation_model.get_pct_passed_kpi(kpi_name=kpi_name)

    if pct_passed is None:
        return None

    return int(round(pct_passed * 100, 0))


@register.simple_tag
def get_n_passed_and_total(aggregation_model, kpi_name: str):
    if (aggregation_model is None) or (not aggregation_model.aggregation_performed()):
        return None

    passed = getattr(aggregation_model, f"{kpi_name}_passed")
    total = getattr(aggregation_model, f"{kpi_name}_total_eligible")

    return f"{passed} / {total}"


def _plural(num):
    if num == 1:
        return ""
    else:
        return "s"


@register.simple_tag
def no_eligible_cases(aggregation_model, kpi_name: str):
    n_ineligible = getattr(aggregation_model, f"{kpi_name}_ineligible")
    n_incomplete = getattr(aggregation_model, f"{kpi_name}_incomplete")

    return mark_safe(
        f"""No eligible Cases to score.<br>
        <b>{n_ineligible}</b> case{_plural(n_ineligible)} ineligible.<br>
        <b>{n_incomplete}</b> case{_plural(n_incomplete)} incomplete."""
    )


# A filter which fully capitalises specific words in the organisation name
# the list of which can be found in 'capitalised_words' below
@register.filter
def capitalise_org_names(organisation_name):
    capitalised_words = ['Ii', 'Rbh', 'Nhs', 'Cdc', '(Hq)', '(Epma)', '(Epact)', 'Gstt', 'Qmc', 'Ctr']
    organisation_name = organisation_name.split()
    organisation_name = [
        name.upper() if name in capitalised_words else name
        for name in organisation_name
    ]
    organisation_name = ' '.join(organisation_name)
    return mark_safe(organisation_name)


# TWO FACTOR TAGS
@register.filter
def get_org_id_from_user(user):
    if not user.organisation_employer:
        return 1

    return user.organisation_employer.id


@register.simple_tag
def site_contact_email():
    return settings.SITE_CONTACT_EMAIL
