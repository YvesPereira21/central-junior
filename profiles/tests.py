from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase
from profiles.models import UserProfile


class ProfileAPITestCase(APITestCase):

    def setUp(self):
        caches['default'].clear()
        caches['view_cache'].clear()

        self.admin_user = User.objects.create_superuser(
            username='admin1',
            password='1234',
            email='admin@gmail.com'
        )

        Group.objects.create(name='Customer profile')
        self.user = User.objects.create_user(
            username='test1',
            first_name='test',
            last_name='profile',
            password='1234',
            email='test@gmail.com'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='test',
            avatar=None,
            expertise='react, django'
        )

        self.user2 = User.objects.create_user(
            username='test3',
            first_name='test3',
            last_name='profile3',
            password='1234',
            email='test3@gmail.com'
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2,
            bio='test3',
            avatar=None,
            expertise='java, angular'
        )

        self.url = reverse('details-profile', kwargs={'pk': self.profile.pk})

    def tearDown(self) -> None:
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_profile(self):
        url = reverse('create-profile')
        create_profile = {
            "user": {
                "username": "test2",
                "first_name": "test_2",
                "last_name": "profile",
                "password": "2345",
                "email": "test2@gmail.com"
            },
            "bio": "Meu nome é test2 e trabalho como desenvolvedor junior na empresa da Netshoes",
            "expertise": "Java, Redis, AWS",
        }

        response = self.client.post(url, create_profile, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_profile(self):
        self.client.force_authenticate(user=self.profile.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], self.user.first_name)

        self.assertEqual(response.data["articles_written"], 0)
        self.assertEqual(response.data["answers_accepted"], 0)

    def test_only_owner_can_update(self):
        self.client.force_authenticate(user=self.profile.user)
        data = {"bio": "trabalho com cibersegurança"}

        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, "trabalho com cibersegurança")

    def test_other_user_cannot_update_profile(self):
        self.client.force_authenticate(user=self.profile2.user)
        data = {"bio": "trabalho como engenheiro de software"}

        response = self.client.patch(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.profile.refresh_from_db()
        self.assertNotEqual(self.profile.bio, "trabalho como engenheiro de software")
        self.assertEqual(self.profile.bio, "test")

    def test_only_owner_can_delete(self):
        self.client.force_authenticate(user=self.profile.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserProfile.objects.filter(pk=self.profile.pk).exists())

    def test_other_user_cannot_delete_profile(self):
        self.client.force_authenticate(user=self.profile2.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(UserProfile.objects.filter(pk=self.profile.pk).exists())

    def test_reputation_score_update(self):
        self.assertEqual(self.profile.level, 'Iniciante')

        self.profile.reputation_score = 500
        self.profile.save()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.level, 'Intermediário')

        self.profile.reputation_score = 1000
        self.profile.save()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.level, 'Especialista')

        self.profile.reputation_score = 2000
        self.profile.save()

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.level, 'Elite')
