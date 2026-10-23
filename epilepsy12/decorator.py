# python imports
import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import AccessMixin
from .models import (
    FirstPaediatricAssessment,
    MultiaxialDiagnosis,
    EpilepsyContext,
    Organisation,
    Investigations,
    Management,
    Registration,
    Case,
    Episode,
    Syndrome,
    AntiEpilepsyMedicine,
    Comorbidity,
    Assessment,
    Epilepsy12User,
)

from .constants import AUDIT_CENTRE_LEAD_CLINICIAN
from epilepsy12.common_view_functions.sanction_user_access import (
    organisation_white_list_for_user,
)
from epilepsy12.general_functions.audit_period_hierarchy import (
    expand_organisation_ids_via_identity,
    resolve_period_parent_for_field,
)

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


def _user_may_view_this_organisation(request, kwargs):
    user = request.user
    if kwargs.get("organisation_id") is not None:
        organisation_requested = Organisation.objects.get(
            pk=kwargs.get("organisation_id")
        )
        organisation_list = organisation_white_list_for_user(
            epilepsy12_user=user
        )
        if (
            (
                organisation_requested in organisation_list
                and user.is_active
                and user.email_confirmed
            )
            or user.is_superuser
            or user.is_rcpch_audit_team_member
        ):
            # user's has an organisation employer in the same trust or LHB as the organisation requested
            if kwargs.get("user_type") is not None:
                if kwargs.get("user_type") == "rcpch-staff" and not user.is_rcpch_staff:
                    # this route is for rcpch staff to create new rcpch staff members only
                    raise PermissionDenied()
            # user is allowed
        else:
            raise PermissionDenied()
    else:
        # organisation requested does not exist
        raise ValueError("Organisation requested does not exist!")


class OrganisationAccessMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        # Raises PermissionDenied
        _user_may_view_this_organisation(request, kwargs)
        return super().dispatch(request, *args, **kwargs)


def user_may_view_this_organisation():
    # decorator receives organisation_id.
    # access is granted only to users who are either:
    # 1. superusers
    # 2. Active RCPCH audit members
    # 3. Active trust/LHB level users where any trust/LHB they have access to includes the id of the organisation requested
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            _user_may_view_this_organisation(request, kwargs)
            return view(request, *args, **kwargs)

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


def _get_case_audit_period(child):
    """Return the ``Registration.audit_period`` for the child Case, or None.

    A case may not yet have a Registration (unregistered), or the
    Registration may not yet have an audit_period (first paediatric
    assessment date not set). In either case, period-aware access cannot
    apply and the caller must fall back to the current-organisation rule.
    """
    try:
        registration = child.registration
    except Registration.DoesNotExist:
        return None
    return registration.audit_period


def _user_has_direct_access(user, child):
    """Direct organisation access (PR 5).

    A user with active employment at an organisation may access all of that
    organisation's historical cases, irrespective of historical affiliation,
    including cases registered against a predecessor ODS code that shares
    the same ``OrganisationIdentity``.

    All of the user's active employers are considered (not just the
    primary one), consistent with ``organisation_white_list_for_user``.

    Before the cutover commands have run, no ``OrganisationIdentity`` links
    exist, so ``expand_organisation_ids_via_identity`` returns only the
    user's active employer IDs. This is a subset of the inherited
    trust-level check below, so the behaviour is unchanged (no-op).
    """
    employer_ids = list(
        Organisation.objects.filter(
            epilepsy12_users__epilepsy12_user=user,
            epilepsy12_users__is_active=True,
        ).values_list("pk", flat=True)
    )
    if not employer_ids:
        return False
    direct_org_ids = expand_organisation_ids_via_identity(employer_ids)
    return Organisation.objects.filter(
        pk__in=direct_org_ids,
        cases=child,
        patient_sites__site_is_actively_involved_in_epilepsy_care=True,
        patient_sites__site_is_primary_centre_of_epilepsy_care=True,
    ).exists()


def _user_has_inherited_access(user, child):
    """Inherited Trust/LHB access (PR 5).

    A user elsewhere in a Trust or LHB may access the child only for audit
    periods in which ``AuditPeriodOrganisation`` assigns the lead site
    organisation to that parent, and only for the parent the user is
    currently affiliated with.

    Before the cutover commands have run, no approved memberships exist.
    ``resolve_period_parent_for_field`` falls back to the current parent
    (``is_period_correct=False``), so the period-aware check is equivalent
    to the pre-foundation trust-level check and the behaviour is unchanged
    (no-op).

    When approved memberships exist but none match the user's parent, access
    is denied (the period-aware restriction). When no approved memberships
    exist, the pre-foundation current-trust check stands.
    """
    user_trust = user.organisation_employer.trust
    user_lhb = user.organisation_employer.local_health_board

    # Pre-foundation current trust/LHB check. For English users this filters
    # by trust; for Welsh users ``trust`` is None which matches all orgs with
    # no trust (the pre-foundation behaviour, preserved as the no-op
    # fallback).
    org_filters = {
        "cases": child,
        "patient_sites__site_is_actively_involved_in_epilepsy_care": True,
        "patient_sites__site_is_primary_centre_of_epilepsy_care": True,
        "trust": user_trust,
    }
    if not Organisation.objects.filter(**org_filters).exists():
        return False

    # Current check passes. Apply the period-aware restriction only when
    # approved memberships exist (post-cutover). Before cutover this is a
    # no-op.
    audit_period = _get_case_audit_period(child)
    if audit_period is None:
        return True  # No period — current behaviour

    lead_orgs = Organisation.objects.filter(
        cases=child,
        patient_sites__site_is_actively_involved_in_epilepsy_care=True,
        patient_sites__site_is_primary_centre_of_epilepsy_care=True,
    )

    has_approved_membership = False
    for lead_org in lead_orgs:
        if user_trust is not None:
            period_parent, is_period_correct = resolve_period_parent_for_field(
                lead_org, audit_period, "trust"
            )
            if is_period_correct:
                has_approved_membership = True
                if period_parent == user_trust:
                    return True
        if user_lhb is not None:
            period_parent, is_period_correct = resolve_period_parent_for_field(
                lead_org, audit_period, "local_health_board"
            )
            if is_period_correct:
                has_approved_membership = True
                if period_parent == user_lhb:
                    return True

    # If approved memberships exist but none matched the user's parent,
    # deny (period-aware restriction). If no approved memberships exist
    # (pre-cutover), the current-trust check above already passed.
    if has_approved_membership:
        return False
    return True


