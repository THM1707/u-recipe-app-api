from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTest(TestCase):
    def test_create_user_with_email(self):
        """Check if new user created successfully"""
        email = 'example@gmail.com'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ Test if email for new user is normalized """
        email = 'example@gmail.COM'
        password = 'password'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ Test create user with invalid email error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'password')

    def test_create_new_superuser(self):
        """ Test creating new superuser """
        user = get_user_model().objects.create_superuser('super@gmail.com', 'password')

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
