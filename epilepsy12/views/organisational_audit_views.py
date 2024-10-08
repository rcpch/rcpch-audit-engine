from django.shortcuts import render

from multiselectfield.utils import MSFList

from ..models import (
    Trust,
    LocalHealthBoard,
    OrganisationalAuditSubmissionPeriod,
    OrganisationalAuditSubmission,
)
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import login_and_otp_required, user_may_view_organisational_audit


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
    required_parent_value = child.help_text.get("parent_question_value", None)

    # For normal fields, is the field set at all? (eg children dependent on a yes/no parent)
    if not model_field.choices:
        if required_parent_value:
            return parent_value == required_parent_value
        elif parent_value == "0":
            return False
        else:
            return bool(parent_value)

    selected_choices = get_selected_choice_indices_as_strings(field)
    other_choice_index = str(required_parent_value)

    return other_choice_index in selected_choices


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

    for field in form:
        model_field = OrganisationalAuditSubmission._meta.get_field(field.name)

        submission = OrganisationalAuditSubmission.objects.filter(
            pk=form.instance.pk
        ).get()  # from should always be bound to an instance

        if getattr(submission, field.name):
            completed = True
            number_completed += 1
        else:
            completed = False

        # TODO MRB: put the help text on the form to avoid migrations every time it changes?
        help_text = field.help_text or model_field.help_text or {}

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
                "completed": completed,
            }

            fields_by_question_number[parent_question_number] = parent

        if parent:
            child = {
                "section": section,
                "field": field,
                "question_number": question_number,
                "hide_question_number": hide_question_number,
                "label": help_text.get("label", field.name),
                "reference": help_text.get("reference", None),
                "hidden": not show_child_field(parent, field),
                "is_child": True,
                "children": [],
                "completed": completed,
            }
            fields_by_question_number[question_number] = child
            parent["children"].append(child)

        else:
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

    return questions_by_section, number_completed, ix


def _organisational_audit(request, group_id, group_model, group_field):
    submission_period = (
        OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True)
        .order_by("-year")
        .first()
    )

    group = group_model.objects.get(id=group_id)

    submission_filter = {"submission_period": submission_period}

    submission_filter[group_field] = group
    submission = OrganisationalAuditSubmission.objects.filter(
        **submission_filter
    ).first()

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
