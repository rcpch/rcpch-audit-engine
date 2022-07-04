import site
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from epilepsy12.constants.user_types import PERMISSIONS, TITLES


class Epilepsy12UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, username, first_name, hospital_trust, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('You must provide an email address'))
        if not username:
            raise ValueError(_('You must provide a username'))
        if not hospital_trust:
            raise ValueError(
                _('You must provide the name of your main hospital trust.'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name,
                          hospital_trust=hospital_trust,  **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """

        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_active') is not True:
            raise ValueError(_('Superuser must have is_active=True.'))
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


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
        # this refers to members of the RCPCH audit team.
        default=False
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    hospital_trust = models.CharField(
        help_text=_("Enter your main hospital trust."),
        max_length=100
    )
    twitter_handle = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    REQUIRED_FIELDS = ['hospital_trust', 'username', 'first_name']
    USERNAME_FIELD = 'email'

    objects = Epilepsy12UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        title = self.get_title_display()
        return f"{title} {self.first_name} {self.surname}"

    def get_short_name(self):
        return self.first_name

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    class Meta:
        permissions = PERMISSIONS


"""
Different Epilepsy12 User groups
The basic user groups are:

Lead Clinician
Clinician (not lead)
Centre Administrator
Audit Lead Administrator
Audit Administrator
Audit Analyst
Patient
Parent

Each will have different permissions
The scope of permissions can be limited to a one or more centres
The Lead Clinician, Clinician or Centre administrator will have their scope limited to the hospitals they cover
The Audit Lead Administrator, Audit Administrator, Audit Analyst will have scope to cover all hospitals
Patients/Parents have their scope limited to their own data

Basic permissions for all groups involve viewing data within their own scope
Creating/updating/deleting rights are applied depending on group
Group allocation can only be performed by audit administrators or superusers
"""
