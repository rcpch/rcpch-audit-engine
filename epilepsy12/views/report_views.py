from collections import defaultdict

from django.shortcuts import render

from ..models import OrganisationalAuditSubmission, OrganisationalAuditSubmissionPeriod, Trust, LocalHealthBoard
from ..decorator import login_and_otp_required, rcpch_full_access_only

@login_and_otp_required()
@rcpch_full_access_only()
def submission_dashboard(request):
    org_audit_by_period_and_trust_lhb = defaultdict(dict)

    submissions = OrganisationalAuditSubmission.objects.select_related(
        'trust', 'local_health_board', 'submission_period'
    ).all()

    for submission in submissions:
        period = submission.submission_period
        if submission.trust:
            org_audit_by_period_and_trust_lhb[period][submission.trust.name] = submission
        elif submission.local_health_board:
            org_audit_by_period_and_trust_lhb[period][submission.local_health_board.name] = submission

    # Fill in the blanks
    periods = OrganisationalAuditSubmissionPeriod.objects.all()
    trusts = Trust.objects.all()
    lhbs = LocalHealthBoard.objects.all()

    for period in periods:
        for trust in trusts:
            if not trust.name in org_audit_by_period_and_trust_lhb[period]:
                org_audit_by_period_and_trust_lhb[period][trust.name] = None
        for lhb in lhbs:
            if not lhb.name in org_audit_by_period_and_trust_lhb[period]:
                org_audit_by_period_and_trust_lhb[period][lhb.name] = None

    # Sort
    for period in org_audit_by_period_and_trust_lhb:
        org_audit_by_period_and_trust_lhb[period] = dict(
            sorted(org_audit_by_period_and_trust_lhb[period].items())
        )
    
    org_audit_by_period_and_trust_lhb = dict(sorted(org_audit_by_period_and_trust_lhb.items(), key=lambda x: x[0].year, reverse=True))

    for period in org_audit_by_period_and_trust_lhb:
        for unit in org_audit_by_period_and_trust_lhb[period]:
            submission = org_audit_by_period_and_trust_lhb[period][unit]
            status = "No data"

            if submission:
                if submission.submitted:
                    status = "Submitted"
                else:
                    status = "In progress"
            org_audit_by_period_and_trust_lhb[period][unit] = status

    context = {"org_audit_by_period_and_trust_lhb": org_audit_by_period_and_trust_lhb}
    return render(request, "epilepsy12/submission_dashboard.html", context)