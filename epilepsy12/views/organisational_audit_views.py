from django.shortcuts import render

from ..models import Trust, LocalHealthBoard, OrganisationalAuditSubmissionPeriod, OrganisationalAuditSubmission
from ..forms_folder import OrganisationalAuditSubmissionForm

from ..decorator import (
    login_and_otp_required,
    user_may_view_organisational_audit
)

def _organisational_audit(request, group, group_field, submission_period, submission):
    context = {
        "group_name": group.name,
        "submission_period": submission_period,
        "form": OrganisationalAuditSubmissionForm(instance=submission)
    }

    if request.method == "POST":
        if not submission:
            submission_args = {
                'submission_period': submission_period
            }
            submission_args[group_field] = group

            submission = OrganisationalAuditSubmission.objects.create(**submission_args)

        context["form"] = OrganisationalAuditSubmissionForm(request.POST, instance=submission)
        context["form"].save()

        return render(request, "epilepsy12/partials/organisational_audit_form.html", context)

    return render(request, "epilepsy12/organisational_audit.html", context)

@login_and_otp_required()
@user_may_view_organisational_audit(Trust, "trust")
def organisational_audit_trust(request, id):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()

    trust = Trust.objects.get(id=id)

    submission = OrganisationalAuditSubmission.objects.filter(submission_period=submission_period, trust=trust).first()

    return _organisational_audit(request, trust, 'trust', submission_period, submission)

@login_and_otp_required()
@user_may_view_organisational_audit(LocalHealthBoard, "local_health_board")
def organisational_audit_local_health_board(request, id):
    submission_period = OrganisationalAuditSubmissionPeriod.objects.filter(is_open=True).order_by('-year').first()
    
    local_health_board = LocalHealthBoard.objects.get(id=id)

    submission = OrganisationalAuditSubmission.objects.filter(submission_period=submission_period, local_health_board=local_health_board).first()

    return _organisational_audit(request, local_health_board, 'local_health_board', submission_period, submission)