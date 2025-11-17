from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import caches
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema
from articles.models import Article
from articles.serializers import ArticleModelSerializer, ArticleDetailModelSerializer
from articles.filters import ArticleFilter
from profiles.models import UserProfile
from profiles.permissions import IsOwner


cache_view = caches['view_cache']

@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ArticleFilter
    search_fields = ['title', 'content']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleModelSerializer

        return ArticleDetailModelSerializer

    def list(self, request, *args, **kwargs):
        key = "list_article"
        cached_data = cache_view.get(key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().list(request, *args, **kwargs)
        cache_view.set(key, response.data, timeout=settings.CACHE_TTL)
        return response

    def perform_create(self, serializer):
        user = self.request.user
        get_user = UserProfile.objects.get(user=user)

        if get_user:
            serializer.save(author=get_user)

        cache_view.delete("list_article")

@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailModelSerializer

    def retrieve(self, request,*args, **kwargs):
        pk = self.kwargs.get('pk')
        key = f"article_{pk}"
        cached_data = cache_view.get(key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        response = super().retrieve(request, *args, **kwargs)
        cache_view.set(key, response.data, timeout=settings.CACHE_TTL)

        return response

    def destroy(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')

        response = super().destroy(request, *args, **kwargs)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            cache_view.delete("list_article")
            cache_view.delete(f"article_{pk}")

        return response

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsOwner()]

@extend_schema(
    tags=['Article (Artigo)']
)
class ArticleToggleView(generics.GenericAPIView):
    queryset = Article.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.Serializer

    def post(self, request, *args, **kwargs):
        article = self.get_object()
        profile = request.user.profile

        if profile in article.likes.all():
            article.likes.remove(profile)
        else:
            article.likes.add(profile)
        
        return Response({"likes_count": article.likes.count()}, status=status.HTTP_200_OK)
