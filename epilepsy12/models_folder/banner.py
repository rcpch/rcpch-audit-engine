import nh3
from django.core.exceptions import ValidationError
from django.db import models

from epilepsy12.constants.user_types import ROLES

class Banner(models.Model):
    url_matcher = models.CharField(max_length=255)
    html = models.TextField()
    disabled = models.BooleanField(default=False)

    # Only show the banner if the user has a given role (eg Lead Clinicians to see Org Audit banner)
    # RCPCH audit team members always see banners so they can check how they look
    user_role_to_target = models.PositiveSmallIntegerField(choices=ROLES, blank=True, null=True)

    def clean(self):
        super().clean()
        # Reject HTML that nh3 would alter, rather than silently stripping it.
        # Banners are admin-only, so surface the issue for them to fix.
        if self.html:
            cleaned = nh3.clean(self.html)
            if cleaned != self.html:
                raise ValidationError({
                    "html": (
                        "This HTML contains content that would be removed by "
                        "sanitisation (e.g. scripts or disallowed tags/attributes). "
                        "Please fix the HTML and resubmit. Sanitised version:\n"
                        f"{cleaned}"
                    )
                })

    def save(self, *args, **kwargs):
        # Defence-in-depth: sanitise on save in case save() is called without
        # clean() (e.g. via shell or scripts).
        if self.html:
            self.html = nh3.clean(self.html)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Banner for {self.url_matcher}"