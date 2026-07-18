# Python imports
from datetime import date

# third-party imports
import pytest

# Django imports
from django.urls import reverse

# E12 imports
from epilepsy12.tests.UserDataClasses import test_user_rcpch_audit_team_data
from epilepsy12.tests.factories import E12CaseFactory
from epilepsy12.tests.view_tests.permissions_tests.perm_tests_utils import (
    twofactor_signin,
)
from epilepsy12.models import (
    Epilepsy12User,
    Organisation,
    AntiEpilepsyMedicine,
    Medicine,
)
from epilepsy12.common_view_functions.recalculate_form_generate_response import (
    completed_fields,
    number_of_completed_fields_in_related_models,
    total_fields_expected,
)


@pytest.mark.django_db
def test_management_htmx_workflow_does_not_overcount_conditional_medicine_fields(
    client, seed_groups_fixture, seed_users_fixture
):
    """
    End-to-end view test for the HTMX Management workflow:
    - toggle AED given
    - add non-rescue medicines
    - select medicine
    - set medicine start date and risk discussed
    - set conditional valproate/topiramate fields

    Then verify persisted AuditProgress and calculated totals do not overcount.
    """

    # Use the same org/user pattern as the other db action tests.
    test_user_org = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    case = E12CaseFactory.create(
        first_name=f"child_{test_user_org.name}",
        organisations__organisation=test_user_org,
        date_of_birth=date(2014, 1, 1),
        sex=2,
    )

    registration = case.registration
    registration.first_paediatric_assessment_date = date(2023, 5, 1)
    registration.audit_period.cohort_number = 6
    registration.save()

    management = registration.management

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )
    client.force_login(test_user)
    twofactor_signin(client, test_user)

    # 1) Toggle "has_an_aed_been_given" to True
    response = client.post(
        reverse("has_an_aed_been_given", kwargs={"management_id": management.id}),
        headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
    )
    assert response.status_code == 200

    # 2) Add three non-rescue medicine rows.
    for _ in range(3):
        response = client.post(
            reverse(
                "add_antiepilepsy_medicine",
                kwargs={
                    "management_id": management.id,
                    "is_rescue_medicine": "is_antiepilepsy_medicine",
                },
            ),
            headers={"Hx-Request": "true"},
        )
        assert response.status_code == 200

    medicines = list(
        AntiEpilepsyMedicine.objects.filter(
            management=management,
            is_rescue_medicine=False,
        ).order_by("id")
    )
    assert len(medicines) == 3

    valproate = Medicine.objects.get(conceptId="387481005")
    topiramate = Medicine.objects.get(conceptId="777808008")
    levetiracetam = Medicine.objects.get(medicine_name="Levetiracetam")

    selections = [valproate, topiramate, levetiracetam]

    for medicine_row, selected_medicine in zip(medicines, selections):
        # 3) Select medicine via the HTMX select endpoint.
        response = client.post(
            reverse(
                "medicine_id",
                kwargs={
                    "antiepilepsy_medicine_id": medicine_row.id,
                    "medicine_status": "epilepsy",
                },
            ),
            headers={"Hx-Request": "true"},
            data={"epilepsy_medicine_id": selected_medicine.id},
        )
        assert response.status_code == 200

        # 4) Set start date
        response = client.post(
            reverse(
                "antiepilepsy_medicine_start_date",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={
                "Hx-Trigger-Name": "antiepilepsy_medicine_start_date",
                "Hx-Request": "true",
            },
            data={"antiepilepsy_medicine_start_date": "2023-06-01"},
        )
        assert response.status_code == 200

        # 5) Risk discussed toggle True
        response = client.post(
            reverse(
                "antiepilepsy_medicine_risk_discussed",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

        # 6) Set conditional fields to True through the full HTMX path.
        response = client.post(
            reverse(
                "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

        response = client.post(
            reverse(
                "is_a_pregnancy_prevention_programme_in_place",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

    management.refresh_from_db()
    registration.refresh_from_db()
    audit_progress = registration.audit_progress
    audit_progress.refresh_from_db()
    assert audit_progress is not None

    all_completed_fields = completed_fields(
        management
    ) + number_of_completed_fields_in_related_models(management)
    all_expected_fields = total_fields_expected(management)

    # Invariant at the heart of this regression: never overcount completion.
    assert all_completed_fields <= all_expected_fields

    # End-to-end persistence check: view workflow wrote equivalent totals to AuditProgress.
    assert audit_progress.management_total_completed_fields == all_completed_fields
    assert audit_progress.management_total_expected_fields == all_expected_fields


@pytest.mark.django_db
def test_management_htmx_delete_and_readd_valproate_does_not_overcount(
    client, seed_groups_fixture, seed_users_fixture
):
    """
    End-to-end view test for the delete-and-readd Management medicine workflow:
    - add medicines and populate fields through HTMX
    - remove a valproate medicine row
    - re-add a new row and select valproate again

    Then verify persisted AuditProgress and calculated totals remain consistent,
    including completed <= expected.
    """

    test_user_org = Organisation.objects.get(ods_code="RP401", trust__ods_code="RP4")
    case = E12CaseFactory.create(
        first_name=f"child_readd_{test_user_org.name}",
        organisations__organisation=test_user_org,
        date_of_birth=date(2014, 1, 1),
        sex=2,
    )

    registration = case.registration
    registration.first_paediatric_assessment_date = date(2023, 5, 1)
    registration.audit_period.cohort_number = 6
    registration.save()

    management = registration.management

    test_user = Epilepsy12User.objects.get(
        first_name=test_user_rcpch_audit_team_data.role_str
    )
    client.force_login(test_user)
    twofactor_signin(client, test_user)

    response = client.post(
        reverse("has_an_aed_been_given", kwargs={"management_id": management.id}),
        headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
    )
    assert response.status_code == 200

    # Add two non-rescue medicine rows.
    for _ in range(2):
        response = client.post(
            reverse(
                "add_antiepilepsy_medicine",
                kwargs={
                    "management_id": management.id,
                    "is_rescue_medicine": "is_antiepilepsy_medicine",
                },
            ),
            headers={"Hx-Request": "true"},
        )
        assert response.status_code == 200

    medicines = list(
        AntiEpilepsyMedicine.objects.filter(
            management=management,
            is_rescue_medicine=False,
        ).order_by("id")
    )
    assert len(medicines) == 2

    valproate = Medicine.objects.get(conceptId="387481005")
    levetiracetam = Medicine.objects.get(medicine_name="Levetiracetam")

    # Populate first row as valproate and second as levetiracetam.
    for medicine_row, selected_medicine in zip(medicines, [valproate, levetiracetam]):
        response = client.post(
            reverse(
                "medicine_id",
                kwargs={
                    "antiepilepsy_medicine_id": medicine_row.id,
                    "medicine_status": "epilepsy",
                },
            ),
            headers={"Hx-Request": "true"},
            data={"epilepsy_medicine_id": selected_medicine.id},
        )
        assert response.status_code == 200

        response = client.post(
            reverse(
                "antiepilepsy_medicine_start_date",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={
                "Hx-Trigger-Name": "antiepilepsy_medicine_start_date",
                "Hx-Request": "true",
            },
            data={"antiepilepsy_medicine_start_date": "2023-06-01"},
        )
        assert response.status_code == 200

        response = client.post(
            reverse(
                "antiepilepsy_medicine_risk_discussed",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

        response = client.post(
            reverse(
                "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

        response = client.post(
            reverse(
                "is_a_pregnancy_prevention_programme_in_place",
                kwargs={"antiepilepsy_medicine_id": medicine_row.id},
            ),
            headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
        )
        assert response.status_code == 200

    deleted_row_id = medicines[0].id
    response = client.post(
        reverse(
            "remove_antiepilepsy_medicine",
            kwargs={"antiepilepsy_medicine_id": deleted_row_id},
        ),
        headers={"Hx-Request": "true"},
    )
    assert response.status_code == 200
    assert not AntiEpilepsyMedicine.objects.filter(id=deleted_row_id).exists()

    # Re-add a new row and select valproate again.
    response = client.post(
        reverse(
            "add_antiepilepsy_medicine",
            kwargs={
                "management_id": management.id,
                "is_rescue_medicine": "is_antiepilepsy_medicine",
            },
        ),
        headers={"Hx-Request": "true"},
    )
    assert response.status_code == 200

    replacement_row = (
        AntiEpilepsyMedicine.objects.filter(
            management=management,
            is_rescue_medicine=False,
        )
        .order_by("-id")
        .first()
    )
    assert replacement_row is not None

    response = client.post(
        reverse(
            "medicine_id",
            kwargs={
                "antiepilepsy_medicine_id": replacement_row.id,
                "medicine_status": "epilepsy",
            },
        ),
        headers={"Hx-Request": "true"},
        data={"epilepsy_medicine_id": valproate.id},
    )
    assert response.status_code == 200

    response = client.post(
        reverse(
            "antiepilepsy_medicine_start_date",
            kwargs={"antiepilepsy_medicine_id": replacement_row.id},
        ),
        headers={
            "Hx-Trigger-Name": "antiepilepsy_medicine_start_date",
            "Hx-Request": "true",
        },
        data={"antiepilepsy_medicine_start_date": "2023-07-01"},
    )
    assert response.status_code == 200

    response = client.post(
        reverse(
            "antiepilepsy_medicine_risk_discussed",
            kwargs={"antiepilepsy_medicine_id": replacement_row.id},
        ),
        headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
    )
    assert response.status_code == 200

    response = client.post(
        reverse(
            "has_a_valproate_annual_risk_acknowledgement_form_been_completed",
            kwargs={"antiepilepsy_medicine_id": replacement_row.id},
        ),
        headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
    )
    assert response.status_code == 200

    response = client.post(
        reverse(
            "is_a_pregnancy_prevention_programme_in_place",
            kwargs={"antiepilepsy_medicine_id": replacement_row.id},
        ),
        headers={"Hx-Trigger-Name": "button-true", "Hx-Request": "true"},
    )
    assert response.status_code == 200

    management.refresh_from_db()
    registration.refresh_from_db()
    audit_progress = registration.audit_progress
    audit_progress.refresh_from_db()
    assert audit_progress is not None

    all_completed_fields = completed_fields(
        management
    ) + number_of_completed_fields_in_related_models(management)
    all_expected_fields = total_fields_expected(management)

    assert all_completed_fields <= all_expected_fields
    assert audit_progress.management_total_completed_fields == all_completed_fields
    assert audit_progress.management_total_expected_fields == all_expected_fields
