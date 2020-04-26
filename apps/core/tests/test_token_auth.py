from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from apps.core.models import User


class TestTokenAuthentication(APITestCase):
    """ Test token auth """

    def setUp(self):
        self.user = User.objects.create(first_name="test_name",
                                        last_name="test_last_name",
                                        username="test_username")

    def test_401(self):
        """
        For any user without Token auth should give HTTP 401 Unauthorized error
        :return:
        """
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 401)

    def test_200(self):
        """
        Request with valid token should give HTTP 200
        :return:
        """
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 200)
