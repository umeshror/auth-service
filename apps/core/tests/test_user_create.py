from django.urls import reverse
from rest_framework.test import APITestCase


class TestCreateUserAPI(APITestCase):
    def test_get_create_api(self):
        resp = self.client.post(reverse('user-create'),
                                data={'first_name': "test_name",
                                      'email': "first_name@example.com",
                                      'phone_number': 9876543210,
                                      'last_name': "test_last_name",
                                      'password': 'admin123'})
        self.assertEqual(resp.status_code, 201)
