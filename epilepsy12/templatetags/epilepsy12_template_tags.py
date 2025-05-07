import re
import math
import json

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from ..models import (
    Country,
    IntegratedCareBoard,
    LocalHealthBoard,
    NHSEnglandRegion,
    Site,
    Trust,
)
from ..constants import ETHNICITIES, SEX_TYPE, KPI_LABEL_MAP

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
        return mark_safe(
            """Data Incomplete
            """
        )
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
    capitalised_words = [
        "Ii",
        "Rbh",
        "Nhs",
        "Cdc",
        "(Hq)",
        "(Epma)",
        "(Epact)",
        "Gstt",
        "Qmc",
        "Ctr",
    ]
    organisation_name = organisation_name.split()
    organisation_name = [
        name.upper() if name in capitalised_words else name
        for name in organisation_name
    ]
    organisation_name = " ".join(organisation_name)
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


@register.filter
def lead_site_for_case(case):
    """
    Returns all active sites for a given case
    """
    site = Site.objects.filter(
        case=case,
        site_is_actively_involved_in_epilepsy_care=True,
        site_is_primary_centre_of_epilepsy_care=True,
    ).first()
    if site:
        return site
    else:
        return None


@register.filter
def subtract(value, arg):
    """Subtracts the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def value_display(value, key):
    """
    Returns the display value for a given key in a dictionary
    """
    if key == "ethnicity":
        return dict(ETHNICITIES)[value]
    elif key == "sex":
        return dict(SEX_TYPE)[int(value)]

    if "_" in value:
        value_str, value_id = value.split("_", 1)
        if value_str == "country":
            return Country.objects.get(id=int(value_id)).name
        elif value_str == "nhsenglandregion":
            return NHSEnglandRegion.objects.get(id=int(value_id)).name
        elif value_str == "icb":
            return IntegratedCareBoard.objects.get(id=int(value_id)).name
        elif value_str == "t":
            return Trust.objects.get(id=int(value_id)).name
        elif value_str == "h":
            return LocalHealthBoard.objects.get(id=int(value_id)).name
    return value.replace("_", " ") if value else value


@register.filter
def get_item(dictionary, key):
    value_type, value_id = key.split("_", 1)
    """Get an item from a dictionary with the given key"""
    if value_id:
        return dictionary.get(value_id)


@register.filter
def make_list(value):
    """Convert a string to a list of characters"""
    return list(value)


@register.filter
def show_topiramate_valproate_fields(
    antiepilepsy_medicine_instance, pregnancy_prevention=False
):
    """
    Boolean function to show pregnancy prevention fields and risk acknowledgement form fields if
    - the medicine is topiramate and the child is 12 years or older
    - the medicine is sodium valproate and the child is a girl

    Note this only applies if the cohort is 7 or above
    """
    # Check if the antiepilepsy_medicine_instance is valid
    if antiepilepsy_medicine_instance.medicine_entity is None:
        return False

    # Get parameters from the antiepilepsy_medicine_instance
    cohort = antiepilepsy_medicine_instance.management.registration.cohort
    child_over_12 = (
        antiepilepsy_medicine_instance.management.registration.case.age_days()
        >= 365.25 * 12
    )
    is_valproate = (
        antiepilepsy_medicine_instance.medicine_entity.conceptId == "387481005"
    )  # Sodium valproate
    is_topiramate = (
        antiepilepsy_medicine_instance.medicine_entity.conceptId == "777808008"
    )  # Topiramate
    is_female = antiepilepsy_medicine_instance.management.registration.case.sex == 2

    if cohort < 7:
        if (
            antiepilepsy_medicine_instance.is_a_pregnancy_prevention_programme_needed
            or antiepilepsy_medicine_instance.has_a_valproate_annual_risk_acknowledgement_form_been_completed
        ):
            return True
    elif cohort >= 7:
        if is_topiramate or is_valproate:
            if pregnancy_prevention:
                if is_female and ((child_over_12 and is_topiramate) or is_valproate):
                    return True
            else:
                return True

    return False


@register.filter
def strip(value):
    if isinstance(value, str):
        return value.strip()
    return value


@register.simple_tag
def build_url_parameters(request, field, selected_field_value=None):
    """
    Build URL parameters, preserving existing ones, adding/removing/toggling
    the specified field, and handling multi-value 'kpi_failed'.

    Args:
        request: The HttpRequest object containing current GET parameters.
        field (str): The name of the parameter field to modify.
        selected_kpis (list): The list of currently selected KPI IDs (strings).
                                This argument is currently unused as logic relies
                                on modifying request.GET directly.
        selected_field_value (str, optional):
            - If field == 'kpi_failed', this is the specific KPI ID (str/int) to toggle.
            - If field != 'kpi_failed', this is the value to set for the field.
              If None, the field should be removed.
            Defaults to None.
    """
    # Create a mutable copy of the current GET parameters
    query_params = request.GET.copy()

    # 1. Always remove 'page' parameter to reset pagination
    if "page" in query_params:
        del query_params["page"]

    # 2. Handle the specified 'field'
    if field == "kpi_failed":
        # Handle multi-value KPI toggling
        # Assumes selected_field_value is the specific KPI ID to add or remove
        if selected_field_value is not None:
            kpi_to_toggle = str(selected_field_value)  # Ensure string comparison
            current_kpis = query_params.getlist("kpi_failed")

            if kpi_to_toggle in current_kpis:
                # KPI is currently selected, remove it
                current_kpis.remove(kpi_to_toggle)
            else:
                # KPI is not selected, add it
                current_kpis.append(kpi_to_toggle)

            # Update the QueryDict with the modified list
            if current_kpis:
                query_params.setlist(
                    "kpi_failed", sorted(list(set(current_kpis)))
                )  # Use set for uniqueness, sort for consistency
            elif "kpi_failed" in query_params:
                # Remove the key entirely if the list becomes empty
                del query_params["kpi_failed"]
        # If selected_field_value is None for kpi_failed, we do nothing based on current template usage.
        # The template always seems to pass the kpi_id to toggle.

    else:
        # Handle single-value fields
        if selected_field_value:
            # Add or update the field with the new value
            # Check if the value is already set to avoid redundant changes (optional)
            # if query_params.get(field) != str(selected_field_value):
            query_params[field] = selected_field_value
        else:
            # Remove the field if selected_field_value is None (signifying removal)
            if field in query_params:
                del query_params[field]

    # 3. Remove empty fields from the query string
    for key in list(query_params.keys()):
        if (
            not query_params.getlist(key)
            or query_params.getlist(key) == [""]
            or query_params.getlist(key) == ""
        ):
            del query_params[key]

    # 4. Encode the final query string
    final_query_string = query_params.urlencode()

    # Return the URL starting with '?'
    # Return just '?' if the final query string is empty
    return "?" + final_query_string if final_query_string else "?"


@register.filter
def kpi_key_to_readable_name(kpi_key):
    """
    Convert a KPI key to a human-readable name.
    """
    label = KPI_LABEL_MAP.get(kpi_key)
    return label if label else kpi_key


@register.filter
def field_key_to_readable_name(field_key):
    """
    Convert a field key to a human-readable name.
    """
    field_keys = {
        "search": "Search (NHS Number/URN/First Name/Surname/Epilepsy12 ID)",
        "ethnicity": "Ethnicity",
        "sex": "Sex",
        "index_of_multiple_deprivation_quintile": "Index of Multiple Deprivation Quintile",
        "trust_or_health_board": "Trust or Local Health Board",
        "integrated_care_board": "Integrated Care Board",
        "nhs_england_region": "NHS England Region",
        "country": "Country",
        "kpi_failed": "KPI",
        "audit_progress_complete": "Audit Progress Complete",
        "audit_progress_incomplete": "Audit Progress Incomplete",
        "registration_cohort": "Cohort",
        "has_support_for_mental_health_support": "Has support for mental health",
        "has_been_referred_for_mental_health_support": "Has been referred for mental health",
        "developmental_learning_or_schooling_problems": "Has developmental, learning or schooling problems",
        "behavioural_or_emotional_problems": "Has behavioural or emotional problems",
        "syndrome_present": "Syndrome present",
        "epilepsy_cause_known": "Epilepsy cause known",
        "global_developmental_delay_or_learning_difficulties": "Global developmental delay or learning difficulties",
        "autistic_spectrum_disorder": "Autistic spectrum disorder",
        "mental_health_issue_identified": "Mental health issue identified",
    }

    return field_keys.get(field_key, field_key)


@register.filter
def field_value_to_readable_name(field_value, field_key):
    """
    Convert a field value to a human-readable name.
    """
    if field_key == "kpi_failed":
        # Convert the field_value to a list of KPI keys
        return [
            f"{kpi_key_formatted(kpi_key=kpi_key)} - {kpi_key_to_readable_name(kpi_key)}"
            for kpi_key in field_value.split(",")
        ][0]
    elif field_value == "true":
        return ""
    elif field_key == "sex":
        return dict(SEX_TYPE)[int(field_value)]
    elif field_key == "ethnicity":
        return dict(ETHNICITIES)[field_value]
    elif field_key == "index_of_multiple_deprivation_quintile":
        if field_value == "1":
            return "1 - Most deprived"
        elif field_value == "5":
            return "5 - Least deprived"
        else:
            return f"{field_value}"
    elif field_key == "trust_or_health_board":
        # Extract the ID from the field_value
        key = field_value.split("_")[0]
        match = re.search(r"_(\d+)$", field_value)
        if match:
            id = match.group(1)
            # Get the corresponding object from the database
            if key == "h":
                try:
                    return LocalHealthBoard.objects.get(id=id).name
                except LocalHealthBoard.DoesNotExist:
                    return field_value
            elif key == "t":
                # Get the corresponding object from the database
                try:
                    return Trust.objects.get(id=id).name
                except Trust.DoesNotExist:
                    return field_value
            else:
                # Handle other cases or return the field_value as is
                return field_value
    elif field_key == "integrated_care_board":
        # Extract the ID from the field_value
        match = re.search(r"_(\d+)$", field_value)
        if match:
            id = match.group(1)
            # Get the corresponding object from the database
            try:
                return IntegratedCareBoard.objects.get(id=id).name
            except IntegratedCareBoard.DoesNotExist:
                return field_value
    elif field_key == "nhs_england_region":
        # Extract the ID from the field_value
        match = re.search(r"_(\d+)$", field_value)
        if match:
            id = match.group(1)
            # Get the corresponding object from the database
            try:
                return NHSEnglandRegion.objects.get(id=id).name
            except NHSEnglandRegion.DoesNotExist:
                return field_value
    elif field_key == "country":
        # Extract the ID from the field_value
        match = re.search(r"_(\d+)$", field_value)
        if match:
            id = match.group(1)
            # Get the corresponding object from the database
            try:
                return Country.objects.get(id=id).name
            except Country.DoesNotExist:
                return field_value
    else:
        # For other field keys, return the value as is
        return field_value


@register.filter
def kpi_key_formatted(kpi_key):
    """
    Convert a KPI key to a human-readable name.
    """
    chars = list(kpi_key.strip())
    last_two_chars = chars[-2:]
    number_component = "".join(char for char in kpi_key if char.isdigit())

    # iif one of the last two charts is a number, return the string untouched
    if any(char.isdigit() for char in last_two_chars):
        return kpi_key

    final_chars = chars[-1:][0]
    key_without_final_char = kpi_key[:-1]

    return f"{key_without_final_char}({final_chars})"


@register.filter
def kpi_category_title(kpi_key):
    """
    Convert a KPI key to a human-readable name.
    """
    # Extract the category from the KPI key
    # Extract the category from the KPI key
    if kpi_key == "1":
        return "Professional Input"
    elif kpi_key == "4":
        return "Appropriate Assessment"
    elif kpi_key == "6":
        return "Mental Health"
    elif kpi_key == "9a":
        return "Care Planning"
    else:
        return ""


@register.simple_tag
def kpi_has_category_title(kpi_key):
    """
    Convert a KPI key to a human-readable name.
    """
    if kpi_key == "1":
        return True
    else:
        return False
