from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import User


class TestCreateUserAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             email='user1@example.com',
                                             password='admin123',
                                             last_name="test_last_name",
                                             username="test_username")

    def test_get_create_api_success(self):
        """
        Test if User create API
        New email address is used to create user
        It should pass as no user exist with given email address
        """
        resp = self.client.post(reverse('user-create'),
                                data={'first_name': "test_name",
                                      'email': "user2@example.com",
                                      'phone_number': 9876543210,
                                      'last_name': "test_last_name",
                                      'password': 'admin123'})
        self.assertEqual(resp.status_code, 201)

    def test_get_create_api_fail(self):
        """
        Test if User create API
        Existing email address is used to create user
        It should fail as user exist with given email address
        """
        resp = self.client.post(reverse('user-create'),
                                data={'first_name': "test_name",
                                      'email': "user1@example.com",
                                      'phone_number': 9876543210,
                                      'last_name': "test_last_name",
                                      'password': 'admin123'})
        self.assertEqual(resp.status_code, 400)
        error_message = resp.json()
        self.assertEqual(len(error_message['email']), 1)
        self.assertEqual('user with this email address already exists.', error_message['email'][0])
