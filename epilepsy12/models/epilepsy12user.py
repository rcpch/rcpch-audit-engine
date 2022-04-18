from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db import models

from epilepsy12.constants.user_types import ROLES, TITLES
from epilepsy12.models import hospital_trust


class Epilepsy12UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, username, first_name, hospital_trust, role, **extra_fields):
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
        if not role:
            raise ValueError(
                _('You must provide your role in the Epilepsy12 audit.'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name,
                          role=role, hospital_trust=hospital_trust,  **extra_fields)
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
        default=False
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLES,
        blank=True,
        null=True
    )
    hospital_trust = models.CharField(
        help_text=_("Enter the main hospital trust where you work."),
        max_length=100
    )
    twitter_handle = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    REQUIRED_FIELDS = ['role', 'hospital_trust', 'username', 'first_name']
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
