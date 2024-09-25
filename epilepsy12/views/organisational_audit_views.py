from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def add_parent_relationships_to_form_fields(form):
    field_values_by_question_number = {}

    for field in form:
        help_text = OrganisationalAuditSubmission._meta.get_field(field.name).help_text or {}
        
        question_number = help_text.get("question_number", None)
        parent_question_number = help_text.get("parent_question_number", None)

        if question_number:
            field_values_by_question_number[question_number] = field.value()
        
        if parent_question_number in field_values_by_question_number and not field_values_by_question_number[parent_question_number]:
            field.hidden = True


def _organisational_audit(request, group_id, group_model, group_field):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()

    group = group_model.objects.get(id=group_id)

    submission_filter = {
        "submission_period": submission_period
    }

    submission_filter[group_field] = group
    submission = OrganisationalAuditSubmission.objects.filter(**submission_filter).first()

    form = OrganisationalAuditSubmissionForm(instance=submission)
    add_parent_relationships_to_form_fields(form)

    context = {
        "group_name": group.name,
        "submission_period": submission_period,
        "form": form
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
        add_parent_relationships_to_form_fields(form)

        context["form"] = form
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