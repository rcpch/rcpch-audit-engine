from django.core.exceptions import PermissionDenied
from epilepsy12.models import InitialAssessment, MultiaxialDiagnosis, EpilepsyContext, HospitalTrust, Investigations, Management, Registration, Case, Site, Episode, Syndrome
from epilepsy12.models.comorbidity import Comorbidity


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


def group_required(*group_names):
    # decorator receives case_id or registration_id from view and group name(s) as arguments.
    # if user is in the list of group_names supplied, access is granted, but only to
    # to those users who are either:
    # 1. superusers
    # 2. RCPCH audit members
    # 3. trust level access where their trust is the same as the child
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.is_active and (user.is_superuser or bool(user.groups.filter(name__in=group_names))):
                # user is in either a trust level or an RCPCH level group but in the correct group otherwise.
                if kwargs.get('registration_id') is not None:
                    registration = Registration.objects.get(
                        pk=kwargs.get('registration_id'))
                    child = registration.case
                elif kwargs.get('management_id') is not None:
                    management = Management.objects.get(
                        pk=kwargs.get('management_id'))
                    child = management.registration.case
                elif kwargs.get('investigations_id') is not None:
                    investigations = Investigations.objects.get(
                        pk=kwargs.get('investigations_id'))
                    child = investigations.registration.case
                elif kwargs.get('initial_assessment_id') is not None:
                    initial_assessment = InitialAssessment.objects.get(
                        pk=kwargs.get('initial_assessment_id'))
                    child = initial_assessment.registration.case
                elif kwargs.get('epilepsy_context_id') is not None:
                    epilepsy_context = EpilepsyContext.objects.get(
                        pk=kwargs.get('epilepsy_context_id'))
                    child = epilepsy_context.registration.case
                elif kwargs.get('multiaxial_diagnosis_id') is not None:
                    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
                        pk=kwargs.get('multiaxial_diagnosis_id'))
                    child = multiaxial_diagnosis.registration.case
                elif kwargs.get('episode_id') is not None:
                    episode = Episode.objects.get(
                        pk=kwargs.get('episode_id'))
                    child = episode.multiaxial_diagnosis.registration.case
                elif kwargs.get('syndrome_id') is not None:
                    syndrome = Syndrome.objects.get(
                        pk=kwargs.get('syndrome_id'))
                    child = syndrome.multiaxial_diagnosis.registration.case
                elif kwargs.get('comorbidity_id') is not None:
                    comorbidity = Comorbidity.objects.get(
                        pk=kwargs.get('comorbidity_id'))
                    child = comorbidity.multiaxial_diagnosis.registration.case
                elif kwargs.get('case_id') is not None:
                    case = Case.objects.get(
                        pk=kwargs.get('case_id'))
                    child = case
                # else:
                #     child = Case.objects.get(pk=kwargs.get('case_id'))

                if user.is_rcpch_audit_team_member:
                    hospital = HospitalTrust.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                    )
                else:
                    # filter for object where hospital where case is registered is the same as that of user
                    hospital = HospitalTrust.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                        ParentName=request.user.hospital_employer.ParentName
                    )

                if hospital.exists() or user.is_rcpch_audit_team_member:
                    return view(request, *args, **kwargs)
                else:
                    raise PermissionDenied()
            else:
                raise PermissionDenied()

        return wrapper
    return decorator
