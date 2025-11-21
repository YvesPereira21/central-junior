from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationAPITestCase(APITestCase):

    def setUp(self):
        cache.clear()

        self.user = User.objects.create_user(
            username='test_auth',
            password='strong_password_123',
            email='auth@test.com'
        )

        self.url_login = reverse('token_obtain_pair')
        self.url_refresh = reverse('token_refresh')
        self.url_logout = reverse('auth_logout')

    def tearDown(self):
        cache.clear()

    def test_user_can_login_and_get_tokens(self):
        data = {
            "username": "test_auth",
            "password": "strong_password_123"
        }

        response_ok = self.client.post(self.url_login, data, format='json')

        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response_ok.data)
        self.assertIn('access', response_ok.data)

    def test_logout_adds_token_to_blacklist_cache(self):
        login_response = self.client.post(self.url_login, {
            'username': 'test_auth', 'password': 'strong_password_123'
        }, format='json')

        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        data = {"refresh": refresh_token}

        response_ok = self.client.post(self.url_logout, data, format='json')

        self.assertEqual(response_ok.status_code, status.HTTP_204_NO_CONTENT)

        get_token = RefreshToken(refresh_token)
        get_jti = get_token['jti']

        cache_key = f"blacklist: {get_jti}"

        in_blacklist = cache.get(cache_key)

        self.assertTrue(in_blacklist)

    def test_cannot_refresh_token_if_blacklisted(self):
        login_response = self.client.post(self.url_login, {
            "username": "test_auth",
            "password": "strong_password_123"
        })
        refresh_token = login_response.data['refresh']
        access_token = login_response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.client.post(self.url_logout, {"refresh": refresh_token})

        self.client.credentials()
        response = self.client.post(self.url_refresh, {"refresh": refresh_token})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
