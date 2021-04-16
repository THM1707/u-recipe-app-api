from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """ Test public user API """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test create user with valid payload successful """
        payload = {
            'email': 'test_user@gmail.com',
            'password': 'password',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_existed(self):
        """ Test creating a user that already existed fails """
        payload = {
            'email': 'test_user@gmail.com',
            'password': 'password',
            'name': 'Test name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that password must be more than 5 characters """
        payload = {
            'email': 'test_user@gmail.com',
            'password': 'pw',
            'name': 'Test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_existed = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_existed)

    def test_create_token_for_user(self):
        """ Test if user have token when created """
        payload = {
            'email': 'test_user@gmail.com',
            'password': 'password',
            'name': 'Test name'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that token is not created if invalid credentials are given """
        create_user(email='test_user@gmail.com', password='password')

        payload = {
            'email': 'test_user@gmail.com',
            'password': 'not_password',
            'name': 'Test name'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def create_token_no_user(self):
        """ Test token is not created if user not exist """
        payload = {
            'email': 'test_user@gmail.com',
            'password': 'not_password',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res)
        self.assertEqual(res, status.HTTP_400_BAD_REQUEST)

    def create_token_missing_fields(self):
        """ Test email and password are required """
        res = self.client.post(TOKEN_URL, {'email': '', 'password': ''})

        self.assertNotIn('token', res)
        self.assertEqual(res, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_authorized(self):
        """ Test that authentication is required for user """
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """ Test API requests that require authentication """

    def setUp(self) -> None:
        self.user = create_user(
            email='test@gmail.com',
            password='password',
            name='test'
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """ Test retrieving profile for authenticated user """
        rest = self.client.get(ME_URL)

        self.assertEqual(rest.status_code, status.HTTP_200_OK)
        self.assertEqual(rest.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """ Test post is not allowed on the me url """
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """ Test updating the user profile for authenticated user """
        payload = {'name': 'new_name', 'password': 'new_password'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
