from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .models import Case, Site


model_primary_keys = [
    {'id': 'case_id', 'model': 'Case'},
    {'id': 'registration_id', 'model': 'Registration'},
    {'id': 'initial_assessment_id', 'model': 'InitialAssessment'},
    {'id': 'epilepsy_context_id', 'model': 'EpilepsyContext'},
    {'id': 'multiaxial_diagnosis_id', 'model': 'MultiaxialDiagnosis'},
    {'id': 'episode_id', 'model': 'Episode'},
    {'id': 'syndrome_id', 'model': 'Syndrome'},
    {'id': 'comorbidity_id', 'model': 'Comorbidity'},
    {'id': 'assessment_id', 'model': 'Assessment'},
    {'id': 'investigations_id', 'model': 'Investigations'},
    {'id': 'management_id', 'model': 'Management'},
    {'id': 'antiepilepsy_medicine_id', 'model': 'AntiEpilepsyMedicine'},
]


def editor_access_for_this_child(*outer_args, **outer_kwargs):
    """
    Decorator for function based view.
    Receives argument outer_args which is a list of groups with access to view
    The inner function decorated() receives argument kwargs which is the view parameters and args (the request)
    The decorator uses the id passed into the view to identify the child and the request to get the user group
    If the user has editor access and the user is either a clinician at the same hospital, or an RCPCH administrator
    access is granted. 
    If access is denied, a PermissionDenied 403 error is raised which returns a custom 403 template
    """

    def decorator(fn):

        def decorated(request, **view_parameters):
            if view_parameters.get('registration_id') is not None:
                case = Case.objects.get(
                    registration=view_parameters.get('registration_id'))
            if view_parameters.get('case_id') is not None:
                case = Case.objects.get(pk=view_parameters.get('case_id'))

            view_only = request.user.groups.filter(name__in=[
                                                   'for_epilepsy12_audit_team_view_only', 'trust_audit_team_view_only', 'patient_access']).exists()

            authorisation = False

            if view_only:
                # You shall not pass!
                authorisation = False
            else:
                if request.user.is_rcpch_audit_team_member:
                    # user is an editor member of the RCPCH audit team
                    authorisation = True
                else:
                    # user is a clinician
                    if Site.objects.filter(
                        registration=case.registration,
                        site_is_actively_involved_in_epilepsy_care=True,
                        hospital_trust=request.user.hospital_employer
                    ).exists():
                        # user is involved in the care of this child

                        authorisation = True
                    else:
                        authorisation = False

            if authorisation:
                return fn(request, **view_parameters)
            else:
                raise PermissionDenied()
        return decorated
    return decorator
