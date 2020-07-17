from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import User


class TestTokenAuthentication(APITestCase):
    """ Test token auth """

    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             email='test_username@test_username.com',
                                             password='admin123',
                                             last_name="test_last_name",
                                             username="test_username")

    def test_401(self):
        """
        For any user without Token auth should give HTTP 401 Unauthorized error
        :return:
        """

        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 401)

    def test_get_token(self):
        """
        Request with valid token should give HTTP 200
        """
        self.user.is_staff = True
        self.user.save()
        data = {'username': self.user.email,
                'password': 'admin123'}

        response = self.client.post(reverse("api_token_auth"), data=data)
        content = response.json()
        token = content['token']

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 200)
