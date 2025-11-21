from django.urls import reverse
from django.core.cache import caches
from django.contrib.auth.models import User, Group
from rest_framework import status
from rest_framework.test import APITestCase
from articles.models import Article
from profiles.models import UserProfile
from technologies.models import Technology


class ArticleAPITestCase(APITestCase):

    def setUp(self) -> None:
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
            user=self.user2, bio='test3', avatar=None, expertise='java, angular'
        )

        self.techonology1 = Technology.objects.create(name='Python', slug='python', color="#FEF60F")
        self.techonology2 = Technology.objects.create(name='Django', slug='django', color='#0C7005')
        self.techonology3 = Technology.objects.create(name='React', slug='react', color='#09C8B1')

        self.article1 = Article.objects.create(
            title='Como fazer autenticação no django', content='Para fazer a autenticação no django, comece com',
            author=self.profile1
        )
        self.article1.technologies.set([self.techonology1, self.techonology2])
        self.article2 = Article.objects.create(
            title='Como centralizar div no React', content='A div se centraliza com esse comando no react',
            author=self.profile2
        )
        self.article2.technologies.set([self.techonology3])

        self.url_post = reverse('create-article')
        self.url_details = reverse('article-details', kwargs={'pk': self.article2.pk})
        self.like_url = reverse('like-article', kwargs={'pk': self.article1.pk})

    def tearDown(self) -> None:
        caches['default'].clear()
        caches['view_cache'].clear()

    def test_unaunthenticated_user_cannot_create_article(self):
        response = self.client.post(self.url_post)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_article_is_published(self):
        self.client.force_authenticate(user=self.profile1.user)

        response = self.client.get(self.url_post, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_see_list_of_articles(self):
        self.client.logout()
        response = self.client.get(self.url_post, format='json')

        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_can_see_article_detail(self):
        response = self.client.get(self.url_details)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.article2.title)

    def test_other_user_cannot_delete_author_article(self):
        self.client.force_authenticate(user=self.profile1.user)

        response = self.client.delete(self.url_details)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Article.objects.filter(pk=self.article2.pk).exists())

    def test_owner_article_can_delete_article(self):
        self.client.force_authenticate(user=self.profile2.user)

        response = self.client.delete(self.url_details)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(pk=self.article2.pk).exists())

    def test_article_created_increased_reputation_to_author(self):
        self.client.force_authenticate(user=self.profile2.user)

        initial_score = self.profile2.reputation_score
        data = {
            "title": "Como utilizar o Celery no Django",
            "content": "Para utilizar o Celery, siga os passos",
            "technologies": [self.techonology1.pk, self.techonology2.pk]
            }

        response = self.client.post(self.url_post, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.profile2.refresh_from_db()

        expected_score = initial_score + 20
        self.assertEqual(self.profile2.reputation_score, expected_score)

    def test_article_deleted_decreased_reputation_author(self):
        self.client.force_authenticate(user=self.profile2.user)

        response = self.client.delete(self.url_details)

        self.profile2.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Article.objects.filter(pk=self.article2.pk).exists())
        self.assertGreaterEqual(self.profile2.reputation_score, 0)

    def test_unauthenticated_user_cannot_like_article(self):
        like_url = reverse('like-article', kwargs={'pk': self.article1.pk})

        self.client.logout()
        response = self.client.post(like_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.article1.refresh_from_db()
        self.assertEqual(self.article1.likes.count(), 0)

    def test_authenticated_user_can_like_article(self):
        self.client.force_authenticate(user=self.profile2.user)
        response = self.client.post(self.like_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 1)

        self.article1.refresh_from_db()
        self.assertTrue(self.profile2 in self.article1.likes.all())
        self.assertEqual(self.article1.likes.count(), 1)

    def test_authenticated_user_can_unlike_article(self):
        self.article1.likes.add(self.profile2)
        self.article1.refresh_from_db()
        self.assertEqual(self.article1.likes.count(), 1)

        self.client.force_authenticate(user=self.profile2.user)
        response = self.client.post(self.like_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['likes_count'], 0)

        self.article1.refresh_from_db()
        self.assertFalse(self.profile2 in self.article1.likes.all())
        self.assertEqual(self.article1.likes.count(), 0)

    def test_article_list_is_cached_and_invalidated_on_create(self):
        self.client.force_authenticate(user=self.profile1.user)
        list_url = reverse('create-article')

        self.client.get(list_url, format='json')
        cached_data_before_post = caches['view_cache'].get("list_article")
        self.assertIsNotNone(cached_data_before_post)

        new_article_data = {
            "title": "Artigo Novo Cache",
            "content": "Conteúdo que quebra o cache",
            "technologies": [self.techonology3.pk]
        }
        self.client.post(list_url, new_article_data, format='json')

        cached_data_after_post = caches['view_cache'].get("list_article")
        self.assertIsNone(cached_data_after_post)

        response2 = self.client.get(list_url, format='json')
        self.assertEqual(len(response2.data['results']), 3)

        cached_data_after_reload = caches['view_cache'].get("list_article")
        self.assertIsNotNone(cached_data_after_reload)

    def test_question_detail_is_cached(self):
        self.client.force_authenticate(user=self.profile2.user)
        article_detail = reverse('article-details', kwargs={"pk": self.article1.pk})

        response_ok = self.client.get(article_detail, format='json')
        self.assertEqual(response_ok.status_code, status.HTTP_200_OK)

        question_cached = caches['view_cache'].get(f"article_{self.article1.pk}")

        self.assertIsNotNone(question_cached)
        self.assertEqual(question_cached['title'], self.article1.title)
