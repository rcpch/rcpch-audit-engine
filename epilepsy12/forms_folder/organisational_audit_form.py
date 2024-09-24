from django import forms
from ..models import OrganisationalAuditSubmission

class OrganisationalAuditSubmissionForm(forms.ModelForm):
    class Meta:
        model = OrganisationalAuditSubmission
        exclude = ["trust", "local_health_board"]
