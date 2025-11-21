from django.urls import reverse
from django.core.cache import caches
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from questions.models import Question
from answers.models import Answer
from profiles.models import UserProfile
from technologies.models import Technology


class QuestionAPITestCase(APITestCase):

    def setUp(self) -> None:
        Group.objects.create(name='Customer profile')
        self.user = User.objects.create_user(
            username='test1',
            first_name='test',
            last_name='profile',
            password='1234',
            email='test@gmail.com'
        )
        self.profile1 = UserProfile.objects.create(
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
            expertise='Rust, Java'
        )

        self.user3 = User.objects.create_user(
            username='test4',
            first_name='test4',
            last_name='profile4',
            password='1234',
            email='test4@gmail.com'
        )
        self.profile3 = UserProfile.objects.create(
            user=self.user3,
            bio='test4',
            avatar=None,
            expertise='Django rest framework'
        )

        self.techonology1 = Technology.objects.create(name='Python', slug='python', color="#FEF60F")
        self.techonology2 = Technology.objects.create(name='Django', slug='django', color='#0C7005')
        self.techonology3 = Technology.objects.create(name='Rust', slug='rust', color="#DC7F14")

        self.question1 = Question.objects.create(
            title='Autenticação no django',
            content='Estou querendo melhorar meu código para que a autenticação...',
            profile=self.profile1
        )
        self.question1.technologies.set([self.techonology1, self.techonology2])
        self.question2 = Question.objects.create(
            title='Lista em Rust',
            content='Vim do Java e estava tentando fazer uma lista em Rust e não estou conseguindo',
            profile=self.profile2
        )
        self.question2.technologies.set([self.techonology3])

        self.answer = Answer.objects.create(
            content='Você precisa fazer isso aqui:', author=self.profile2, 
            question=self.question1
        )

        self.url_create_list_question = reverse('create-question')
        self.url_detail_question = reverse('detail-question', kwargs={"pk": self.question1.pk})
        self.url_like_question = reverse('like-question', kwargs={"pk": self.question1.pk})

    def tearDown(self) -> None:
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unaunthenticated_user_cannot_create_question(self):
        self.client.logout()
        response_post = self.client.post(self.url_create_list_question)

        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_question_successfully(self):
        self.client.force_authenticate(user=self.profile2.user)

        data = {
            "title": "Como usar Docker com Django?",
            "content": "Estou tendo dificuldades com o Dockerfile...",
            "technologies": [self.techonology1.pk, self.techonology2.pk]
        }

        response = self.client.post(self.url_create_list_question, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Question.objects.count(), 3)

        new_question = Question.objects.get(title="Como usar Docker com Django?")
        self.assertEqual(new_question.profile, self.profile2)

    def test_create_question_fails_without_base_information(self):
        self.client.force_authenticate(user=self.profile1.user)

        data_without_title_and_technology = {
            "content": "Estou com dúvida por que essa linha de código não funciona"
        }

        response1 = self.client.post(self.url_create_list_question, data_without_title_and_technology, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        data_without_content = {
            "title": "Como fazer um fatiamento de string em Rust",
            "technologies": [self.techonology3.pk]
        }

        response2 = self.client.post(self.url_create_list_question, data_without_content, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anyone_can_list_question(self):
        self.client.logout()
        response = self.client.get(self.url_create_list_question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_anyone_can_see_question_details(self):
        response = self.client.get(self.url_detail_question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_see_question_not_published(self):
        self.client.force_authenticate(user=self.profile1.user)

        data = {"is_published": False}

        patch_response = self.client.patch(self.url_detail_question, data, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        self.question1.refresh_from_db()
        self.assertFalse(self.question1.is_published)

        response = self.client.get(self.url_detail_question)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_only_owner_can_delete_your_own_question(self):
        data = {"is_published": False}

        unaunthorized_response = self.client.patch(self.url_detail_question, data, format='json')
        self.assertEqual(unaunthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile2.user)
        forbbiden_response = self.client.patch(self.url_detail_question, data, format='json')
        self.assertEqual(forbbiden_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile1.user)
        response = self.client.patch(self.url_detail_question, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.question1.refresh_from_db()
        self.assertTrue(Question.objects.filter(pk=self.question1.pk, is_published=False))

    def test_delete_question_removes_points_from_accepted_answer_author(self):
        url_accept = reverse('answer-accept', kwargs={'pk': self.answer.pk})

        self.client.force_authenticate(user=self.profile1.user)
        initial_points = self.profile2.reputation_score
        self.client.patch(url_accept, {"is_accepted": True}, format='json')

        self.profile2.refresh_from_db()
        points = initial_points + 20
        self.assertEqual(self.profile2.reputation_score, points)

        self.client.delete(self.url_detail_question)

        self.profile2.refresh_from_db()
        points_after_delete = points - 20
        self.assertEqual(self.profile2.reputation_score, points_after_delete)

    def test_authenticated_user_can_like_question(self):
        self.client.force_authenticate(user=self.profile2.user)
        response = self.client.post(self.url_like_question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

        self.question1.refresh_from_db()
        self.assertTrue(self.profile2 in self.question1.likes.all())
        self.assertEqual(self.question1.likes.count(), 1)

    def test_authenticated_user_can_unlike_question(self):
        self.question1.likes.add(self.profile2)
        self.question1.refresh_from_db()
        self.assertEqual(self.question1.likes.count(), 1)

        self.client.force_authenticate(user=self.profile2.user)
        response = self.client.post(self.url_like_question)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 0)

        self.question1.refresh_from_db()
        self.assertFalse(self.profile2 in self.question1.likes.all())
        self.assertEqual(self.question1.likes.count(), 0)

    def test_question_list_is_cached_and_invalidated_on_create(self):
        self.client.force_authenticate(user=self.profile1.user)
        list_question_url = reverse('create-question')

        self.client.get(list_question_url, format='json')
        cached_data_before_post = caches['view_cache'].get("list_all_question_published")
        self.assertIsNotNone(cached_data_before_post)

        new_question_data = {
            "title": "Pergunta Novo Cache",
            "content": "Conteúdo que quebra o cache",
            "technologies": [self.techonology3.pk]
        }
        self.client.post(list_question_url, new_question_data, format='json')

        cached_data_after_post = caches['view_cache'].get("list_all_question_published")
        self.assertIsNone(cached_data_after_post)

        response2 = self.client.get(list_question_url, format='json')
        self.assertEqual(len(response2.data['results']), 3)

        cached_data_after_reload = caches['view_cache'].get("list_all_question_published")
        self.assertIsNotNone(cached_data_after_reload)

    def test_question_detail_is_cached(self):
        self.client.force_authenticate(user=self.profile1.user)
        question_detail = reverse('detail-question', kwargs={"pk": self.question1.pk})

        response_ok = self.client.get(question_detail, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        question_cached = caches['view_cache'].get(f"question_detail_{self.question1.pk}")

        self.assertIsNotNone(question_cached)
        self.assertEqual(question_cached['title'], self.question1.title)
