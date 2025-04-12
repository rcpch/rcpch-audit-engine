# python imports
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import (
    FirstPaediatricAssessment,
    MultiaxialDiagnosis,
    EpilepsyContext,
    Organisation,
    Investigations,
    Management,
    Registration,
    Case,
    Site,
    Episode,
    Syndrome,
    AntiEpilepsyMedicine,
    Comorbidity,
    Assessment,
    Epilepsy12User,
)

from .constants import AUDIT_CENTRE_LEAD_CLINICIAN

# Logging setup
logger = logging.getLogger(__name__)

model_primary_keys = [
    {"id": "case_id", "model": "Case"},
    {"id": "registration_id", "model": "Registration"},
    {"id": "first_paediatric_assessment", "model": "FirstPaediatricAssessment"},
    {"id": "epilepsy_context_id", "model": "EpilepsyContext"},
    {"id": "multiaxial_diagnosis_id", "model": "MultiaxialDiagnosis"},
    {"id": "episode_id", "model": "Episode"},
    {"id": "syndrome_id", "model": "Syndrome"},
    {"id": "comorbidity_id", "model": "Comorbidity"},
    {"id": "assessment_id", "model": "Assessment"},
    {"id": "investigations_id", "model": "Investigations"},
    {"id": "management_id", "model": "Management"},
    {"id": "antiepilepsy_medicine_id", "model": "AntiEpilepsyMedicine"},
]


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
            if user.is_active and (
                user.is_superuser or bool(user.groups.filter(name__in=group_names))
            ):
                # user is in either a trust level or an RCPCH level group but in the correct group otherwise.
                if kwargs.get("registration_id") is not None:
                    registration = Registration.objects.get(
                        pk=kwargs.get("registration_id")
                    )
                    child = registration.case
                elif kwargs.get("management_id") is not None:
                    management = Management.objects.get(pk=kwargs.get("management_id"))
                    child = management.registration.case
                elif kwargs.get("investigations_id") is not None:
                    investigations = Investigations.objects.get(
                        pk=kwargs.get("investigations_id")
                    )
                    child = investigations.registration.case
                elif kwargs.get("first_paediatric_assessment_id") is not None:
                    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
                        pk=kwargs.get("first_paediatric_assessment_id")
                    )
                    child = first_paediatric_assessment.registration.case
                elif kwargs.get("epilepsy_context_id") is not None:
                    epilepsy_context = EpilepsyContext.objects.get(
                        pk=kwargs.get("epilepsy_context_id")
                    )
                    child = epilepsy_context.registration.case
                elif kwargs.get("multiaxial_diagnosis_id") is not None:
                    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
                        pk=kwargs.get("multiaxial_diagnosis_id")
                    )
                    child = multiaxial_diagnosis.registration.case
                elif kwargs.get("episode_id") is not None:
                    episode = Episode.objects.get(pk=kwargs.get("episode_id"))
                    child = episode.multiaxial_diagnosis.registration.case
                elif kwargs.get("syndrome_id") is not None:
                    syndrome = Syndrome.objects.get(pk=kwargs.get("syndrome_id"))
                    child = syndrome.multiaxial_diagnosis.registration.case
                elif kwargs.get("comorbidity_id") is not None:
                    comorbidity = Comorbidity.objects.get(
                        pk=kwargs.get("comorbidity_id")
                    )
                    child = comorbidity.multiaxial_diagnosis.registration.case
                elif kwargs.get("antiepilepsy_medicine_id") is not None:
                    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
                        pk=kwargs.get("antiepilepsy_medicine_id")
                    )
                    child = antiepilepsy_medicine.management.registration.case
                elif kwargs.get("case_id") is not None:
                    case = Case.objects.get(pk=kwargs.get("case_id"))
                    child = case

                # else:
                #     child = Case.objects.get(pk=kwargs.get('case_id'))

                if user.is_rcpch_audit_team_member:
                    organisation = Organisation.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                        active=True,
                    )
                else:
                    # filter for object where trust (not just organisation) where case is registered is the same as that of user
                    organisation = Organisation.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                        trust=request.user.organisation_employer.trust,
                        active=True,
                    )

                if organisation.exists() or user.is_rcpch_audit_team_member:
                    return view(request, *args, **kwargs)
                else:
                    raise PermissionDenied()
            else:
                raise PermissionDenied()

        return wrapper

    return decorator


