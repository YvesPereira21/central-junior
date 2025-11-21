from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase
from credentials.models import Credential
from profiles.models import UserProfile


class CredentialAPITestCase(APITestCase):

    def setUp(self):
        caches['default'].clear()
        caches['view_cache'].clear()

        self.admin_user = User.objects.create_superuser(
            username='admin1',
            password='1234',
            email='admin@gmail.com'
        )

        self.user = User.objects.create_user(
            username='test_cred',
            password='123',
            email='cred@test.com',
            first_name='Dev',
            last_name='Júnior'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            bio='Bio teste',
            expertise='Python'
        )

        self.user2 = User.objects.create_user(
            username='test_cred2',
            password='123',
            email='cred2@test.com',
            first_name='Dev',
            last_name='Sênior'
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2,
            bio='Bio teste',
            expertise='Python'
        )

        self.credential_academic = Credential.objects.create(
            profile=self.profile,
            role="Ciência da Computação",
            type_credential="GRA",
            experience="JR",
            institution="Universidade Federal",
            start_date="2019-01-01",
            end_date="2023-12-01",
        )

        self.credential_professional = Credential.objects.create(
            profile=self.profile2,
            role="Desenvolvedor Backend",
            type_credential="PRO",
            experience="SR",
            institution="Tech Solutions",
            start_date="2024-01-01",
        )

        self.url_create = reverse('credential-create')
        self.url_detail = reverse('credential-details', kwargs={'pk': self.credential_professional.pk})
        self.url_validate_credential = reverse('credential-validate', kwargs={'pk': self.credential_professional.pk})

    def tearDown(self):
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unaunthenticated_user_cannot_create_credential(self):
        data = {
            "profile": self.profile.pk,
            "role": "Ciência da Computação",
            "type_credential": "GRA",
            "experience": "JR",
            "institution": "Universidade Federal",
            "start_date": "2019-01-01",
            "end_date": "2023-12-01"
        }

        response_unaunthorized = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response_unaunthorized.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_credential_successfully(self):
        self.client.force_authenticate(user=self.profile2.user)
        data = {
            "role": "Cybersegurança",
            "type_credential": "PRO",
            "experience": "PL",
            "institution": "Bug bounty",
            "start_date": "2019-01-01",
            "end_date": "2024-11-21"
        }

        response_created = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response_created.status_code, status.HTTP_201_CREATED)

        self.profile2.refresh_from_db()

        new_post = Credential.objects.get(institution="Bug bounty", profile=self.profile2)
        self.assertEqual(new_post.profile, self.profile2)
        self.assertEqual(Credential.objects.filter(profile=self.profile2).count(), 2)

    def test_create_credential_fails_without_base_information(self):
        self.client.force_authenticate(user=self.profile.user)

        data_without_role_and_start_date = {
            "type_credential": "PRO",
            "experience": "PL",
            "institution": "Bug bounty",
            "end_date": "2024-11-21"
        }
        response_fail1 = self.client.post(self.url_create, data_without_role_and_start_date, format='json')
        self.assertEqual(response_fail1.status_code, status.HTTP_400_BAD_REQUEST)

        data_without_institution_type_credential_and_experience = {
            "start_date": "2019-01-01",
            "end_date": "2024-11-21"
        }
        response_fail2 = self.client.post(self.url_create, data_without_institution_type_credential_and_experience, format='json')
        self.assertEqual(response_fail2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_credential_fails_with_invalid_choices(self):
        self.client.force_authenticate(user=self.profile.user)

        data_invalid_choices = {
            "role": "Security Analyst",
            "institution": "HackerOne",
            "start_date": "2023-01-01",
            "type_credential": "MASTER_DEGREE",
            "experience": "MEGA_SENIOR"
        }

        response = self.client.post(self.url_create, data_invalid_choices, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_attributes = [error['attr'] for error in response.data['errors']]

        self.assertIn('type_credential', error_attributes)
        self.assertIn('experience', error_attributes)

    def test_create_credential_fails_without_valid_date(self):
        self.client.force_authenticate(user=self.profile.user)

        data_without_role_and_start_date = {
            "role": "Cybersegurança",
            "type_credential": "PRO",
            "experience": "PL",
            "institution": "Bug bounty",
            "start_date": "2027-03-01",
        }
        response_fail1 = self.client.post(self.url_create, data_without_role_and_start_date, format='json')
        self.assertEqual(response_fail1.status_code, status.HTTP_400_BAD_REQUEST)

        data_without_institution_type_credential_and_experience = {
            "role": "Cybersegurança",
            "type_credential": "PRO",
            "experience": "PL",
            "institution": "Bug bounty",
            "start_date": "2030-08-17",
            "end_date": "2024-11-21"
        }
        response_fail2 = self.client.post(self.url_create, data_without_institution_type_credential_and_experience, format='json')
        self.assertEqual(response_fail2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_see_your_own_unique_credential(self):
        response_unauthorized = self.client.get(self.url_detail)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile.user)
        response_forbidden = self.client.get(self.url_detail)
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile2.user)
        response_ok = self.client.get(self.url_detail)
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

    def test_only_owner_can_delete_your_own_credential(self):
        response_unauthorized = self.client.delete(self.url_detail)
        self.assertEqual(response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile.user)
        response_forbidden = self.client.delete(self.url_detail)
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile2.user)
        response_no_content = self.client.delete(self.url_detail)
        self.assertEqual(response_no_content.status_code, status.HTTP_204_NO_CONTENT)

    def test_only_owner_can_update_your_own_credential(self):
        data_update = {
            "role": "Cybersecurity",
            "type_credential": "PRO",
            "experience": "SR",
            "institution": "Big bount"
        }

        response_unauthorized = self.client.put(self.url_detail, data_update, format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile.user)
        response_forbidden = self.client.put(self.url_detail, data_update, format='json')
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile2.user)
        response_ok = self.client.put(self.url_detail, data_update, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

    def test_only_admin_can_verify_user_credential(self):
        self.client.logout()
        response_unauthorized = self.client.patch(self.url_validate_credential, {"is_verified": True}, format='json')
        self.assertEqual(response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile2.user)
        response_forbidden = self.client.patch(self.url_validate_credential, {"is_verified": True}, format='json')
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.admin_user)
        response_ok = self.client.patch(self.url_validate_credential, {"is_verified": True}, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        self.credential_professional.refresh_from_db()
        self.assertTrue(self.credential_professional.is_verified)

    def test_owner_cannot_update_your_own_credential_verified(self):
        self.client.force_authenticate(user=self.admin_user)

        response_ok = self.client.patch(self.url_validate_credential, {"is_verified": True}, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        self.credential_professional.refresh_from_db()
        self.assertTrue(self.credential_professional.is_verified)

        self.client.force_authenticate(user=self.profile2.user)

        data_update = {
            "role": "Cybersecurity",
            "type_credential": "PRO",
            "experience": "SR",
            "institution": "Big bount"
        }

        response_conflict = self.client.put(self.url_detail, data_update, format='json')
        self.assertEqual(response_conflict.status_code, status.HTTP_409_CONFLICT)

    def test_credential_verified_turn_user_to_professional(self):
        self.client.force_authenticate(user=self.admin_user)
        response_ok = self.client.patch(self.url_validate_credential, {"is_verified": True}, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        self.profile2.refresh_from_db()
        self.assertTrue(self.profile2.is_professional)

        self.client.force_authenticate(user=self.profile2.user)

        response_no_content = self.client.delete(self.url_detail)
        self.assertEqual(response_no_content.status_code, status.HTTP_204_NO_CONTENT)

        self.profile2.refresh_from_db()
        self.assertFalse(self.profile2.is_professional)

    def test_professional_status_persists_after_deleting_one_of_multiple_verified_credentials(self):
        cred1 = Credential.objects.create(
            profile=self.profile2,
            role="Dev Senior",
            type_credential="PRO",
            experience="SR",
            institution="Google",
            start_date="2020-01-01",
            is_verified=False
        )
        url_validate_1 = reverse('credential-validate', kwargs={'pk': cred1.pk})

        self.client.force_authenticate(user=self.admin_user)
        self.client.patch(url_validate_1, {"is_verified": True}, format='json')

        self.client.force_authenticate(user=self.profile2.user)
        data = {
            "role": "Cybersegurança",
            "type_credential": "PRO",
            "experience": "PL",
            "institution": "Bug bounty",
            "start_date": "2019-01-01",
            "end_date": "2024-11-21",
        }

        response_created = self.client.post(self.url_create, data, format='json')
        self.assertEqual(response_created.status_code, status.HTTP_201_CREATED)

        self.profile2.refresh_from_db()
        credential2 = Credential.objects.get(institution='Bug bounty', profile=self.profile2)

        url_get = reverse('credential-details', kwargs={'pk': credential2.pk})
        url_validate = reverse('credential-validate', kwargs={'pk': credential2.pk})

        self.client.force_authenticate(user=self.admin_user)
        response_ok = self.client.patch(url_validate, {"is_verified": True}, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.profile2.user)
        response_no_content = self.client.delete(url_get)
        self.assertEqual(response_no_content.status_code, status.HTTP_204_NO_CONTENT)

        self.profile2.refresh_from_db()
        self.assertTrue(self.profile2.is_professional)

    def test_pontuation_was_added_to_user_with_verified_credential(self):
        cred1 = Credential.objects.create(
            profile=self.profile,
            role="Dev Senior",
            type_credential="PRO",
            experience="SR",
            institution="Google",
            start_date="2020-01-01",
            is_verified=False
        )
        url_validate_1 = reverse('credential-validate', kwargs={'pk': cred1.pk})

        self.client.force_authenticate(user=self.admin_user)
        self.client.patch(url_validate_1, {"is_verified": True}, format='json')

        self.profile.refresh_from_db()
        self.assertGreaterEqual(self.profile.reputation_score, 500)

    def test_pontuation_was_removed_to_user_with_verified_credential(self):
        cred1 = Credential.objects.create(
            profile=self.profile,
            role="Dev Senior",
            type_credential="PRO",
            experience="SR",
            institution="Google",
            start_date="2020-01-01",
            is_verified=False
        )
        url_validate_1 = reverse('credential-validate', kwargs={'pk': cred1.pk})
        url_detail_1 = reverse('credential-details', kwargs={'pk': cred1.pk})

        self.client.force_authenticate(user=self.admin_user)
        self.client.patch(url_validate_1, {"is_verified": True}, format='json')

        self.profile.refresh_from_db()
        score_before_delete = self.profile.reputation_score

        self.assertGreater(score_before_delete, 0)

        self.client.force_authenticate(user=self.profile.user)
        self.client.delete(url_detail_1)

        self.profile.refresh_from_db()

        expected_score = max(0, score_before_delete - 500)
        self.assertEqual(self.profile.reputation_score, expected_score)
