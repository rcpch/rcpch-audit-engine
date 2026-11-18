from datetime import date, timedelta
from io import StringIO
from unittest.mock import patch

import pytest

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone

from epilepsy12.models import Case


@pytest.fixture
def superuser(e12_user_factory):
    user = e12_user_factory(is_superuser=True)
    user.refresh_from_db()
    return user


@pytest.mark.django_db
@override_settings(LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA=True)
def test_admin_dashboard_links_to_case_removal_tool(client, superuser):
    client.force_login(superuser)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert reverse("admin:remove_unregistered_cases") in response.content.decode()


@pytest.mark.django_db
@override_settings(LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA=True)
def test_case_removal_tool_previews_then_runs_command(client, superuser):
    client.force_login(superuser)
    url = reverse("admin:remove_unregistered_cases")
    before = date(2025, 1, 1)

    def write_preview(*args, stdout, **kwargs):
        stdout.write("[DRY RUN] 3 case(s) would be deleted")

    with patch("epilepsy12.admin.call_command", side_effect=write_preview) as command:
        response = client.post(url, {"action": "preview", "before": before.isoformat()})

    assert response.status_code == 200
    assert b"3 case(s) would be deleted" in response.content
    assert b"Delete matching cases" in response.content
    assert command.call_args.args == ("remove_unregistered_cases",)
    assert command.call_args.kwargs["before"] == before
    assert command.call_args.kwargs["dry_run"] is True

    def write_deletion(*args, stdout, **kwargs):
        stdout.write("Deleted 3 case(s).")

    with patch("epilepsy12.admin.call_command", side_effect=write_deletion) as command:
        response = client.post(url, {"action": "delete", "before": before.isoformat()})

    assert response.status_code == 302
    assert response.url == reverse("admin:index")
    assert command.call_args.args == ("remove_unregistered_cases",)
    assert command.call_args.kwargs["before"] == before
    assert command.call_args.kwargs["no_input"] is True


@pytest.mark.django_db
def test_case_removal_tool_rejects_non_superuser(e12_user_factory):
    request = RequestFactory().get("/")
    request.user = e12_user_factory(is_superuser=False)

    with pytest.raises(PermissionDenied):
        admin.site.remove_unregistered_cases_view(request)


@pytest.mark.django_db
def test_remove_unregistered_cases_no_input_deletes_without_prompt(e12_case_factory):
    case = e12_case_factory(registration=None)
    Case.objects.filter(pk=case.pk).update(
        created_at=timezone.now() - timedelta(days=2)
    )
    stdout = StringIO()

    with patch("builtins.input", side_effect=AssertionError("input called")):
        call_command(
            "remove_unregistered_cases",
            "--before",
            timezone.localdate().isoformat(),
            "--no-input",
            stdout=stdout,
        )

    assert not Case.objects.filter(pk=case.pk).exists()
    assert "Deleted 1 case(s)." in stdout.getvalue()