def user_may_view_this_organisation():
    # decorator receives organisation_id.
    # access is granted only to users who are either:
    # 1. superusers
    # 2. Active RCPCH audit members
    # 3. Active trust level users where their trust matches the id of the organisation requested
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = request.user

            if kwargs.get("organisation_id") is not None:
                organisation_requested = Organisation.objects.get(
                    pk=kwargs.get("organisation_id")
                )
                if (user.is_active and user.email_confirmed) or user.is_superuser:
                    if (
                        user.is_rcpch_audit_team_member
                        or user.is_rcpch_staff
                        or user.is_superuser
                    ):
                        # RCPCH staff or E12 RCPCH staff can see all children across the UK
                        return view(request, *args, **kwargs)
                    else:
                        # regular user - not a member of RCPCH
                        if (
                            user.organisation_employer.country.boundary_identifier
                            == "W92000004"
                        ):
                            user_parent = user.organisation_employer.local_health_board
                        else:
                            user_parent = user.organisation_employer.trust

                        if (
                            organisation_requested.country.boundary_identifier
                            == "W92000004"
                        ):
                            organisation_requested_parent = (
                                organisation_requested.local_health_board
                            )
                        else:
                            organisation_requested_parent = organisation_requested.trust

                        if user_parent == organisation_requested_parent:
                            # user's employing trust is the same as the trust of the organisation requested
                            if kwargs.get("user_type") is not None:
                                if kwargs.get("user_type") == "rcpch-staff":
                                    # this route is for rcpch staff to create new rcpch staff members only
                                    raise PermissionDenied()
                            return view(request, *args, **kwargs)
                        else:
                            raise PermissionDenied()

                else:
                    # user is not active or email confirmed
                    raise PermissionDenied()
            else:
                raise ValueError("Organisation requested does not exist!")

        return wrapper

    return decorator


def user_may_view_organisational_audit(parent_model, parent_type):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = request.user

            requested_id = kwargs.get("id")
            parent = (
                getattr(user.organisation_employer, parent_type)
                if user.organisation_employer
                else None
            )

            can_view_parent = parent and parent.id == requested_id
            is_lead_clinican = user.role == AUDIT_CENTRE_LEAD_CLINICIAN

            if user.is_rcpch_audit_team_member or (
                can_view_parent and is_lead_clinican
            ):
                if not parent_model.objects.filter(id=requested_id).exists():
                    raise Http404

                return view(request, *args, **kwargs)

            raise PermissionDenied()

        return wrapper

    return decorator


