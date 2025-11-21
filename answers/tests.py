from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.core.cache import caches
from rest_framework import status
from rest_framework.test import APITestCase
from answers.models import Answer
from profiles.models import UserProfile
from technologies.models import Technology
from questions.models import Question


class AnswerAPITestCase(APITestCase):

    def setUp(self):
        caches['default'].clear()
        caches['view_cache'].clear()

        Group.objects.create(name='Customer profile')
        self.user = User.objects.create_user(
            username='test1', first_name='test', last_name='profile', password='1234', email='test@gmail.com'
        )
        self.profile1 = UserProfile.objects.create(
            user=self.user, bio='test', avatar=None, expertise='react, django'
        )

        self.user2 = User.objects.create_user(
            username='test3', first_name='test3', last_name='profile3', password='1234', email='test3@gmail.com'
        )
        self.profile2 = UserProfile.objects.create(
            user=self.user2, bio='test3', avatar=None, expertise='Rust, Java'
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

        self.answer1 = Answer.objects.create(
            content='Você precisa fazer isso aqui:',
            author=self.profile2,
            question=self.question1
        )

        self.url_post = reverse('create-answer')
        self.url_details = reverse('answer-details', kwargs={'pk': self.answer1.pk})
        self.url_answer_accepted = reverse('answer-accept', kwargs={'pk': self.answer1.pk})

    def tearDown(self) -> None:
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unaunthenticated_user_cannot_create_answer(self):
        self.client.logout()
        response_post = self.client.post(self.url_post)

        self.assertEqual(response_post.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_answer_successfully(self):
        self.client.force_authenticate(user=self.profile1.user)

        data = {
            "content": "Para você fazer uma lista em Rust, é preciso fazer isso [código]",
            "question": self.question2.pk
        }

        response_post = self.client.post(self.url_post, data, format='json')
        self.assertEqual(response_post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Answer.objects.count(), 2)

        new_answer = Answer.objects.get(
            content="Para você fazer uma lista em Rust, é preciso fazer isso [código]",
            author=self.profile1
        )
        self.assertEqual(new_answer.author, self.profile1)

    def test_create_answer_fails_without_base_information(self):
        self.client.force_authenticate(user=self.profile2.user)

        data_without_content = {
            "question": self.question2.pk
        }

        response1 = self.client.post(self.url_post, data_without_content, format='json')
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)

        data_without_question = {
            "content": "Para você fazer uma lista em Rust, é preciso fazer isso [código]"
        }

        response2 = self.client.post(self.url_post, data_without_question, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_only_owner_can_delete_your_own_answer(self):
        unaunthorized_response = self.client.delete(self.url_details)
        self.assertEqual(unaunthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.profile1.user)
        forbbiden_response = self.client.delete(self.url_details)
        self.assertEqual(forbbiden_response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile2.user)
        response = self.client.delete(self.url_details)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Answer.objects.filter(pk=self.answer1.pk).exists())

    def test_only_owner_question_can_accept_answer(self):
        self.client.force_authenticate(user=self.profile2.user)

        data = {"is_accepted": True}

        response_forbidden = self.client.patch(self.url_answer_accepted, data, format='json')
        self.assertEqual(response_forbidden.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.profile1.user)
        response_ok = self.client.patch(self.url_answer_accepted, data, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

    def test_add_points_when_answer_is_accepted(self):
        self.client.force_authenticate(user=self.profile1.user)
        points_added = self.profile2.reputation_score

        data = {"is_accepted": True}

        response_ok = self.client.patch(self.url_answer_accepted, data, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        self.profile2.refresh_from_db()
        points_added += 20

        self.assertEqual(self.profile2.reputation_score, points_added)

    def test_decrease_points_when_answer_is_deleted(self):
        self.client.force_authenticate(user=self.profile2.user)
        points_decreased = self.profile2.reputation_score

        response_ok = self.client.delete(self.url_details)
        self.assertEqual(response_ok.status_code, status.HTTP_204_NO_CONTENT)

        self.profile2.refresh_from_db()
        points_decreased = max(0, points_decreased - 20)
        self.assertEqual(self.profile2.reputation_score, points_decreased)

    def test_accepting_answer_automatically_marks_question_as_solutioned(self):
        self.assertFalse(self.question1.is_solutioned)

        self.client.force_authenticate(user=self.profile1.user)
        data = {"is_accepted": True}
        response = self.client.patch(self.url_answer_accepted, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.question1.refresh_from_db()

        self.assertTrue(self.question1.is_solutioned)
