import json

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.models import Application
from rest_framework.test import APITestCase


class TestOAuth2(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             last_name="test_last_name",
                                             password='admin123',
                                             username="test_username")

        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost http://example.com",
            user=self.user,
            client_type="public",
            authorization_grant_type="password",
        )
        self.application.save()

    def test_oauth2_401(self):
        """
        Attempt GET without authentication
        """
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 401)

    def test_get_access_token_pass(self):
        """
        Get Access token with client_id, client_secret and credentials
        :return:
        """
        data = {'client_id': self.application.client_id,
                'client_secret': self.application.client_secret,
                'grant_type': 'password',
                'username': self.user.username,
                'password': 'admin123'}

        response = self.client.post(reverse("oauth2_provider:token"), data=data)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))

        resp = self.client.get(reverse('users-list'),
                               HTTP_AUTHORIZATION="Bearer {}".format(content['access_token']))
        self.assertEqual(resp.status_code, 200, resp.content)

    def test_get_access_token_fail(self):
        """
        Get Access token with wrong client_id
        """
        data = {'client_id': 'ZYDPLLBWSK3MVQJSIYHB1OR2JXCY0X2C5UJ2QAR2MAAIT5Q',
                'client_secret': self.application.client_secret,
                'grant_type': 'password',
                'username': self.user.username,
                'password': 'admin123'}

        response = self.client.post(reverse("oauth2_provider:token"), data=data)
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(content['error'], "invalid_client")
        self.assertEqual(response.status_code, 401)

    def test_get_refresh_token_pass(self):
        """
        Get Access token with client_id, client_secret and refresh_token
        """
        access_token_data = {'client_id': self.application.client_id,
                             'client_secret': self.application.client_secret,
                             'grant_type': 'password',  # grant_type is password now
                             'username': self.user.username,
                             'password': 'admin123'}
        response = self.client.post(reverse("oauth2_provider:token"), data=access_token_data)
        content = json.loads(response.content.decode("utf-8"))

        refresh_token_data = {'client_id': self.application.client_id,
                              'client_secret': self.application.client_secret,
                              'grant_type': 'refresh_token',  # grant_type is refresh_token now
                              'refresh_token': content['refresh_token'],
                              }
        response = self.client.post(reverse("oauth2_provider:token"), data=refresh_token_data)
        content = json.loads(response.content.decode("utf-8"))

        resp = self.client.get(reverse('users-list'),
                               HTTP_AUTHORIZATION="Bearer {}".format(content['access_token']))
        self.assertEqual(resp.status_code, 200, resp.content)