def user_may_view_this_child():
    # decorator receives case_id or registration_id from view as argument.
    # access is granted only to users who are either:
    # 1. superusers
    # 2. Active RCPCH audit members
    # 3. Active trust level users where their trust is the same as the child
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if (user.is_active and user.email_confirmed) or user.is_superuser:
                # user is registered and active or a superuser
                if kwargs.get("registration_id") is not None:
                    registration = Registration.objects.get(
                        pk=kwargs.get("registration_id")
                    )
                    child = registration.case
                elif kwargs.get("management_id") is not None:
                    management = Management.objects.get(pk=kwargs.get("management_id"))
                    child = management.registration.case
                elif kwargs.get("investigations_id") is not None:
                    investigations = Investigations.objects.get(
                        pk=kwargs.get("investigations_id")
                    )
                    child = investigations.registration.case
                elif kwargs.get("first_paediatric_assessment_id") is not None:
                    first_paediatric_assessment = FirstPaediatricAssessment.objects.get(
                        pk=kwargs.get("first_paediatric_assessment_id")
                    )
                    child = first_paediatric_assessment.registration.case
                elif kwargs.get("epilepsy_context_id") is not None:
                    epilepsy_context = EpilepsyContext.objects.get(
                        pk=kwargs.get("epilepsy_context_id")
                    )
                    child = epilepsy_context.registration.case
                elif kwargs.get("multiaxial_diagnosis_id") is not None:
                    multiaxial_diagnosis = MultiaxialDiagnosis.objects.get(
                        pk=kwargs.get("multiaxial_diagnosis_id")
                    )
                    child = multiaxial_diagnosis.registration.case
                elif kwargs.get("episode_id") is not None:
                    episode = Episode.objects.get(pk=kwargs.get("episode_id"))
                    child = episode.multiaxial_diagnosis.registration.case
                elif kwargs.get("syndrome_id") is not None:
                    syndrome = Syndrome.objects.get(pk=kwargs.get("syndrome_id"))
                    child = syndrome.multiaxial_diagnosis.registration.case
                elif kwargs.get("comorbidity_id") is not None:
                    comorbidity = Comorbidity.objects.get(
                        pk=kwargs.get("comorbidity_id")
                    )
                    child = comorbidity.multiaxial_diagnosis.registration.case
                elif kwargs.get("antiepilepsy_medicine_id") is not None:
                    antiepilepsy_medicine = AntiEpilepsyMedicine.objects.get(
                        pk=kwargs.get("antiepilepsy_medicine_id")
                    )
                    child = antiepilepsy_medicine.management.registration.case
                elif kwargs.get("assessment_id") is not None:
                    assessment = Assessment.objects.get(pk=kwargs.get("assessment_id"))
                    child = assessment.registration.case
                elif kwargs.get("case_id") is not None:
                    case = Case.objects.get(pk=kwargs.get("case_id"))
                    child = case

                if user.is_rcpch_audit_team_member:
                    organisation = Organisation.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                    )
                else:
                    # filter for object where trust (not just organisation) where case is registered is the same as that of user
                    organisation = Organisation.objects.filter(
                        cases=child,
                        site__site_is_actively_involved_in_epilepsy_care=True,
                        site__site_is_primary_centre_of_epilepsy_care=True,
                        trust=request.user.organisation_employer.trust,
                    )

                if (
                    organisation.exists()
                    or user.is_rcpch_audit_team_member
                    or user.is_rcpch_staff
                    or user.is_superuser
                ):
                    return view(request, *args, **kwargs)
                else:
                    raise PermissionDenied()
            else:
                raise PermissionDenied()

        return wrapper

    return decorator


def rcpch_full_access_only():
    """
    Only permits access to rcpch_audit_team_full_access group members
    """

    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.groups.filter(name="epilepsy12_audit_team_full_access").exists():
                return view(request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return wrapper

    return decorator


def user_can_access_user():
    """
    Only permit people from the same organisation of the user being edited to access
    """

    def decorator(view):
        def wrapper(request, *args, **kwargs):
            user_to_edit_id = kwargs["epilepsy12_user_id"]
            user_to_edit = Epilepsy12User.objects.get(pk=user_to_edit_id)

            if (
                request.user.is_rcpch_audit_team_member
                or request.user.is_rcpch_staff
                or request.user.is_superuser
                or (
                    user_to_edit.organisation_employer.trust is not None
                    and user_to_edit.organisation_employer.trust
                    == request.user.organisation_employer.trust
                )
                or (
                    user_to_edit.organisation_employer.local_health_board is not None
                    and user_to_edit.organisation_employer.local_health_board
                    == request.user.organisation_employer.local_health_board
                )
            ):
                # allow access if user requesting acess is:
                # 1. a superuser
                # 2. rcpch_autdit_team_member
                # 3. rcpch_staff
                # 4. not 1-3 but is in the same trust as the user being accessed
                return view(request, *args, **kwargs)
            else:
                raise PermissionDenied()

        return wrapper

    return decorator


def login_and_otp_required():
    """
    Must have verified via 2FA
    """

    def decorator(view):
        # First use login_required on decorator
        login_required(view)

        def wrapper(request, *args, **kwargs):
            # Then, ensure 2fa verified
            user = request.user

            # Bypass 2fa if local dev, with warning message
            if settings.DEBUG and user.is_superuser:
                logger.warning(
                    "User %s has bypassed 2FA for %s as settings.DEBUG is %s and user is superuser",
                    user,
                    view,
                    settings.DEBUG,
                )
                return view(request, *args, **kwargs)

            # Prevent unverified users
            if not user.is_verified():
                user_list = user.__dict__
                epilepsy12_user = user_list["_wrapped"]
                logger.info(
                    "User %s is unverified. Tried accessing %s",
                    epilepsy12_user,
                    view.__qualname__,
                )
                raise PermissionDenied()

            return view(request, *args, **kwargs)

        return wrapper

    return decorator
