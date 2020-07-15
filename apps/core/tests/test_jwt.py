from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import User


class TestJWT(APITestCase):
    """ Test token auth """

    def setUp(self):
        self.user = User.objects.create_user(first_name="test_name",
                                             last_name="test_last_name",
                                             password='admin123',
                                             username='test_username',
                                             email="test_username@gmail.com")

    def test_401(self):
        """
        For any user without JWT Token auth should give HTTP 401 Unauthorized error
        :return:
        """
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 401)

    def test_200(self):
        """
        Request with valid token should give HTTP 200
        """
        self.user.is_staff = True
        self.user.save()
        data = {'email': self.user.email,
                'password': 'admin123'}

        response = self.client.post(reverse("jwt_token_obtain_pair"), data=data)
        content = response.json()
        self.assertTrue('refresh' in content)
        self.assertTrue('access' in content)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + content['access'])
        response = self.client.get(reverse('users-list'))
        self.assertEqual(response.status_code, 200)

    def test_refresh_token(self):
        """
        Request with valid token should give HTTP 200
        """
        data = {'email': self.user.email,
                'password': 'admin123'}

        response = self.client.post(reverse("jwt_token_obtain_pair"), data=data)
        content = response.json()
        response = self.client.post(reverse("jwt_token_refresh"), data={
            'refresh': content['refresh']
        })
        content = response.json()
        self.assertTrue('access' in content)
