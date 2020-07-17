import datetime
import json

from django.urls import reverse
from django.utils import timezone
from oauth2_provider.models import Application, AccessToken
from rest_framework.test import APITestCase

from apps.core.models import User


class TestOAuth2(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             last_name="test_last_name",
                                             password='admin123',
                                             phone_number='+911234567890',
                                             username="test_username",
                                             email="test_username@gmail.com")

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
                'username': self.user.email,
                'password': 'admin123'}
        self.user.is_staff = True
        self.user.save()

        response = self.client.post(reverse("oauth2_provider:token"), data=data)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))
        # use this access_token for further interactions
        access_token = content['access_token']

        # get should pass as default scope will be set READ and WRITE
        resp = self.client.get(reverse('users-list'),
                               HTTP_AUTHORIZATION="Bearer {}".format(access_token))
        self.assertEqual(resp.status_code, 200)

    def test_get_access_token_fail(self):
        """
        Get Access token with wrong client_id
        It should fail and should give 401 : invalid_client error
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

        Now use this refresh token to get new Access Token so that we user
        doesnt need to add username and password again
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
        self.user.is_staff = True
        self.user.save()
        resp = self.client.get(reverse('users-list'),
                               HTTP_AUTHORIZATION="Bearer {}".format(content['access_token']))
        self.assertEqual(resp.status_code, 200, resp.content)

    def test_restricted_access(self):
        """
        Get Access token with client_id, client_secret and credentials
        """
        data = {'client_id': self.application.client_id,
                'client_secret': self.application.client_secret,
                'grant_type': 'password',
                'scope': 'read',
                'username': self.user.username,
                'password': 'admin123'}

        response = self.client.post(reverse("oauth2_provider:token"), data=data)

        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content.decode("utf-8"))

        # write should be fail
        resp = self.client.post(reverse('users-list'),
                                HTTP_AUTHORIZATION="Bearer {}".format(content['access_token']),
                                data={'first_name': "test_name",
                                      'last_name': "test_last_name",
                                      'password': 'admin123',
                                      'username': "test_username2"})
        content = json.loads(resp.content.decode("utf-8"))
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(content['detail'], "You do not have permission to perform this action.")

    def test_revoke_access_token(self):
        """
        """
        tok = AccessToken.objects.create(user=self.user,
                                         token='1234567890',
                                         application=self.application,
                                         expires=timezone.now() + datetime.timedelta(days=1),
                                         scope='read write')
        data = {
            'client_id': self.application.client_id,
            'client_secret': self.application.client_secret,
            'token': tok.token,
        }
        response = self.client.post(reverse("oauth2_provider:revoke-token"), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'')
        self.assertFalse(AccessToken.objects.filter(id=tok.id).exists())