def lookup_child_if_user_has_permission(request_kwargs, user):
    # Guard against users with no active primary employer
    if not user.organisation_employer:
        return None

    via_registration = lambda obj: obj.registration.case
    via_multiaxial_dagnosis = lambda obj: obj.multiaxial_diagnosis.registration.case
    via_management = lambda obj: obj.management.registration.case

    lookup = {
        "registration_id": (Registration, lambda reg: reg.case),
        "management_id": (Management, via_registration),
        "investigations_id": (Investigations, via_registration),
        "first_paediatric_assessment_id": (FirstPaediatricAssessment, via_registration),
        "epilepsy_context_id": (EpilepsyContext, via_registration),
        "multiaxial_diagnosis_id": (MultiaxialDiagnosis, via_registration),
        "episode_id": (Episode, via_multiaxial_dagnosis),
        "syndrome_id": (Syndrome, via_multiaxial_dagnosis),
        "comorbidity_id": (Comorbidity, via_multiaxial_dagnosis),
        "antiepilepsy_medicine_id": (AntiEpilepsyMedicine, via_management),
        "assessment_id": (Assessment, via_registration),
        "case_id": (Case, lambda o: o),
    }

    for key, (model, via_fn) in lookup.items():
        pk = request_kwargs.get(key)

        if pk is not None:
            obj = model.objects.get(pk=pk)
            child = via_fn(obj)

            # Direct access across the OrganisationIdentity succession
            # chain takes precedence — a user employed at the current ODS
            # code may view cases registered against a predecessor ODS
            # code. No-op before cutover (identity expansion is a no-op).
            if _user_has_direct_access(user, child):
                return child

            # Inherited Trust/LHB access, period-aware when memberships
            # exist. No-op before cutover (falls back to current trust
            # check).
            if _user_has_inherited_access(user, child):
                return child


def lookup_user_permissions_on_child(request, request_kwargs):
    # Lookup sub object by id and walk backwards to case.
    # Access is granted only to users who are either:
    # 1. superusers
    # 2. Active RCPCH audit members with confirmed email
    # 3. Active trust level users with confirmed email where their trust is the same as the child
    # Editing is allowed if the cohort is still open or if you are an RCPCH audit member
    user = request.user

    # Check user is active and has confirmed their email (unless superuser)
    if not user.is_superuser and not (user.is_active and user.email_confirmed):
        return {
            "can_view": False,
            "can_edit": False,
        }

    is_admin = user.is_rcpch_audit_team_member or user.is_rcpch_staff or user.is_superuser

    if is_admin:
        return {
            "can_view": True,
            "can_edit": True,
        }

    child = lookup_child_if_user_has_permission(request_kwargs, request.user)

    if child:
        return {
            "can_view": True,
            "can_edit": child.editable(),
        }

    return {
        "can_view": False,
        "can_edit": False,
    }


def user_may_view_this_child():
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            permissions = lookup_user_permissions_on_child(request, kwargs)

            if request.method not in ["GET", "HEAD", "OPTIONS"] and not permissions["can_edit"]:
                raise PermissionDenied()

            if permissions["can_view"]:
                return view(request, permissions["can_edit"], *args, **kwargs)

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
                or request.user.organisation_employer
                in organisation_white_list_for_user(user_to_edit)
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
        def wrapper(request, *args, **kwargs):
            # Then, ensure 2fa verified
            user = request.user
            # Bypass 2fa if local dev, with warning message
            if settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA and user.is_authenticated:
                logger.warning(
                    "User %s has bypassed 2FA for %s as settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA is %s",
                    user,
                    view,
                    settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA,
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

        return login_required(wrapper)

    return decorator


class LoginAndOTPRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # Check if the user is authenticated
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Bypass 2fa if local dev, with warning message
        if settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA and user.is_authenticated:
            logger.warning(
                "User %s has bypassed 2FA for %s as settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA is %s",
                user,
                self.__class__.__name__,
                settings.LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA,
            )
            return super().dispatch(request, *args, **kwargs)

        # Prevent unverified users
        if not user.is_verified():
            user_list = user.__dict__
            epilepsy12_user = user_list["_wrapped"]
            logger.info(
                "User %s is unverified. Tried accessing %s",
                epilepsy12_user,
                self.__class__.__name__,
            )
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)
