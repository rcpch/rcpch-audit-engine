from django.test import TestCase
from django.contrib.auth import get_user_model


class Epilepsy12UserTests(TestCase):

    def test_new_superuser(self):
        # These are required fields: 'role', 'hospital_trust', 'username', 'first_name'
        db = get_user_model()
        superuser = db.objects.create_superuser(
            email="testuser@epilepsy12.com",
            username="epilepsy12user",
            password="epilepsy12password",
            first_name="John",
            role=1,
            hospital_trust="St Elsewhere"
        )
        self.assertEqual(
            superuser.email,
            "testuser@epilepsy12.com"
        )
        self.assertEqual(
            superuser.username,
            "epilepsy12user"
        )
        self.assertEqual(
            superuser.first_name,
            "John"
        )
        self.assertEqual(
            superuser.role,
            1
        )
        self.assertEqual(
            superuser.hospital_trust,
            "St Elsewhere"
        )
        self.assertTrue(
            superuser.is_superuser,
        )
        self.assertTrue(
            superuser.is_staff,
        )
        self.assertTrue(
            superuser.is_active,
        )
        self.assertEqual(
            str(superuser),
            "testuser@epilepsy12.com"
        )

        with self.assertRaises(ValueError):
            # set superuser to false
            db.objects.create_superuser(
                email="testuser@epilepsy12.com",
                username="epilepsy12user",
                password="epilepsy12password",
                first_name="John",
                role="Audit Analyst",
                hospital_trust="St Elsewhere",
                is_superuser=False
            )

        with self.assertRaises(ValueError):
            # set is_staff to false
            db.objects.create_superuser(
                email="testuser@epilepsy12.com",
                username="epilepsy12user",
                password="epilepsy12password",
                first_name="John",
                role=1,
                hospital_trust="St Elsewhere",
                is_staff=False
            )

        with self.assertRaises(ValueError):
            # set is_active to false
            db.objects.create_superuser(
                email="testuser@epilepsy12.com",
                username="epilepsy12user",
                password="epilepsy12password",
                first_name="John",
                role=1,
                hospital_trust="St Elsewhere",
                is_active=False
            )

    def test_new_user(self):

        db = get_user_model()

        user = db.objects.create_user(
            email="testuser@epilepsy12.com",
            username="epilepsy12user",
            password="epilepsy12password",
            title=4,
            first_name="Henry",
            surname="Gastaut",
            role=1,
            hospital_trust="St Elsewhere"
        )

        self.assertEqual(
            user.email,
            "testuser@epilepsy12.com"
        )
        self.assertEqual(
            user.username,
            "epilepsy12user"
        )
        self.assertEqual(
            user.first_name,
            "Henry"
        )
        self.assertEqual(
            user.surname,
            "Gastaut"
        )
        self.assertEqual(
            user.role,
            1
        )
        self.assertEqual(
            user.hospital_trust,
            "St Elsewhere"
        )
        self.assertFalse(
            user.is_staff,
        )
        self.assertFalse(
            user.is_active,
        )
        self.assertEqual(
            str(user),
            "testuser@epilepsy12.com"
        )
        self.assertEqual(
            user.get_full_name(),
            "Dr Henry Gastaut"
        )
        self.assertEqual(
            user.get_short_name(),
            "Henry"
        )
        self.assertFalse(
            user.is_superuser
        )

        with self.assertRaises(ValueError):
            # no email
            db.objects.create_user(
                email="",
                username="epilepsy12user",
                first_name="Henry",
                surname="Gastaut",
                title=4,
                password="epilepsy12password",
                role=1,
                hospital_trust="St Elsewhere"
            )
        with self.assertRaises(ValueError):
            # no hospital trust
            db.objects.create_user(
                email="testuser@epilepsy12.com",
                username="epilepsy12user",
                first_name="Henry",
                surname="Gastaut",
                title=4,
                password="epilepsy12password",
                role=1,
                hospital_trust=""
            )
        with self.assertRaises(ValueError):
            # no username
            db.objects.create_user(
                email="testuser@epilepsy12.com",
                username="",
                first_name="Henry",
                surname="Gastaut",
                title=4,
                password="epilepsy12password",
                role=1,
                hospital_trust="St Elsewhere"
            )
