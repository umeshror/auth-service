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

    def test_oauth2_200(self):
        """

        :return:
        """
        data = {'client_id': self.application.client_id,
                'client_secret': self.application.client_secret,
                'grant_type': 'password',
                'username': self.user.username,
                'password': 'admin123'}

        response = self.client.post(reverse("oauth2_provider:token"), data=data)

        self.assertEqual(response.status_code, 200, str(response.content))
        content = json.loads(response.content.decode("utf-8"))

        resp = self.client.get(reverse('users-list'),
                               HTTP_AUTHORIZATION="Bearer {}".format(content['access_token']))
        self.assertEqual(resp.status_code, 200, resp.content)
