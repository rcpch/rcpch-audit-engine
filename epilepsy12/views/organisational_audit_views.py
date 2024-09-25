from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def group_form_fields(form):
    fields_by_question_number = {}

    ix = 0

    for field in form:
        # TODO MRB: put the help text on the form to avoid migrations every time it changes?
        help_text = OrganisationalAuditSubmission._meta.get_field(field.name).help_text or {}
        
        question_number = help_text.get("question_number", ix)
        parent_question_number = help_text.get("parent_question_number", None)
        
        parent = fields_by_question_number.get(parent_question_number, None)

        if parent:
            parent["children"].append({
                "field": field,
                "hidden": not parent["field"].value()
            })
        else:
            fields_by_question_number[question_number] = {
                "field": field,
                "children": []
            }
        
        ix += 1

    return fields_by_question_number


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
        "submission_period": submission_period,
        "fields_by_question_number": group_form_fields(form)
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

        context["fields_by_question_number"] = group_form_fields(form)
        form.save()

        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    return _organisational_audit(request, id, Trust, 'trust')

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    return _organisational_audit(request, id, LocalHealthBoard, 'local_health_board')