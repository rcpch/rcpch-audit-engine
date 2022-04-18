from datetime import date
from django.test import TestCase
from ..models import Case


class CaseTests(TestCase):

    def setUp(self) -> None:
        Case.objects.create(
            nhs_number=2345456123,
            first_name="Fyodor",
            surname="Dostoyevsky",
            gender=1,
            date_of_birth=date(2009, 11, 5),
            postcode="WC1X 8SH",
            locked=False,
            ethnicity="A"
        )

    def test_case_valid(self):
        fyodor = Case.objects.get(first_name="Fyodor")

        self.assertEqual(
            fyodor.first_name,
            "Fyodor"
        )
        self.assertEqual(
            fyodor.surname,
            "Dostoyevsky"
        )
        self.assertEqual(
            fyodor.gender,
            1
        )
        self.assertEqual(
            fyodor.date_of_birth,
            date(2009, 11, 5)
        )
        self.assertEqual(
            fyodor.postcode,
            "WC1X 8SH"
        )
        self.assertEqual(
            fyodor.ethnicity,
            "A"
        )
        self.assertFalse(
            fyodor.locked
        )
        self.assertEqual(
            str(fyodor),
            "Fyodor Dostoyevsky"
        )
