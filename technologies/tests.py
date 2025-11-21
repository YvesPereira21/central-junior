from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase
from technologies.models import Technology


class TechnologyAPITestCase(APITestCase):

    def setUp(self):
        caches['default'].clear()
        caches['view_cache'].clear()

        self.admin_user = User.objects.create_superuser(
            username='admin_tech',
            password='123',
            email='admin@tech.com'
        )
        self.user = User.objects.create_user(
            username='user_tech',
            password='123',
            email='user@tech.com'
        )

        self.technology = Technology.objects.create(
            name="Python",
            slug="python",
            color="#3776AB",
            prism_lang="python"
        )

        self.url_create = reverse('technology-create')
        self.url_detail = reverse('technology-detail', kwargs={'pk': self.technology.pk})

    def tearDown(self):
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unauthenticated_user_cannot_create_technology(self):
        data = {"name": "Java", "slug": "java", "color": "#000000"}
        self.client.logout()
        response = self.client.post(self.url_create, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_create_technology(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Java", "slug": "java", "color": "#000000"}

        response = self.client.post(self.url_create, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Garante que não criou no banco
        self.assertFalse(Technology.objects.filter(slug='java').exists())

    def test_admin_user_can_create_technology(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Rust",
            "slug": "rust",
            "color": "#DEA584",
            "prism_lang": "rust"
        }

        response = self.client.post(self.url_create, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Technology.objects.filter(slug='rust').exists())

    def test_create_technology_fails_with_duplicate_name(self):
        self.client.force_authenticate(user=self.admin_user)

        data = {
            "name": "Python",
            "slug": "python-new",
            "color": "#000000"
        }

        response = self.client.post(self.url_create, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_attributes = response.data['errors']
        self.assertIn('name', error_attributes[0]['attr'])

    def test_unauthenticated_user_cannot_see_technology_detail(self):
        self.client.logout()
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_can_see_technology_detail(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.technology.name)

    def test_regular_user_cannot_update_technology(self):
        self.client.force_authenticate(user=self.user)
        data = {"name": "Python Updated", "slug": "python", "color": "#000000"}

        response = self.client.put(self.url_detail, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.technology.refresh_from_db()
        self.assertNotEqual(self.technology.name, "Python Updated")

    def test_admin_user_can_update_technology(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Python 3",
            "slug": "python",
            "color": "#3776AB",
            "prism_lang": "python"
        }

        response = self.client.put(self.url_detail, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.technology.refresh_from_db()
        self.assertEqual(self.technology.name, "Python 3")

    def test_regular_user_cannot_delete_technology(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Technology.objects.filter(pk=self.technology.pk).exists())

    def test_admin_user_can_delete_technology(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Technology.objects.filter(pk=self.technology.pk).exists())
