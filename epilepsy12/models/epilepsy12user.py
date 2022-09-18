from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from epilepsy12.constants.user_types import ROLES, TITLES, AUDIT_CENTRE_LEAD_CLINICIAN, TRUST_AUDIT_TEAM_FULL_ACCESS, AUDIT_CENTRE_CLINICIAN, TRUST_AUDIT_TEAM_EDIT_ACCESS, AUDIT_CENTRE_ADMINISTRATOR, TRUST_AUDIT_TEAM_EDIT_ACCESS, RCPCH_AUDIT_LEAD, EPILEPSY12_AUDIT_TEAM_FULL_ACCESS, RCPCH_AUDIT_ANALYST, EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS, RCPCH_AUDIT_ADMINISTRATOR, EPILEPSY12_AUDIT_TEAM_VIEW_ONLY, RCPCH_AUDIT_PATIENT_FAMILY, PATIENT_ACCESS, TRUST_AUDIT_TEAM_VIEW_ONLY
from epilepsy12.models.hospital_trust import HospitalTrust


class Epilepsy12UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, username, first_name, hospital_employer, role, is_rcpch_audit_team_member, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('You must provide an email address'))
        if not username:
            raise ValueError(_('You must provide a username'))
        if not hospital_employer and not is_rcpch_audit_team_member:
            raise ValueError(
                _('You must provide the name of your main hospital trust.'))
        if not role:
            raise ValueError(
                _('You must provide your role in the Epilepsy12 audit.'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name,
                          role=role, hospital_employer=hospital_employer,  **extra_fields)
        user.set_password(password)
        """
        Allocate Roles
        """
        user.is_superuser = False
        if user.role == AUDIT_CENTRE_LEAD_CLINICIAN:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
            user.is_staff = True
        elif user.role == AUDIT_CENTRE_CLINICIAN:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            user.is_staff = True
        elif user.role == AUDIT_CENTRE_ADMINISTRATOR:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            user.is_staff = True
        elif user.role == RCPCH_AUDIT_LEAD:
            group = Group.objects.get(
                name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
        elif user.role == RCPCH_AUDIT_ANALYST:
            group = Group.objects.get(
                name=EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS)
        elif user.role == RCPCH_AUDIT_ADMINISTRATOR:
            group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_VIEW_ONLY)
        elif user.role == RCPCH_AUDIT_PATIENT_FAMILY:
            group = Group.objects.get(name=PATIENT_ACCESS)
        else:
            # no group
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
        user.save()
        user.groups.add(group)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_rcpch_audit_team_member', True)
        extra_fields.setdefault('has_rcpch_view_preference', True)
        hospital_trust = HospitalTrust.objects.filter(
            OrganisationID=41042).get()
        extra_fields.setdefault('hospital_employer', hospital_trust)

        if extra_fields.get('is_active') is not True:
            raise ValueError(_('Superuser must have is_active=True.'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        logged_in_user = self.create_user(email, password, **extra_fields)

        """
        Allocate Roles
        """

        if logged_in_user.role == AUDIT_CENTRE_LEAD_CLINICIAN:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_FULL_ACCESS)
            logged_in_user.is_staff = True
        elif logged_in_user.role == AUDIT_CENTRE_CLINICIAN:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            logged_in_user.is_staff = True
        elif logged_in_user.role == AUDIT_CENTRE_ADMINISTRATOR:
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_EDIT_ACCESS)
            logged_in_user.is_staff = True
        elif logged_in_user.role == RCPCH_AUDIT_LEAD:
            group = Group.objects.get(
                name=EPILEPSY12_AUDIT_TEAM_FULL_ACCESS)
        elif logged_in_user.role == RCPCH_AUDIT_ANALYST:
            group = Group.objects.get(
                name=EPILEPSY12_AUDIT_TEAM_EDIT_ACCESS)
        elif logged_in_user.role == RCPCH_AUDIT_ADMINISTRATOR:
            group = Group.objects.get(name=EPILEPSY12_AUDIT_TEAM_VIEW_ONLY)
        elif logged_in_user.role == RCPCH_AUDIT_PATIENT_FAMILY:
            group = Group.objects.get(name=PATIENT_ACCESS)
        else:
            # no group
            group = Group.objects.get(name=TRUST_AUDIT_TEAM_VIEW_ONLY)
        logged_in_user.groups.add(group)


class Epilepsy12User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(
        _("first name"),
        help_text=_("Enter your first name"),
        max_length=150,
        null=True,
        blank=True
    )
    surname = models.CharField(
        _('Surname'),
        help_text=_("Enter your surname"),
        max_length=150,
        null=True,
        blank=True
    )
    title = models.PositiveSmallIntegerField(
        choices=TITLES,
        blank=True,
        null=True
    )
    email = models.EmailField(
        _('email address'),
        help_text=_("Enter your email address."),
        unique=True
    )
    username = models.CharField(
        help_text="Select a unique username.",
        max_length=150,
        unique=True
    )
    bio = models.CharField(
        help_text=_("Share something about yourself."),
        max_length=500,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=False
    )
    is_staff = models.BooleanField(
        default=False
    )
    is_superuser = models.BooleanField(
        default=False
    )
    is_rcpch_audit_team_member = models.BooleanField(
        default=False
    )
    has_rcpch_view_preference = models.BooleanField(
        default=True
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLES,
        blank=True,
        null=True
    )
    twitter_handle = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    REQUIRED_FIELDS = ['role',
                       'username', 'first_name', 'surname', 'is_rcpch_audit_team_member']
    USERNAME_FIELD = 'email'

    objects = Epilepsy12UserManager()

    hospital_employer = models.ForeignKey(
        HospitalTrust,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    def get_full_name(self):
        title = self.get_title_display()
        concatenated_name = ''
        if title:
            concatenated_name += f'{title} '
        if self.first_name:
            concatenated_name += f'{self.first_name} '
        if self.surname:
            concatenated_name += f'{self.surname}'
        return concatenated_name

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        verbose_name = "Epilepsy12 User"
        verbose_name_plural = "Epilepsy12 Users"

    def __str__(self) -> str:
        return self.get_full_name()
