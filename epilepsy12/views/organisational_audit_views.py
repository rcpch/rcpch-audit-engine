from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def is_child_field_hidden(parent):
    if not "field" in parent:
        return False
    
    parent_field = parent["field"]
    parent_model_field = OrganisationalAuditSubmission._meta.get_field(parent_field.name)

    if parent_model_field.choices:
        # Field values can be integers on page load but strings in request.POST
        field_value_str = str(parent_field.value())

        for (choice_id, choice_name) in parent_model_field.choices:
            choice_id_str = str(choice_id)

            if(choice_id_str == field_value_str):
                return choice_name != "Other"
        
        return False

    return not parent_field.value()

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

        if parent:
            parent["children"].append({
                "section": section,
                "field": field,
                "question_number": question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "hidden": is_child_field_hidden(parent),
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

        context["questions_by_section"] = group_form_fields(form)
        form.save()

        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)
    
    form = OrganisationalAuditSubmissionForm(instance=submission)
    context["questions_by_section"] = group_form_fields(form)

    for _, questions in context["questions_by_section"].items():
        for question in questions:
            print(f"!! {question['question_number']} {question.get('field', None)}")

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    return _organisational_audit(request, id, Trust, 'trust')

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    return _organisational_audit(request, id, LocalHealthBoard, 'local_health_board')