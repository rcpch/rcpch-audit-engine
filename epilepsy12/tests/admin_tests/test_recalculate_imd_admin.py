from unittest.mock import patch

import pytest

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, override_settings
from django.urls import reverse

from epilepsy12.models import AuditPeriod


@pytest.fixture
def superuser(e12_user_factory):
    user = e12_user_factory(is_superuser=True)
    user.refresh_from_db()
    return user


@pytest.mark.django_db
@override_settings(LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA=True)
def test_admin_dashboard_links_to_recalculate_imd_tool(client, superuser):
    client.force_login(superuser)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
    assert reverse("admin:recalculate_imd") in response.content.decode()


@pytest.mark.django_db
@override_settings(LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA=True)
def test_recalculate_imd_tool_lists_cohorts(client, superuser):
    cohort = AuditPeriod.objects.exclude(cohort_number__isnull=True).first()
    if cohort is None:
        pytest.skip("No seeded audit periods")
    client.force_login(superuser)

    response = client.get(reverse("admin:recalculate_imd"))

    assert response.status_code == 200
    assert f"Cohort {cohort.cohort_number}" in response.content.decode()


@pytest.mark.django_db
@override_settings(LOCAL_DEV_BYPASS_2FA_AND_CAPTCHA=True)
@pytest.mark.parametrize(
    "cohort_value, expected_options",
    [("COHORT", "cohort"), ("all", "all_cohorts")],
)
def test_recalculate_imd_tool_previews_then_runs_command(
    client, superuser, cohort_value, expected_options
):
    audit_period = AuditPeriod.objects.exclude(cohort_number__isnull=True).first()
    if audit_period is None:
        pytest.skip("No seeded audit periods")
    if cohort_value == "COHORT":
        cohort_value = str(audit_period.cohort_number)
        expected = {"cohort": audit_period.cohort_number}
    else:
        expected = {"all_cohorts": True}

    client.force_login(superuser)
    url = reverse("admin:recalculate_imd")

    def write_preview(*args, stdout, **kwargs):
        stdout.write("[DRY RUN] 3 case(s) would have IMD recalculated.")

    with patch("epilepsy12.admin.call_command", side_effect=write_preview) as command:
        response = client.post(url, {"action": "preview", "cohort": cohort_value})

    assert response.status_code == 200
    assert b"3 case(s) would have IMD recalculated" in response.content
    assert b"Recalculate" in response.content
    assert command.call_args.args == ("recalculate_imd",)
    assert command.call_args.kwargs["dry_run"] is True
    for key, value in expected.items():
        assert command.call_args.kwargs[key] == value

    def write_run(*args, stdout, **kwargs):
        stdout.write("Done (cohort, 3 cases).")

    with patch("epilepsy12.admin.call_command", side_effect=write_run) as command:
        response = client.post(url, {"action": "run", "cohort": cohort_value})

    assert response.status_code == 302
    assert response.url == reverse("admin:index")
    assert command.call_args.args == ("recalculate_imd",)
    assert "dry_run" not in command.call_args.kwargs
    for key, value in expected.items():
        assert command.call_args.kwargs[key] == value


@pytest.mark.django_db
def test_recalculate_imd_tool_rejects_non_superuser(e12_user_factory):
    request = RequestFactory().get("/")
    request.user = e12_user_factory(is_superuser=False)

    with pytest.raises(PermissionDenied):
        admin.site.recalculate_imd_view(request)
