from collections.abc import Iterable

from django.shortcuts import render

from ..models import (
    Trust,
    LocalHealthBoard,
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
)
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import login_and_otp_required, user_may_view_organisational_audit


def show_child_field(parent, child):
    parent_value = parent.value()
    parent_choices = getattr(parent.field, "choices", None)

    if parent_choices:
        required_parent_value = child.help_text.get("parent_question_value", 'Y')

        if isinstance(parent_value, Iterable) and not type(parent_value) == str:
            # Multiselect - on page load is a MSFList, on POST is a list of strings
            parent_values = [str(value) for value in parent_value]
            return required_parent_value in parent_values
        else:
            # Single value choice
            return str(parent_value) == required_parent_value
    else:
        # Special case for 1.4 S01WTEEpilepsySpecialistNurses
        if parent_value == "0":
            return False
        
        return bool(parent_value)


def accumulate_children(question, parent_hidden):
    ret = []

    # If the parent is hidden the children should be too (for example nested Other options in 6.3 and 7.3)
    question["hidden"] = parent_hidden or question.get("hidden", parent_hidden)
    children = question.get("children", [])

    for child in children:
        ret.append(child)
        ret.extend(accumulate_children(child, parent_hidden=question["hidden"]))

    return ret


def group_questions(fields_by_question_number):
    questions_by_section = {}

    for question in fields_by_question_number.values():
        if question.get("is_child", False):
            continue

        section = question.get("section", "XX. Other")

        if not section in questions_by_section:
            questions_by_section[section] = []

        # Avoid writing recursive rendering code by bringing every child question up to their top level parent
        question["children"] = accumulate_children(question, parent_hidden=False)

        questions_by_section[section].append(question)

    return questions_by_section


def group_form_fields(form):
    # Loops trough the form fields and groups them by section and question number
    # The question number is taken from the help text of the field
    # This function is called with every field updated in the form and rerenders the form partial

    fields_by_question_number = {}

    ix = 0
    number_completed = 0
    total_questions = 0

    for field in form:
        if field.value() is not None and field.value() != "" and field.value() != []:
            completed = True
            number_completed += 1
        else:
            completed = False

        help_text = field.help_text or {}

        section = help_text.get("section", "Other")
        parent_question_number = help_text.get("parent_question_number", None)
        parent = fields_by_question_number.get(parent_question_number, None)

        question_number = help_text.get("question_number", None)
        hide_question_number = False

        if not question_number:
            question_number = f"XX.{ix}"
            hide_question_number = True

        # Some questions like 3.5 don't have a direct representation in the model so construct them
        # from help text defined on the first child
        if parent_question_number and not parent:
            parent = {
                "section": section,
                "question_number": parent_question_number,
                "label": help_text.get("parent_question_label", None),
                "reference": help_text.get("parent_question_reference", None),
                "children": [],
                # don't show a completed status
            }

            fields_by_question_number[parent_question_number] = parent

        if parent:
            # Synthesised parent question (Eg 3.5)
            if not "field" in parent:
                hidden = False
            else:
                hidden = not show_child_field(parent["field"], field)

            if not hidden:
                total_questions += 1

            child = {
                "section": section,
                "field": field,
                "question_number": question_number,
                "hide_question_number": hide_question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "hidden": hidden,
                "is_child": True,
                "children": [],
                "completed": completed,
            }
            fields_by_question_number[question_number] = child
            parent["children"].append(child)

        else:
            total_questions += 1

            fields_by_question_number[question_number] = {
                "section": section,
                "field": field,
                "question_number": question_number,
                "hide_question_number": hide_question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "children": [],
                "completed": completed,
            }

        ix += 1

    questions_by_section = group_questions(fields_by_question_number)

    return questions_by_section, number_completed, total_questions


def get_submission(submission_period, group, group_field):
    submission_filter = {"submission_period": submission_period}
    submission_filter[group_field] = group

    return OrganisationalAuditSubmission.objects.filter(
        **submission_filter
    ).first()


def _organisational_audit(request, group_id, group_model, group_field):
    submission_periods = (
        OrganisationalAuditSubmissionPeriod.objects
        .order_by("-year")
        .all()
    )

    if not submission_periods:
        submission_period = None
    elif len(submission_periods) == 1:
        submission_period = submission_periods[0]
        last_submission_period = None
    else:
        submission_period = submission_periods[0]
        last_submission_period = submission_periods[1]

    group = group_model.objects.get(id=group_id)

    submission = get_submission(submission_period, group, group_field)
    last_submission = get_submission(last_submission_period, group, group_field)

    form = OrganisationalAuditSubmissionForm(instance=submission)

    context = {"group_name": group.name, "submission_period": submission_period}

    if request.method == "POST":
        if not submission:
            submission_args = {
                "submission_period": submission_period,
                "created_by": request.user,
            }
            submission_args[group_field] = group

            submission = OrganisationalAuditSubmission.objects.create(**submission_args)

        form = OrganisationalAuditSubmissionForm(request.POST, instance=submission)
        submission = form.save()

        questions_by_section, number_completed, total_questions = group_form_fields(
            form
        )
        context["questions_by_section"] = questions_by_section
        context["number_completed"] = number_completed
        context["total_questions"] = total_questions
        context["percentage_completed"] = int(
            (number_completed / total_questions) * 100
        )

        return render(
            request, "epilepsy12/partials/organisational_audit_form.html", context
        )

    form = OrganisationalAuditSubmissionForm(instance=submission)

    questions_by_section, number_completed, total_questions = group_form_fields(form)
    context["questions_by_section"] = questions_by_section
    context["number_completed"] = number_completed
    context["total_questions"] = total_questions
    context["percentage_completed"] = int((number_completed / total_questions) * 100)
    context["form"] = form

    return render(request, "epilepsy12/organisational_audit.html", context)


@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    return _organisational_audit(request, id, Trust, "trust")


@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    return _organisational_audit(request, id, LocalHealthBoard, "local_health_board")
