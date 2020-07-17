from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import User


class TestGoogleAuthAPI(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             email='user1@example.com',
                                             password='admin123',
                                             last_name="test_last_name",
                                             username="test_username")

    def test_new_login_case1(self):
        """
        Test if New User gives permission to profile
        New email address along with other profile data
         is used to create user
                  '
        """
        data = {
            "first_name": "first_name",
            "last_name": "last_name",
            "email": "user2@example.com",
            "country_code": "91",
            "phone_number": "1231231231",
            "password": "admin123",
            "profile_picture_url": "http://www.google.com/123",
        }
        response = self.client.post(reverse('google_auth'),
                                    data=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue('refresh' in response_data)
        self.assertTrue('access' in response_data)

    def test_new_login_case2(self):
        """
        Test if User create API
        Send minimal data
        """
        response = self.client.post(reverse('google_auth'),
                                    data={'first_name': "test_name",
                                          'email': "user1@example.com"})
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue('refresh' in response_data)
        self.assertTrue('access' in response_data)

    def test_new_login_case3(self):
        """
        Test if User create API
        Dont send Email
        """
        response = self.client.post(reverse('google_auth'),
                                    data={"first_name": "test_name"})
        self.assertEqual(response.status_code, 400)

        error_message = response.json()
        self.assertEqual(len(error_message['email']), 1)
        self.assertEqual('This field is required.', error_message['email'][0])

    def test_new_login_case4(self):
        """
        Test if User create r API
        Send existing email, It should pass without creating new user
        """
        response = self.client.post(reverse('google_auth'),
                                    data={"first_name": "test_name",
                                          "email": "user1@example.com"})
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue('refresh' in response_data)
        self.assertTrue('access' in response_data)
