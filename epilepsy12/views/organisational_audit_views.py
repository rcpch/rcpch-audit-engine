from django.shortcuts import render

from multiselectfield.utils import MSFList

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)


# On page load values are integers.
# For Mutiselect they're an multiselectfield.utils.MSFList.
# On POST values are strings (for multiselect a list of strings).
def get_selected_choice_indices_as_strings(field):
    if type(field.value()) == str:
        return [field.value()]
    elif type(field.value()) == int:
        return [str(field.value())]
    elif type(field.value()) in [list, MSFList]:
        return [str(value) for value in field.value()]
        
    return []

def show_child_field(parent, child):
    if not "field" in parent:
        return True
    
    field = parent["field"]
    model_field = OrganisationalAuditSubmission._meta.get_field(field.name)

    parent_value = field.value()
    required_parent_value = child.help_text.get("parent_question_value", True)

    # For normal fields, is the field set at all? (eg children dependent on a yes/no parent)
    if not model_field.choices:
        print(f"!! {field.name} {parent_value} == {required_parent_value}")
        return parent_value == required_parent_value

    selected_choices = get_selected_choice_indices_as_strings(field)
    other_choice_index = str(required_parent_value)

    print(f"!! {field.name} {other_choice_index} in {selected_choices}")

    return other_choice_index in selected_choices

def get_question_by_number(question_number, fields_by_question_number):
    def _get_question_by_number(question):
        if question["question_number"] == question_number:
            return question
        
        for child in question.get("children", []):
            result = _get_question_by_number(child)
            if result:
                return result

    for question in fields_by_question_number.values():
        result = _get_question_by_number(question)
        if result:
            return result

def group_by_section(fields_by_question_number):
    questions_by_section = {}

    for question in fields_by_question_number.values():
        section = question["section"]

        if not section in questions_by_section:
            questions_by_section[section] = []

        questions_by_section[section].append(question)

    return questions_by_section

def hoist_nested_children(fields_by_question_number):
    def _accumulate_nested_children(question, children):
        for child in question.get("children", []):
            children.append(child)
            _accumulate_nested_children(child, children)
        
        return children

    for question in fields_by_question_number.values():
        question["children"] = _accumulate_nested_children(question, [])

def group_form_fields(form):
    fields_by_question_number = {}

    ix = 0

    for field in form:
        model_field = OrganisationalAuditSubmission._meta.get_field(field.name)

        # TODO MRB: put the help text on the form to avoid migrations every time it changes?
        help_text = model_field.help_text or {}
        
        section = help_text.get("section", "Other")
        question_number = help_text.get("question_number", ix)
        parent_question_number = help_text.get("parent_question_number", None)
        
        parent = get_question_by_number(parent_question_number, fields_by_question_number)

        # Some questions like 3.5 don't have a direct representation in the model so construct them
        # from help text defined on the first child
        if parent_question_number and not parent:
            parent = {
                "section": section,
                "question_number": parent_question_number,
                "label": help_text.get("parent_question_label", None),
                "reference": help_text.get("parent_question_reference", None),
                "children": []
            }

            fields_by_question_number[parent_question_number] = parent

        print(f"!! {question_number} - parent: {parent}")

        if parent:
            parent["children"].append({
                "section": section,
                "field": field,
                "question_number": question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "hidden": not show_child_field(parent, field),
                "children": []
            })
        else:
            fields_by_question_number[question_number] = {
                "section": section,
                "field": field,
                "question_number": question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "children": []
            }
        
        ix += 1

    hoist_nested_children(fields_by_question_number)
    questions_by_section = group_by_section(fields_by_question_number)

    return questions_by_section


def _organisational_audit(request, group_id, group_model, group_field):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()

    group = group_model.objects.get(id=group_id)

    submission_filter = {
        "submission_period": submission_period
    }

    submission_filter[group_field] = group
    submission = OrganisationalAuditSubmission.objects.filter(**submission_filter).first()

    form = OrganisationalAuditSubmissionForm(instance=submission)

    context = {
        "group_name": group.name,
        "submission_period": submission_period
    }

    if request.method == "POST":
        if not submission:
            submission_args = {
                "submission_period": submission_period,
                "created_by": request.user
            }
            submission_args[group_field] = group

            submission = OrganisationalAuditSubmission.objects.create(**submission_args)

        form = OrganisationalAuditSubmissionForm(request.POST, instance=submission)
        submission = form.save()

        context["questions_by_section"] = group_form_fields(form)

        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)
    
    form = OrganisationalAuditSubmissionForm(instance=submission)
    context["questions_by_section"] = group_form_fields(form)

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    return _organisational_audit(request, id, Trust, 'trust')

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    return _organisational_audit(request, id, LocalHealthBoard, 'local_health_board')